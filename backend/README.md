# RAG Evaluation Backend API

FastAPI-based REST API for RAG retrieval system evaluation with HTTP polling for real-time updates.

## Features

- **Document Management**: Upload PDF, TXT, and DOCX files
- **Evaluation Engine**: Run background evaluations with 4 retrieval systems
- **AI Analysis**: LangGraph-powered multi-agent analysis
- **Real-time Updates**: HTTP polling for progress tracking
- **Export Functionality**: Export results as JSON, CSV, or Markdown
- **Auto-generated API Docs**: OpenAPI/Swagger documentation

## Tech Stack

- **Framework**: FastAPI 0.104+
- **Python**: 3.9+
- **Validation**: Pydantic v2
- **LLMs**: OpenAI, Cohere (optional)
- **Vector Store**: Qdrant
- **Evaluation**: RAGAS
- **AI Analysis**: LangGraph

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application
│   ├── config.py               # Configuration management
│   ├── models/                 # Pydantic models
│   │   ├── document.py
│   │   ├── evaluation.py
│   │   ├── results.py
│   │   └── analysis.py
│   ├── routes/                 # API endpoints
│   │   ├── documents.py        # Document upload/retrieval
│   │   ├── evaluations.py      # Evaluation management
│   │   ├── analysis.py         # AI analysis
│   │   └── results.py          # Results & export
│   ├── services/               # Business logic
│   │   ├── document_processor.py
│   │   ├── retrieval_systems.py
│   │   ├── evaluation_engine.py
│   │   ├── export_manager.py
│   │   └── langgraph_analyzer.py
│   └── utils/
│       └── background_tasks.py # Task management
├── tests/
├── requirements.txt
├── .env.example
└── README.md
```

## Installation

### Prerequisites

- Python 3.9 or higher
- OpenAI API key (required)
- Cohere API key (optional, for reranking)

### Setup

1. **Install dependencies**:

```bash
cd backend
pip install -r requirements.txt
```

2. **Configure environment variables**:

```bash
# Copy the example env file
cp .env.example .env

# Edit .env and add your API keys
OPENAI_API_KEY="your-openai-key-here"
COHERE_API_KEY="your-cohere-key-here"  # Optional
```

3. **Run the server**:

```bash
# Development mode (with auto-reload)
python -m app.main

# Or using uvicorn directly
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

4. **Access the API**:

- **API**: http://localhost:8000
- **Swagger Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/api/v1/health

## API Endpoints

### Documents

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/documents/upload` | Upload a document |
| GET | `/api/v1/documents/{id}` | Get document info |
| DELETE | `/api/v1/documents/{id}` | Delete a document |

### Evaluations

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/evaluations/start` | Start evaluation (background) |
| GET | `/api/v1/evaluations/{id}/status` | Get evaluation status (poll) |
| POST | `/api/v1/evaluations/{id}/cancel` | Cancel evaluation |

### Results

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/evaluations/{id}/results` | Get evaluation results |
| POST | `/api/v1/results/export` | Export results (JSON/CSV/MD) |
| GET | `/api/v1/results/export/{id}/{format}` | Download results file |

### AI Analysis

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/analysis/start` | Start AI analysis (background) |
| GET | `/api/v1/analysis/{id}/status` | Get analysis status (poll) |
| GET | `/api/v1/analysis/{id}/results` | Get analysis results |

## Usage Examples

### 1. Upload a Document

```bash
curl -X POST "http://localhost:8000/api/v1/documents/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@your_document.pdf"
```

Response:
```json
{
  "success": true,
  "document_id": "123e4567-e89b-12d3-a456-426614174000",
  "filename": "your_document.pdf",
  "file_size": 1024000,
  "file_type": "pdf",
  "message": "Document uploaded successfully"
}
```

### 2. Start an Evaluation

```bash
curl -X POST "http://localhost:8000/api/v1/evaluations/start" \
  -H "Content-Type: application/json" \
  -d '{
    "document_id": "123e4567-e89b-12d3-a456-426614174000",
    "systems": [
      {
        "name": "Simple Recursive",
        "type": "simple_recursive",
        "config": {
          "chunk_size": 1000,
          "chunk_overlap": 200
        }
      },
      {
        "name": "Advanced Semantic",
        "type": "advanced_semantic",
        "config": {
          "threshold_type": "percentile",
          "threshold_amount": 95
        }
      }
    ],
    "num_test_questions": 5,
    "use_multihop": false
  }'
```

