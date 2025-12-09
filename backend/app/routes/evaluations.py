"""
Evaluation API endpoints with background task support
"""

import asyncio
import json
import uuid
from datetime import datetime
from typing import Dict, Optional

from fastapi import APIRouter, BackgroundTasks, File, HTTPException, UploadFile, status
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.models.evaluation import (
    CancelEvaluationResponse,
    EvaluationInfo,
    EvaluationProgress,
    EvaluationRequest,
    EvaluationStatus,
    EvaluationStatusResponse,
    StartEvaluationResponse,
)
from app.routes.documents import documents_store
from app.services.evaluation_engine import EvaluationEngine
from app.utils.background_tasks import TaskStatus, task_manager

# Get settings
settings = get_settings()

# Create router
router = APIRouter()

# In-memory storage for evaluation info (in production, use database)
evaluations_store: Dict[str, EvaluationInfo] = {}
evaluation_results_store: Dict[str, dict] = {}


async def run_evaluation_task(
    evaluation_id: str,
    evaluation_request: EvaluationRequest,
    document_path: str,
):
    """
    Background task to run evaluation

    Args:
        evaluation_id: Evaluation ID
        evaluation_request: Evaluation request data
        document_path: Path to the document file
    """
    try:
        # Update status to running
        task_manager.update_task_status(
            evaluation_id,
            TaskStatus.RUNNING,
            progress=0.0,
            message="Starting evaluation..."
        )

        # Update evaluation info
        if evaluation_id in evaluations_store:
            evaluations_store[evaluation_id].status = EvaluationStatus.RUNNING
            evaluations_store[evaluation_id].started_at = datetime.now()

        # Get API keys
        openai_key = evaluation_request.openai_api_key or settings.OPENAI_API_KEY
        cohere_key = evaluation_request.cohere_api_key or settings.COHERE_API_KEY

        if not openai_key:
            raise ValueError("OpenAI API key is required")

        # Initialize evaluation engine
        engine = EvaluationEngine(
            document_path=document_path,
            openai_api_key=openai_key,
            cohere_api_key=cohere_key
        )

        # Run evaluation for each system
        results = {}
        total_systems = len(evaluation_request.systems)

        for idx, system_config in enumerate(evaluation_request.systems):
            current_progress = 10.0 + (idx / total_systems) * 80.0

            try:
                # Run evaluation for this system
                result = engine.evaluate_system(
                    system_type=system_config.type.value,
                    system_config=system_config.config.model_dump(),
                    num_test_questions=evaluation_request.num_test_questions,
                    use_multihop=evaluation_request.use_multihop
                )

                results[system_config.name] = result

            except Exception as system_error:
                # Log error but continue with other systems
                print(f"Failed to evaluate {system_config.name}: {str(system_error)}")

        if not results:
            raise ValueError("All system evaluations failed")

        # Store results
        evaluation_results_store[evaluation_id] = results

        # Update status to completed
        task_manager.update_task_status(
            evaluation_id,
            TaskStatus.COMPLETED,
            progress=100.0,
            message="Evaluation completed successfully"
        )
        task_manager.set_task_result(evaluation_id, results)

        # Update evaluation info
        if evaluation_id in evaluations_store:
            evaluations_store[evaluation_id].status = EvaluationStatus.COMPLETED
            evaluations_store[evaluation_id].completed_at = datetime.now()

    except asyncio.CancelledError:
        # Task was cancelled
        task_manager.update_task_status(
            evaluation_id,
            TaskStatus.CANCELLED,
            message="Evaluation cancelled by user"
        )

        if evaluation_id in evaluations_store:
            evaluations_store[evaluation_id].status = EvaluationStatus.CANCELLED

    except Exception as e:
        # Task failed
        error_msg = str(e)
        task_manager.update_task_status(
            evaluation_id,
            TaskStatus.FAILED,
            message=f"Evaluation failed: {error_msg}",
            error=error_msg
        )

        if evaluation_id in evaluations_store:
            evaluations_store[evaluation_id].status = EvaluationStatus.FAILED
            evaluations_store[evaluation_id].error = error_msg

    finally:
        # Cleanup
        task_manager.cleanup_task(evaluation_id)


@router.post(
    "/evaluations/start",
    response_model=StartEvaluationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Start a new evaluation",
    description="Start a new RAG retrieval system evaluation as a background task",
)
async def start_evaluation(
    request: EvaluationRequest,
    background_tasks: BackgroundTasks,
) -> StartEvaluationResponse:
    """
    Start a new evaluation

    Args:
        request: Evaluation request
        background_tasks: FastAPI background tasks

    Returns:
        StartEvaluationResponse: Evaluation ID and status

    Raises:
        HTTPException: If document not found or validation fails
    """
    # Validate document exists
    doc_info = documents_store.get(request.document_id)
    if not doc_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID '{request.document_id}' not found"
        )

    # Generate evaluation ID
    evaluation_id = str(uuid.uuid4())

    # Create task
    task_manager.create_task("evaluation", evaluation_id)

    # Create evaluation info
    eval_info = EvaluationInfo(
        evaluation_id=evaluation_id,
        document_id=request.document_id,
        status=EvaluationStatus.PENDING,
        systems=request.systems,
        num_test_questions=request.num_test_questions,
        progress=EvaluationProgress(
            current_system=None,
            total_systems=len(request.systems),
            completed_systems=0,
            current_step="Initializing",
            progress_percentage=0.0
        ),
        created_at=datetime.now(),
    )

    evaluations_store[evaluation_id] = eval_info

    # Start background task
    background_tasks.add_task(
        run_evaluation_task,
        evaluation_id,
        request,
        doc_info.file_path
    )

    # Return response
    return StartEvaluationResponse(
        success=True,
        evaluation_id=evaluation_id,
        message="Evaluation started successfully"
    )


