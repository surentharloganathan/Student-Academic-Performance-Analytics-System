
from flask import Blueprint, request, jsonify
from sqlalchemy.exc import IntegrityError

from app import db
from app.models import Student
from app.services.spark_service import invalidate_spark_cache

students_bp = Blueprint(
    "students",
    __name__,
    url_prefix="/students"
)


# CREATE: Add a student
@students_bp.route("/", methods=["POST"])
def add_student():
    data = request.get_json(silent=True) or {}

    name = data.get("name", "").strip()
    register_number = data.get("register_number", "").strip()
    department = data.get("department", "").strip()

    if not name or not register_number or not department:
        return jsonify({
            "error": "Name, register number and department are required"
        }), 400

    student = Student(
        name=name,
        register_number=register_number,
        department=department
    )

    try:
        db.session.add(student)
        db.session.commit()
        invalidate_spark_cache()
    except IntegrityError:
        db.session.rollback()
        return jsonify({
            "error": "Register number already exists"
        }), 409

    return jsonify({
        "message": "Student added successfully",
        "id": student.id,
        "name": student.name,
        "register_number": student.register_number,
        "department": student.department
    }), 201




# READ: View all students
@students_bp.route("/", methods=["GET"])
def get_students():
    students = db.session.execute(
        db.select(Student).order_by(Student.id)
    ).scalars().all()

    return jsonify([
        {
            "id": student.id,
            "name": student.name,
            "register_number": student.register_number,
            "department": student.department
        }
        for student in students
    ]), 200



# UPDATE: Update an existing student
@students_bp.route("/<int:student_id>", methods=["PUT"])
def update_student(student_id):
    student = db.session.get(Student, student_id)

    if student is None:
        return jsonify({"error": "Student not found"}), 404

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "A JSON object is required"}), 400

    allowed_fields = ["name", "register_number", "department"]

    if not data or any(key not in allowed_fields for key in data):
        return jsonify({
            "error": "Provide valid student fields to update"
        }), 400

    for field in allowed_fields:
        if field in data:
            value = data[field]

            if not isinstance(value, str) or not value.strip():
                return jsonify({
                    "error": f"{field} must be a non-empty string"
                }), 400

            setattr(student, field, value.strip())

    try:
        db.session.commit()
        invalidate_spark_cache()
    except IntegrityError:
        db.session.rollback()
        return jsonify({
            "error": "Register number already exists"
        }), 409

    return jsonify({
        "message": "Student updated successfully",
        "id": student.id,
        "name": student.name,
        "register_number": student.register_number,
        "department": student.department
    }), 200



# DELETE: Delete an existing student
@students_bp.route("/<int:student_id>", methods=["DELETE"])
def delete_student(student_id):
    student = db.session.get(Student, student_id)

    if student is None:
        return jsonify({"error": "Student not found"}), 404

    try:
        db.session.delete(student)
        db.session.commit()
        invalidate_spark_cache()
    except Exception:
        db.session.rollback()
        return jsonify({
            "error": "Unable to delete student"
        }), 500

    return jsonify({
        "message": "Student deleted successfully",
        "id": student_id
    }), 200
