# RAG Evaluation Frontend

Modern React TypeScript frontend for the RAG retrieval system evaluation platform.

## Tech Stack

- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite
- **UI Library**: Material UI (MUI) v5
- **Charts**: Recharts
- **State Management**: Zustand + React Query (TanStack Query)
- **HTTP Client**: Axios
- **Notifications**: Notistack
- **Form Validation**: React Hook Form + Zod
- **Routing**: React Router v6

## Features

- ✅ **Document Upload**: Drag-and-drop file upload with validation
- ✅ **System Selection**: Configure multiple retrieval systems
- ✅ **Real-time Evaluation**: HTTP polling progress tracking
- ✅ **Results Visualization**: Interactive charts with Recharts
- ✅ **AI Analysis**: Multi-agent analysis with LangGraph
- ✅ **Export**: Download results as JSON, CSV, or Markdown
- ✅ **Responsive Design**: Works on desktop, tablet, and mobile
- ✅ **Type Safety**: Full TypeScript coverage

## Project Structure

```
frontend/
├── public/                 # Static assets
├── src/
│   ├── main.tsx           # Application entry point
│   ├── App.tsx            # Root component with routing
│   ├── vite-env.d.ts      # Vite type definitions
│   ├── components/        # Reusable components
│   │   ├── DocumentUploader/
│   │   │   ├── DocumentUploader.tsx
│   │   │   └── index.ts
│   │   ├── SystemSelector/
│   │   │   ├── SystemSelector.tsx
│   │   │   └── index.ts
│   │   ├── EvaluationRunner/
│   │   │   ├── EvaluationRunner.tsx
│   │   │   └── index.ts
│   │   ├── ResultsVisualization/
│   │   │   ├── ResultsVisualization.tsx
│   │   │   └── index.ts
│   │   └── AIAnalysis/
│   │       ├── AIAnalysisPanel.tsx
│   │       └── index.ts
│   ├── pages/             # Page components
│   │   └── HomePage.tsx
│   ├── hooks/             # Custom React hooks
│   ├── services/          # API services
│   │   ├── api.ts
│   │   ├── documentService.ts
│   │   ├── evaluationService.ts
│   │   ├── resultsService.ts
│   │   └── analysisService.ts
│   ├── store/             # Zustand state management
│   │   └── useAppStore.ts
│   ├── types/             # TypeScript type definitions
│   │   ├── api.types.ts
│   │   ├── document.types.ts
│   │   ├── evaluation.types.ts
│   │   ├── results.types.ts
│   │   └── analysis.types.ts
│   ├── theme/             # MUI theme configuration
│   │   └── theme.ts
│   └── utils/             # Utility functions
├── .env.example           # Environment variables template
├── index.html
├── tsconfig.json          # TypeScript configuration
├── vite.config.ts         # Vite configuration
├── package.json
└── README.md
```

## Installation

### Prerequisites

- Node.js 18+ or npm/pnpm
- Backend API running on `http://localhost:8000`

### Setup

1. **Install dependencies**:

```bash
cd frontend
npm install
```

2. **Configure environment variables**:

```bash
# Copy the example env file
cp .env.example .env

# Edit .env (optional - defaults work with standard backend setup)
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_APP_NAME=RAG Evaluation Platform
```

3. **Start development server**:

```bash
npm run dev
```

The app will be available at **http://localhost:3000**

## Available Scripts

```bash
# Development server with hot reload
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

## Usage Guide

### 1. Upload a Document

- Drag and drop a PDF, TXT, or DOCX file
- Or click to browse and select a file
- Maximum file size: 100 MB
- Supported formats: PDF, TXT, DOCX

### 2. Select Retrieval Systems

Choose from 4 retrieval system types:

**Simple Systems:**
- **Simple Recursive**: RecursiveCharacterTextSplitter + Vector Search
- **Simple Semantic**: SemanticChunker + Vector Search

**Advanced Systems:**
- **Advanced Recursive**: Recursive + BM25 + Multi-Query + Reranking
- **Advanced Semantic**: Semantic + BM25 + Multi-Query + Reranking

**Configuration Options:**

For Recursive systems:
- **Chunk Size** (100-2000): Size of text chunks
- **Chunk Overlap** (0-500): Overlap between chunks

For Semantic systems:
- **Threshold Type**: percentile, standard_deviation, or interquartile
- **Threshold Amount** (50-99): Sensitivity level

### 3. Run Evaluation

- Set the number of test questions (3-20)
- Optionally enable multi-hop questions
- Provide OpenAI API key if not set on backend
- Click "Start Evaluation"
- Watch real-time progress via HTTP polling

### 4. View Results

**Summary Table:**
- Compare all systems side-by-side
- View all RAGAS metrics
- Identify the best-performing system

**Charts:**
- **Bar Chart**: Average score comparison
- **Radar Chart**: Multi-metric visualization

**Export Options:**
- Download as JSON
- Download as CSV
- Download as Markdown

### 5. AI Analysis

- Review the default analysis query or write your own
- Click "Run AI Analysis"
- Watch the 4 LangGraph agents work:
  1. Metrics Analyzer
  2. Performance Analyzer
  3. Recommendation Agent
  4. Report Generator
- Read the comprehensive analysis report
- Expand accordions to see detailed agent outputs

## Components

### DocumentUploader

Drag-and-drop file uploader with:
- File type validation
- File size validation
- Progress indicator
- Success/error feedback

### SystemSelector

Multi-system selector with:
- Checkbox selection
- Expandable configuration forms
- Dynamic form fields based on system type
- Visual feedback for selected systems

### EvaluationRunner

Evaluation orchestrator with:
- Configuration panel
- HTTP polling for real-time updates
- Progress bar and stepper
- System-by-system progress tracking
- Cancellation support

### ResultsVisualization

Results display with:
- Summary metrics table
- Recharts integration (Bar chart, Radar chart)
- Best system identification
- Export functionality

### AIAnalysisPanel

AI analysis interface with:
- Custom query input
- Real-time agent progress tracking
- Comprehensive report display
- Expandable detailed analyses
- Agent communication log

## State Management

### Zustand Store

Global state persisted to localStorage:

```typescript
{
  currentDocument: DocumentInfo | null
  currentEvaluation: EvaluationInfo | null
  currentResults: EvaluationResults | null
  currentAnalysis: AnalysisResult | null
}
```

### React Query

Server state caching with automatic:
- Background refetching
- Cache invalidation
- Error retry logic
- Loading states

## API Integration

All API calls go through typed service layers:

```typescript
// Example: Start evaluation
import { evaluationService } from '@/services/evaluationService'

