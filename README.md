# RAG Retrieval System Evaluation Platform

A comprehensive full-stack application for comparing and evaluating different RAG (Retrieval-Augmented Generation) retrieval strategies using RAGAS metrics.

## Overview

This platform allows developers and researchers to:

- **Upload Documents**: PDF, TXT, or DOCX files
- **Compare Systems**: Evaluate 4 different retrieval strategies
- **View Metrics**: Comprehensive RAGAS evaluation metrics
- **Get AI Insights**: Multi-agent analysis powered by LangGraph
- **Export Results**: Download in JSON, CSV, or Markdown formats

## Architecture

### Backend (FastAPI)

- **Framework**: FastAPI with async/await
- **Validation**: Pydantic v2 models
- **Progress Updates**: HTTP polling for real-time status
- **Background Tasks**: Long-running evaluations
- **AI Analysis**: LangGraph multi-agent system
- **Export**: Multiple format support

**API Documentation**: Auto-generated Swagger docs at `/docs`

### Frontend (React + TypeScript)

- **Framework**: React 18 with TypeScript
- **UI**: Material UI (MUI) v5
- **Charts**: Recharts for data visualization
- **State**: Zustand + React Query (TanStack)
- **Updates**: HTTP polling (Streamlit-style)
- **Build**: Vite for fast development

## Features

### 🔍 4 Retrieval Systems

1. **Simple Recursive**
   - RecursiveCharacterTextSplitter + Vector Search
   - Fast initialization, good baseline

2. **Simple Semantic**
   - SemanticChunker + Vector Search
   - Context-aware splitting

3. **Advanced Recursive**
   - Recursive + BM25 + Multi-Query + Reranking
   - Balanced performance

4. **Advanced Semantic**
   - Semantic + BM25 + Multi-Query + Reranking
   - Highest quality

### 📊 RAGAS Metrics

- **Faithfulness**: Factual consistency
- **Context Recall**: Ground truth coverage
- **Context Precision**: Signal-to-noise ratio
- **Answer Relevancy**: Question relevance
- **Factual Correctness**: Ground truth overlap

### 🤖 AI-Powered Analysis

Multi-agent system with 4 specialized agents:

1. **Metrics Analyzer**: Identifies patterns in scores
2. **Performance Analyzer**: Discovers strengths/weaknesses
3. **Recommendation Agent**: Generates actionable insights
4. **Report Generator**: Synthesizes comprehensive report

### 📈 Visualization

- **Summary Tables**: Compare all systems side-by-side
- **Bar Charts**: Average score comparisons
- **Radar Charts**: Multi-metric visualization
- **Real-time Progress**: HTTP polling updates

### 💾 Export Options

- **JSON**: Complete data with all details
- **CSV**: Tabular format for analysis
- **Markdown**: Formatted reports for documentation

## Quick Start

### Prerequisites

- **Python** 3.9+ (for backend)
- **Node.js** 18+ (for frontend)
- **OpenAI API Key** (required)
- **Cohere API Key** (optional, for reranking)

### Installation

#### 1. Clone the Repository

```bash
git clone <repository-url>
cd evaluation_retrieval_system
```

#### 2. Backend Setup

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your API keys

# Start the server
python -m app.main
```

Backend will be available at:
- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/docs
- **Health**: http://localhost:8000/api/v1/health

#### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment (optional - defaults work)
cp .env.example .env

# Start development server
npm run dev
```

Frontend will be available at:
- **App**: http://localhost:3000

## Usage

### Step 1: Upload Document

- Drag and drop a PDF, TXT, or DOCX file
- Maximum size: 100 MB
- Supported formats: `.pdf`, `.txt`, `.docx`

### Step 2: Select Systems

Choose one or more retrieval systems to evaluate:

- **Simple Systems**: Quick baseline evaluations
- **Advanced Systems**: Production-ready with reranking

Configure parameters:
- **Chunk Size**: 100-2000 characters
- **Chunk Overlap**: 0-500 characters
- **Threshold Type**: For semantic chunking
- **Threshold Amount**: Sensitivity level (50-99)

### Step 3: Run Evaluation

- Set number of test questions (3-20)
- Optionally enable multi-hop questions
- Click "Start Evaluation"
- Watch real-time progress

### Step 4: View Results

- Summary metrics table with color coding
- Best system identification
- Interactive charts (Bar + Radar)
- Detailed metric breakdowns

### Step 5: AI Analysis

- Review or customize analysis query
- Click "Run AI Analysis"
- Watch 4 agents work in real-time
- Read comprehensive analysis report
- Get actionable recommendations

### Step 6: Export

Download results in your preferred format:
- **JSON** for programmatic access
- **CSV** for spreadsheet analysis
- **Markdown** for documentation

## API Endpoints

### Documents

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/documents/upload` | Upload document |
| GET | `/api/v1/documents/{id}` | Get document info |
| DELETE | `/api/v1/documents/{id}` | Delete document |

### Evaluations

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/evaluations/start` | Start evaluation |
| GET | `/api/v1/evaluations/{id}/status` | Get status (poll for updates) |
| POST | `/api/v1/evaluations/{id}/cancel` | Cancel evaluation |

### Results

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/evaluations/{id}/results` | Get results |
| POST | `/api/v1/results/export` | Export results |
| GET | `/api/v1/results/export/{id}/{format}` | Download file |

### AI Analysis

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/analysis/start` | Start analysis |
| GET | `/api/v1/analysis/{id}/status` | Get status (poll for updates) |
| GET | `/api/v1/analysis/{id}/results` | Get results |

