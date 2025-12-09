/**
 * Home page - Streamlit-style layout with sidebar and tabs
 */

import React, { useState, useEffect, useRef } from 'react'
import {
  Box,
  Drawer,
  Typography,
  TextField,
  Slider,
  Checkbox,
  FormControlLabel,
  Divider,
  Tabs,
  Tab,
  Paper,
  Alert,
  Grid,
  InputAdornment,
  IconButton,
  Tooltip,
  Menu,
  MenuItem,
  ListItemIcon,
  ListItemText,
} from '@mui/material'
import {
  Visibility,
  VisibilityOff,
  MoreVert as MoreVertIcon,
  LightMode as LightModeIcon,
  DarkMode as DarkModeIcon,
  Settings as SettingsIcon,
} from '@mui/icons-material'
import DocumentUploader from '@/components/DocumentUploader'
import SystemSelector from '@/components/SystemSelector'
import EvaluationRunner from '@/components/EvaluationRunner'
import ResultsVisualization from '@/components/ResultsVisualization'
import AIAnalysisPanel from '@/components/AIAnalysis'
import ResultsImporter from '@/components/ResultsImporter'
import { useAppStore } from '@/store/useAppStore'
import { useThemeMode } from '@/theme/ThemeContext'
import type { SystemSelection } from '@/types/evaluation.types'

const DEFAULT_DRAWER_WIDTH = 320
const MIN_DRAWER_WIDTH = 200
const MAX_DRAWER_WIDTH = 600

interface TabPanelProps {
  children?: React.ReactNode
  index: number
  value: number
}

const TabPanel: React.FC<TabPanelProps> = ({ children, value, index }) => {
  return (
    <div role="tabpanel" hidden={value !== index}>
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  )
}