Response:
```json
{
  "success": true,
  "evaluation_id": "456e7890-e89b-12d3-a456-426614174001",
  "message": "Evaluation started successfully"
}
```

### 3. Check Evaluation Status (Poll)

```bash
# Poll this endpoint every 2 seconds to get real-time updates
curl "http://localhost:8000/api/v1/evaluations/456e7890-e89b-12d3-a456-426614174001/status"
```

### 4. Get Results

```bash
curl "http://localhost:8000/api/v1/evaluations/456e7890-e89b-12d3-a456-426614174001/results"
```

### 5. Start AI Analysis

```bash
curl -X POST "http://localhost:8000/api/v1/analysis/start" \
  -H "Content-Type: application/json" \
  -d '{
    "evaluation_id": "456e7890-e89b-12d3-a456-426614174001",
    "analysis_query": "Which retrieval system performs best and why?"
  }'
```

### 6. Export Results

```bash
# Download as JSON
curl "http://localhost:8000/api/v1/results/export/456e7890-e89b-12d3-a456-426614174001/json" \
  -o results.json

# Download as CSV
curl "http://localhost:8000/api/v1/results/export/456e7890-e89b-12d3-a456-426614174001/csv" \
  -o results.csv

# Download as Markdown
curl "http://localhost:8000/api/v1/results/export/456e7890-e89b-12d3-a456-426614174001/markdown" \
  -o results.md
```

## HTTP Polling for Progress Updates

Poll status endpoints for real-time updates:

```javascript
// JavaScript example
const evaluationId = '456e7890-e89b-12d3-a456-426614174001';

// Poll every 2 seconds
const pollInterval = setInterval(async () => {
  const response = await fetch(`http://localhost:8000/api/v1/evaluations/${evaluationId}/status`);
  const data = await response.json();

  console.log('Progress:', data);

  if (data.data.status === 'completed' || data.data.status === 'failed') {
    clearInterval(pollInterval);
    console.log('Evaluation finished:', data.data.status);
  }
}, 2000);
```

## Configuration

All configuration is managed through environment variables. See `.env.example` for available options:

- `API_TITLE`: API title
- `API_VERSION`: API version
- `HOST`: Server host (default: 0.0.0.0)
- `PORT`: Server port (default: 8000)
- `OPENAI_API_KEY`: OpenAI API key (required)
- `COHERE_API_KEY`: Cohere API key (optional)
- `UPLOAD_DIR`: Upload directory (default: temp_uploads)
- `MAX_UPLOAD_SIZE`: Max file size in bytes (default: 100MB)
- `CORS_ORIGINS`: Allowed origins (comma-separated)

## Development

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest tests/

# Run with coverage
pytest --cov=app tests/
```

### Code Quality

```bash
# Format code
black app/

# Sort imports
isort app/

# Lint
ruff check app/

# Type checking
mypy app/
```

## Architecture

### Background Tasks

Long-running operations (evaluations, AI analysis) run as FastAPI background tasks with:

- **Task Management**: Track status, progress, and results
- **HTTP Polling**: Status endpoints for progress tracking
- **Cancellation Support**: Cancel running tasks
- **Error Handling**: Graceful error recovery

### Data Flow

1. **Client** uploads document → **API** saves file → Returns document ID
2. **Client** starts evaluation → **API** creates background task
3. **Background Task** runs evaluation → Updates status in memory
4. **Client** polls status endpoint → Receives progress updates
5. **Client** requests results → **API** returns formatted data

## Troubleshooting

### "OpenAI API key not found"

Set the `OPENAI_API_KEY` environment variable in `.env`:

```bash
OPENAI_API_KEY="sk-..."
```

### "File too large"

Increase `MAX_UPLOAD_SIZE` in `.env`:

```bash
MAX_UPLOAD_SIZE=209715200  # 200 MB
```

### CORS Errors

Add your frontend URL to `CORS_ORIGINS`:

```bash
CORS_ORIGINS="http://localhost:3000,http://localhost:5173"
```

## License

[Your License Here]

## Support

For issues, questions, or feature requests, please open an issue in the repository.
