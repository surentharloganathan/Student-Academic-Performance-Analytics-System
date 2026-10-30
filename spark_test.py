import os
import sys
from pyspark.sql import SparkSession

python_path = sys.executable


os.environ["PYSPARK_PYTHON"] = python_path
os.environ["PYSPARK_DRIVER_PYTHON"] = python_path
# Create Spark session
spark = (
    SparkSession.builder
    .appName("StudentAcademicPerformance")
    .master("local[*]")
    .getOrCreate()
)

print("Spark session created successfully!")

# Sample student marks
data = [
    (1, "Arun", "Python", 85),
    (1, "Arun", "Java", 90),
    (2, "Bala", "Python", 65),
    (2, "Bala", "Java", 70),
    (3, "Charan", "Python", 35),
    (3, "Charan", "Java", 45)
]

columns = ["student_id", "student_name", "subject", "marks"]

# Create Spark DataFrame
df = spark.createDataFrame(data, columns)

print("\nStudent Marks:")
df.show()

# Calculate average marks for each student
print("\nStudent Average Marks:")

df.groupBy("student_id", "student_name") \
    .avg("marks") \
    .withColumnRenamed("avg(marks)", "average_marks") \
    .show()

# Calculate subject-wise average
print("\nSubject-wise Average:")

df.groupBy("subject") \
    .avg("marks") \
    .show()

spark.stop()
