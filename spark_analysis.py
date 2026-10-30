
import os
import sys
import json
import pymysql
from dotenv import load_dotenv

load_dotenv()   

from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, avg, sum as spark_sum, max as spark_max,
    min as spark_min, when, count, round as spark_round
)
from pyspark.sql.types import (
    StructType, StructField, IntegerType,
    StringType, DoubleType
)


# Use the Python interpreter running this script
python_path = sys.executable
os.environ["PYSPARK_PYTHON"] = python_path
os.environ["PYSPARK_DRIVER_PYTHON"] = python_path


def get_mysql_connection():
    return pymysql.connect(
        host=os.getenv("DB_HOST", "127.0.0.1"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME", "student_performance"),
        cursorclass=pymysql.cursors.DictCursor
    )


def fetch_database_data():
    connection = get_mysql_connection()

    try:
        with connection.cursor() as cursor:

            cursor.execute("""
                SELECT id, name, register_number, department
                FROM student
                ORDER BY id
            """)
            students = cursor.fetchall()

            cursor.execute("""
                SELECT
                    m.student_id,
                    s.name AS student_name,
                    s.register_number,
                    m.subject_id,
                    sub.name AS subject_name,
                    m.score,
                    sub.max_marks,
                    sub.pass_mark
                FROM mark m
                JOIN student s ON m.student_id = s.id
                JOIN subject sub ON m.subject_id = sub.id
                ORDER BY m.student_id, m.subject_id
            """)
            marks = cursor.fetchall()

        return students, marks

    finally:
        connection.close()


def analyze_with_spark(students, marks):

    
    spark = SparkSession.builder \
            .appName("StudentPerformanceAnalytics") \
            .master("local[2]") \
            .config("spark.driver.host", "127.0.0.1") \
            .config("spark.driver.bindAddress", "127.0.0.1") \
            .config("spark.default.parallelism", "2") \
            .config("spark.sql.shuffle.partitions", "2") \
    .getOrCreate()


    spark.sparkContext.setLogLevel("ERROR")

    try:
        # Explicit schema also supports empty tables
        mark_schema = StructType([
            StructField("student_id", IntegerType(), False),
            StructField("student_name", StringType(), True),
            StructField("register_number", StringType(), True),
            StructField("subject_id", IntegerType(), False),
            StructField("subject_name", StringType(), True),
            StructField("score", DoubleType(), False),
            StructField("max_marks", IntegerType(), False),
            StructField("pass_mark", IntegerType(), False)
        ])

        mark_rows = [
            (
                int(m["student_id"]),
                m["student_name"],
                m["register_number"],
                int(m["subject_id"]),
                m["subject_name"],
                float(m["score"]),
                int(m["max_marks"]),
                int(m["pass_mark"])
            )
            for m in marks
        ]

        df = spark.createDataFrame(mark_rows, mark_schema)

        student_results = []

        if not df.isEmpty():

            # Student-wise analysis
            student_df = (
                df.groupBy(
                    "student_id",
                    "student_name",
                    "register_number"
                )
                .agg(
                    spark_sum("score").alias("total_marks"),
                    spark_sum("max_marks").alias("total_max_marks"),
                    avg("score").alias("average_marks"),
                    spark_sum(
                        when(col("score") >= col("pass_mark"), 1)
                        .otherwise(0)
                    ).alias("passed_subjects"),
                    count("*").alias("total_subjects")
                )
                .withColumn(
                    "percentage",
                    spark_round(
                        col("total_marks") /
                        col("total_max_marks") * 100, 2
                    )
                )
                .withColumn(
                    "status",
                    when(
                        col("passed_subjects") == col("total_subjects"),
                        "Pass"
                    ).otherwise("Fail")
                )
            )

            for row in student_df.collect():
                student_results.append({
                    "student_id": row["student_id"],
                    "student_name": row["student_name"],
                    "register_number": row["register_number"],
                    "total_marks": round(float(row["total_marks"]), 2),
                    "total_max_marks": float(row["total_max_marks"]),
                    "average_marks": round(float(row["average_marks"]), 2),
                    "percentage": float(row["percentage"]),
                    "status": row["status"]
                })

            # Subject-wise analysis
            subject_df = (
                df.groupBy("subject_id", "subject_name")
                .agg(
                    count("*").alias("students_count"),
                    avg("score").alias("average_marks"),
                    avg(
                        col("score") / col("max_marks") * 100
                    ).alias("average_percentage"),
                    spark_max("score").alias("highest_marks"),
                    spark_min("score").alias("lowest_marks"),
                    avg(
                        when(col("score") >= col("pass_mark"), 1.0)
                        .otherwise(0.0)
                    ).alias("pass_percentage")
                )
            )

            subject_results = []

            for row in subject_df.collect():
                subject_results.append({
                    "subject_id": row["subject_id"],
                    "subject_name": row["subject_name"],
                    "students_count": row["students_count"],
                    "average_marks": round(float(row["average_marks"]), 2),
                    "average_percentage": round(
                        float(row["average_percentage"]), 2
                    ),
                    "highest_marks": float(row["highest_marks"]),
                    "lowest_marks": float(row["lowest_marks"]),
                    "pass_percentage": round(
                        float(row["pass_percentage"]) * 100, 2
                    )
                })

        else:
            subject_results = []

        # Include students who have not received marks
        evaluated_ids = {
            student["student_id"] for student in student_results
        }

        for student in students:
            if student["id"] not in evaluated_ids:
                student_results.append({
                    "student_id": student["id"],
                    "student_name": student["name"],
                    "register_number": student["register_number"],
                    "total_marks": 0,
                    "total_max_marks": 0,
                    "average_marks": 0,
                    "percentage": 0,
                    "status": "Not Evaluated"
                })

        student_results.sort(key=lambda x: x["student_id"])

        weak_subjects = [
            subject for subject in subject_results
            if subject["average_percentage"] < 50
            or subject["pass_percentage"] < 60
        ]

        return {
            "students": student_results,
            "subjects": subject_results,
            "weak_subjects": weak_subjects
        }

    finally:
        spark.stop()


if __name__ == "__main__":
    try:
        students, marks = fetch_database_data()
        result = analyze_with_spark(students, marks)

        print(json.dumps(result))

    except Exception as error:
        print(
            json.dumps({"error": str(error)}),
            file=sys.stderr
        )
        sys.exit(1)
