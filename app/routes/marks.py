
from flask import Blueprint, request, jsonify
from sqlalchemy.exc import IntegrityError

from app import db
from app.models import Student, Subject, Mark
from app.services.spark_service import invalidate_spark_cache
marks_bp = Blueprint(
    "marks",
    __name__,
    url_prefix="/marks"
)


def mark_to_dict(mark):
    return {
        "id": mark.id,
        "student_id": mark.student_id,
        "student_name": mark.student.name,
        "subject_id": mark.subject_id,
        "subject_name": mark.subject.name,
        "score": mark.score,
        "max_marks": mark.subject.max_marks,
        "pass_mark": mark.subject.pass_mark
    }


# CREATE: Assign marks
@marks_bp.route("/", methods=["POST"])
def add_mark():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "A JSON object is required"}), 400

    student_id = data.get("student_id")
    subject_id = data.get("subject_id")
    score = data.get("score")

    if (type(student_id) is not int or
            type(subject_id) is not int or
            type(score) not in (int, float)):
        return jsonify({
            "error": "student_id, subject_id and numeric score are required"
        }), 400

    student = db.session.get(Student, student_id)
    subject = db.session.get(Subject, subject_id)

    if student is None:
        return jsonify({"error": "Student not found"}), 404

    if subject is None:
        return jsonify({"error": "Subject not found"}), 404

    if not 0 <= score <= subject.max_marks:
        return jsonify({
            "error": f"Score must be between 0 and {subject.max_marks}"
        }), 400

    mark = Mark(
        student_id=student_id,
        subject_id=subject_id,
        score=score
    )

    try:
        db.session.add(mark)
        db.session.commit()

        invalidate_spark_cache()
    except IntegrityError:
        db.session.rollback()
        return jsonify({
            "error": "Marks already exist for this student and subject"
        }), 409

    return jsonify({
        "message": "Marks added successfully",
        "mark": mark_to_dict(mark)
    }), 201


# READ: View all marks
@marks_bp.route("/", methods=["GET"])
def get_marks():
    marks = db.session.execute(
        db.select(Mark).order_by(Mark.id)
    ).scalars().all()

    return jsonify([mark_to_dict(mark) for mark in marks]), 200


# READ: View marks for one student
@marks_bp.route("/student/<int:student_id>", methods=["GET"])
def get_student_marks(student_id):
    student = db.session.get(Student, student_id)

    if student is None:
        return jsonify({"error": "Student not found"}), 404

    marks = db.session.execute(
        db.select(Mark)
        .where(Mark.student_id == student_id)
        .order_by(Mark.id)
    ).scalars().all()

    return jsonify([mark_to_dict(mark) for mark in marks]), 200


# UPDATE: Update a mark
@marks_bp.route("/<int:mark_id>", methods=["PUT"])
def update_mark(mark_id):
    mark = db.session.get(Mark, mark_id)

    if mark is None:
        return jsonify({"error": "Mark record not found"}), 404

    data = request.get_json(silent=True)

    if not isinstance(data, dict) or set(data) != {"score"}:
        return jsonify({
            "error": "Provide only the score field"
        }), 400

    score = data["score"]

    if type(score) not in (int, float):
        return jsonify({"error": "Score must be numeric"}), 400

    if not 0 <= score <= mark.subject.max_marks:
        return jsonify({
            "error": f"Score must be between 0 and {mark.subject.max_marks}"
        }), 400

    mark.score = score
    db.session.commit()

    invalidate_spark_cache()

    return jsonify({
        "message": "Marks updated successfully",
        "mark": mark_to_dict(mark)
    }), 200


# DELETE: Delete a mark
@marks_bp.route("/<int:mark_id>", methods=["DELETE"])
def delete_mark(mark_id):
    mark = db.session.get(Mark, mark_id)

    if mark is None:
        return jsonify({"error": "Mark record not found"}), 404

    db.session.delete(mark)
    db.session.commit()

    invalidate_spark_cache()
    return jsonify({
        "message": "Marks deleted successfully",
        "id": mark_id
    }), 200
