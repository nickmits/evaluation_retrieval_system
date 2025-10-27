"""
Visualizations
Handles result visualization and display in Streamlit
"""

from typing import Dict, Any, List
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px


class ResultsVisualizer:
    """Visualize evaluation results in Streamlit"""

    def __init__(self, results: Dict[str, Any]):
        self.results = results

    def display_summary_metrics(self):
        """Display summary metrics for all systems"""

        # Create DataFrame for comparison
        comparison_data = []

        for system_name, result in self.results.items():
            metrics = result['metrics']
            comparison_data.append({
                'System': system_name,
                'Average Score': result['average_score'],
                'Faithfulness': metrics['faithfulness'],
                'Context Recall': metrics['context_recall'],
                'Context Precision': metrics['context_precision'],
                'Answer Relevancy': metrics['answer_relevancy'],
                'Factual Correctness': metrics['factual_correctness'],
                'Init Time (s)': result['system_info']['initialization_time'],
                'Num Chunks': result['system_info']['num_chunks']
            })

        df = pd.DataFrame(comparison_data)

        # Display metrics table with color coding
        def highlight_scores(val):
            """Color code scores: green for good, yellow for medium, red for low"""
            if isinstance(val, (int, float)):
                if val >= 0.7:
                    color = '#90EE90'  # Light green
                elif val >= 0.5:
                    color = '#FFE4B5'  # Light yellow
                else:
                    color = '#FFB6C1'  # Light red
                return f'background-color: {color}'
            return ''

        # Format and style the dataframe
        styled_df = df.style.format({
            'Average Score': '{:.4f}',
            'Faithfulness': '{:.4f}',
            'Context Recall': '{:.4f}',
            'Context Precision': '{:.4f}',
            'Answer Relevancy': '{:.4f}',
            'Factual Correctness': '{:.4f}',
            'Init Time (s)': '{:.2f}'
        }).applymap(
            highlight_scores,
            subset=['Average Score', 'Faithfulness', 'Context Recall',
                    'Context Precision', 'Answer Relevancy', 'Factual Correctness']
        )

        st.dataframe(styled_df, use_container_width=True)

        # Bar chart comparison
        st.markdown("### Average Score Comparison")

        fig = px.bar(
            df,
            x='System',
            y='Average Score',
            color='Average Score',
            color_continuous_scale='RdYlGn',
            range_color=[0, 1],
            text='Average Score'
        )

        fig.update_traces(texttemplate='%{text:.4f}', textposition='outside')
        fig.update_layout(
            xaxis_title="Retrieval System",
            yaxis_title="Average RAGAS Score",
            yaxis_range=[0, 1.1],
            showlegend=False
        )

        st.plotly_chart(fig, use_container_width=True)

    def display_detailed_metrics(self):
        """Display detailed metrics breakdown"""

        # Create tabs for each system
        tabs = st.tabs(list(self.results.keys()))

        for tab, (system_name, result) in zip(tabs, self.results.items()):
            with tab:
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric(
                        "Average Score",
                        f"{result['average_score']:.4f}",
                        help="Overall average of all RAGAS metrics"
                    )

                with col2:
                    st.metric(
                        "Initialization Time",
                        f"{result['system_info']['initialization_time']:.2f}s",
                        help="Time taken to initialize the retrieval system"
                    )

                with col3:
                    st.metric(
                        "Number of Chunks",
                        result['system_info']['num_chunks'],
                        help="Total number of document chunks created"
                    )

                st.markdown("---")

                # Individual metrics
                st.markdown("#### RAGAS Metrics")

                metrics = result['metrics']

                col1, col2 = st.columns(2)

                with col1:
                    st.metric("Faithfulness", f"{metrics['faithfulness']:.4f}")
                    st.caption("Factual consistency with context")

                    st.metric("Context Recall", f"{metrics['context_recall']:.4f}")
                    st.caption("Ground truth coverage")

                    st.metric("Context Precision", f"{metrics['context_precision']:.4f}")
                    st.caption("Signal-to-noise ratio")

                with col2:
                    st.metric("Answer Relevancy", f"{metrics['answer_relevancy']:.4f}")
                    st.caption("Relevance to question")

                    st.metric("Factual Correctness", f"{metrics['factual_correctness']:.4f}")
                    st.caption("Ground truth overlap")

                # Configuration
                st.markdown("---")
                st.markdown("#### System Configuration")
                st.json(result['system_info']['config'])

    def display_radar_chart(self):
        """Display radar chart comparing all systems"""

        fig = go.Figure()

        metrics_to_plot = [
            'faithfulness',
            'context_recall',
            'context_precision',
            'answer_relevancy',
            'factual_correctness'
        ]

        metric_labels = [
            'Faithfulness',
            'Context Recall',
            'Context Precision',
            'Answer Relevancy',
            'Factual Correctness'
        ]

        for system_name, result in self.results.items():
            metrics = result['metrics']

            values = [metrics[m] for m in metrics_to_plot]
            values.append(values[0])  # Close the radar chart

            fig.add_trace(go.Scatterpolar(
                r=values,
                theta=metric_labels + [metric_labels[0]],
                fill='toself',
                name=system_name
            ))

        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 1]
                )
            ),
            showlegend=True,
            title="Multi-Metric Radar Comparison"
        )

        st.plotly_chart(fig, use_container_width=True)

    def display_recommendations(self):
        """Display recommendations based on results"""

        # Find best system overall
        best_system = max(
            self.results.items(),
            key=lambda x: x[1]['average_score']
        )

        # Find fastest system
        fastest_system = min(
            self.results.items(),
            key=lambda x: x[1]['system_info']['initialization_time']
        )

        # Find best faithfulness
        best_faithfulness = max(
            self.results.items(),
            key=lambda x: x[1]['metrics']['faithfulness']
        )

        # Find best context recall
        best_recall = max(
            self.results.items(),
            key=lambda x: x[1]['metrics']['context_recall']
        )

        st.markdown("### Key Findings")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### Best Overall Performance")
            st.success(f"**{best_system[0]}**")
            st.write(f"Average Score: {best_system[1]['average_score']:.4f}")
            st.caption("Recommended for balanced performance across all metrics")

            st.markdown("#### Fastest Initialization")
            st.info(f"**{fastest_system[0]}**")
            st.write(f"Init Time: {fastest_system[1]['system_info']['initialization_time']:.2f}s")
            st.caption("Recommended for low-latency requirements")

        with col2:
            st.markdown("#### Best Faithfulness")
            st.success(f"**{best_faithfulness[0]}**")
            st.write(f"Faithfulness: {best_faithfulness[1]['metrics']['faithfulness']:.4f}")
            st.caption("Recommended for factual accuracy")

            st.markdown("#### Best Context Recall")
            st.success(f"**{best_recall[0]}**")
            st.write(f"Context Recall: {best_recall[1]['metrics']['context_recall']:.4f}")
            st.caption("Recommended for comprehensive retrieval")

        # General recommendations
        st.markdown("---")
        st.markdown("### General Guidelines")

        st.markdown("""
        - **Simple Recursive**: Great baseline, fast initialization, good for prototyping
        - **Simple Semantic**: Better context understanding, slower initialization
        - **Advanced Recursive**: Balanced performance with ensemble methods
        - **Advanced Semantic**: Best quality, requires more compute resources

        **Trade-offs to consider:**
        - Initialization time vs. retrieval quality
        - Chunk size vs. context granularity
        - Simple vs. ensemble retrieval methods
        """)
