
from flask import Blueprint, render_template
import json

from app.models import Student
from app.services.spark_service import get_spark_analytics

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/dashboard")
def dashboard_home():

    # Get analytics calculated by PySpark
    analytics = get_spark_analytics()

    students = analytics["students"]
    subjects = analytics["subjects"]
    weak_subjects = analytics["weak_subjects"]

    total_students = len(students)
    total_subjects = len(subjects)

    # Calculate overall pass percentage
    evaluated_students = [
        student for student in students
        if student["status"] != "Not Evaluated"
    ]

    pass_count = sum(
        student["status"] == "Pass"
        for student in evaluated_students
    )

    overall_pass_percentage = (
        pass_count / len(evaluated_students) * 100
        if evaluated_students else 0
    )

    return render_template(
        "dashboard.html",
        students=students,
        subjects=subjects,
        weak_subjects=weak_subjects,
        total_students=total_students,
        total_subjects=total_subjects,
        overall_pass_percentage=round(
            overall_pass_percentage, 2
        ),
        student_chart_data=json.dumps([
            {
                "name": student["student_name"],
                "percentage": student["percentage"]
            }
            for student in students
        ]),
        subject_chart_data=json.dumps([
            {
                "name": subject["subject_name"],
                "percentage": subject["pass_percentage"]
            }
            for subject in subjects
        ])
    )


@dashboard_bp.route("/students")
def students_page():

    students = Student.query.order_by(
        Student.id.desc()
    ).all()

    return render_template(
        "students.html",
        students=students
    )


@dashboard_bp.route("/subjects-page")
def subjects_page():
    return render_template("subjects.html")


@dashboard_bp.route("/marks-page")
def marks_page():
    return render_template("marks.html")
