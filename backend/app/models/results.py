"""
Pydantic models for results-related API schemas
"""

from typing import Any, Dict, List, Optional
from enum import Enum
from pydantic import BaseModel, Field


class MetricScores(BaseModel):
    """RAGAS metric scores for a system"""

    faithfulness: float = Field(..., ge=0, le=1, description="Factual consistency score")
    context_recall: float = Field(..., ge=0, le=1, description="Ground truth coverage score")
    context_precision: float = Field(..., ge=0, le=1, description="Signal-to-noise ratio score")
    answer_relevancy: float = Field(..., ge=0, le=1, description="Question relevance score")
    factual_correctness: float = Field(..., ge=0, le=1, description="Ground truth overlap score")


class SystemResult(BaseModel):
    """Evaluation results for a single retrieval system"""

    system_name: str = Field(..., description="Name of the retrieval system")
    system_type: str = Field(..., description="Type of the retrieval system")
    metrics: MetricScores = Field(..., description="RAGAS metric scores")
    average_score: float = Field(..., ge=0, le=1, description="Average of all metrics")
    initialization_time: float = Field(..., description="Time taken to initialize (seconds)")
    evaluation_time: float = Field(..., description="Time taken to evaluate (seconds)")
    config: Dict[str, Any] = Field(..., description="System configuration")


class EvaluationResults(BaseModel):
    """Complete evaluation results"""

    evaluation_id: str = Field(..., description="Evaluation ID")
    document_id: str = Field(..., description="Document ID")
    results: Dict[str, SystemResult] = Field(..., description="Results for each system")
    best_system: Optional[str] = Field(None, description="Name of the best performing system")
    best_average_score: Optional[float] = Field(None, description="Best average score")
    completed_at: str = Field(..., description="Completion timestamp")


class ResultsResponse(BaseModel):
    """Response schema for evaluation results"""

    success: bool = True
    data: Optional[EvaluationResults] = None
    error: Optional[str] = None
    message: str = "Results retrieved successfully"


class ExportFormat(str, Enum):
    """Export format enum"""

    JSON = "json"
    CSV = "csv"
    MARKDOWN = "markdown"


class ExportRequest(BaseModel):
    """Request schema for exporting results"""

    evaluation_id: str = Field(..., description="ID of the evaluation to export")
    format: ExportFormat = Field(..., description="Export format (json, csv, markdown)")


class ExportResponse(BaseModel):
    """Response schema for export"""

    success: bool = True
    data: str = Field(..., description="Exported data as string")
    filename: str = Field(..., description="Suggested filename")
    content_type: str = Field(..., description="MIME content type")
    message: str = "Results exported successfully"
