"""
Export Manager
Handles exporting evaluation results to different formats
"""

from typing import Dict, Any
import json
import pandas as pd
from datetime import datetime


class ExportManager:
    """Export evaluation results to various formats"""

    def __init__(self, results: Dict[str, Any]):
        self.results = results
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def to_json(self) -> str:
        """Export results as JSON"""

        export_data = {
            "evaluation_timestamp": self.timestamp,
            "results": self.results
        }

        return json.dumps(export_data, indent=2)

    def to_csv(self) -> str:
        """Export results as CSV"""

        rows = []

        for system_name, result in self.results.items():
            metrics = result['metrics']
            system_info = result['system_info']

            row = {
                'System': system_name,
                'Average Score': result['average_score'],
                'Faithfulness': metrics['faithfulness'],
                'Context Recall': metrics['context_recall'],
                'Context Precision': metrics['context_precision'],
                'Answer Relevancy': metrics['answer_relevancy'],
                'Factual Correctness': metrics['factual_correctness'],
                'Initialization Time (s)': system_info['initialization_time'],
                'Number of Chunks': system_info['num_chunks'],
                'Evaluation Timestamp': self.timestamp
            }

            rows.append(row)

        df = pd.DataFrame(rows)
        return df.to_csv(index=False)

    def to_markdown(self) -> str:
        """Export results as Markdown"""

        md_content = f"""# RAG Retrieval System Evaluation Report

**Evaluation Date:** {self.timestamp}

## Summary

"""

        # Create comparison table
        md_content += "| System | Avg Score | Faithfulness | Context Recall | Context Precision | Answer Relevancy | Factual Correctness | Init Time (s) | Chunks |\n"
        md_content += "|--------|-----------|--------------|----------------|-------------------|------------------|---------------------|---------------|--------|\n"

        for system_name, result in self.results.items():
            metrics = result['metrics']
            system_info = result['system_info']

            md_content += f"| {system_name} | "
            md_content += f"{result['average_score']:.4f} | "
            md_content += f"{metrics['faithfulness']:.4f} | "
            md_content += f"{metrics['context_recall']:.4f} | "
            md_content += f"{metrics['context_precision']:.4f} | "
            md_content += f"{metrics['answer_relevancy']:.4f} | "
            md_content += f"{metrics['factual_correctness']:.4f} | "
            md_content += f"{system_info['initialization_time']:.2f} | "
            md_content += f"{system_info['num_chunks']} |\n"

        # Add detailed sections for each system
        md_content += "\n## Detailed Results\n\n"

        for system_name, result in self.results.items():
            md_content += f"### {system_name}\n\n"

            metrics = result['metrics']
            system_info = result['system_info']

            md_content += f"**Average Score:** {result['average_score']:.4f}\n\n"
            md_content += f"**System Information:**\n"
            md_content += f"- Initialization Time: {system_info['initialization_time']:.2f}s\n"
            md_content += f"- Number of Chunks: {system_info['num_chunks']}\n"
            md_content += f"- System Type: {system_info['system_name']}\n\n"

            md_content += "**RAGAS Metrics:**\n\n"
            md_content += f"| Metric | Score |\n"
            md_content += f"|--------|-------|\n"
            md_content += f"| Faithfulness | {metrics['faithfulness']:.4f} |\n"
            md_content += f"| Context Recall | {metrics['context_recall']:.4f} |\n"
            md_content += f"| Context Precision | {metrics['context_precision']:.4f} |\n"
            md_content += f"| Answer Relevancy | {metrics['answer_relevancy']:.4f} |\n"
            md_content += f"| Factual Correctness | {metrics['factual_correctness']:.4f} |\n\n"

            md_content += "**Configuration:**\n"
            md_content += "```json\n"
            md_content += json.dumps(system_info['config'], indent=2)
            md_content += "\n```\n\n"

            md_content += "---\n\n"

        # Add recommendations
        best_system = max(
            self.results.items(),
            key=lambda x: x[1]['average_score']
        )

        md_content += "## Recommendations\n\n"
        md_content += f"**Best Overall System:** {best_system[0]}\n"
        md_content += f"- Average Score: {best_system[1]['average_score']:.4f}\n\n"

        md_content += "### Metric Descriptions\n\n"
        md_content += "- **Faithfulness**: Measures factual consistency of the answer with the context\n"
        md_content += "- **Context Recall**: Measures how well retrieved context aligns with ground truth\n"
        md_content += "- **Context Precision**: Measures signal-to-noise ratio of retrieved contexts\n"
        md_content += "- **Answer Relevancy**: Measures how relevant the answer is to the question\n"
        md_content += "- **Factual Correctness**: Measures factual overlap between answer and ground truth\n\n"

        md_content += "*Score Range: 0.0 (worst) to 1.0 (best)*\n"

        return md_content
