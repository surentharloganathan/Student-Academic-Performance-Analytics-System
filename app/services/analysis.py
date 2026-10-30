
import numpy as np
import pandas as pd

from app import db
from app.models import Student, Subject, Mark


def get_marks_dataframe():
    """Fetch marks and related student/subject details from MySQL."""

    records = db.session.execute(
        db.select(Mark, Student, Subject)
        .join(Student, Mark.student_id == Student.id)
        .join(Subject, Mark.subject_id == Subject.id)
        .order_by(Student.id, Subject.id)
    ).all()

    data = []

    for mark, student, subject in records:
        data.append({
            "student_id": student.id,
            "student_name": student.name,
            "register_number": student.register_number,
            "subject_id": subject.id,
            "subject_name": subject.name,
            "score": mark.score,
            "max_marks": subject.max_marks,
            "pass_mark": subject.pass_mark
        })

    return pd.DataFrame(data)


def get_student_performance():
    df = get_marks_dataframe()

    # Fetch every student, including students without marks
    students = Student.query.order_by(Student.id).all()

    result = []

    for student in students:
        student_marks = (
            df[df["student_id"] == student.id]
            if not df.empty
            else pd.DataFrame()
        )

        # Student has not received any marks yet
        if student_marks.empty:
            result.append({
                "student_id": student.id,
                "student_name": student.name,
                "register_number": student.register_number,
                "total_marks": 0,
                "total_max_marks": 0,
                "average_marks": 0,
                "percentage": 0,
                "status": "Not Evaluated"
            })
            continue

        total_marks = float(np.sum(student_marks["score"]))
        total_max_marks = float(np.sum(student_marks["max_marks"]))
        average_marks = float(np.mean(student_marks["score"]))

        percentage = (
            (total_marks / total_max_marks) * 100
            if total_max_marks > 0 else 0
        )

        passed = (
            student_marks["score"] >= student_marks["pass_mark"]
        ).all()

        result.append({
            "student_id": student.id,
            "student_name": student.name,
            "register_number": student.register_number,
            "total_marks": round(total_marks, 2),
            "total_max_marks": total_max_marks,
            "average_marks": round(average_marks, 2),
            "percentage": round(percentage, 2),
            "status": "Pass" if passed else "Fail"
        })

    return result


def get_subject_performance():
    """Calculate subject averages and pass percentages."""

    df = get_marks_dataframe()

    if df.empty:
        return []

    df["percentage"] = (
        df["score"] / df["max_marks"].replace(0, np.nan)
    ) * 100

    df["passed"] = df["score"] >= df["pass_mark"]

    result = []

    for subject_id, group in df.groupby("subject_id"):
        result.append({
            "subject_id": int(subject_id),
            "subject_name": group["subject_name"].iloc[0],
            "students_count": int(len(group)),
            "average_marks": round(float(np.mean(group["score"])), 2),
            "average_percentage": round(
                float(group["percentage"].mean()), 2
            ),
            "highest_marks": float(group["score"].max()),
            "lowest_marks": float(group["score"].min()),
            "pass_percentage": round(
                float(group["passed"].mean() * 100), 2
            )
        })

    return result


def get_weak_subjects():
    """Identify subjects with low average or pass percentage."""

    subjects = get_subject_performance()

    weak_subjects = [
        subject for subject in subjects
        if subject["average_percentage"] < 50
        or subject["pass_percentage"] < 60
    ]

    return weak_subjects
