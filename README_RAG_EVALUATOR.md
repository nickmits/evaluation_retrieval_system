# RAG Retrieval System Evaluation Platform

A web application for comparing and evaluating different RAG (Retrieval-Augmented Generation) retrieval strategies using RAGAS metrics.

## Overview

This platform allows developers to:
- Upload their own documents (PDF, TXT, DOCX)
- Select from multiple retrieval system strategies
- Run comprehensive RAGAS evaluations
- Compare performance metrics side-by-side
- Export results in multiple formats (JSON, CSV, Markdown)
- Get recommendations for the best retrieval system for their use case

## Features

### 4 Retrieval Systems Available

1. **Simple Recursive Chunking**
   - RecursiveCharacterTextSplitter + Vector Search
   - Fast initialization, good baseline performance
   - Configurable chunk size and overlap

2. **Simple Semantic Chunking**
   - SemanticChunker + Vector Search
   - Context-aware splitting for better coherence
   - Configurable threshold parameters

3. **Advanced Recursive (Ensemble)**
   - Recursive chunking + BM25 + Multi-Query + Reranking
   - Balanced performance with ensemble methods
   - Production-ready system

4. **Advanced Semantic (Ensemble)**
   - Semantic chunking + BM25 + Multi-Query + Reranking
   - Highest quality, more compute-intensive
   - Best for accuracy-critical applications

### RAGAS Metrics Evaluated

- **Faithfulness**: Factual consistency with context
- **Context Recall**: Ground truth coverage
- **Context Precision**: Signal-to-noise ratio
- **Answer Relevancy**: Relevance to question
- **Factual Correctness**: Ground truth overlap

## Installation

### Prerequisites

- Python 3.9 or higher
- OpenAI API key (required)
- Cohere API key (optional, for advanced reranking)

### Setup

1. Clone the repository and navigate to the project directory:

```bash
cd book_customer_support
```

2. Install dependencies:

```bash
pip install -r requirements_streamlit.txt
```

3. Set up environment variables:

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=your_openai_api_key_here
COHERE_API_KEY=your_cohere_api_key_here  # Optional
```

## Usage

### Running the Application

Start the Streamlit app:

```bash
streamlit run app.py
```

The application will open in your default web browser at `http://localhost:8501`.

### Step-by-Step Guide

#### 1. Configure API Keys

In the sidebar:
- Enter your OpenAI API key (required)
- Optionally enter your Cohere API key for advanced reranking

#### 2. Upload Your Document

Navigate to the "Upload & Configure" tab:
- Click "Choose a document file"
- Upload a PDF, TXT, or DOCX file
- Your document will be processed for evaluation

#### 3. Select Retrieval Systems

Choose one or more retrieval systems to evaluate:
- Check the boxes for systems you want to compare
- Configure parameters for each system (chunk size, thresholds, etc.)

Available configurations:
- **Chunk Size**: Size of text chunks (100-2000 characters)
- **Chunk Overlap**: Overlap between chunks (0-500 characters)
- **Threshold Type**: For semantic chunking (percentile, standard_deviation, interquartile)
- **Threshold Amount**: Sensitivity level (50-99)

#### 4. Set Evaluation Parameters

In the sidebar:
- **Number of Test Questions**: How many questions to generate (3-20)
- **Include Multi-hop Questions**: Enable complex reasoning questions

#### 5. Run Evaluation

Navigate to the "Run Evaluation" tab:
- Review your configuration
- Click "Start Evaluation"
- Wait for the evaluation to complete (may take several minutes)

#### 6. View Results

Navigate to the "Results & Export" tab:

**Overall Performance Comparison**
- Summary metrics table with color-coded scores
- Bar chart comparing average scores

**Detailed Metrics Breakdown**
- Individual tabs for each system
- All RAGAS metrics with explanations
- System configuration details

**Radar Chart Comparison**
- Visual comparison across all metrics
- Easy identification of strengths/weaknesses

**Recommendations**
- Best overall system
- Fastest initialization
- Best for specific metrics
- General guidelines for selection

#### 7. Export Results

Choose from multiple export formats:
- **JSON**: Complete results with all details
- **CSV**: Tabular format for spreadsheet analysis
- **Markdown**: Formatted report for documentation

## Project Structure

```
book_customer_support/
├── app.py                          # Main Streamlit application
├── rag_evaluator/                  # Evaluation platform package
│   ├── __init__.py
│   ├── document_processor.py       # Document upload and processing
│   ├── retrieval_systems.py        # Retrieval system implementations
│   ├── evaluation_engine.py        # RAGAS evaluation pipeline
│   ├── visualizations.py           # Results visualization
│   └── export_manager.py           # Export functionality
├── requirements_streamlit.txt      # Python dependencies
├── README_RAG_EVALUATOR.md        # This file
└── temp_uploads/                   # Temporary storage for uploads
```