const HomePage: React.FC = () => {
  const [selectedSystems, setSelectedSystems] = useState<SystemSelection[]>([])
  const [activeTab, setActiveTab] = useState(0)
  const [completedEvaluationId, setCompletedEvaluationId] = useState<string | null>(null)
  const [numQuestions, setNumQuestions] = useState(5)
  const [useMultihop, setUseMultihop] = useState(false)
  const [openaiKey, setOpenaiKey] = useState('')
  const [cohereKey, setCohereKey] = useState('')
  const [showOpenaiKey, setShowOpenaiKey] = useState(false)
  const [showCohereKey, setShowCohereKey] = useState(false)
  const [isEvaluationRunning, setIsEvaluationRunning] = useState(false)

  // Resizable sidebar state
  const [drawerWidth, setDrawerWidth] = useState(() => {
    const saved = localStorage.getItem('drawer-width')
    return saved ? parseInt(saved, 10) : DEFAULT_DRAWER_WIDTH
  })
  const [isResizing, setIsResizing] = useState(false)
  const drawerRef = useRef<HTMLDivElement>(null)

  // Settings menu state
  const [menuAnchor, setMenuAnchor] = useState<null | HTMLElement>(null)

  const { currentDocument } = useAppStore()
  const { mode, toggleTheme, setThemeMode } = useThemeMode()

  // Check for ongoing evaluation
  useEffect(() => {
    const checkEvaluationStatus = () => {
      const ongoingEvaluation = localStorage.getItem('current_evaluation_id')
      const wasRunning = isEvaluationRunning
      const isRunning = !!ongoingEvaluation

      setIsEvaluationRunning(isRunning)

      // If evaluation just started and we're not on the Run Evaluation tab, switch to it
      if (isRunning && !wasRunning && activeTab !== 1) {
        setActiveTab(1)
      }
    }

    // Check on mount
    checkEvaluationStatus()

    // Check periodically (in case user has multiple tabs open)
    const interval = setInterval(checkEvaluationStatus, 1000)
    return () => clearInterval(interval)
  }, [isEvaluationRunning, activeTab])

  const handleEvaluationComplete = (evaluationId: string) => {
    setCompletedEvaluationId(evaluationId)
    setIsEvaluationRunning(false)
    setActiveTab(2) // Switch to Results tab
  }

  const handleImportSuccess = (evaluationId: string) => {
    setCompletedEvaluationId(evaluationId)
    setActiveTab(2) // Switch to Results tab automatically
  }

  // Resizable sidebar handlers
  const handleMouseDown = () => {
    setIsResizing(true)
  }

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (!isResizing) return

      const newWidth = e.clientX
      if (newWidth >= MIN_DRAWER_WIDTH && newWidth <= MAX_DRAWER_WIDTH) {
        setDrawerWidth(newWidth)
        localStorage.setItem('drawer-width', newWidth.toString())
      }
    }

    const handleMouseUp = () => {
      setIsResizing(false)
    }

    if (isResizing) {
      document.addEventListener('mousemove', handleMouseMove)
      document.addEventListener('mouseup', handleMouseUp)
    }

    return () => {
      document.removeEventListener('mousemove', handleMouseMove)
      document.removeEventListener('mouseup', handleMouseUp)
    }
  }, [isResizing])

  // Settings menu handlers
  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setMenuAnchor(event.currentTarget)
  }

  const handleMenuClose = () => {
    setMenuAnchor(null)
  }

  const handleThemeChange = (newMode: 'light' | 'dark') => {
    setThemeMode(newMode)
    handleMenuClose()
  }

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh', width: '100%' }}>
      {/* Sidebar - Streamlit style with resizable handle */}
      <Drawer
        ref={drawerRef}
        variant="permanent"
        sx={{
          width: drawerWidth,
          flexShrink: 0,
          '& .MuiDrawer-paper': {
            width: drawerWidth,
            boxSizing: 'border-box',
            bgcolor: (theme) => theme.palette.mode === 'light' ? '#f0f2f6' : theme.palette.background.paper,
            borderRight: '1px solid #e0e0e0',
            position: 'relative',
            overflow: 'hidden',
          },
        }}
      >
        <Box sx={{ p: 3 }}>
          {/* Configuration Header */}
          <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
            ⚙️ Configuration
          </Typography>

          <Divider sx={{ my: 2 }} />

          {/* API Keys Section */}
          <Typography variant="subtitle2" gutterBottom sx={{ fontWeight: 600, mt: 2 }}>
            🔑 API Keys
          </Typography>

          <TextField
            label="OpenAI API Key"
            type={showOpenaiKey ? 'text' : 'password'}
            fullWidth
            size="small"
            value={openaiKey}
            onChange={(e) => setOpenaiKey(e.target.value)}
            helperText="Required for embeddings and LLM"
            sx={{ mt: 1, mb: 2 }}
            InputProps={{
              endAdornment: (
                <InputAdornment position="end">
                  <IconButton
                    size="small"
                    onClick={() => setShowOpenaiKey(!showOpenaiKey)}
                    edge="end"
                  >
                    {showOpenaiKey ? <VisibilityOff fontSize="small" /> : <Visibility fontSize="small" />}
                  </IconButton>
                </InputAdornment>
              ),
            }}
          />

          <TextField
            label="Cohere API Key (Optional)"
            type={showCohereKey ? 'text' : 'password'}
            fullWidth
            size="small"
            value={cohereKey}
            onChange={(e) => setCohereKey(e.target.value)}
            helperText="For reranking in advanced systems"
            sx={{ mb: 2 }}
            InputProps={{
              endAdornment: (
                <InputAdornment position="end">
                  <IconButton
                    size="small"
                    onClick={() => setShowCohereKey(!showCohereKey)}
                    edge="end"
                  >
                    {showCohereKey ? <VisibilityOff fontSize="small" /> : <Visibility fontSize="small" />}
                  </IconButton>
                </InputAdornment>
              ),
            }}
          />

          <Divider sx={{ my: 2 }} />

          {/* Evaluation Settings */}
          <Typography variant="subtitle2" gutterBottom sx={{ fontWeight: 600, mt: 2 }}>
            📊 Evaluation Settings
          </Typography>

          <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mt: 2 }}>
            <Typography variant="caption">
              Number of Test Questions
            </Typography>
            <Tooltip title="Number of questions to generate for evaluation" arrow>
              <IconButton size="small" sx={{ padding: 0.25 }}>
                <span style={{ fontSize: '12px' }}>ℹ️</span>
              </IconButton>
            </Tooltip>
          </Box>
          <Slider
            value={numQuestions}
            onChange={(_, value) => setNumQuestions(value as number)}
            min={3}
            max={20}
            marks={[
              { value: 3, label: '3' },
              { value: 10, label: '10' },
              { value: 20, label: '20' },
            ]}
            valueLabelDisplay="auto"
            sx={{ mt: 1, mb: 2 }}
          />

          <FormControlLabel
            control={
              <Checkbox
                checked={useMultihop}
                onChange={(e) => setUseMultihop(e.target.checked)}
                size="small"
              />
            }
            label={
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                <Typography variant="body2">
                  Include Multi-hop Questions
                </Typography>
                <Tooltip title="Generate more complex multi-hop reasoning questions" arrow>
                  <IconButton size="small" sx={{ padding: 0.25 }}>
                    <span style={{ fontSize: '12px' }}>ℹ️</span>
                  </IconButton>
                </Tooltip>
              </Box>
            }
            sx={{ mb: 2 }}
          />

          <Divider sx={{ my: 2 }} />

          {/* About RAGAS Metrics */}
          <Typography variant="subtitle2" gutterBottom sx={{ fontWeight: 600, mt: 2 }}>
            📈 About RAGAS Metrics
          </Typography>
          <Typography variant="caption" component="div" sx={{ mt: 1 }}>
            • <strong>Faithfulness</strong>: Factual consistency
          </Typography>
          <Typography variant="caption" component="div">
            • <strong>Context Recall</strong>: Ground truth coverage
          </Typography>
          <Typography variant="caption" component="div">
            • <strong>Context Precision</strong>: Signal-to-noise ratio
          </Typography>
          <Typography variant="caption" component="div">
            • <strong>Answer Relevancy</strong>: Question relevance
          </Typography>
          <Typography variant="caption" component="div">
            • <strong>Factual Correctness</strong>: Ground truth overlap
          </Typography>

          <Divider sx={{ my: 2 }} />

          <Alert severity="info" sx={{ mt: 2 }}>
            <Typography variant="caption">
              ℹ️ <strong>Note</strong>: Multi-hop questions are currently disabled due to RAGAS compatibility. Single-hop questions provide reliable results.
            </Typography>
          </Alert>
        </Box>

        {/* Resize Handle */}
        <Box
          onMouseDown={handleMouseDown}
          sx={{
            position: 'absolute',
            right: 0,
            top: 0,
            bottom: 0,
            width: '8px',
            cursor: 'col-resize',
            backgroundColor: 'transparent',
            '&:hover': {
              backgroundColor: (theme) => theme.palette.primary.main + '40',
            },
            ...(isResizing && {
              backgroundColor: (theme) => theme.palette.primary.main + '80',
            }),
            zIndex: 1,
          }}
        />
      </Drawer>

      {/* Main Content Area */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          bgcolor: 'background.default',
          minHeight: '100vh',
          overflow: 'auto',
        }}
      >
        {/* Header */}
        <Paper
          elevation={0}
          sx={{
            p: 3,
            borderBottom: '2px solid',
            borderColor: 'divider',
            bgcolor: 'background.paper',
            position: 'relative',
          }}
        >
          {/* Settings Menu Button */}
          <IconButton
            onClick={handleMenuOpen}
            sx={{
              position: 'absolute',
              top: 16,
              right: 16,
            }}
          >
            <MoreVertIcon />
          </IconButton>

          <Typography
            variant="h4"
            component="h1"
            sx={{
              fontSize: '2.5rem',
              fontWeight: 'bold',
              color: '#1f77b4',
              textAlign: 'center',
            }}
          >
            🔍 RAG Retrieval System Evaluation Platform
          </Typography>
          <Divider sx={{ my: 2 }} />
          <Typography variant="body1" sx={{ textAlign: 'center' }}>
            <strong>Compare different RAG retrieval strategies</strong> and find the best system for your use case.
            Upload your documents, select retrieval systems, and get detailed RAGAS metrics.
          </Typography>
        </Paper>

        {/* Settings Menu */}
        <Menu
          anchorEl={menuAnchor}
          open={Boolean(menuAnchor)}
          onClose={handleMenuClose}
          anchorOrigin={{
            vertical: 'bottom',
            horizontal: 'right',
          }}
          transformOrigin={{
            vertical: 'top',
            horizontal: 'right',
          }}
        >
          <MenuItem disabled>
            <ListItemIcon>
              <SettingsIcon fontSize="small" />
            </ListItemIcon>
            <ListItemText>Settings</ListItemText>
          </MenuItem>
          <Divider />
          <MenuItem onClick={() => handleThemeChange('light')} selected={mode === 'light'}>
            <ListItemIcon>
              <LightModeIcon fontSize="small" />
            </ListItemIcon>
            <ListItemText>Light Mode</ListItemText>
          </MenuItem>
          <MenuItem onClick={() => handleThemeChange('dark')} selected={mode === 'dark'}>
            <ListItemIcon>
              <DarkModeIcon fontSize="small" />
            </ListItemIcon>
            <ListItemText>Dark Mode</ListItemText>
          </MenuItem>
        </Menu>

        {/* Tabs */}
        <Box sx={{ borderBottom: 1, borderColor: 'divider', bgcolor: 'background.paper' }}>
          <Tabs
            value={activeTab}
            onChange={(_, newValue) => {
              // Only allow switching to Run Evaluation tab during evaluation
              if (isEvaluationRunning && newValue !== 1) {
                return
              }
              setActiveTab(newValue)
            }}
            variant="fullWidth"
          >
            <Tab label="📄 Upload & Configure" disabled={isEvaluationRunning} />
            <Tab label="✏️ Run Evaluation" />
            <Tab label="📊 Results & Export" disabled={isEvaluationRunning} />
            <Tab label="🤖 AI Analysis" disabled={isEvaluationRunning} />
          </Tabs>
        </Box>

        {/* Evaluation Running Alert */}
        {isEvaluationRunning && activeTab !== 1 && (
          <Alert severity="warning" sx={{ m: 2 }}>
            An evaluation is currently running. Please go to the "Run Evaluation" tab to monitor progress.
          </Alert>
        )}

        {/* Tab 1: Upload & Configure */}
        <TabPanel value={activeTab} index={0}>
          <Typography variant="h5" gutterBottom>
            Step 1: Upload Your Document
          </Typography>
          <DocumentUploader
            onUploadSuccess={() => {
              // Document uploaded successfully
            }}
          />

          <Divider sx={{ my: 4 }} />

          <Typography variant="h5" gutterBottom>
            Step 2: Select Retrieval Systems to Compare
          </Typography>
          <SystemSelector
            selectedSystems={selectedSystems}
            onChange={setSelectedSystems}
          />

          {selectedSystems.length > 0 && (
            <Alert severity="success" sx={{ mt: 3 }}>
              ✅ {selectedSystems.length} system(s) selected for evaluation
            </Alert>
          )}

          {selectedSystems.length === 0 && (
            <Alert severity="warning" sx={{ mt: 3 }}>
              ⚠️ Please select at least one retrieval system
            </Alert>
          )}

          <Divider sx={{ my: 4 }} />

          <Typography variant="h5" gutterBottom>
            Or: Import Previous Results
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Already have evaluation results? Skip re-running evaluations by importing a JSON file
          </Typography>
          <ResultsImporter onImportSuccess={handleImportSuccess} />
        </TabPanel>

        {/* Tab 2: Run Evaluation */}
        <TabPanel value={activeTab} index={1}>
          <Typography variant="h5" gutterBottom>
            🚀 Run Evaluation
          </Typography>

          {!currentDocument && (
            <Alert severity="warning" sx={{ mt: 2 }}>
              ⚠️ Please upload a document in the 'Upload & Configure' tab
            </Alert>
          )}

          {currentDocument && selectedSystems.length === 0 && (
            <Alert severity="warning" sx={{ mt: 2 }}>
              ⚠️ Please select at least one retrieval system in the 'Upload & Configure' tab
            </Alert>
          )}

          {currentDocument && selectedSystems.length > 0 && (
            <Box>
              <Alert severity="info" sx={{ mb: 3 }}>
                <Typography variant="body2">
                  📄 Document: <strong>{currentDocument.filename}</strong>
                </Typography>
                <Typography variant="body2">
                  🔧 Systems to evaluate: <strong>{selectedSystems.length}</strong>
                </Typography>
                <Typography variant="body2">
                  📊 Test questions: <strong>{numQuestions}</strong>
                </Typography>
              </Alert>

              <EvaluationRunner
                documentId={currentDocument.document_id}
                selectedSystems={selectedSystems}
                onComplete={handleEvaluationComplete}
              />
            </Box>
          )}
        </TabPanel>

        {/* Tab 3: Results & Export */}
        <TabPanel value={activeTab} index={2}>
          <Typography variant="h5" gutterBottom>
            📊 Evaluation Results
          </Typography>

          {!completedEvaluationId && (
            <Alert severity="info" sx={{ mt: 2 }}>
              No evaluation results yet. Run an evaluation in the 'Run Evaluation' tab.
            </Alert>
          )}

          {completedEvaluationId && (
            <ResultsVisualization evaluationId={completedEvaluationId} />
          )}
        </TabPanel>

        {/* Tab 4: AI Analysis */}
        <TabPanel value={activeTab} index={3}>
          <Typography variant="h5" gutterBottom>
            🤖 AI-Powered Analysis with LangGraph
          </Typography>
          <Typography variant="body1" sx={{ mb: 3 }}>
            <strong>Multiagent Analysis System</strong> - Let AI agents analyze your evaluation results and provide insights!
          </Typography>
          <Typography variant="body2" sx={{ mb: 2 }}>
            This system uses <strong>4 specialized LangGraph agents</strong> working together:
          </Typography>
          <Typography variant="body2" component="div" sx={{ mb: 1 }}>
            • 📊 <strong>Metrics Analyzer</strong>: Identifies best/worst systems and key patterns
          </Typography>
          <Typography variant="body2" component="div" sx={{ mb: 1 }}>
            • 🔍 <strong>Performance Analyzer</strong>: Discovers strengths, weaknesses, and patterns
          </Typography>
          <Typography variant="body2" component="div" sx={{ mb: 1 }}>
            • 💡 <strong>Recommendation Agent</strong>: Generates actionable recommendations
          </Typography>
          <Typography variant="body2" component="div" sx={{ mb: 3 }}>
            • 📋 <strong>Report Generator</strong>: Synthesizes everything into a comprehensive report
          </Typography>

          {!completedEvaluationId && (
            <Alert severity="warning" sx={{ mt: 2 }}>
              ⚠️ Please run an evaluation first in the 'Run Evaluation' tab before using AI analysis.
            </Alert>
          )}

          {completedEvaluationId && (
            <Box>
              <Alert severity="success" sx={{ mb: 3 }}>
                ✅ Evaluation results available for analysis
              </Alert>

              <AIAnalysisPanel evaluationId={completedEvaluationId} />
            </Box>
          )}
        </TabPanel>
      </Box>
    </Box>
  )
}

export default HomePage