@router.get(
    "/evaluations/{evaluation_id}/status",
    response_model=EvaluationStatusResponse,
    summary="Get evaluation status",
    description="Get the current status of an evaluation",
)
async def get_evaluation_status(evaluation_id: str) -> EvaluationStatusResponse:
    """
    Get evaluation status

    Args:
        evaluation_id: Evaluation ID

    Returns:
        EvaluationStatusResponse: Current status

    Raises:
        HTTPException: If evaluation not found
    """
    eval_info = evaluations_store.get(evaluation_id)

    if not eval_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Evaluation with ID '{evaluation_id}' not found"
        )

    # Update progress from task manager
    task = task_manager.get_task(evaluation_id)
    if task and eval_info.progress:
        eval_info.progress.progress_percentage = task.progress
        eval_info.progress.current_step = task.message

    return EvaluationStatusResponse(
        success=True,
        data=eval_info,
        message="Evaluation status retrieved successfully"
    )


@router.post(
    "/evaluations/{evaluation_id}/cancel",
    response_model=CancelEvaluationResponse,
    summary="Cancel an evaluation",
    description="Cancel a running evaluation",
)
async def cancel_evaluation(evaluation_id: str) -> CancelEvaluationResponse:
    """
    Cancel an evaluation

    Args:
        evaluation_id: Evaluation ID

    Returns:
        CancelEvaluationResponse: Cancellation confirmation

    Raises:
        HTTPException: If evaluation not found or not running
    """
    eval_info = evaluations_store.get(evaluation_id)

    if not eval_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Evaluation with ID '{evaluation_id}' not found"
        )

    if eval_info.status not in [EvaluationStatus.PENDING, EvaluationStatus.RUNNING]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot cancel evaluation with status '{eval_info.status}'"
        )

    # Cancel the task
    cancelled = await task_manager.cancel_task(evaluation_id)

    if not cancelled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Evaluation could not be cancelled (may have already finished)"
        )

    return CancelEvaluationResponse(
        success=True,
        evaluation_id=evaluation_id,
        message="Evaluation cancelled successfully"
    )


@router.post(
    "/evaluations/import",
    response_model=StartEvaluationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Import evaluation results from JSON",
    description="Import previously exported evaluation results from a JSON file",
)
async def import_evaluation_results(
    file: UploadFile = File(...),
) -> StartEvaluationResponse:
    """
    Import evaluation results from a JSON file

    Args:
        file: JSON file containing evaluation results

    Returns:
        StartEvaluationResponse: Evaluation ID for the imported results

    Raises:
        HTTPException: If file is invalid or JSON structure is incorrect
    """
    # Validate file type
    if not file.filename or not file.filename.endswith('.json'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be a JSON file (.json)"
        )

    try:
        # Read and parse JSON
        contents = await file.read()
        imported_data = json.loads(contents)

        # Validate JSON structure
        if not isinstance(imported_data, dict):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid JSON structure: Expected a dictionary"
            )

        # Check if it's the export format (with "results" key) or direct system results
        if "results" in imported_data:
            # Export format: {"evaluation_timestamp": "...", "results": {...}}
            results_data = imported_data["results"]
        else:
            # Direct format: {"System Name": {...}, ...}
            results_data = imported_data

        # Validate that we have system results
        if not isinstance(results_data, dict) or len(results_data) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No system results found in JSON file"
            )

        # Validate that each system has required fields
        for system_name, system_data in results_data.items():
            if not isinstance(system_data, dict):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid structure for system '{system_name}'"
                )

            # Check for required keys
            if "metrics" not in system_data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"System '{system_name}' missing 'metrics' field"
                )

            if "system_info" not in system_data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"System '{system_name}' missing 'system_info' field"
                )

        # Generate evaluation ID for imported results
        evaluation_id = str(uuid.uuid4())

        # Store results
        evaluation_results_store[evaluation_id] = results_data

        # Create evaluation info (mark as imported)
        eval_info = EvaluationInfo(
            evaluation_id=evaluation_id,
            document_id="imported",  # Special marker for imported results
            status=EvaluationStatus.COMPLETED,
            systems=[],  # No system configs for imported results
            num_test_questions=0,
            progress=EvaluationProgress(
                current_system=None,
                total_systems=len(results_data),
                completed_systems=len(results_data),
                current_step="Imported from JSON",
                progress_percentage=100.0
            ),
            created_at=datetime.now(),
            completed_at=datetime.now(),
        )

        evaluations_store[evaluation_id] = eval_info

        return StartEvaluationResponse(
            success=True,
            evaluation_id=evaluation_id,
            message=f"Evaluation results imported successfully ({len(results_data)} systems)"
        )

    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid JSON file: {str(e)}"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to import evaluation results: {str(e)}"
        )