## Use Cases

### 1. Selecting a Retrieval System

You're building a RAG application and need to decide which retrieval strategy works best for your documents:

1. Upload a representative document
2. Evaluate all 4 systems
3. Compare metrics and initialization times
4. Choose based on your priorities (speed vs. accuracy)

### 2. Optimizing Parameters

You want to find the optimal chunk size for your use case:

1. Select one retrieval system
2. Run evaluations with different chunk sizes
3. Compare results to find the sweet spot

### 3. Benchmarking Performance

You want to establish baseline performance metrics:

1. Use your production documents
2. Evaluate with your current retrieval strategy
3. Save results for future comparison

### 4. Research and Development

You're researching different chunking strategies:

1. Compare semantic vs. recursive chunking
2. Analyze trade-offs between methods
3. Export detailed results for publication

## Understanding the Metrics

### Faithfulness (0.0 - 1.0)
- Measures if the answer is factually consistent with the retrieved context
- **High score**: Answer only contains information from context
- **Low score**: Answer includes hallucinated information

### Context Recall (0.0 - 1.0)
- Measures how much of the ground truth answer is covered by retrieved contexts
- **High score**: Retrieved contexts contain all necessary information
- **Low score**: Important information is missing from retrieved contexts

### Context Precision (0.0 - 1.0)
- Measures the signal-to-noise ratio of retrieved contexts
- **High score**: Retrieved contexts are all relevant
- **Low score**: Many irrelevant contexts retrieved

### Answer Relevancy (0.0 - 1.0)
- Measures how relevant the answer is to the question
- **High score**: Answer directly addresses the question
- **Low score**: Answer is off-topic or incomplete

### Factual Correctness (0.0 - 1.0)
- Measures factual overlap between the answer and ground truth
- **High score**: Answer matches ground truth facts
- **Low score**: Answer contains incorrect or missing facts

## Performance Considerations

### Initialization Time
- **Simple systems**: ~5-30 seconds
- **Semantic chunking**: ~60-120 seconds (embedding-intensive)
- **Advanced systems**: ~30-90 seconds (ensemble complexity)

### Evaluation Time
- Depends on number of test questions
- ~30-60 seconds per question
- Example: 5 questions × 2 systems = ~5-10 minutes

### Resource Usage
- **Memory**: ~2-4GB for most documents
- **CPU**: Multi-threading for embeddings
- **API Calls**: OpenAI and optionally Cohere

## Troubleshooting

### "OpenAI API key not found"
- Ensure your API key is set in the sidebar or `.env` file
- Check that the key is valid and has available credits

### "Document upload failed"
- Check file format (PDF, TXT, DOCX only)
- Ensure file is not corrupted
- Try a smaller file (< 50MB recommended)

### "Evaluation taking too long"
- Reduce number of test questions
- Use simple systems first (faster)
- Check your internet connection (API calls)

### "Out of memory"
- Use smaller documents
- Reduce chunk overlap
- Close other applications

## Best Practices

1. **Start with simple systems** to establish baselines
2. **Use 5-10 test questions** for initial evaluation
3. **Compare 2-3 systems** at a time to avoid long wait times
4. **Save your results** using export functionality
5. **Test with representative documents** from your actual use case
6. **Consider trade-offs** between speed and accuracy
7. **Use Cohere reranking** for production systems (better quality)

## Advanced Configuration

### Custom Chunking Parameters

For **Recursive Chunking**:
- Smaller chunks (500-800): Better precision, more chunks
- Larger chunks (1200-1500): Better context, fewer chunks
- Higher overlap (300-400): Better continuity, more redundancy

For **Semantic Chunking**:
- Lower threshold (75-85): More, smaller chunks
- Higher threshold (90-99): Fewer, larger chunks
- Percentile mode: Most consistent results

### Evaluation Parameters

For **Simple Questions**:
- Use single-hop query synthesizer
- Faster evaluation
- Good for factual Q&A

For **Complex Questions**:
- Enable multi-hop questions
- Tests reasoning capabilities
- Better for complex use cases

## Limitations

- **Document size**: Large documents (>100 pages) may require more time
- **API costs**: Evaluations use OpenAI API (costs apply)
- **Language**: Currently optimized for English documents
- **File types**: PDF, TXT, DOCX only

## Contributing

This project was originally a bookstore customer support system and has been generalized into a RAG evaluation platform. Contributions are welcome!

## License

[Your License Here]

## Support

For issues, questions, or feature requests, please open an issue in the repository.

## Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- Evaluation powered by [RAGAS](https://github.com/explodinggradients/ragas)
- LLM orchestration with [LangChain](https://langchain.com/)
- Vector storage with [Qdrant](https://qdrant.tech/)
