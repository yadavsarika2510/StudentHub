
from fastapi import FastAPI, HTTPException, Path
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator, computed_field
from pathlib import Path as FilePath
import json


# --------------------------------------------------
# FASTAPI APPLICATION
# --------------------------------------------------

app = FastAPI(
    title="StudentHub API",
    description="Student Management System API",
    version="1.0.0"
)


# --------------------------------------------------
# CORS CONFIGURATION
# --------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"]
)


# --------------------------------------------------
# JSON FILE CONFIGURATION
# --------------------------------------------------

JSON_FILE = FilePath(__file__).parent / "students.json"


def load_data():

    if not JSON_FILE.exists():
        return []

    with open(JSON_FILE, "r") as file:
        return json.load(file)


def save_data(students):

    with open(JSON_FILE, "w") as file:
        json.dump(students, file, indent=4)


# --------------------------------------------------
# STUDENT MODEL
# --------------------------------------------------

class Student(BaseModel):

    id: str = Field(..., description="Student identifier")
    name: str = Field(..., min_length=1)
    age: int = Field(..., gt=0, le=120)
    grade: str

    @field_validator("grade")
    @classmethod
    def validate_grade(cls, v: str) -> str:

        v = v.upper()

        if v not in ["A", "B", "C", "D", "F"]:
            raise ValueError(
                "Grade must be A, B, C, D or F"
            )

        return v

    @computed_field
    @property
    def is_adult(self) -> bool:
        return self.age >= 18

    @computed_field
    @property
    def grade_message(self) -> str:

        messages = {
            "A": "Excellent",
            "B": "Very Good",
            "C": "Good",
            "D": "Needs Improvement",
            "F": "Failed"
        }

        return messages.get(self.grade, "Unknown grade")


# --------------------------------------------------
# STUDENT UPDATE MODEL
# --------------------------------------------------

class StudentUpdate(BaseModel):

    name: str | None = Field(default=None, min_length=1)
    age: int | None = Field(default=None, gt=0, le=120)
    grade: str | None = None

    @field_validator("grade")
    @classmethod
    def validate_grade(cls, v: str | None) -> str | None:

        if v is None:
            return v

        v = v.upper()

        if v not in ["A", "B", "C", "D", "F"]:
            raise ValueError(
                "Grade must be A, B, C, D or F"
            )

        return v


# --------------------------------------------------
# HOME ROUTE
# --------------------------------------------------

@app.get("/")
def home():

    return {
        "message": "Welcome to StudentHub API",
        "status": "Running"
    }


# --------------------------------------------------
# HEALTH CHECK
# --------------------------------------------------

@app.get("/health")
def health_check():

    return {
        "status": "healthy"
    }


# --------------------------------------------------
# CREATE STUDENT
# --------------------------------------------------

@app.post("/create", status_code=201)
def create_student(student: Student):

    students = load_data()

    for s in students:

        if s.get("id") == student.id:

            raise HTTPException(
                status_code=400,
                detail="Student with this ID already exists"
            )

    students.append(student.model_dump())

    save_data(students)

    return {
        "message": "Student created successfully",
        "student": student
    }


# --------------------------------------------------
# GET ALL STUDENTS
# --------------------------------------------------

@app.get("/students")
def get_students():

    students = load_data()

    return {
        "count": len(students),
        "students": students
    }


# --------------------------------------------------
# GET STUDENT BY ID
# --------------------------------------------------

@app.get("/students/{student_id}")
def get_student(
    student_id: str = Path(
        ...,
        description="The ID of the student",
        examples=["001"]
    )
):

    students = load_data()

    student = next(
        (s for s in students if s.get("id") == student_id),
        None
    )

    if student is None:

        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    return student


# --------------------------------------------------
# UPDATE STUDENT
# --------------------------------------------------

@app.put("/update/{student_id}")
def update_student(
    student_update: StudentUpdate,
    student_id: str = Path(
        ...,
        description="The ID of the student",
        examples=["001"]
    )
):

    students = load_data()

    existing_index = None

    for index, student in enumerate(students):

        if student.get("id") == student_id:

            existing_index = index
            break

    if existing_index is None:

        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    existing = students[existing_index]

    update_data = student_update.model_dump(
        exclude_unset=True,
        exclude_none=True
    )

    existing.update(update_data)

    students[existing_index] = existing

    save_data(students)

    return {
        "message": "Student updated successfully",
        "student": existing
    }


# --------------------------------------------------
# DELETE STUDENT
# --------------------------------------------------

@app.delete("/delete/{student_id}")
def delete_student(student_id: str):

    students = load_data()

    student = next(
        (s for s in students if s.get("id") == student_id),
        None
    )

    if student is None:

        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    students = [
        s for s in students
        if s.get("id") != student_id
    ]

    save_data(students)

    return {
        "message": "Student deleted successfully",
        "student": student
    }
