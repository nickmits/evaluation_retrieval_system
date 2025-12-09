/**
 * System selector component with configuration forms
 */

import React, { useState } from 'react'
import {
  Box,
  Card,
  CardContent,
  Typography,
  Checkbox,
  FormControlLabel,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Slider,
  Collapse,
  Grid,
  Chip,
  Stack,
  Tooltip,
  IconButton,
} from '@mui/material'
import { ExpandMore as ExpandIcon, InfoOutlined as InfoIcon, Settings as SettingsIcon } from '@mui/icons-material'
import type { SystemSelection, SystemType, SystemConfig } from '@/types/evaluation.types'

interface SystemSelectorProps {
  selectedSystems: SystemSelection[]
  onChange: (systems: SystemSelection[]) => void
}

interface SystemInfo {
  type: SystemType
  name: string
  description: string
  category: 'simple' | 'advanced'
  configType: 'recursive' | 'semantic' | 'parent_document'
  emoji: string
  tooltip: string
}

const AVAILABLE_SYSTEMS: SystemInfo[] = [
  {
    type: 'simple_recursive',
    name: 'Simple Recursive Chunking',
    description: 'RecursiveCharacterTextSplitter + Vector Search',
    category: 'simple',
    configType: 'recursive',
    emoji: '📋',
    tooltip: 'Baseline: RecursiveCharacterTextSplitter + Vector Search',
  },
  {
    type: 'simple_semantic',
    name: 'Simple Semantic Chunking',
    description: 'SemanticChunker + Vector Search',
    category: 'simple',
    configType: 'semantic',
    emoji: '🧠',
    tooltip: 'SemanticChunker + Vector Search (slower but often better)',
  },
  {
    type: 'advanced_recursive',
    name: 'Advanced Recursive (Ensemble)',
    description: 'Recursive + BM25 + Multi-Query + Reranking',
    category: 'advanced',
    configType: 'recursive',
    emoji: '⚡',
    tooltip: 'Recursive chunking + BM25 + Multi-Query + Reranking',
  },
  {
    type: 'advanced_semantic',
    name: 'Advanced Semantic (Ensemble)',
    description: 'Semantic + BM25 + Multi-Query + Reranking',
    category: 'advanced',
    configType: 'semantic',
    emoji: '🔬',
    tooltip: 'Semantic chunking + BM25 + Multi-Query + Reranking',
  },
  {
    type: 'parent_document',
    name: 'Parent Document Retrieval',
    description: 'Search small chunks, retrieve larger parent documents',
    category: 'advanced',
    configType: 'parent_document',
    emoji: '📚',
    tooltip: 'Stores small chunks for precise search but retrieves full parent documents for better context',
  },
  {
    type: 'advanced_parent_document',
    name: 'Advanced Parent Document (Ensemble)',
    description: 'Parent Document + BM25 + Multi-Query + Reranking',
    category: 'advanced',
    configType: 'parent_document',
    emoji: '🚀',
    tooltip: 'Parent Document retrieval combined with BM25, Multi-Query, and Cohere Reranking',
  },
]

