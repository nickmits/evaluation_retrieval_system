/**
 * Advanced Configuration Component
 * Allows users to configure embeddings, retrieval parameters, and ensemble weights
 */

import React from 'react'
import {
  Box,
  Typography,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Slider,
  Grid,
  Paper,
  Divider,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Tooltip,
  IconButton,
} from '@mui/material'
import {
  ExpandMore as ExpandMoreIcon,
  InfoOutlined as InfoIcon,
} from '@mui/icons-material'
import type { EmbeddingConfig, RetrievalConfig, EnsembleWeights } from '@/types/evaluation.types'

interface AdvancedConfigProps {
  embeddingConfig: EmbeddingConfig
  retrievalConfig: RetrievalConfig
  ensembleWeights: EnsembleWeights
  onEmbeddingChange: (config: EmbeddingConfig) => void
  onRetrievalChange: (config: RetrievalConfig) => void
  onWeightsChange: (weights: EnsembleWeights) => void
}

const EMBEDDING_MODELS = {
  openai: [
    'text-embedding-3-small',
    'text-embedding-3-large',
    'text-embedding-ada-002',
  ],
  cohere: [
    'embed-english-v3.0',
    'embed-english-light-v3.0',
    'embed-multilingual-v3.0',
  ],
  huggingface: [
    'sentence-transformers/all-MiniLM-L6-v2',
    'sentence-transformers/all-mpnet-base-v2',
    'BAAI/bge-small-en-v1.5',
  ],
}

