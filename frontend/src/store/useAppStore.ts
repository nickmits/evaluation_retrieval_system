/**
 * Zustand store for global app state
 */

import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type { DocumentInfo } from '@/types/document.types'
import type { EvaluationInfo } from '@/types/evaluation.types'
import type { EvaluationResults } from '@/types/results.types'
import type { AnalysisResult } from '@/types/analysis.types'

interface AppState {
  // Document state
  currentDocument: DocumentInfo | null
  setCurrentDocument: (document: DocumentInfo | null) => void

  // Evaluation state
  currentEvaluation: EvaluationInfo | null
  setCurrentEvaluation: (evaluation: EvaluationInfo | null) => void

  // Results state
  currentResults: EvaluationResults | null
  setCurrentResults: (results: EvaluationResults | null) => void

  // Analysis state
  currentAnalysis: AnalysisResult | null
  setCurrentAnalysis: (analysis: AnalysisResult | null) => void

  // Reset all state
  reset: () => void
}

export const useAppStore = create<AppState>()(
  persist(
    (set) => ({
      // Document state
      currentDocument: null,
      setCurrentDocument: (document) => set({ currentDocument: document }),

      // Evaluation state
      currentEvaluation: null,
      setCurrentEvaluation: (evaluation) => set({ currentEvaluation: evaluation }),

      // Results state
      currentResults: null,
      setCurrentResults: (results) => set({ currentResults: results }),

      // Analysis state
      currentAnalysis: null,
      setCurrentAnalysis: (analysis) => set({ currentAnalysis: analysis }),

      // Reset
      reset: () =>
        set({
          currentDocument: null,
          currentEvaluation: null,
          currentResults: null,
          currentAnalysis: null,
        }),
    }),
    {
      name: 'rag-evaluation-store',
    }
  )
)
