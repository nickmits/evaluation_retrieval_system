"""
Pydantic models for evaluation-related API schemas
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from enum import Enum
from pydantic import BaseModel, Field


class EvaluationStatus(str, Enum):
    """Evaluation status enum"""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class SystemType(str, Enum):
    """Retrieval system type enum"""

    SIMPLE_RECURSIVE = "simple_recursive"
    SIMPLE_SEMANTIC = "simple_semantic"
    ADVANCED_RECURSIVE = "advanced_recursive"
    ADVANCED_SEMANTIC = "advanced_semantic"


class SystemConfig(BaseModel):
    """Configuration for a retrieval system"""

    chunk_size: Optional[int] = Field(1000, ge=100, le=2000, description="Chunk size for text splitting")
    chunk_overlap: Optional[int] = Field(200, ge=0, le=500, description="Overlap between chunks")
    threshold_type: Optional[str] = Field("percentile", description="Threshold type for semantic chunking")
    threshold_amount: Optional[int] = Field(95, ge=50, le=99, description="Threshold amount for semantic chunking")


class SystemSelection(BaseModel):
    """System selection with configuration"""

    name: str = Field(..., description="Display name for the system")
    type: SystemType = Field(..., description="System type")
    config: SystemConfig = Field(default_factory=SystemConfig, description="System configuration")


class EvaluationRequest(BaseModel):
    """Request schema for starting an evaluation"""

    document_id: str = Field(..., description="ID of the uploaded document")
    systems: List[SystemSelection] = Field(..., min_length=1, max_length=4, description="Retrieval systems to evaluate")
    num_test_questions: int = Field(5, ge=3, le=20, description="Number of test questions to generate")
    use_multihop: bool = Field(False, description="Include multi-hop questions")
    openai_api_key: Optional[str] = Field(None, description="OpenAI API key (if not in env)")
    cohere_api_key: Optional[str] = Field(None, description="Cohere API key (if not in env)")


class EvaluationProgress(BaseModel):
    """Progress information for an evaluation"""

    current_system: Optional[str] = None
    total_systems: int = 0
    completed_systems: int = 0
    current_step: str = "Initializing"
    progress_percentage: float = Field(0.0, ge=0, le=100)


class EvaluationInfo(BaseModel):
    """Evaluation information schema"""

    evaluation_id: str = Field(..., description="Unique identifier for the evaluation")
    document_id: str = Field(..., description="Document being evaluated")
    status: EvaluationStatus = Field(..., description="Current evaluation status")
    systems: List[SystemSelection] = Field(..., description="Systems being evaluated")
    num_test_questions: int = Field(..., description="Number of test questions")
    progress: Optional[EvaluationProgress] = None
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None


class StartEvaluationResponse(BaseModel):
    """Response schema for starting an evaluation"""

    success: bool = True
    evaluation_id: str = Field(..., description="Unique identifier for the evaluation")
    message: str = "Evaluation started successfully"


class EvaluationStatusResponse(BaseModel):
    """Response schema for evaluation status"""

    success: bool = True
    data: Optional[EvaluationInfo] = None
    error: Optional[str] = None
    message: str = "Evaluation status retrieved successfully"


class CancelEvaluationResponse(BaseModel):
    """Response schema for canceling an evaluation"""

    success: bool = True
    evaluation_id: str = Field(..., description="ID of the cancelled evaluation")
    message: str = "Evaluation cancelled successfully"
