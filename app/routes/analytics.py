
from flask import Blueprint, jsonify

from app.services.analysis import (
    get_student_performance,
    get_subject_performance,
    get_weak_subjects
)

analytics_bp = Blueprint(
    "analytics",
    __name__,
    url_prefix="/analytics"
)


@analytics_bp.route("/students", methods=["GET"])
def student_analytics():
    return jsonify(get_student_performance()), 200


@analytics_bp.route("/subjects", methods=["GET"])
def subject_analytics():
    return jsonify(get_subject_performance()), 200


@analytics_bp.route("/weak-subjects", methods=["GET"])
def weak_subject_analytics():
    return jsonify(get_weak_subjects()), 200
