"""
Pydantic models for document-related API schemas
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class DocumentUploadResponse(BaseModel):
    """Response schema for document upload"""

    success: bool = True
    document_id: str = Field(..., description="Unique identifier for the uploaded document")
    filename: str = Field(..., description="Original filename")
    file_size: int = Field(..., description="File size in bytes")
    file_type: str = Field(..., description="File type (pdf, txt, docx)")
    file_path: str = Field(..., description="Path to the saved file")
    uploaded_at: datetime = Field(default_factory=datetime.now, description="Upload timestamp")
    message: str = "Document uploaded successfully"


class DocumentInfo(BaseModel):
    """Document information schema"""

    document_id: str = Field(..., description="Unique identifier for the document")
    filename: str = Field(..., description="Original filename")
    file_size: int = Field(..., description="File size in bytes")
    file_type: str = Field(..., description="File type (pdf, txt, docx)")
    file_path: str = Field(..., description="Path to the saved file")
    uploaded_at: datetime = Field(..., description="Upload timestamp")


class DocumentResponse(BaseModel):
    """Response schema for document retrieval"""

    success: bool = True
    data: Optional[DocumentInfo] = None
    error: Optional[str] = None
    message: str = "Document retrieved successfully"
