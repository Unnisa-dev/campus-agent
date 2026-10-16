import os

from typing import Annotated
from pydantic import Field

from dotenv import load_dotenv
from fastmcp import FastMCP
from pymongo import MongoClient
from pymongo.errors import PyMongoError

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

mcp = FastMCP("Campus Agent",
    strict_input_validation=True,
    mask_error_details=True,
    )

uri = os.getenv("MONGODB_URI")
if not uri:
    raise RuntimeError("MONGODB_URI is missing from .env")

mongo_client = MongoClient(
    uri,
    serverSelectionTimeoutMS=10000,
)

db = mongo_client["campus_db"]
students = db["students"]


def find_student_record(student_id: Annotated[int, Field(gt=0)]):
    """Find one student and return a JSON-friendly record."""
    try:
        student = students.find_one({"student_id": student_id})

        if student is None:
            return {"error": f"Student {student_id} not found"}

        student.pop("_id", None)
        return student

    except PyMongoError:
        logger.exception("MongoDB query failed")
    return {
        "error": "Student information is temporarily unavailable"
    }


@mcp.tool()
def find_student(student_id: Annotated[int, Field(ge=1)]) -> dict:
    """Find a student by their student ID."""
    return find_student_record(student_id)


@mcp.tool()
def get_attendance(student_id: Annotated[int, Field(ge=1)]) -> dict:
    """Get a student's attendance percentage."""
    student = find_student_record(student_id)

    if "error" in student:
        return student

    if "attendance" not in student:
        return {"error": "Attendance information is unavailable"}

    return {
        "student_id": student["student_id"],
        "name": student.get("name", "Unknown"),
        "attendance": student["attendance"],
    }


@mcp.tool()
def get_exam_date(student_id: Annotated[int, Field(ge=1)]) -> dict:
    """Get a student's exam date."""
    student = find_student_record(student_id)

    if "error" in student:
        return student

    if "exam_date" not in student:
        return {"error": "Exam date information is unavailable"}

    return {
        "student_id": student["student_id"],
        "name": student.get("name", "Unknown"),
        "exam_date": student["exam_date"],
    }


if __name__ == "__main__":
    mcp.run()
