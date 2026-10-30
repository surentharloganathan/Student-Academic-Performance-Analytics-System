
from app import db


class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)

    register_number = db.Column(
        db.String(30), unique=True, nullable=False
    )

    department = db.Column(db.String(100), nullable=False)

    marks = db.relationship(
        "Mark",
        back_populates="student",
        cascade="all, delete-orphan"
    )


class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), unique=True, nullable=False)

    max_marks = db.Column(db.Integer, nullable=False, default=100)

    pass_mark = db.Column(db.Integer, nullable=False, default=40)

    marks = db.relationship(
        "Mark",
        back_populates="subject"
    )


class Mark(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    student_id = db.Column(
        db.Integer,
        db.ForeignKey("student.id"),
        nullable=False
    )

    subject_id = db.Column(
        db.Integer,
        db.ForeignKey("subject.id"),
        nullable=False
    )

    score = db.Column(db.Float, nullable=False)

    student = db.relationship(
        "Student",
        back_populates="marks"
    )

    subject = db.relationship(
        "Subject",
        back_populates="marks"
    )

    __table_args__ = (
        db.UniqueConstraint(
            "student_id",
            "subject_id",
            name="unique_student_subject"
        ),
    )
