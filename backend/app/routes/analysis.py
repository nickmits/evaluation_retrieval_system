"""
AI Analysis API endpoints with background task support (LangGraph)
"""

import asyncio
import uuid
from datetime import datetime
from typing import Dict, Optional

from fastapi import APIRouter, BackgroundTasks, HTTPException, status

from app.config import get_settings
from app.models.analysis import (
    AnalysisInfo,
    AnalysisProgress,
    AnalysisRequest,
    AnalysisResult,
    AnalysisResultResponse,
    AnalysisStatus,
    AnalysisStatusResponse,
    StartAnalysisResponse,
)
from app.routes.evaluations import evaluation_results_store
from app.services.langgraph_analyzer import analyze_evaluation_results
from app.utils.background_tasks import TaskStatus, task_manager

# Get settings
settings = get_settings()

# Create router
router = APIRouter()

# In-memory storage for analysis info (in production, use database)
analysis_store: Dict[str, AnalysisInfo] = {}
analysis_results_store: Dict[str, AnalysisResult] = {}


async def run_analysis_task(
    analysis_id: str,
    analysis_request: AnalysisRequest,
    evaluation_results: dict,
):
    """
    Background task to run AI analysis

    Args:
        analysis_id: Analysis ID
        analysis_request: Analysis request data
        evaluation_results: Evaluation results to analyze
    """
    try:
        # Update status to running
        task_manager.update_task_status(
            analysis_id,
            TaskStatus.RUNNING,
            progress=0.0,
            message="Starting AI analysis..."
        )

        # Update analysis info
        if analysis_id in analysis_store:
            analysis_store[analysis_id].status = AnalysisStatus.RUNNING
            analysis_store[analysis_id].started_at = datetime.now()

        # Get API key
        openai_key = analysis_request.openai_api_key or settings.OPENAI_API_KEY

        if not openai_key:
            raise ValueError("OpenAI API key is required")

        # Run the LangGraph analysis
        analysis_result_data = await analyze_evaluation_results(
            evaluation_results=evaluation_results,
            analysis_query=analysis_request.analysis_query,
            openai_api_key=openai_key,
        )

        # Create analysis result
        analysis_result = AnalysisResult(
            analysis_id=analysis_id,
            evaluation_id=analysis_request.evaluation_id,
            query=analysis_request.analysis_query,
            metrics_analysis=analysis_result_data.get("metrics_analysis", "Not available"),
            performance_insights=analysis_result_data.get("performance_insights", "Not available"),
            recommendations=analysis_result_data.get("recommendations", "Not available"),
            final_report=analysis_result_data.get("final_report", "No report generated"),
            messages=analysis_result_data.get("messages", []),
            completed_at=datetime.now(),
        )

        # Store result
        analysis_results_store[analysis_id] = analysis_result

        # Update status to completed
        task_manager.update_task_status(
            analysis_id,
            TaskStatus.COMPLETED,
            progress=100.0,
            message="AI analysis completed successfully"
        )
        task_manager.set_task_result(analysis_id, analysis_result)

        # Update analysis info
        if analysis_id in analysis_store:
            analysis_store[analysis_id].status = AnalysisStatus.COMPLETED
            analysis_store[analysis_id].completed_at = datetime.now()

    except asyncio.CancelledError:
        # Task was cancelled
        task_manager.update_task_status(
            analysis_id,
            TaskStatus.CANCELLED,
            message="Analysis cancelled by user"
        )

        if analysis_id in analysis_store:
            analysis_store[analysis_id].status = AnalysisStatus.FAILED
            analysis_store[analysis_id].error = "Cancelled by user"

    except Exception as e:
        # Task failed
        error_msg = str(e)
        task_manager.update_task_status(
            analysis_id,
            TaskStatus.FAILED,
            message=f"Analysis failed: {error_msg}",
            error=error_msg
        )

        if analysis_id in analysis_store:
            analysis_store[analysis_id].status = AnalysisStatus.FAILED
            analysis_store[analysis_id].error = error_msg

    finally:
        # Cleanup
        task_manager.cleanup_task(analysis_id)


@router.post(
    "/analysis/start",
    response_model=StartAnalysisResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Start AI analysis",
    description="Start AI-powered analysis of evaluation results using LangGraph agents",
)
async def start_analysis(
    request: AnalysisRequest,
    background_tasks: BackgroundTasks,
) -> StartAnalysisResponse:
    """
    Start AI analysis of evaluation results

    Args:
        request: Analysis request
        background_tasks: FastAPI background tasks

    Returns:
        StartAnalysisResponse: Analysis ID and status

    Raises:
        HTTPException: If evaluation not found or results not available
    """
    # Validate evaluation results exist
    evaluation_results = evaluation_results_store.get(request.evaluation_id)
    if not evaluation_results:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Evaluation results for ID '{request.evaluation_id}' not found. Please run evaluation first."
        )

    # Generate analysis ID
    analysis_id = str(uuid.uuid4())

    # Create task
    task_manager.create_task("analysis", analysis_id)

    # Create analysis info
    analysis_info = AnalysisInfo(
        analysis_id=analysis_id,
        evaluation_id=request.evaluation_id,
        status=AnalysisStatus.PENDING,
        query=request.analysis_query,
        progress=AnalysisProgress(
            current_agent=None,
            total_agents=4,
            completed_agents=0,
            current_step="Initializing",
            progress_percentage=0.0
        ),
        created_at=datetime.now(),
    )

    analysis_store[analysis_id] = analysis_info

    # Start background task
    background_tasks.add_task(
        run_analysis_task,
        analysis_id,
        request,
        evaluation_results
    )

    # Return response
    return StartAnalysisResponse(
        success=True,
        analysis_id=analysis_id,
        message="AI analysis started successfully"
    )


@router.get(
    "/analysis/{analysis_id}/status",
    response_model=AnalysisStatusResponse,
    summary="Get analysis status",
    description="Get the current status of an AI analysis",
)
async def get_analysis_status(analysis_id: str) -> AnalysisStatusResponse:
    """
    Get analysis status

    Args:
        analysis_id: Analysis ID

    Returns:
        AnalysisStatusResponse: Current status

    Raises:
        HTTPException: If analysis not found
    """
    analysis_info = analysis_store.get(analysis_id)

    if not analysis_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Analysis with ID '{analysis_id}' not found"
        )

    # Update progress from task manager
    task = task_manager.get_task(analysis_id)
    if task and analysis_info.progress:
        analysis_info.progress.progress_percentage = task.progress
        analysis_info.progress.current_step = task.message

    return AnalysisStatusResponse(
        success=True,
        data=analysis_info,
        message="Analysis status retrieved successfully"
    )


@router.get(
    "/analysis/{analysis_id}/results",
    response_model=AnalysisResultResponse,
    summary="Get analysis results",
    description="Get the results of a completed AI analysis",
)
async def get_analysis_results(analysis_id: str) -> AnalysisResultResponse:
    """
    Get analysis results

    Args:
        analysis_id: Analysis ID

    Returns:
        AnalysisResultResponse: Analysis results

    Raises:
        HTTPException: If analysis not found or not completed
    """
    analysis_info = analysis_store.get(analysis_id)

    if not analysis_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Analysis with ID '{analysis_id}' not found"
        )

    if analysis_info.status != AnalysisStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Analysis not completed yet. Current status: {analysis_info.status}"
        )

    analysis_result = analysis_results_store.get(analysis_id)

    if not analysis_result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Analysis results for ID '{analysis_id}' not found"
        )

    return AnalysisResultResponse(
        success=True,
        data=analysis_result,
        message="Analysis results retrieved successfully"
    )
