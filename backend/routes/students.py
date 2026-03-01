"""
Student API routes.
RESTful endpoints for student management.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from database import get_db
from schemas import (
    StudentCreate, StudentUpdate, StudentResponse,
    PaginatedResponse, ErrorResponse
)
from services import StudentService

router = APIRouter(prefix="/students", tags=["Students"])


@router.post(
    "/",
    response_model=StudentResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid input data"},
        409: {"model": ErrorResponse, "description": "Roll number or email already exists"}
    }
)
def create_student(
    student_data: StudentCreate,
    db: Session = Depends(get_db)
) -> StudentResponse:
    """
    Create a new student.
    
    - **roll_number**: Unique student roll number
    - **name**: Full name of the student
    - **email**: Valid email address
    - **department**: Department name
    - **semester**: Semester number (1-8)
    """
    service = StudentService(db)
    
    # Check for duplicates
    if service.get_by_roll_number(student_data.roll_number):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Roll number '{student_data.roll_number}' already exists"
        )
    
    if service.get_by_id(student_data.semester):  # type: ignore
        existing = db.query(StudentService).filter(
            StudentService.email == student_data.email  # type: ignore
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Email '{student_data.email}' already exists"
            )
    
    student = service.create(student_data)
    return StudentResponse.model_validate(student)


@router.get(
    "/",
    response_model=PaginatedResponse,
    responses={
        200: {"description": "List of students"}
    }
)
def get_students(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=500, description="Maximum records to return"),
    department: Optional[str] = Query(None, description="Filter by department"),
    semester: Optional[int] = Query(None, ge=1, le=8, description="Filter by semester"),
    db: Session = Depends(get_db)
) -> PaginatedResponse:
    """
    Get all students with optional filtering and pagination.
    
    - **skip**: Number of records to skip for pagination
    - **limit**: Maximum number of records to return
    - **department**: Optional department filter
    - **semester**: Optional semester filter
    """
    service = StudentService(db)
    students = service.get_all(
        skip=skip,
        limit=limit,
        department=department,
        semester=semester
    )
    
    total = db.query(service.db.query(StudentService).model).filter(
        StudentService.is_active == True  # type: ignore
    ).count()
    
    return PaginatedResponse(
        items=[StudentResponse.model_validate(s) for s in students],
        total=total,
        page=(skip // limit) + 1,
        page_size=limit,
        total_pages=(total + limit - 1) // limit
    )


@router.get(
    "/{student_id}",
    response_model=StudentResponse,
    responses={
        404: {"model": ErrorResponse, "description": "Student not found"}
    }
)
def get_student(
    student_id: int,
    db: Session = Depends(get_db)
) -> StudentResponse:
    """Get a specific student by ID."""
    service = StudentService(db)
    student = service.get_by_id(student_id)
    
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with id {student_id} not found"
        )
    
    return StudentResponse.model_validate(student)


@router.put(
    "/{student_id}",
    response_model=StudentResponse,
    responses={
        404: {"model": ErrorResponse, "description": "Student not found"},
        409: {"model": ErrorResponse, "description": "Email already exists"}
    }
)
def update_student(
    student_id: int,
    student_data: StudentUpdate,
    db: Session = Depends(get_db)
) -> StudentResponse:
    """
    Update student information.
    
    Only provided fields will be updated.
    """
    service = StudentService(db)
    student = service.update(student_id, student_data)
    
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with id {student_id} not found"
        )
    
    return StudentResponse.model_validate(student)


@router.delete(
    "/{student_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        404: {"model": ErrorResponse, "description": "Student not found"}
    }
)
def delete_student(
    student_id: int,
    db: Session = Depends(get_db)
) -> None:
    """
    Soft delete a student (sets is_active=False).
    
    This preserves historical attendance data.
    """
    service = StudentService(db)
    success = service.delete(student_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with id {student_id} not found"
        )


# Import Student for the duplicate check
from models import Student
