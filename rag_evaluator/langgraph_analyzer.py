"""
LangGraph Multiagent System for RAG Evaluation Analysis
Analyzes RAGAS evaluation results using specialized agents
"""

from typing import Literal, Dict, Any
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command

from .analysis_state import (
    AnalysisState,
    MetricsAnalysis,
    PerformanceInsights,
    Recommendations,
    FinalReport,
)


# ============================================================================
# AGENT 1: METRICS ANALYZER
# ============================================================================


async def metrics_analyzer_agent(
    state: AnalysisState, openai_api_key: str
) -> Command[Literal["performance_analyzer"]]:
    """
    Analyzes RAGAS metrics to identify best/worst systems and key patterns.
    """

    evaluation_results = state.get("evaluation_results", {})
    analysis_query = state.get("analysis_query", "")

    # Initialize LLM with structured output
    model = init_chat_model(
        model="openai:gpt-4o-mini",
        api_key=openai_api_key,
        temperature=0.1,
        max_tokens=1500,
    )

    structured_model = model.with_structured_output(MetricsAnalysis)

    # Build comprehensive prompt
    systems_summary = []
    for system_name, result in evaluation_results.items():
        metrics = result.get("metrics", {})
        avg_score = result.get("average_score", 0)

        systems_summary.append(
            f"""
**{system_name}**:
- Average Score: {avg_score:.4f}
- Faithfulness: {metrics.get('faithfulness', 0):.4f}
- Context Recall: {metrics.get('context_recall', 0):.4f}
- Context Precision: {metrics.get('context_precision', 0):.4f}
- Answer Relevancy: {metrics.get('answer_relevancy', 0):.4f}
- Factual Correctness: {metrics.get('factual_correctness', 0):.4f}
"""
        )

    systems_text = "\n".join(systems_summary)

    prompt = f"""You are an expert RAG evaluation analyst. Analyze these RAGAS evaluation results.

USER QUERY: {analysis_query}

EVALUATION RESULTS:
{systems_text}

METRIC DEFINITIONS:
- **Faithfulness**: How factually consistent the answer is with the context (no hallucinations)
- **Context Recall**: How much of the ground truth is captured in retrieved contexts
- **Context Precision**: Ratio of relevant to irrelevant contexts (signal-to-noise)
- **Answer Relevancy**: How relevant the answer is to the question
- **Factual Correctness**: How much the answer overlaps with ground truth

TASK:
1. Identify the best and worst performing systems
2. Analyze each metric across all systems
3. Find 3-5 key insights or patterns
4. Determine if deeper analysis is needed

Provide a thorough analysis with specific numbers and comparisons."""

    # Get structured analysis
    analysis = await structured_model.ainvoke([HumanMessage(content=prompt)])

    # Format analysis as text
    analysis_text = f"""
## 📊 Metrics Analysis

**Best System**: {analysis.best_system} ({analysis.best_system_score:.4f})
**Worst System**: {analysis.worst_system} ({analysis.worst_system_score:.4f})

**Key Findings**:
{chr(10).join(f'- {finding}' for finding in analysis.key_findings)}

**Metric Breakdown**:
{chr(10).join(f'- **{metric}**: {analysis_text}' for metric, analysis_text in analysis.metric_breakdown.items())}

**Reasoning**: {analysis.reasoning}
"""

    return Command(
        goto="performance_analyzer",
        update={
            "metrics_analysis": analysis_text,
            "messages": [f"✅ Metrics analyzed - Best: {analysis.best_system}"],
        },
    )


# ============================================================================
# AGENT 2: PERFORMANCE ANALYZER
# ============================================================================