const response = await evaluationService.startEvaluation({
  document_id: documentId,
  systems: selectedSystems,
  num_test_questions: 5,
  use_multihop: false,
})
```

## HTTP Polling Integration

Real-time updates via polling:

```typescript
import { useEffect } from 'react'

useEffect(() => {
  if (!evaluationId || !isRunning) return

  const pollInterval = setInterval(async () => {
    try {
      const status = await evaluationService.getEvaluationStatus(evaluationId)

      if (status.status === 'completed' || status.status === 'failed') {
        clearInterval(pollInterval)
      }
    } catch (error) {
      console.error('Error polling status:', error)
    }
  }, 2000) // Poll every 2 seconds

  return () => clearInterval(pollInterval)
}, [evaluationId, isRunning])
```

## Styling

### Material UI Theme

Custom theme configuration in `src/theme/theme.ts`:

```typescript
const theme = createTheme({
  palette: {
    primary: { main: '#1976d2' },
    secondary: { main: '#9c27b0' },
    // ...
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    // ...
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          borderRadius: 8,
        },
      },
    },
  },
})
```

### Styling Approaches

1. **MUI sx prop** (preferred):
```typescript
<Box sx={{ p: 2, bgcolor: 'background.paper' }}>
```

2. **MUI styled components**:
```typescript
const StyledPaper = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(2),
}))
```

3. **MUI theme hook**:
```typescript
const theme = useTheme()
```

## Type Safety

Full TypeScript coverage with:

- Strict mode enabled
- No `any` types
- Explicit return types
- Comprehensive interface definitions
- Type inference where appropriate

Example type definition:

```typescript
interface EvaluationRequest {
  document_id: string
  systems: SystemSelection[]
  num_test_questions: number
  use_multihop: boolean
  openai_api_key?: string
  cohere_api_key?: string
}
```

## Performance Optimizations

- **Code splitting**: Lazy-loaded routes
- **Memoization**: React.memo for expensive components
- **Debouncing**: Input debouncing with custom hooks
- **Virtual scrolling**: For large lists
- **Image optimization**: Lazy loading images
- **Bundle optimization**: Tree shaking with Vite

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Troubleshooting

### CORS Errors

Ensure backend CORS configuration includes frontend URL:

```python
# backend/app/main.py
CORS_ORIGINS = ["http://localhost:3000"]
```

### Build Errors

Clear cache and reinstall:

```bash
rm -rf node_modules package-lock.json
npm install
```

### Type Errors

Run type checking to identify issues:

```bash
npm run type-check
```

## Development Tips

1. **Hot Module Replacement**: Vite provides instant HMR
2. **React DevTools**: Install browser extension for debugging
3. **Redux DevTools**: Works with Zustand for state inspection
4. **React Query DevTools**: Add to see query cache

```typescript
import { ReactQueryDevtools } from '@tanstack/react-query-devtools'

// In your App component
<ReactQueryDevtools initialIsOpen={false} />
```

## Production Build

```bash
# Build for production
npm run build

# Build output in dist/
# Serve with any static file server

# Preview production build locally
npm run preview
```

## Deployment

### Static Hosting (Vercel, Netlify, etc.)

1. Build the app: `npm run build`
2. Deploy the `dist/` directory
3. Configure environment variables on hosting platform
4. Set up custom domain (optional)

### Docker

```dockerfile
FROM node:18-alpine as build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

## Contributing

1. Follow TypeScript strict mode guidelines
2. Use MUI components with sx prop for styling
3. Add type definitions for all new features
4. Write tests for critical components
5. Follow existing code structure

## License

[Your License Here]

## Support

For issues, questions, or feature requests, please open an issue in the repository.
