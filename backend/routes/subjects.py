"""
Subject API routes.
RESTful endpoints for subject management.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from database import get_db
from schemas import (
    SubjectCreate, SubjectUpdate, SubjectResponse,
    PaginatedResponse, ErrorResponse
)
from services import SubjectService

router = APIRouter(prefix="/subjects", tags=["Subjects"])


@router.post(
    "/",
    response_model=SubjectResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid input data"},
        409: {"model": ErrorResponse, "description": "Subject code already exists"}
    }
)
def create_subject(
    subject_data: SubjectCreate,
    db: Session = Depends(get_db)
) -> SubjectResponse:
    """
    Create a new subject.
    
    - **subject_code**: Unique subject code (e.g., CS101)
    - **subject_name**: Full subject name
    - **department**: Department offering the subject
    - **semester**: Semester number (1-8)
    - **credits**: Credit hours (1-6)
    - **total_classes_required**: Total classes for the course (30-120)
    """
    service = SubjectService(db)
    
    # Check for duplicate code
    if service.get_by_code(subject_data.subject_code):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Subject code '{subject_data.subject_code}' already exists"
        )
    
    subject = service.create(subject_data)
    return SubjectResponse.model_validate(subject)


@router.get(
    "/",
    response_model=PaginatedResponse,
    responses={
        200: {"description": "List of subjects"}
    }
)
def get_subjects(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=500, description="Maximum records to return"),
    department: Optional[str] = Query(None, description="Filter by department"),
    semester: Optional[int] = Query(None, ge=1, le=8, description="Filter by semester"),
    db: Session = Depends(get_db)
) -> PaginatedResponse:
    """
    Get all subjects with optional filtering and pagination.
    """
    service = SubjectService(db)
    subjects = service.get_all(
        skip=skip,
        limit=limit,
        department=department,
        semester=semester
    )
    
    # Get total count
    query = db.query(SubjectService.db.query(SubjectService).model)  # type: ignore
    if department:
        query = query.filter(SubjectService.department == department)  # type: ignore
    if semester:
        query = query.filter(SubjectService.semester == semester)  # type: ignore
    total = query.count()
    
    return PaginatedResponse(
        items=[SubjectResponse.model_validate(s) for s in subjects],
        total=total,
        page=(skip // limit) + 1,
        page_size=limit,
        total_pages=(total + limit - 1) // limit
    )


@router.get(
    "/{subject_id}",
    response_model=SubjectResponse,
    responses={
        404: {"model": ErrorResponse, "description": "Subject not found"}
    }
)
def get_subject(
    subject_id: int,
    db: Session = Depends(get_db)
) -> SubjectResponse:
    """Get a specific subject by ID."""
    service = SubjectService(db)
    subject = service.get_by_id(subject_id)
    
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Subject with id {subject_id} not found"
        )
    
    return SubjectResponse.model_validate(subject)


@router.put(
    "/{subject_id}",
    response_model=SubjectResponse,
    responses={
        404: {"model": ErrorResponse, "description": "Subject not found"}
    }
)
def update_subject(
    subject_id: int,
    subject_data: SubjectUpdate,
    db: Session = Depends(get_db)
) -> SubjectResponse:
    """
    Update subject information.
    
    Only provided fields will be updated.
    """
    service = SubjectService(db)
    subject = service.update(subject_id, subject_data)
    
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Subject with id {subject_id} not found"
        )
    
    return SubjectResponse.model_validate(subject)


@router.delete(
    "/{subject_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        404: {"model": ErrorResponse, "description": "Subject not found"}
    }
)
def delete_subject(
    subject_id: int,
    db: Session = Depends(get_db)
) -> None:
    """
    Delete a subject.
    
    Note: This will cascade delete all associated attendance records.
    """
    service = SubjectService(db)
    success = service.delete(subject_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Subject with id {subject_id} not found"
        )
