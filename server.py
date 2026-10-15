from fastmcp import FastMCP

mcp = FastMCP()

students = {
    101: {
        "name": "Sana",
        "attendance": 87,
        "exam_date": "2026-11-10"
    },
    102: {
        "name": "Ayesha",
        "attendance": 92,
        "exam_date": "2026-11-10"
    }
}

@mcp.tool
def find_student(student_id: int) -> dict:
    """Find a student using their student ID."""
    student = students.get(student_id)

    if student is None:
        return {"error": "Student not found"}

    return {
        "student_id": student_id,
        "name": student["name"]
    }


@mcp.tool
def get_attendance(student_id: int) -> dict:
    """Get a student's attendance percentage."""
    student = students.get(student_id)

    if student is None:
        return {"error": "Student not found"}

    return {
        "student_id": student_id,
        "attendance": student["attendance"]
    }


@mcp.tool
def get_exam_date(student_id: int) -> dict:
    """Get a student's exam date."""
    student = students.get(student_id)

    if student is None:
        return {"error": "Student not found"}

    return {
        "student_id": student_id,
        "exam_date": student["exam_date"]
    }


if __name__ == "__main__":
    mcp.run()