## Project Structure

```
evaluation_retrieval_system/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── main.py            # FastAPI application
│   │   ├── config.py          # Configuration
│   │   ├── models/            # Pydantic models
│   │   ├── routes/            # API endpoints
│   │   ├── services/          # Business logic
│   │   └── utils/             # Utilities
│   ├── requirements.txt
│   ├── .env.example
│   └── README.md
├── frontend/                   # React frontend
│   ├── src/
│   │   ├── main.tsx           # Entry point
│   │   ├── App.tsx            # Root component
│   │   ├── components/        # UI components
│   │   ├── pages/             # Page components
│   │   ├── hooks/             # Custom hooks
│   │   ├── services/          # API services
│   │   ├── store/             # State management
│   │   ├── types/             # TypeScript types
│   │   └── theme/             # MUI theme
│   ├── package.json
│   ├── vite.config.ts
│   └── README.md
├── rag_evaluator/             # Original Streamlit app (deprecated)
├── .gitignore
└── README.md                  # This file
```

## Development

### Backend Development

```bash
cd backend

# Run with auto-reload
python -m app.main

# Or with uvicorn
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# View logs
# Logs appear in terminal

# API docs
# http://localhost:8000/docs
```

### Frontend Development

```bash
cd frontend

# Development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Type checking
npm run type-check

# Linting
npm run lint
```

## Testing

### Backend Tests

```bash
cd backend
pytest tests/ --cov=app
```

### Frontend Tests

```bash
cd frontend
npm run test
```

## Environment Variables

### Backend (.env)

```env
# API Configuration
OPENAI_API_KEY=your-openai-key
COHERE_API_KEY=your-cohere-key  # Optional

# Server
HOST=0.0.0.0
PORT=8000
DEBUG=True

# CORS
CORS_ORIGINS="http://localhost:3000,http://127.0.0.1:3000"

# File Upload
UPLOAD_DIR=temp_uploads
MAX_UPLOAD_SIZE=104857600  # 100 MB
```

### Frontend (.env)

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_WS_URL=ws://localhost:8000/ws
VITE_APP_NAME=RAG Evaluation Platform
```

## Deployment

### Docker Compose (Recommended)

```yaml
version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - COHERE_API_KEY=${COHERE_API_KEY}
    volumes:
      - ./backend/temp_uploads:/app/temp_uploads

  frontend:
    build: ./frontend
    ports:
      - "3000:80"
    depends_on:
      - backend
```

### Manual Deployment

1. **Backend**: Deploy to any Python hosting (Heroku, AWS, GCP)
2. **Frontend**: Deploy to static hosting (Vercel, Netlify, AWS S3)

## Troubleshooting

### Backend Issues

**"OpenAI API key not found"**
- Set `OPENAI_API_KEY` in backend `.env` file

**"Module not found"**
- Run `pip install -r requirements.txt`

**CORS errors**
- Add frontend URL to `CORS_ORIGINS` in backend config

### Frontend Issues

**"Cannot connect to API"**
- Ensure backend is running on port 8000
- Check `VITE_API_BASE_URL` in frontend `.env`

**Build errors**
- Clear cache: `rm -rf node_modules && npm install`

## Performance

### Backend

- **Async/await**: Non-blocking I/O operations
- **Background Tasks**: Long-running evaluations don't block API
- **HTTP Polling**: Streamlit-style status updates
- **Connection Pooling**: Optimized database connections

### Frontend

- **Code Splitting**: Lazy-loaded routes
- **Memoization**: Optimized re-renders
- **Vite**: Fast HMR and builds
- **React Query**: Intelligent caching

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (follow Gitflow conventions)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Commit Convention

```
<type>(<scope>): <subject>

feat(backend): add new evaluation metric
fix(frontend): resolve polling status update issue
docs(readme): update installation instructions
```

## Tech Stack Summary

### Backend
- FastAPI (async Python web framework)
- Pydantic v2 (data validation)
- LangChain (LLM orchestration)
- LangGraph (multi-agent workflows)
- OpenAI (embeddings + LLM)
- Cohere (reranking)
- Qdrant (vector database)
- RAGAS (evaluation metrics)

### Frontend
- React 18 (UI framework)
- TypeScript (type safety)
- Material UI v5 (component library)
- Recharts (data visualization)
- Zustand (state management)
- React Query (server state)
- Axios (HTTP client)
- Vite (build tool)

## License

[Your License Here]

## Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- UI components from [Material UI](https://mui.com/)
- Charts powered by [Recharts](https://recharts.org/)
- Evaluation metrics from [RAGAS](https://github.com/explodinggradients/ragas)
- LLM orchestration with [LangChain](https://langchain.com/)
- Multi-agent workflows with [LangGraph](https://langchain-ai.github.io/langgraph/)

## Support

For issues, questions, or feature requests:
- Open an issue in the repository
- Check documentation in `/backend/README.md` and `/frontend/README.md`
- Review API documentation at `/docs`

## Roadmap

- [ ] Add user authentication
- [ ] Implement result persistence (database)
- [ ] Add evaluation history
- [ ] Support more document formats
- [ ] Add more retrieval systems
- [ ] Implement batch evaluations
- [ ] Add A/B testing capabilities

---

Made with ❤️ for the RAG community
