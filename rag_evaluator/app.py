"""
RAG Retrieval System Evaluation Platform
A web application for comparing different RAG retrieval strategies using RAGAS metrics
"""

import streamlit as st
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from rag_evaluator.document_processor import DocumentProcessor
from rag_evaluator.retrieval_systems import RetrievalSystemFactory
from rag_evaluator.evaluation_engine import EvaluationEngine
from rag_evaluator.visualizations import ResultsVisualizer
from rag_evaluator.export_manager import ExportManager
from rag_evaluator.langgraph_analyzer import analyze_evaluation_results
import asyncio

# Page configuration
st.set_page_config(
    page_title="RAG Evaluation Platform",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if 'evaluation_results' not in st.session_state:
        st.session_state.evaluation_results = None
    if 'processed_document' not in st.session_state:
        st.session_state.processed_document = None
    if 'uploaded_file_name' not in st.session_state:
        st.session_state.uploaded_file_name = None

def main():
    initialize_session_state()

    # Header
    st.markdown('<div class="main-header">🔍 RAG Retrieval System Evaluation Platform</div>', unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("""
    **Compare different RAG retrieval strategies** and find the best system for your use case.
    Upload your documents, select retrieval systems, and get detailed RAGAS metrics.
    """)

    # Sidebar - Configuration
    with st.sidebar:
        st.header("⚙️ Configuration")

        # API Keys
        st.subheader("🔑 API Keys")
        openai_key = st.text_input(
            "OpenAI API Key",
            type="password",
            value=os.getenv("OPENAI_API_KEY", ""),
            help="Required for embeddings and LLM"
        )
        cohere_key = st.text_input(
            "Cohere API Key (Optional)",
            type="password",
            value=os.getenv("COHERE_API_KEY", ""),
            help="Optional: For reranking in advanced systems"
        )

        # Set environment variables
        if openai_key:
            os.environ["OPENAI_API_KEY"] = openai_key
        if cohere_key:
            os.environ["COHERE_API_KEY"] = cohere_key

        st.markdown("---")

        # Evaluation Parameters
        st.subheader("📊 Evaluation Settings")
        num_test_questions = st.slider(
            "Number of Test Questions",
            min_value=3,
            max_value=20,
            value=5,
            help="Number of questions to generate for evaluation"
        )

        use_multihop = st.checkbox(
            "Include Multi-hop Questions",
            value=False,
            help="Generate more complex multi-hop reasoning questions"
        )

        st.markdown("---")
        st.markdown("### 📈 About RAGAS Metrics")
        st.markdown("""
        - **Faithfulness**: Factual consistency
        - **Context Recall**: Ground truth coverage
        - **Context Precision**: Signal-to-noise ratio
        - **Answer Relevancy**: Question relevance
        - **Factual Correctness**: Ground truth overlap
        """)

        st.markdown("---")
        st.info("ℹ️ **Note**: Multi-hop questions are currently disabled due to RAGAS compatibility. Single-hop questions provide reliable results.")

    # Main content tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📤 Upload & Configure", "🚀 Run Evaluation", "📊 Results & Export", "🤖 AI Analysis"])

    with tab1:
        st.header("Step 1: Upload Your Document")
        uploaded_file = st.file_uploader(
            "Choose a document file",
            type=['pdf', 'txt', 'docx'],
            help="Upload a PDF, TXT, or DOCX file to evaluate"
        )

        if uploaded_file is not None:
            st.success(f"✅ File uploaded: {uploaded_file.name}")
            st.session_state.uploaded_file_name = uploaded_file.name

            # Save uploaded file temporarily
            temp_dir = Path("temp_uploads")
            temp_dir.mkdir(exist_ok=True)
            temp_file_path = temp_dir / uploaded_file.name

            with open(temp_file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            st.session_state.processed_document = str(temp_file_path)

            st.info(f"📄 Document saved: {temp_file_path}")

        st.markdown("---")

        st.header("Step 2: Select Retrieval Systems to Compare")

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Simple Systems")
            simple_recursive = st.checkbox(
                "📋 Simple Recursive Chunking",
                value=True,
                help="Baseline: RecursiveCharacterTextSplitter + Vector Search"
            )
            if simple_recursive:
                with st.expander("⚙️ Configure"):
                    chunk_size_recursive = st.number_input(
                        "Chunk Size",
                        min_value=100,
                        max_value=2000,
                        value=1000,
                        step=100,
                        key="simple_recursive_chunk_size"
                    )
                    chunk_overlap_recursive = st.number_input(
                        "Chunk Overlap",
                        min_value=0,
                        max_value=500,
                        value=200,
                        step=50,
                        key="simple_recursive_overlap"
                    )

            simple_semantic = st.checkbox(
                "🧠 Simple Semantic Chunking",
                value=False,
                help="SemanticChunker + Vector Search (slower but often better)"
            )
            if simple_semantic:
                with st.expander("⚙️ Configure"):
                    threshold_type = st.selectbox(
                        "Breakpoint Type",
                        ["percentile", "standard_deviation", "interquartile"],
                        key="semantic_threshold_type"
                    )
                    threshold_amount = st.slider(
                        "Threshold Amount",
                        min_value=50,
                        max_value=99,
                        value=95,
                        key="semantic_threshold_amount"
                    )

        with col2:
            st.subheader("Advanced Systems")
            advanced_recursive = st.checkbox(
                "⚡ Advanced Recursive (Ensemble)",
                value=False,
                help="Recursive chunking + BM25 + Multi-Query + Reranking"
            )
            if advanced_recursive:
                with st.expander("⚙️ Configure"):
                    adv_chunk_size = st.number_input(
                        "Chunk Size",
                        min_value=100,
                        max_value=2000,
                        value=1000,
                        step=100,
                        key="adv_recursive_chunk_size"
                    )
                    adv_chunk_overlap = st.number_input(
                        "Chunk Overlap",
                        min_value=0,
                        max_value=500,
                        value=200,
                        step=50,
                        key="adv_recursive_overlap"
                    )

            advanced_semantic = st.checkbox(
                "🔬 Advanced Semantic (Ensemble)",
                value=False,
                help="Semantic chunking + BM25 + Multi-Query + Reranking"
            )
            if advanced_semantic:
                with st.expander("⚙️ Configure"):
                    adv_threshold_type = st.selectbox(
                        "Breakpoint Type",
                        ["percentile", "standard_deviation", "interquartile"],
                        key="adv_semantic_threshold_type"
                    )
                    adv_threshold_amount = st.slider(
                        "Threshold Amount",
                        min_value=50,
                        max_value=99,
                        value=95,
                        key="adv_semantic_threshold_amount"
                    )

        # Store selected systems
        selected_systems = []
        if simple_recursive:
            selected_systems.append({
                "name": "Simple Recursive",
                "type": "simple_recursive",
                "config": {
                    "chunk_size": chunk_size_recursive if simple_recursive else 1000,
                    "chunk_overlap": chunk_overlap_recursive if simple_recursive else 200
                }
            })
        if simple_semantic:
            selected_systems.append({
                "name": "Simple Semantic",
                "type": "simple_semantic",
                "config": {
                    "threshold_type": threshold_type if simple_semantic else "percentile",
                    "threshold_amount": threshold_amount if simple_semantic else 95
                }
            })
        if advanced_recursive:
            selected_systems.append({
                "name": "Advanced Recursive",
                "type": "advanced_recursive",
                "config": {
                    "chunk_size": adv_chunk_size if advanced_recursive else 1000,
                    "chunk_overlap": adv_chunk_overlap if advanced_recursive else 200
                }
            })
        if advanced_semantic:
            selected_systems.append({
                "name": "Advanced Semantic",
                "type": "advanced_semantic",
                "config": {
                    "threshold_type": adv_threshold_type if advanced_semantic else "percentile",
                    "threshold_amount": adv_threshold_amount if advanced_semantic else 95
                }
            })

        st.session_state.selected_systems = selected_systems

        if selected_systems:
            st.success(f"✅ {len(selected_systems)} system(s) selected for evaluation")
        else:
            st.warning("⚠️ Please select at least one retrieval system")

    with tab2:
        st.header("🚀 Run Evaluation")

        if not openai_key:
            st.error("❌ Please provide an OpenAI API key in the sidebar")
            return

        if not st.session_state.processed_document:
            st.warning("⚠️ Please upload a document in the 'Upload & Configure' tab")
            return

        if not st.session_state.selected_systems:
            st.warning("⚠️ Please select at least one retrieval system in the 'Upload & Configure' tab")
            return

        st.info(f"📄 Document: {st.session_state.uploaded_file_name}")
        st.info(f"🔧 Systems to evaluate: {len(st.session_state.selected_systems)}")
        st.info(f"📊 Test questions: {num_test_questions}")

        if st.button("▶️ Start Evaluation", type="primary", use_container_width=True):
            with st.spinner("🔄 Running evaluation... This may take several minutes..."):
                try:
                    # Initialize evaluation engine
                    engine = EvaluationEngine(
                        document_path=st.session_state.processed_document,
                        openai_api_key=openai_key,
                        cohere_api_key=cohere_key if cohere_key else None
                    )

                    # Run evaluation for each system
                    results = {}
                    progress_bar = st.progress(0)
                    status_text = st.empty()

                    for idx, system_config in enumerate(st.session_state.selected_systems):
                        status_text.text(f"Evaluating {system_config['name']}...")

                        try:
                            result = engine.evaluate_system(
                                system_type=system_config['type'],
                                system_config=system_config['config'],
                                num_test_questions=num_test_questions,
                                use_multihop=use_multihop
                            )
                            results[system_config['name']] = result
                            progress_bar.progress((idx + 1) / len(st.session_state.selected_systems))
                        except Exception as eval_error:
                            st.warning(f"⚠️ Failed to evaluate {system_config['name']}: {str(eval_error)}")
                            # Continue with other systems
                            continue

                    if results:
                        st.session_state.evaluation_results = results
                        status_text.text("✅ Evaluation complete!")
                        st.success(f"🎉 Evaluation completed! Successfully evaluated {len(results)} system(s). Check the 'Results & Export' tab.")
                    else:
                        st.error("❌ All evaluations failed. Please check the error messages above.")

                except Exception as e:
                    st.error(f"❌ Error during evaluation setup: {str(e)}")

                    # Show helpful error messages
                    error_msg = str(e).lower()
                    if "api" in error_msg or "key" in error_msg:
                        st.info("💡 This looks like an API key issue. Please check your OpenAI API key in the sidebar.")
                    elif "rate limit" in error_msg:
                        st.info("💡 You may have hit API rate limits. Try reducing the number of test questions or wait a moment.")
                    elif "file" in error_msg or "document" in error_msg:
                        st.info("💡 There may be an issue with your uploaded document. Try uploading a different file.")
                    else:
                        st.info("💡 Try reducing the number of test questions or selecting a simpler retrieval system.")

                    with st.expander("🔍 View detailed error"):
                        import traceback
                        st.code(traceback.format_exc())

    with tab3:
        st.header("📊 Evaluation Results")

        if not st.session_state.evaluation_results:
            st.info("No evaluation results yet. Run an evaluation in the 'Run Evaluation' tab.")
            return

        # Display results
        visualizer = ResultsVisualizer(st.session_state.evaluation_results)

        # Summary metrics
        st.subheader("📈 Overall Performance Comparison")
        visualizer.display_summary_metrics()

        st.markdown("---")

        # Detailed metrics
        st.subheader("🔍 Detailed Metrics Breakdown")
        visualizer.display_detailed_metrics()

        st.markdown("---")

        # Radar chart comparison
        st.subheader("📡 Radar Chart Comparison")
        visualizer.display_radar_chart()

        st.markdown("---")

        # Export section
        st.subheader("💾 Export Results")

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("📄 Export as JSON", use_container_width=True):
                exporter = ExportManager(st.session_state.evaluation_results)
                json_data = exporter.to_json()
                st.download_button(
                    label="Download JSON",
                    data=json_data,
                    file_name="rag_evaluation_results.json",
                    mime="application/json"
                )

        with col2:
            if st.button("📊 Export as CSV", use_container_width=True):
                exporter = ExportManager(st.session_state.evaluation_results)
                csv_data = exporter.to_csv()
                st.download_button(
                    label="Download CSV",
                    data=csv_data,
                    file_name="rag_evaluation_results.csv",
                    mime="text/csv"
                )

        with col3:
            if st.button("📝 Export as Markdown", use_container_width=True):
                exporter = ExportManager(st.session_state.evaluation_results)
                md_data = exporter.to_markdown()
                st.download_button(
                    label="Download Markdown",
                    data=md_data,
                    file_name="rag_evaluation_results.md",
                    mime="text/markdown"
                )

        st.markdown("---")

        # Recommendations
        st.subheader("💡 Recommendations")
        visualizer.display_recommendations()

    with tab4:
        st.header("🤖 AI-Powered Analysis with LangGraph")

        st.markdown("""
        **Multiagent Analysis System** - Let AI agents analyze your evaluation results and provide insights!

        This system uses **4 specialized LangGraph agents** working together:
        - 📊 **Metrics Analyzer**: Identifies best/worst systems and key patterns
        - 🔍 **Performance Analyzer**: Discovers strengths, weaknesses, and patterns
        - 💡 **Recommendation Agent**: Generates actionable recommendations
        - 📋 **Report Generator**: Synthesizes everything into a comprehensive report
        """)

        if not st.session_state.evaluation_results:
            st.warning("⚠️ Please run an evaluation first in the 'Run Evaluation' tab before using AI analysis.")
            return

        st.success(f"✅ Evaluation results available for {len(st.session_state.evaluation_results)} system(s)")

        st.markdown("---")

        # Analysis query input
        st.subheader("💬 What would you like to analyze?")

        analysis_query = st.text_area(
            "Your Question or Analysis Request",
            value="Analyze the evaluation results and tell me which retrieval system performs best and why. What should I do to improve performance?",
            height=100,
            help="Ask specific questions about the evaluation results, or request general analysis"
        )

        # Example queries
        with st.expander("💡 Example Questions"):
            st.markdown("""
            - "Which retrieval system should I use in production and why?"
            - "What are the main weaknesses in my current setup?"
            - "How can I improve context precision?"
            - "Compare the semantic vs recursive chunking strategies"
            - "What configuration changes would have the biggest impact?"
            - "Why is the advanced system not performing as expected?"
            """)

        st.markdown("---")

        # Run analysis button
        if st.button("🚀 Run AI Analysis", type="primary", use_container_width=True):
            if not openai_key:
                st.error("❌ Please provide an OpenAI API key in the sidebar")
                return

            with st.spinner("🤖 AI agents are analyzing your results... This may take 30-60 seconds..."):
                try:
                    # Create progress indicators
                    progress_placeholder = st.empty()
                    agent_status = st.empty()

                    # Show progress
                    progress_placeholder.progress(0.0)
                    agent_status.info("🔄 Agent 1/4: Metrics Analyzer is analyzing...")

                    # Run the analysis
                    analysis_result = asyncio.run(
                        analyze_evaluation_results(
                            evaluation_results=st.session_state.evaluation_results,
                            analysis_query=analysis_query,
                            openai_api_key=openai_key,
                        )
                    )

                    # Clear progress
                    progress_placeholder.empty()
                    agent_status.empty()

                    # Store result in session state
                    st.session_state.ai_analysis_result = analysis_result

                    st.success("✅ AI analysis complete! See results below.")

                except Exception as e:
                    st.error(f"❌ Error during AI analysis: {str(e)}")
                    with st.expander("🔍 View error details"):
                        import traceback
                        st.code(traceback.format_exc())
                    return

        # Display results if available
        if 'ai_analysis_result' in st.session_state and st.session_state.ai_analysis_result:
            st.markdown("---")
            st.markdown("## 📊 Analysis Results")

            result = st.session_state.ai_analysis_result

            # Show agent communication log
            with st.expander("🔄 Agent Communication Log"):
                messages = result.get("messages", [])
                for i, msg in enumerate(messages, 1):
                    st.text(f"{i}. {msg}")

            st.markdown("---")

            # Display final report
            st.markdown("### 📋 Final Analysis Report")
            final_report = result.get("final_report", "No report generated")
            st.markdown(final_report)

            st.markdown("---")

            # Show intermediate analyses in expandable sections
            col1, col2 = st.columns(2)

            with col1:
                with st.expander("📊 View Metrics Analysis"):
                    metrics_analysis = result.get("metrics_analysis", "Not available")
                    st.markdown(metrics_analysis)

                with st.expander("💡 View Recommendations"):
                    recommendations = result.get("recommendations", "Not available")
                    st.markdown(recommendations)

            with col2:
                with st.expander("🔍 View Performance Insights"):
                    performance_insights = result.get("performance_insights", "Not available")
                    st.markdown(performance_insights)

            # Download report button
            st.markdown("---")
            st.subheader("💾 Export AI Analysis")

            col1, col2, col3 = st.columns(3)

            with col1:
                if st.button("📄 Download Full Report", use_container_width=True):
                    report_content = f"""# RAG Evaluation AI Analysis Report

## Query
{analysis_query}

---

{final_report}

---

## Detailed Agent Outputs

### Metrics Analysis
{result.get("metrics_analysis", "Not available")}

### Performance Insights
{result.get("performance_insights", "Not available")}

### Recommendations
{result.get("recommendations", "Not available")}

---

*Generated by LangGraph Multiagent Analysis System*
"""
                    st.download_button(
                        label="Download Markdown Report",
                        data=report_content,
                        file_name="ai_analysis_report.md",
                        mime="text/markdown"
                    )

            with col2:
                if st.button("🔄 Run New Analysis", use_container_width=True):
                    if 'ai_analysis_result' in st.session_state:
                        del st.session_state.ai_analysis_result
                    st.rerun()

if __name__ == "__main__":
    main()
