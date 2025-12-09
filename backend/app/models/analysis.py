"""
Pydantic models for AI analysis-related API schemas
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from enum import Enum
from pydantic import BaseModel, Field


class AnalysisStatus(str, Enum):
    """Analysis status enum"""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class AnalysisRequest(BaseModel):
    """Request schema for starting AI analysis"""

    evaluation_id: str = Field(..., description="ID of the evaluation to analyze")
    analysis_query: str = Field(
        "Analyze the evaluation results and tell me which retrieval system performs best and why. What should I do to improve performance?",
        description="Custom analysis query or question"
    )
    openai_api_key: Optional[str] = Field(None, description="OpenAI API key (if not in env)")


class AnalysisProgress(BaseModel):
    """Progress information for AI analysis"""

    current_agent: Optional[str] = None
    total_agents: int = 4
    completed_agents: int = 0
    current_step: str = "Initializing"
    progress_percentage: float = Field(0.0, ge=0, le=100)


class AnalysisInfo(BaseModel):
    """Analysis information schema"""

    analysis_id: str = Field(..., description="Unique identifier for the analysis")
    evaluation_id: str = Field(..., description="Evaluation being analyzed")
    status: AnalysisStatus = Field(..., description="Current analysis status")
    query: str = Field(..., description="Analysis query")
    progress: Optional[AnalysisProgress] = None
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None


class AnalysisResult(BaseModel):
    """AI analysis result"""

    analysis_id: str = Field(..., description="Analysis ID")
    evaluation_id: str = Field(..., description="Evaluation ID")
    query: str = Field(..., description="Analysis query")
    metrics_analysis: str = Field(..., description="Metrics analyzer output")
    performance_insights: str = Field(..., description="Performance analyzer output")
    recommendations: str = Field(..., description="Recommendation agent output")
    final_report: str = Field(..., description="Final synthesized report")
    messages: List[str] = Field(default_factory=list, description="Agent communication log")
    completed_at: datetime = Field(default_factory=datetime.now, description="Completion timestamp")


class StartAnalysisResponse(BaseModel):
    """Response schema for starting analysis"""

    success: bool = True
    analysis_id: str = Field(..., description="Unique identifier for the analysis")
    message: str = "AI analysis started successfully"


class AnalysisStatusResponse(BaseModel):
    """Response schema for analysis status"""

    success: bool = True
    data: Optional[AnalysisInfo] = None
    error: Optional[str] = None
    message: str = "Analysis status retrieved successfully"


class AnalysisResultResponse(BaseModel):
    """Response schema for analysis results"""

    success: bool = True
    data: Optional[AnalysisResult] = None
    error: Optional[str] = None
    message: str = "Analysis results retrieved successfully"
