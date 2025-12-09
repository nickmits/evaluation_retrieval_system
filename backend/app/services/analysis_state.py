"""
State definitions for LangGraph RAG Evaluation Analysis
Defines the state and response models for the multiagent analysis system
"""

from typing import TypedDict, List, Dict, Any, Optional, Annotated
from pydantic import BaseModel, Field
import operator


class AnalysisState(TypedDict):
    """State for the evaluation analysis multiagent system"""

    # Input data
    evaluation_results: Dict[str, Any]  # The RAGAS evaluation results
    analysis_query: str  # User's question or analysis request

    # Agent outputs
    metrics_analysis: Optional[str]  # Output from metrics analyzer
    performance_insights: Optional[str]  # Output from performance analyzer
    recommendations: Optional[str]  # Output from recommendation agent
    final_report: Optional[str]  # Final synthesized report

    # Tracking
    messages: Annotated[List[str], operator.add]  # Agent communication log
    iteration: int  # Current iteration for loops


class MetricsAnalysis(BaseModel):
    """Structured output from metrics analyzer agent"""

    best_system: str = Field(description="Name of the best performing system")
    best_system_score: float = Field(description="Average score of best system")
    worst_system: str = Field(description="Name of the worst performing system")
    worst_system_score: float = Field(description="Average score of worst system")

    key_findings: List[str] = Field(default_factory=list, description="3-5 key findings from the metrics")
    metric_breakdown: Dict[str, str] = Field(
        default_factory=dict,
        description="Analysis of each metric (faithfulness, recall, precision, relevancy, correctness)"
    )

    needs_deeper_analysis: bool = Field(
        default=False,
        description="Whether deeper analysis is needed"
    )
    reasoning: str = Field(default="", description="Reasoning for the analysis")


class PerformanceInsights(BaseModel):
    """Structured output from performance analyzer agent"""

    strengths: List[str] = Field(default_factory=list, description="Strengths of the best system")
    weaknesses: List[str] = Field(default_factory=list, description="Weaknesses identified")
    patterns: List[str] = Field(default_factory=list, description="Patterns discovered across systems")

    context_quality_assessment: str = Field(
        default="",
        description="Assessment of context recall and precision"
    )
    answer_quality_assessment: str = Field(
        default="",
        description="Assessment of faithfulness and relevancy"
    )

    reasoning: str = Field(default="", description="Reasoning for the insights")


class Recommendations(BaseModel):
    """Structured output from recommendation agent"""

    immediate_actions: List[str] = Field(
        default_factory=list,
        description="2-3 immediate actions to improve performance"
    )
    configuration_changes: List[str] = Field(
        default_factory=list,
        description="Suggested configuration changes (chunk size, retrieval method, etc.)"
    )
    next_experiments: List[str] = Field(
        default_factory=list,
        description="Suggested next experiments to run"
    )

    best_system_recommendation: str = Field(
        default="",
        description="Recommendation for which system to use and why"
    )
    reasoning: str = Field(default="", description="Reasoning for recommendations")


class FinalReport(BaseModel):
    """Structured output for final analysis report"""

    executive_summary: str = Field(
        default="",
        description="2-3 sentence executive summary"
    )
    detailed_analysis: str = Field(
        default="",
        description="Detailed analysis in markdown format"
    )
    action_plan: List[str] = Field(
        default_factory=list,
        description="Prioritized action plan"
    )
    confidence_level: str = Field(
        default="medium",
        description="Confidence level: high, medium, or low"
    )