async def performance_analyzer_agent(
    state: AnalysisState, openai_api_key: str
) -> Command[Literal["recommendation_agent"]]:
    """
    Analyzes performance patterns, strengths, and weaknesses.
    """

    evaluation_results = state.get("evaluation_results", {})
    metrics_analysis = state.get("metrics_analysis", "")
    analysis_query = state.get("analysis_query", "")

    model = init_chat_model(
        model="openai:gpt-4o-mini",
        api_key=openai_api_key,
        temperature=0.2,
        max_tokens=1500,
    )

    structured_model = model.with_structured_output(PerformanceInsights)

    # Build context about system configurations
    config_summary = []
    for system_name, result in evaluation_results.items():
        system_info = result.get("system_info", {})
        config = system_info.get("config", {})
        config_summary.append(f"- **{system_name}**: {config}")

    configs_text = "\n".join(config_summary)

    prompt = f"""You are a RAG performance expert. Analyze the performance patterns and provide insights.

USER QUERY: {analysis_query}

PREVIOUS METRICS ANALYSIS:
{metrics_analysis}

SYSTEM CONFIGURATIONS:
{configs_text}

TASK:
1. Identify strengths of the best performing system(s)
2. Identify weaknesses and failure patterns
3. Discover patterns across different retrieval strategies
4. Assess context quality (recall + precision)
5. Assess answer quality (faithfulness + relevancy)

Focus on WHY certain systems perform better and WHAT patterns emerge."""

    insights = await structured_model.ainvoke([HumanMessage(content=prompt)])

    insights_text = f"""
## 🔍 Performance Insights

**Strengths**:
{chr(10).join(f'- {strength}' for strength in insights.strengths)}

**Weaknesses**:
{chr(10).join(f'- {weakness}' for weakness in insights.weaknesses)}

**Patterns Discovered**:
{chr(10).join(f'- {pattern}' for pattern in insights.patterns)}

**Context Quality Assessment**:
{insights.context_quality_assessment}

**Answer Quality Assessment**:
{insights.answer_quality_assessment}

**Analysis Reasoning**: {insights.reasoning}
"""

    return Command(
        goto="recommendation_agent",
        update={
            "performance_insights": insights_text,
            "messages": [f"✅ Performance patterns identified - {len(insights.patterns)} key patterns found"],
        },
    )


# ============================================================================
# AGENT 3: RECOMMENDATION AGENT
# ============================================================================


async def recommendation_agent(
    state: AnalysisState, openai_api_key: str
) -> Command[Literal["report_generator"]]:
    """
    Generates actionable recommendations based on analysis.
    """

    metrics_analysis = state.get("metrics_analysis", "")
    performance_insights = state.get("performance_insights", "")
    analysis_query = state.get("analysis_query", "")

    model = init_chat_model(
        model="openai:gpt-4o-mini",
        api_key=openai_api_key,
        temperature=0.3,
        max_tokens=1500,
    )

    structured_model = model.with_structured_output(Recommendations)

    prompt = f"""You are a RAG optimization consultant. Provide actionable recommendations.

USER QUERY: {analysis_query}

METRICS ANALYSIS:
{metrics_analysis}

PERFORMANCE INSIGHTS:
{performance_insights}

TASK:
Provide specific, actionable recommendations:

1. **Immediate Actions**: 2-3 quick wins that can be implemented right away
2. **Configuration Changes**: Specific parameter tweaks (chunk sizes, retrieval methods, etc.)
3. **Next Experiments**: What should be tested next to improve further
4. **Best System Recommendation**: Which system to deploy and why

Make recommendations specific and actionable, not generic advice."""

    recs = await structured_model.ainvoke([HumanMessage(content=prompt)])

    recommendations_text = f"""
## 💡 Recommendations

### Immediate Actions
{chr(10).join(f'{i+1}. {action}' for i, action in enumerate(recs.immediate_actions))}

### Configuration Changes
{chr(10).join(f'- {change}' for change in recs.configuration_changes)}

### Next Experiments
{chr(10).join(f'- {exp}' for exp in recs.next_experiments)}

### 🎯 Best System Recommendation
{recs.best_system_recommendation}

**Reasoning**: {recs.reasoning}
"""

    return Command(
        goto="report_generator",
        update={
            "recommendations": recommendations_text,
            "messages": [f"✅ Generated {len(recs.immediate_actions)} immediate actions"],
        },
    )


# ============================================================================
# AGENT 4: REPORT GENERATOR (Supervisor)
# ============================================================================