const AdvancedConfig: React.FC<AdvancedConfigProps> = ({
  embeddingConfig,
  retrievalConfig,
  ensembleWeights,
  onEmbeddingChange,
  onRetrievalChange,
  onWeightsChange,
}) => {
  const weightsTotal =
    ensembleWeights.bm25_weight +
    ensembleWeights.vector_weight +
    ensembleWeights.multi_query_weight +
    ensembleWeights.reranking_weight

  const isValidWeights = Math.abs(weightsTotal - 1.0) < 0.01

  return (
    <Box sx={{ mt: 2 }}>
      <Accordion defaultExpanded={false}>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Typography variant="h6">
            ⚙️ Advanced Configuration
          </Typography>
          <Tooltip title="Configure embeddings, retrieval parameters, and ensemble weights to match your production setup" arrow>
            <IconButton size="small" sx={{ ml: 1 }}>
              <InfoIcon fontSize="small" />
            </IconButton>
          </Tooltip>
        </AccordionSummary>
        <AccordionDetails>
          <Grid container spacing={3}>
            {/* Embedding Configuration */}
            <Grid item xs={12}>
              <Paper sx={{ p: 2, bgcolor: 'background.default' }}>
                <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
                  📊 Embedding Model
                </Typography>
                <Typography variant="caption" color="text.secondary" sx={{ mb: 2, display: 'block' }}>
                  Choose the embedding model that matches your production setup. Different models have different dimensionality and semantic understanding.
                </Typography>

                <Grid container spacing={2} sx={{ mt: 1 }}>
                  <Grid item xs={12} sm={6}>
                    <FormControl fullWidth size="small">
                      <InputLabel>Provider</InputLabel>
                      <Select
                        value={embeddingConfig.provider}
                        label="Provider"
                        onChange={(e) =>
                          onEmbeddingChange({
                            ...embeddingConfig,
                            provider: e.target.value as 'openai' | 'cohere' | 'huggingface',
                            model: EMBEDDING_MODELS[e.target.value as keyof typeof EMBEDDING_MODELS][0],
                          })
                        }
                      >
                        <MenuItem value="openai">OpenAI</MenuItem>
                        <MenuItem value="cohere">Cohere</MenuItem>
                        <MenuItem value="huggingface">HuggingFace</MenuItem>
                      </Select>
                    </FormControl>
                  </Grid>

                  <Grid item xs={12} sm={6}>
                    <FormControl fullWidth size="small">
                      <InputLabel>Model</InputLabel>
                      <Select
                        value={embeddingConfig.model}
                        label="Model"
                        onChange={(e) =>
                          onEmbeddingChange({
                            ...embeddingConfig,
                            model: e.target.value,
                          })
                        }
                      >
                        {EMBEDDING_MODELS[embeddingConfig.provider].map((model) => (
                          <MenuItem key={model} value={model}>
                            {model}
                          </MenuItem>
                        ))}
                      </Select>
                    </FormControl>
                  </Grid>
                </Grid>
              </Paper>
            </Grid>

            {/* Retrieval Configuration */}
            <Grid item xs={12}>
              <Paper sx={{ p: 2, bgcolor: 'background.default' }}>
                <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
                  🔍 Retrieval Parameters (Top-K)
                </Typography>
                <Typography variant="caption" color="text.secondary" sx={{ mb: 2, display: 'block' }}>
                  Configure how many documents each retriever fetches. Higher values provide more context but may reduce precision.
                </Typography>

                <Grid container spacing={2} sx={{ mt: 1 }}>
                  <Grid item xs={12} sm={6}>
                    <Typography variant="body2" gutterBottom>
                      Base Vector Search K: {retrievalConfig.base_k}
                    </Typography>
                    <Slider
                      value={retrievalConfig.base_k}
                      onChange={(_, value) =>
                        onRetrievalChange({
                          ...retrievalConfig,
                          base_k: value as number,
                        })
                      }
                      min={1}
                      max={50}
                      step={1}
                      marks={[
                        { value: 5, label: '5' },
                        { value: 25, label: '25' },
                        { value: 50, label: '50' },
                      ]}
                      valueLabelDisplay="auto"
                    />
                  </Grid>

                  <Grid item xs={12} sm={6}>
                    <Typography variant="body2" gutterBottom>
                      BM25 Search K: {retrievalConfig.bm25_k}
                    </Typography>
                    <Slider
                      value={retrievalConfig.bm25_k}
                      onChange={(_, value) =>
                        onRetrievalChange({
                          ...retrievalConfig,
                          bm25_k: value as number,
                        })
                      }
                      min={1}
                      max={50}
                      step={1}
                      marks={[
                        { value: 5, label: '5' },
                        { value: 25, label: '25' },
                        { value: 50, label: '50' },
                      ]}
                      valueLabelDisplay="auto"
                    />
                  </Grid>

                  <Grid item xs={12} sm={6}>
                    <Typography variant="body2" gutterBottom>
                      Multi-Query K: {retrievalConfig.multi_query_k}
                    </Typography>
                    <Slider
                      value={retrievalConfig.multi_query_k}
                      onChange={(_, value) =>
                        onRetrievalChange({
                          ...retrievalConfig,
                          multi_query_k: value as number,
                        })
                      }
                      min={1}
                      max={50}
                      step={1}
                      marks={[
                        { value: 5, label: '5' },
                        { value: 25, label: '25' },
                        { value: 50, label: '50' },
                      ]}
                      valueLabelDisplay="auto"
                    />
                  </Grid>

                  <Grid item xs={12} sm={6}>
                    <Typography variant="body2" gutterBottom>
                      Final Return K: {retrievalConfig.final_k}
                    </Typography>
                    <Slider
                      value={retrievalConfig.final_k}
                      onChange={(_, value) =>
                        onRetrievalChange({
                          ...retrievalConfig,
                          final_k: value as number,
                        })
                      }
                      min={1}
                      max={50}
                      step={1}
                      marks={[
                        { value: 5, label: '5' },
                        { value: 25, label: '25' },
                        { value: 50, label: '50' },
                      ]}
                      valueLabelDisplay="auto"
                    />
                  </Grid>
                </Grid>
              </Paper>
            </Grid>

            {/* Ensemble Weights */}
            <Grid item xs={12}>
              <Paper sx={{ p: 2, bgcolor: 'background.default' }}>
                <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
                  ⚖️ Ensemble Weights (Advanced Systems Only)
                </Typography>
                <Typography variant="caption" color="text.secondary" sx={{ mb: 2, display: 'block' }}>
                  Configure how retrievers are combined. Weights must sum to 1.0. These only apply to advanced ensemble systems.
                </Typography>

                <Grid container spacing={2} sx={{ mt: 1 }}>
                  <Grid item xs={12} sm={6}>
                    <Typography variant="body2" gutterBottom>
                      BM25 Weight: {ensembleWeights.bm25_weight.toFixed(2)}
                    </Typography>
                    <Slider
                      value={ensembleWeights.bm25_weight}
                      onChange={(_, value) =>
                        onWeightsChange({
                          ...ensembleWeights,
                          bm25_weight: value as number,
                        })
                      }
                      min={0}
                      max={1}
                      step={0.05}
                      valueLabelDisplay="auto"
                    />
                  </Grid>

                  <Grid item xs={12} sm={6}>
                    <Typography variant="body2" gutterBottom>
                      Vector Weight: {ensembleWeights.vector_weight.toFixed(2)}
                    </Typography>
                    <Slider
                      value={ensembleWeights.vector_weight}
                      onChange={(_, value) =>
                        onWeightsChange({
                          ...ensembleWeights,
                          vector_weight: value as number,
                        })
                      }
                      min={0}
                      max={1}
                      step={0.05}
                      valueLabelDisplay="auto"
                    />
                  </Grid>

                  <Grid item xs={12} sm={6}>
                    <Typography variant="body2" gutterBottom>
                      Multi-Query Weight: {ensembleWeights.multi_query_weight.toFixed(2)}
                    </Typography>
                    <Slider
                      value={ensembleWeights.multi_query_weight}
                      onChange={(_, value) =>
                        onWeightsChange({
                          ...ensembleWeights,
                          multi_query_weight: value as number,
                        })
                      }
                      min={0}
                      max={1}
                      step={0.05}
                      valueLabelDisplay="auto"
                    />
                  </Grid>

                  <Grid item xs={12} sm={6}>
                    <Typography variant="body2" gutterBottom>
                      Reranking Weight: {ensembleWeights.reranking_weight.toFixed(2)}
                    </Typography>
                    <Slider
                      value={ensembleWeights.reranking_weight}
                      onChange={(_, value) =>
                        onWeightsChange({
                          ...ensembleWeights,
                          reranking_weight: value as number,
                        })
                      }
                      min={0}
                      max={1}
                      step={0.05}
                      valueLabelDisplay="auto"
                    />
                  </Grid>
                </Grid>

                <Divider sx={{ my: 2 }} />

                <Box sx={{ textAlign: 'center' }}>
                  <Typography
                    variant="body2"
                    color={isValidWeights ? 'success.main' : 'error.main'}
                    fontWeight="bold"
                  >
                    Total Weight: {weightsTotal.toFixed(2)} / 1.00
                    {isValidWeights ? ' ✓' : ' ⚠️ Must equal 1.00'}
                  </Typography>
                </Box>
              </Paper>
            </Grid>
          </Grid>
        </AccordionDetails>
      </Accordion>
    </Box>
  )
}

export default AdvancedConfig