const SystemSelector: React.FC<SystemSelectorProps> = ({ selectedSystems, onChange }) => {
  const [expandedConfigs, setExpandedConfigs] = useState<Set<SystemType>>(new Set())

  const isSystemSelected = (type: SystemType): boolean => {
    return selectedSystems.some((s) => s.type === type)
  }

  const getSystemConfig = (type: SystemType): SystemConfig => {
    const system = selectedSystems.find((s) => s.type === type)
    return (
      system?.config || {
        chunk_size: 1000,
        chunk_overlap: 200,
        threshold_type: 'percentile',
        threshold_amount: 95,
        parent_chunk_size: 2000,
        parent_chunk_overlap: 200,
        child_chunk_size: 400,
        child_chunk_overlap: 50,
      }
    )
  }

  const toggleSystem = (systemInfo: SystemInfo) => {
    if (isSystemSelected(systemInfo.type)) {
      // Remove system
      onChange(selectedSystems.filter((s) => s.type !== systemInfo.type))
      const newExpanded = new Set(expandedConfigs)
      newExpanded.delete(systemInfo.type)
      setExpandedConfigs(newExpanded)
    } else {
      // Add system with default config
      const newSystem: SystemSelection = {
        name: systemInfo.name,
        type: systemInfo.type,
        config: {
          chunk_size: 1000,
          chunk_overlap: 200,
          threshold_type: 'percentile',
          threshold_amount: 95,
          parent_chunk_size: 2000,
          parent_chunk_overlap: 200,
          child_chunk_size: 400,
          child_chunk_overlap: 50,
        },
      }
      onChange([...selectedSystems, newSystem])
    }
  }

  const toggleConfigExpanded = (type: SystemType) => {
    const newExpanded = new Set(expandedConfigs)
    if (newExpanded.has(type)) {
      newExpanded.delete(type)
    } else {
      newExpanded.add(type)
    }
    setExpandedConfigs(newExpanded)
  }

  const updateSystemConfig = (type: SystemType, config: Partial<SystemConfig>) => {
    onChange(
      selectedSystems.map((s) =>
        s.type === type
          ? {
              ...s,
              config: { ...s.config, ...config },
            }
          : s
      )
    )
  }

  const renderRecursiveConfig = (type: SystemType, config: SystemConfig) => (
    <Box sx={{ mt: 2, pl: 4 }}>
      <Grid container spacing={2}>
        <Grid item xs={12} sm={6}>
          <TextField
            label="Chunk Size"
            type="number"
            fullWidth
            value={config.chunk_size || 1000}
            onChange={(e) =>
              updateSystemConfig(type, { chunk_size: parseInt(e.target.value) })
            }
            inputProps={{ min: 100, max: 2000, step: 100 }}
            helperText="Size of text chunks (100-2000)"
          />
        </Grid>
        <Grid item xs={12} sm={6}>
          <TextField
            label="Chunk Overlap"
            type="number"
            fullWidth
            value={config.chunk_overlap || 200}
            onChange={(e) =>
              updateSystemConfig(type, { chunk_overlap: parseInt(e.target.value) })
            }
            inputProps={{ min: 0, max: 500, step: 50 }}
            helperText="Overlap between chunks (0-500)"
          />
        </Grid>
      </Grid>
    </Box>
  )

  const renderSemanticConfig = (type: SystemType, config: SystemConfig) => (
    <Box sx={{ mt: 2, pl: 4 }}>
      <Grid container spacing={2}>
        <Grid item xs={12} sm={6}>
          <FormControl fullWidth>
            <InputLabel>Threshold Type</InputLabel>
            <Select
              value={config.threshold_type || 'percentile'}
              label="Threshold Type"
              onChange={(e) =>
                updateSystemConfig(type, { threshold_type: e.target.value })
              }
            >
              <MenuItem value="percentile">Percentile</MenuItem>
              <MenuItem value="standard_deviation">Standard Deviation</MenuItem>
              <MenuItem value="interquartile">Interquartile</MenuItem>
            </Select>
          </FormControl>
        </Grid>
        <Grid item xs={12} sm={6}>
          <Typography gutterBottom>Threshold Amount: {config.threshold_amount || 95}</Typography>
          <Slider
            value={config.threshold_amount || 95}
            onChange={(_, value) =>
              updateSystemConfig(type, { threshold_amount: value as number })
            }
            min={50}
            max={99}
            step={1}
            marks={[
              { value: 50, label: '50' },
              { value: 75, label: '75' },
              { value: 99, label: '99' },
            ]}
          />
        </Grid>
      </Grid>
    </Box>
  )

  const renderParentDocumentConfig = (type: SystemType, config: SystemConfig) => (
    <Box sx={{ mt: 2, pl: 4 }}>
      <Typography variant="subtitle2" gutterBottom sx={{ fontWeight: 'bold' }}>
        Parent Chunks (Retrieved Documents)
      </Typography>
      <Grid container spacing={2}>
        <Grid item xs={12} sm={6}>
          <TextField
            label="Parent Chunk Size"
            type="number"
            fullWidth
            value={config.parent_chunk_size || 2000}
            onChange={(e) =>
              updateSystemConfig(type, { parent_chunk_size: parseInt(e.target.value) })
            }
            inputProps={{ min: 500, max: 4000, step: 100 }}
            helperText="Size of returned documents (500-4000)"
          />
        </Grid>
        <Grid item xs={12} sm={6}>
          <TextField
            label="Parent Chunk Overlap"
            type="number"
            fullWidth
            value={config.parent_chunk_overlap || 200}
            onChange={(e) =>
              updateSystemConfig(type, { parent_chunk_overlap: parseInt(e.target.value) })
            }
            inputProps={{ min: 0, max: 500, step: 50 }}
            helperText="Overlap between parents (0-500)"
          />
        </Grid>
      </Grid>

      <Typography variant="subtitle2" gutterBottom sx={{ fontWeight: 'bold', mt: 3 }}>
        Child Chunks (Searchable Units)
      </Typography>
      <Grid container spacing={2}>
        <Grid item xs={12} sm={6}>
          <TextField
            label="Child Chunk Size"
            type="number"
            fullWidth
            value={config.child_chunk_size || 400}
            onChange={(e) =>
              updateSystemConfig(type, { child_chunk_size: parseInt(e.target.value) })
            }
            inputProps={{ min: 100, max: 1000, step: 50 }}
            helperText="Size of search chunks (100-1000)"
          />
        </Grid>
        <Grid item xs={12} sm={6}>
          <TextField
            label="Child Chunk Overlap"
            type="number"
            fullWidth
            value={config.child_chunk_overlap || 50}
            onChange={(e) =>
              updateSystemConfig(type, { child_chunk_overlap: parseInt(e.target.value) })
            }
            inputProps={{ min: 0, max: 200, step: 25 }}
            helperText="Overlap between children (0-200)"
          />
        </Grid>
      </Grid>
    </Box>
  )

  const simpleSystems = AVAILABLE_SYSTEMS.filter((s) => s.category === 'simple')
  const advancedSystems = AVAILABLE_SYSTEMS.filter((s) => s.category === 'advanced')

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Select Retrieval Systems
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
          Choose one or more retrieval systems to evaluate and compare
        </Typography>

        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
              Simple Systems
            </Typography>
            <Stack spacing={2}>
              {simpleSystems.map((system) => (
                <Card key={system.type} variant="outlined">
                  <CardContent>
                    <FormControlLabel
                      control={
                        <Checkbox
                          checked={isSystemSelected(system.type)}
                          onChange={() => toggleSystem(system)}
                        />
                      }
                      label={
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <Box sx={{ flexGrow: 1 }}>
                            <Typography variant="body1" fontWeight="bold">
                              {system.emoji} {system.name}
                            </Typography>
                            <Typography variant="caption" color="text.secondary">
                              {system.description}
                            </Typography>
                          </Box>
                          <Tooltip title={system.tooltip} arrow>
                            <IconButton size="small">
                              <InfoIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                        </Box>
                      }
                    />

                    {isSystemSelected(system.type) && (
                      <Box>
                        <Chip
                          label={expandedConfigs.has(system.type) ? 'Hide Config' : '⚙️ Configure'}
                          size="small"
                          onClick={() => toggleConfigExpanded(system.type)}
                          icon={<ExpandIcon />}
                          sx={{ mt: 1 }}
                        />
                        <Collapse in={expandedConfigs.has(system.type)}>
                          {system.configType === 'recursive'
                            ? renderRecursiveConfig(system.type, getSystemConfig(system.type))
                            : system.configType === 'semantic'
                            ? renderSemanticConfig(system.type, getSystemConfig(system.type))
                            : renderParentDocumentConfig(system.type, getSystemConfig(system.type))}
                        </Collapse>
                      </Box>
                    )}
                  </CardContent>
                </Card>
              ))}
            </Stack>
          </Grid>

          <Grid item xs={12} md={6}>
            <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
              Advanced Systems
            </Typography>
            <Stack spacing={2}>
              {advancedSystems.map((system) => (
                <Card key={system.type} variant="outlined">
                  <CardContent>
                    <FormControlLabel
                      control={
                        <Checkbox
                          checked={isSystemSelected(system.type)}
                          onChange={() => toggleSystem(system)}
                        />
                      }
                      label={
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <Box sx={{ flexGrow: 1 }}>
                            <Typography variant="body1" fontWeight="bold">
                              {system.emoji} {system.name}
                            </Typography>
                            <Typography variant="caption" color="text.secondary">
                              {system.description}
                            </Typography>
                          </Box>
                          <Tooltip title={system.tooltip} arrow>
                            <IconButton size="small">
                              <InfoIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                        </Box>
                      }
                    />

                    {isSystemSelected(system.type) && (
                      <Box>
                        <Chip
                          label={expandedConfigs.has(system.type) ? 'Hide Config' : '⚙️ Configure'}
                          size="small"
                          onClick={() => toggleConfigExpanded(system.type)}
                          icon={<ExpandIcon />}
                          sx={{ mt: 1 }}
                        />
                        <Collapse in={expandedConfigs.has(system.type)}>
                          {system.configType === 'recursive'
                            ? renderRecursiveConfig(system.type, getSystemConfig(system.type))
                            : system.configType === 'semantic'
                            ? renderSemanticConfig(system.type, getSystemConfig(system.type))
                            : renderParentDocumentConfig(system.type, getSystemConfig(system.type))}
                        </Collapse>
                      </Box>
                    )}
                  </CardContent>
                </Card>
              ))}
            </Stack>
          </Grid>
        </Grid>

        {selectedSystems.length > 0 && (
          <Box sx={{ mt: 3, p: 2, bgcolor: 'success.light', borderRadius: 1 }}>
            <Typography variant="body2" fontWeight="bold">
              ✓ {selectedSystems.length} system(s) selected for evaluation
            </Typography>
          </Box>
        )}
      </CardContent>
    </Card>
  )
}

export default SystemSelector
