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
    PARENT_DOCUMENT = "parent_document"
    ADVANCED_PARENT_DOCUMENT = "advanced_parent_document"


class EmbeddingConfig(BaseModel):
    """Configuration for embedding model"""

    provider: str = Field("openai", description="Embedding provider (openai, cohere, huggingface)")
    model: str = Field("text-embedding-3-small", description="Embedding model name")
    dimensions: Optional[int] = Field(None, description="Embedding dimensions (auto-detected if not specified)")


class RetrievalConfig(BaseModel):
    """Configuration for retrieval parameters"""

    base_k: int = Field(10, ge=1, le=50, description="Number of documents for base vector search")
    bm25_k: int = Field(10, ge=1, le=50, description="Number of documents for BM25 search")
    multi_query_k: int = Field(15, ge=1, le=50, description="Number of documents for multi-query retrieval")
    final_k: int = Field(10, ge=1, le=50, description="Final number of documents to return")


class EnsembleWeights(BaseModel):
    """Configuration for ensemble retriever weights"""

    bm25_weight: float = Field(0.3, ge=0, le=1, description="Weight for BM25 retriever")
    vector_weight: float = Field(0.3, ge=0, le=1, description="Weight for vector retriever")
    multi_query_weight: float = Field(0.2, ge=0, le=1, description="Weight for multi-query retriever")
    reranking_weight: float = Field(0.2, ge=0, le=1, description="Weight for reranking retriever")


class SystemConfig(BaseModel):
    """Configuration for a retrieval system"""

    # Chunking configs
    chunk_size: Optional[int] = Field(1000, ge=100, le=2000, description="Chunk size for text splitting")
    chunk_overlap: Optional[int] = Field(200, ge=0, le=500, description="Overlap between chunks")
    threshold_type: Optional[str] = Field("percentile", description="Threshold type for semantic chunking")
    threshold_amount: Optional[int] = Field(95, ge=50, le=99, description="Threshold amount for semantic chunking")
    parent_chunk_size: Optional[int] = Field(2000, ge=500, le=4000, description="Parent chunk size for parent document retrieval")
    parent_chunk_overlap: Optional[int] = Field(200, ge=0, le=500, description="Overlap between parent chunks")
    child_chunk_size: Optional[int] = Field(400, ge=100, le=1000, description="Child chunk size for parent document retrieval")
    child_chunk_overlap: Optional[int] = Field(50, ge=0, le=200, description="Overlap between child chunks")

    # Dynamic configs
    embedding_config: Optional[EmbeddingConfig] = Field(default_factory=EmbeddingConfig, description="Embedding model configuration")
    retrieval_config: Optional[RetrievalConfig] = Field(default_factory=RetrievalConfig, description="Retrieval parameters")
    ensemble_weights: Optional[EnsembleWeights] = Field(default_factory=EnsembleWeights, description="Ensemble weights")


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
