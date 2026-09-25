from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

DATA_FILE = "courses.json"
PORT = 5000

VALID_STATUSES = ["Not Started", "In Progress", "Completed"]


def load_courses():
    """Load courses from courses.json."""
    if not os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as file:
                json.dump([], file, indent=2)
            return []
        except OSError as error:
            raise RuntimeError(f"Could not create data file: {error}")

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except json.JSONDecodeError:
        raise RuntimeError("courses.json contains invalid JSON")
    except OSError as error:
        raise RuntimeError(f"Could not read data file: {error}")


def save_courses(courses):
    """Save courses to courses.json."""
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as file:
            json.dump(courses, file, indent=2)
    except OSError as error:
        raise RuntimeError(f"Could not write data file: {error}")


def get_next_id(courses):
    """Generate the next course ID."""
    if not courses:
        return 1

    return max(course["id"] for course in courses) + 1


def validate_date(date_string):
    """Check that a date uses YYYY-MM-DD format."""
    try:
        datetime.strptime(date_string, "%Y-%m-%d")
        return True
    except (ValueError, TypeError):
        return False


@app.route("/api/courses", methods=["GET"])
def get_all_courses():
    try:
        courses = load_courses()

        return jsonify({
            "success": True,
            "count": len(courses),
            "courses": courses
        }), 200

    except RuntimeError as error:
        return jsonify({
            "success": False,
            "error": str(error)
        }), 500

@app.route("/api/courses/stats", methods=["GET"])
def get_course_stats():
    try:
        courses = load_courses()

        stats = {
            "Not Started": 0,
            "In Progress": 0,
            "Completed": 0
        }

        for course in courses:
            status = course.get("status")
            if status in stats:
                stats[status] += 1

        return jsonify({
            "success": True,
            "total_courses": len(courses),
            "by_status": stats
        }), 200

    except RuntimeError as error:
        return jsonify({
            "success": False,
            "error": str(error)
        }), 500
@app.route("/api/courses/<int:course_id>", methods=["GET"])
def get_course(course_id):
    try:
        courses = load_courses()

        course = next(
            (course for course in courses if course["id"] == course_id),
            None
        )

        if course is None:
            return jsonify({
                "success": False,
                "error": "Course not found"
            }), 404

        return jsonify({
            "success": True,
            "course": course
        }), 200

    except RuntimeError as error:
        return jsonify({
            "success": False,
            "error": str(error)
        }), 500


@app.route("/api/courses", methods=["POST"])
def add_course():
    try:
        data = request.get_json(silent=True)

        if not data:
            return jsonify({
                "success": False,
                "error": "Request body must contain JSON data"
            }), 400

        required_fields = ["name", "description", "target_date", "status"]

        missing_fields = [
            field for field in required_fields
            if not data.get(field)
        ]

        if missing_fields:
            return jsonify({
                "success": False,
                "error": f"Missing required fields: {', '.join(missing_fields)}"
            }), 400

        if data["status"] not in VALID_STATUSES:
            return jsonify({
                "success": False,
                "error": f"Status must be one of: {', '.join(VALID_STATUSES)}"
            }), 400

        if not validate_date(data["target_date"]):
            return jsonify({
                "success": False,
                "error": "target_date must use YYYY-MM-DD format"
            }), 400

        courses = load_courses()

        new_course = {
            "id": get_next_id(courses),
            "name": data["name"],
            "description": data["description"],
            "target_date": data["target_date"],
            "status": data["status"],
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        courses.append(new_course)
        save_courses(courses)

        return jsonify({
            "success": True,
            "message": "Course added successfully",
            "course": new_course
        }), 201

    except RuntimeError as error:
        return jsonify({
            "success": False,
            "error": str(error)
        }), 500


@app.route("/api/courses/<int:course_id>", methods=["PUT"])
def update_course(course_id):
    try:
        data = request.get_json(silent=True)

        if not data:
            return jsonify({
                "success": False,
                "error": "Request body must contain JSON data"
            }), 400

        courses = load_courses()

        course_index = next(
            (
                index
                for index, course in enumerate(courses)
                if course["id"] == course_id
            ),
            None
        )

        if course_index is None:
            return jsonify({
                "success": False,
                "error": "Course not found"
            }), 404

        if "status" in data and data["status"] not in VALID_STATUSES:
            return jsonify({
                "success": False,
                "error": f"Status must be one of: {', '.join(VALID_STATUSES)}"
            }), 400

        if "target_date" in data and not validate_date(data["target_date"]):
            return jsonify({
                "success": False,
                "error": "target_date must use YYYY-MM-DD format"
            }), 400

        course = courses[course_index]

        for field in ["name", "description", "target_date", "status"]:
            if field in data:
                course[field] = data[field]

        save_courses(courses)

        return jsonify({
            "success": True,
            "message": "Course updated successfully",
            "course": course
        }), 200

    except RuntimeError as error:
        return jsonify({
            "success": False,
            "error": str(error)
        }), 500


@app.route("/api/courses/<int:course_id>", methods=["DELETE"])
def delete_course(course_id):
    try:
        courses = load_courses()

        course_index = next(
            (
                index
                for index, course in enumerate(courses)
                if course["id"] == course_id
            ),
            None
        )

        if course_index is None:
            return jsonify({
                "success": False,
                "error": "Course not found"
            }), 404

        deleted_course = courses.pop(course_index)
        save_courses(courses)

        return jsonify({
            "success": True,
            "message": "Course deleted successfully",
            "deleted_course": deleted_course
        }), 200

    except RuntimeError as error:
        return jsonify({
            "success": False,
            "error": str(error)
        }), 500


if __name__ == "__main__":
    print("CodeCraftHub API is starting...")
    print(f"Data will be stored in: {os.path.abspath(DATA_FILE)}")
    print(f"API will be available at: http://localhost:{PORT}")

    app.run(
        debug=True,
        host="0.0.0.0",
        port=PORT
    )