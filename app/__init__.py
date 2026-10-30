
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from sqlalchemy.engine import URL

db = SQLAlchemy()


def create_app():
    load_dotenv()

    app = Flask(__name__)

    database_url = URL.create(
        drivername="mysql+pymysql",
        username=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST", "127.0.0.1"),
        port=int(os.getenv("DB_PORT", "3306")),
        database=os.getenv("DB_NAME", "student_performance")
    )

    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Initialize the SAME db instance
    db.init_app(app)

    with app.app_context():

        from app.models import Student, Subject, Mark

        db.create_all()

    # Register blueprints
    from app.routes.students import students_bp
    from app.routes.subjects import subjects_bp
    from app.routes.marks import marks_bp
    from app.routes.analytics import analytics_bp
    from app.routes.dashboard import dashboard_bp

    app.register_blueprint(students_bp)
    app.register_blueprint(subjects_bp)
    app.register_blueprint(marks_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(dashboard_bp)

    return app
