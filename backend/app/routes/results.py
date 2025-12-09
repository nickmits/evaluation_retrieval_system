"""
Results retrieval and export API endpoints
"""

from typing import Dict

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import Response

from app.models.results import (
    EvaluationResults,
    ExportFormat,
    ExportRequest,
    ExportResponse,
    MetricScores,
    ResultsResponse,
    SystemResult,
)
from app.routes.evaluations import evaluation_results_store, evaluations_store
from app.services.export_manager import ExportManager

# Create router
router = APIRouter()


@router.get(
    "/evaluations/{evaluation_id}/results",
    response_model=ResultsResponse,
    summary="Get evaluation results",
    description="Get the complete results of an evaluation",
)
async def get_evaluation_results(evaluation_id: str) -> ResultsResponse:
    """
    Get evaluation results

    Args:
        evaluation_id: Evaluation ID

    Returns:
        ResultsResponse: Evaluation results

    Raises:
        HTTPException: If evaluation not found or not completed
    """
    # Check if evaluation exists
    eval_info = evaluations_store.get(evaluation_id)
    if not eval_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Evaluation with ID '{evaluation_id}' not found"
        )

    # Check if results are available
    results = evaluation_results_store.get(evaluation_id)
    if not results:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Results for evaluation '{evaluation_id}' not found. Evaluation may not be completed yet."
        )

    # Convert results to response format
    system_results: Dict[str, SystemResult] = {}
    best_system = None
    best_score = 0.0

    for system_name, result_data in results.items():
        # Extract metrics from nested structure
        metrics_data = result_data.get("metrics", {})
        metrics = MetricScores(
            faithfulness=metrics_data.get("faithfulness", 0.0),
            context_recall=metrics_data.get("context_recall", 0.0),
            context_precision=metrics_data.get("context_precision", 0.0),
            answer_relevancy=metrics_data.get("answer_relevancy", 0.0),
            factual_correctness=metrics_data.get("factual_correctness", 0.0),
        )

        # Use pre-calculated average score
        avg_score = result_data.get("average_score", 0.0)

        # Track best system
        if avg_score > best_score:
            best_score = avg_score
            best_system = system_name

        # Extract system info
        system_info = result_data.get("system_info", {})

        # Create system result
        system_result = SystemResult(
            system_name=system_info.get("system_name", system_name),
            system_type=system_info.get("system_type", "unknown"),
            metrics=metrics,
            average_score=avg_score,
            initialization_time=system_info.get("initialization_time", 0.0),
            evaluation_time=result_data.get("evaluation_time", 0.0),
            config=system_info.get("config", {}),
        )

        system_results[system_name] = system_result

    # Create evaluation results
    evaluation_results = EvaluationResults(
        evaluation_id=evaluation_id,
        document_id=eval_info.document_id,
        results=system_results,
        best_system=best_system,
        best_average_score=best_score,
        completed_at=eval_info.completed_at.isoformat() if eval_info.completed_at else ""
    )

    return ResultsResponse(
        success=True,
        data=evaluation_results,
        message="Results retrieved successfully"
    )


@router.post(
    "/results/export",
    response_model=ExportResponse,
    summary="Export evaluation results",
    description="Export evaluation results in JSON, CSV, or Markdown format",
)
async def export_results(request: ExportRequest) -> ExportResponse:
    """
    Export evaluation results

    Args:
        request: Export request with format

    Returns:
        ExportResponse: Exported data

    Raises:
        HTTPException: If evaluation not found or results not available
    """
    # Check if results are available
    results = evaluation_results_store.get(request.evaluation_id)
    if not results:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Results for evaluation '{request.evaluation_id}' not found"
        )

    # Create export manager
    exporter = ExportManager(results)

    # Export based on format
    try:
        if request.format == ExportFormat.JSON:
            data = exporter.to_json()
            filename = f"evaluation_results_{request.evaluation_id}.json"
            content_type = "application/json"

        elif request.format == ExportFormat.CSV:
            data = exporter.to_csv()
            filename = f"evaluation_results_{request.evaluation_id}.csv"
            content_type = "text/csv"

        elif request.format == ExportFormat.MARKDOWN:
            data = exporter.to_markdown()
            filename = f"evaluation_results_{request.evaluation_id}.md"
            content_type = "text/markdown"

        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported export format: {request.format}"
            )

        return ExportResponse(
            success=True,
            data=data,
            filename=filename,
            content_type=content_type,
            message=f"Results exported successfully as {request.format}"
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export results: {str(e)}"
        )


@router.get(
    "/results/export/{evaluation_id}/{format}",
    summary="Download evaluation results",
    description="Download evaluation results file in specified format",
)
async def download_results(evaluation_id: str, format: str):
    """
    Download evaluation results as a file

    Args:
        evaluation_id: Evaluation ID
        format: Export format (json, csv, markdown)

    Returns:
        Response: File download

    Raises:
        HTTPException: If evaluation not found or results not available
    """
    # Validate format
    format_lower = format.lower()
    if format_lower not in ["json", "csv", "markdown"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported format: {format}. Use: json, csv, or markdown"
        )

    # Check if results are available
    results = evaluation_results_store.get(evaluation_id)
    if not results:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Results for evaluation '{evaluation_id}' not found"
        )

    # Create export manager
    exporter = ExportManager(results)

    # Export and return file
    try:
        if format_lower == "json":
            data = exporter.to_json()
            filename = f"evaluation_results_{evaluation_id}.json"
            media_type = "application/json"

        elif format_lower == "csv":
            data = exporter.to_csv()
            filename = f"evaluation_results_{evaluation_id}.csv"
            media_type = "text/csv"

        else:  # markdown
            data = exporter.to_markdown()
            filename = f"evaluation_results_{evaluation_id}.md"
            media_type = "text/markdown"

        return Response(
            content=data,
            media_type=media_type,
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export results: {str(e)}"
        )
