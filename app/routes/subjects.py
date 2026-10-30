
from flask import Blueprint, request, jsonify
from sqlalchemy.exc import IntegrityError

from app import db
from app.models import Subject
from app.services.spark_service import invalidate_spark_cache

subjects_bp = Blueprint(
    "subjects",
    __name__,
    url_prefix="/subjects"
)


# CREATE: Add a subject
@subjects_bp.route("/", methods=["POST"])
def add_subject():
    data = request.get_json(silent=True) or {}

    name = data.get("name")
    max_marks = data.get("max_marks", 100)
    pass_mark = data.get("pass_mark", 40)

    if not isinstance(name, str) or not name.strip():
        return jsonify({"error": "Subject name is required"}), 400

    if (type(max_marks) is not int or max_marks <= 0
            or type(pass_mark) is not int
            or pass_mark < 0 or pass_mark > max_marks):
        return jsonify({
            "error": "Invalid maximum marks or passing marks"
        }), 400

    subject = Subject(
        name=name.strip(),
        max_marks=max_marks,
        pass_mark=pass_mark
    )

    try:
        db.session.add(subject)
        db.session.commit()
        invalidate_spark_cache()
    except IntegrityError:
        db.session.rollback()
        return jsonify({
            "error": "Subject already exists"
        }), 409

    return jsonify({
        "message": "Subject added successfully",
        "id": subject.id,
        "name": subject.name,
        "max_marks": subject.max_marks,
        "pass_mark": subject.pass_mark
    }), 201


# READ: View all subjects
@subjects_bp.route("/", methods=["GET"])
def get_subjects():
    subjects = db.session.execute(
        db.select(Subject).order_by(Subject.id)
    ).scalars().all()

    return jsonify([
        {
            "id": subject.id,
            "name": subject.name,
            "max_marks": subject.max_marks,
            "pass_mark": subject.pass_mark
        }
        for subject in subjects
    ]), 200


# UPDATE: Update a subject
@subjects_bp.route("/<int:subject_id>", methods=["PUT"])
def update_subject(subject_id):
    subject = db.session.get(Subject, subject_id)

    if subject is None:
        return jsonify({"error": "Subject not found"}), 404

    data = request.get_json(silent=True)

    if not isinstance(data, dict) or not data:
        return jsonify({"error": "A JSON object is required"}), 400

    allowed = {"name", "max_marks", "pass_mark"}

    if any(key not in allowed for key in data):
        return jsonify({"error": "Invalid subject field"}), 400

    name = data.get("name", subject.name)
    max_marks = data.get("max_marks", subject.max_marks)
    pass_mark = data.get("pass_mark", subject.pass_mark)

    if not isinstance(name, str) or not name.strip():
        return jsonify({"error": "Subject name is required"}), 400

    if (type(max_marks) is not int or max_marks <= 0
            or type(pass_mark) is not int
            or pass_mark < 0 or pass_mark > max_marks):
        return jsonify({"error": "Invalid marks configuration"}), 400

    subject.name = name.strip()
    subject.max_marks = max_marks
    subject.pass_mark = pass_mark

    try:
        db.session.commit()
        invalidate_spark_cache()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Subject name already exists"}), 409

    return jsonify({
        "message": "Subject updated successfully",
        "id": subject.id,
        "name": subject.name,
        "max_marks": subject.max_marks,
        "pass_mark": subject.pass_mark
    }), 200


# DELETE: Delete a subject
@subjects_bp.route("/<int:subject_id>", methods=["DELETE"])
def delete_subject(subject_id):
    subject = db.session.get(Subject, subject_id)

    if subject is None:
        return jsonify({"error": "Subject not found"}), 404

    if subject.marks:
        return jsonify({
            "error": "Cannot delete a subject that has marks recorded"
        }), 409

    db.session.delete(subject)
    db.session.commit()
    invalidate_spark_cache()

    return jsonify({
        "message": "Subject deleted successfully"
    }), 200
