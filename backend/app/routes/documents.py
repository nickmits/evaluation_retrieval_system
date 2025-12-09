"""
Document upload and retrieval API endpoints
"""

import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, File, HTTPException, UploadFile, status
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.models.document import (
    DocumentInfo,
    DocumentResponse,
    DocumentUploadResponse,
)

# Get settings
settings = get_settings()

# Create router
router = APIRouter()

# In-memory storage for document metadata (in production, use database)
documents_store: dict[str, DocumentInfo] = {}


@router.post(
    "/documents/upload",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload a document",
    description="Upload a PDF, TXT, or DOCX document for evaluation",
)
async def upload_document(file: UploadFile = File(...)) -> DocumentUploadResponse:
    """
    Upload a document file

    Args:
        file: Uploaded file (PDF, TXT, or DOCX)

    Returns:
        DocumentUploadResponse: Upload confirmation with document ID

    Raises:
        HTTPException: If file type not allowed or upload fails
    """
    # Validate file type
    file_extension = file.filename.split(".")[-1].lower()
    if file_extension not in settings.ALLOWED_FILE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type '.{file_extension}' not allowed. Allowed types: {settings.ALLOWED_FILE_TYPES}",
        )

    # Generate unique document ID
    document_id = str(uuid.uuid4())

    # Create upload directory if it doesn't exist
    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)

    # Generate unique filename
    unique_filename = f"{document_id}_{file.filename}"
    file_path = upload_dir / unique_filename

    try:
        # Read and save file
        contents = await file.read()
        file_size = len(contents)

        # Check file size
        if file_size > settings.MAX_UPLOAD_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File too large. Maximum size: {settings.MAX_UPLOAD_SIZE / (1024*1024):.0f} MB",
            )

        # Write file to disk
        with open(file_path, "wb") as f:
            f.write(contents)

        # Create document info
        doc_info = DocumentInfo(
            document_id=document_id,
            filename=file.filename,
            file_size=file_size,
            file_type=file_extension,
            file_path=str(file_path),
            uploaded_at=datetime.now(),
        )

        # Store document metadata
        documents_store[document_id] = doc_info

        # Return response
        return DocumentUploadResponse(
            success=True,
            document_id=document_id,
            filename=file.filename,
            file_size=file_size,
            file_type=file_extension,
            file_path=str(file_path),
            uploaded_at=doc_info.uploaded_at,
            message=f"Document '{file.filename}' uploaded successfully",
        )

    except HTTPException:
        raise
    except Exception as e:
        # Clean up file if it was created
        if file_path.exists():
            file_path.unlink()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload document: {str(e)}",
        )


@router.get(
    "/documents/{document_id}",
    response_model=DocumentResponse,
    summary="Get document information",
    description="Retrieve information about an uploaded document",
)
async def get_document(document_id: str) -> DocumentResponse:
    """
    Get document information by ID

    Args:
        document_id: Document ID

    Returns:
        DocumentResponse: Document information

    Raises:
        HTTPException: If document not found
    """
    doc_info = documents_store.get(document_id)

    if not doc_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID '{document_id}' not found",
        )

    return DocumentResponse(
        success=True,
        data=doc_info,
        message="Document retrieved successfully",
    )


@router.delete(
    "/documents/{document_id}",
    summary="Delete a document",
    description="Delete an uploaded document and its metadata",
)
async def delete_document(document_id: str) -> JSONResponse:
    """
    Delete a document by ID

    Args:
        document_id: Document ID

    Returns:
        JSONResponse: Deletion confirmation

    Raises:
        HTTPException: If document not found
    """
    doc_info = documents_store.get(document_id)

    if not doc_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID '{document_id}' not found",
        )

    # Delete file from disk
    file_path = Path(doc_info.file_path)
    if file_path.exists():
        file_path.unlink()

    # Remove from storage
    del documents_store[document_id]

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "success": True,
            "document_id": document_id,
            "message": "Document deleted successfully",
        },
    )