async def report_generator_agent(
    state: AnalysisState, openai_api_key: str
) -> Command[Literal["__end__"]]:
    """
    Synthesizes all agent outputs into a comprehensive final report.
    """

    metrics_analysis = state.get("metrics_analysis", "")
    performance_insights = state.get("performance_insights", "")
    recommendations = state.get("recommendations", "")
    analysis_query = state.get("analysis_query", "")

    model = init_chat_model(
        model="openai:gpt-4o-mini",
        api_key=openai_api_key,
        temperature=0.2,
        max_tokens=2500,
    )

    structured_model = model.with_structured_output(FinalReport)

    prompt = f"""You are a senior RAG evaluation consultant. Synthesize all analyses into a final report.

USER QUERY: {analysis_query}

METRICS ANALYSIS:
{metrics_analysis}

PERFORMANCE INSIGHTS:
{performance_insights}

RECOMMENDATIONS:
{recommendations}

TASK:
Create a comprehensive final report with:

1. **Executive Summary**: 2-3 sentences capturing the most important findings
2. **Detailed Analysis**: Well-structured markdown report combining all insights
3. **Action Plan**: Prioritized list of next steps
4. **Confidence Level**: Your confidence in these recommendations (high/medium/low)

The report should be clear, actionable, and valuable for decision-making."""

    report = await structured_model.ainvoke([HumanMessage(content=prompt)])

    final_report_text = f"""
# 📋 RAG Evaluation Analysis Report

## Executive Summary
{report.executive_summary}

---

{report.detailed_analysis}

---

## 📝 Action Plan (Prioritized)
{chr(10).join(f'{i+1}. {action}' for i, action in enumerate(report.action_plan))}

---

**Confidence Level**: {report.confidence_level.upper()}

---

*Report generated by LangGraph Multiagent Analysis System*
"""

    return Command(
        goto=END,
        update={
            "final_report": final_report_text,
            "messages": [f"✅ Final report generated - Confidence: {report.confidence_level}"],
        },
    )


# ============================================================================
# BUILD THE GRAPH
# ============================================================================


def build_analysis_graph(openai_api_key: str):
    """
    Build the LangGraph multiagent analysis system.

    Agent Flow:
    1. Metrics Analyzer → Identifies best/worst systems and key metrics
    2. Performance Analyzer → Discovers patterns and insights
    3. Recommendation Agent → Generates actionable recommendations
    4. Report Generator → Synthesizes everything into final report
    """

    # Create wrapper functions with API key bound
    async def metrics_analyzer_wrapper(state):
        return await metrics_analyzer_agent(state, openai_api_key)

    async def performance_analyzer_wrapper(state):
        return await performance_analyzer_agent(state, openai_api_key)

    async def recommendation_wrapper(state):
        return await recommendation_agent(state, openai_api_key)

    async def report_generator_wrapper(state):
        return await report_generator_agent(state, openai_api_key)

    # Build the graph
    builder = StateGraph(AnalysisState)

    # Add nodes
    builder.add_node("metrics_analyzer", metrics_analyzer_wrapper)
    builder.add_node("performance_analyzer", performance_analyzer_wrapper)
    builder.add_node("recommendation_agent", recommendation_wrapper)
    builder.add_node("report_generator", report_generator_wrapper)

    # Define edges (linear flow for now)
    builder.add_edge(START, "metrics_analyzer")
    # Command-based routing is handled by the return values

    return builder.compile()


# ============================================================================
# CONVENIENCE FUNCTION
# ============================================================================


async def analyze_evaluation_results(
    evaluation_results: Dict[str, Any],
    analysis_query: str,
    openai_api_key: str,
) -> Dict[str, Any]:
    """
    Main entry point for analyzing evaluation results.

    Args:
        evaluation_results: The RAGAS evaluation results from your RAG systems
        analysis_query: User's question or analysis request
        openai_api_key: OpenAI API key

    Returns:
        Dictionary with final report and intermediate analyses
    """

    # Build the graph
    graph = build_analysis_graph(openai_api_key)

    # Initialize state
    initial_state = {
        "evaluation_results": evaluation_results,
        "analysis_query": analysis_query,
        "metrics_analysis": None,
        "performance_insights": None,
        "recommendations": None,
        "final_report": None,
        "messages": [],
        "iteration": 0,
    }

    # Run the graph
    result = await graph.ainvoke(initial_state)

    return {
        "final_report": result.get("final_report", ""),
        "metrics_analysis": result.get("metrics_analysis", ""),
        "performance_insights": result.get("performance_insights", ""),
        "recommendations": result.get("recommendations", ""),
        "messages": result.get("messages", []),
    }
