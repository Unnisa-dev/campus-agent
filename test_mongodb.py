
import os

from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

uri = os.getenv("MONGODB_URI")
if not uri:
    raise RuntimeError("MONGODB_URI is missing from .env")

client = MongoClient(uri, serverSelectionTimeoutMS=10000)

try:
    client.admin.command("ping")
    print("Connected successfully to MongoDB!")

    db = client["campus_db"]
    students = db["students"]

    student = students.find_one({"student_id": 101})

    if student:
        student.pop("_id", None)
        print("Student found:", student)
    else:
        print("Student 101 was not found in the collection.")

except Exception as error:
    print("MongoDB connection or query failed.")
    print("Error type:", type(error).__name__)
    print("Check your URI, database credentials, and Atlas Network Access.")

finally:
    client.close()
