"""Pydantic models for API request/response validation"""

from .document import (
    DocumentUploadResponse,
    DocumentInfo,
    DocumentResponse,
)
from .evaluation import (
    EvaluationStatus,
    SystemType,
    SystemConfig,
    SystemSelection,
    EvaluationRequest,
    EvaluationProgress,
    EvaluationInfo,
    StartEvaluationResponse,
    EvaluationStatusResponse,
    CancelEvaluationResponse,
)
from .results import (
    MetricScores,
    SystemResult,
    EvaluationResults,
    ResultsResponse,
    ExportFormat,
    ExportRequest,
    ExportResponse,
)
from .analysis import (
    AnalysisStatus,
    AnalysisRequest,
    AnalysisProgress,
    AnalysisInfo,
    AnalysisResult,
    StartAnalysisResponse,
    AnalysisStatusResponse,
    AnalysisResultResponse,
)

__all__ = [
    # Document models
    "DocumentUploadResponse",
    "DocumentInfo",
    "DocumentResponse",
    # Evaluation models
    "EvaluationStatus",
    "SystemType",
    "SystemConfig",
    "SystemSelection",
    "EvaluationRequest",
    "EvaluationProgress",
    "EvaluationInfo",
    "StartEvaluationResponse",
    "EvaluationStatusResponse",
    "CancelEvaluationResponse",
    # Results models
    "MetricScores",
    "SystemResult",
    "EvaluationResults",
    "ResultsResponse",
    "ExportFormat",
    "ExportRequest",
    "ExportResponse",
    # Analysis models
    "AnalysisStatus",
    "AnalysisRequest",
    "AnalysisProgress",
    "AnalysisInfo",
    "AnalysisResult",
    "StartAnalysisResponse",
    "AnalysisStatusResponse",
    "AnalysisResultResponse",
]
