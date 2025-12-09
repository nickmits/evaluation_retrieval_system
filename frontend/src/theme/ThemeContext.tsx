/**
 * Theme context for managing dark/light mode
 */

import React, { createContext, useContext, useState, useEffect, useMemo } from 'react'
import { ThemeProvider as MuiThemeProvider, PaletteMode } from '@mui/material/styles'
import { CssBaseline } from '@mui/material'
import { getTheme } from './theme'

interface ThemeContextType {
  mode: PaletteMode
  toggleTheme: () => void
  setThemeMode: (mode: PaletteMode) => void
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined)

export const useThemeMode = () => {
  const context = useContext(ThemeContext)
  if (!context) {
    throw new Error('useThemeMode must be used within ThemeProvider')
  }
  return context
}

interface ThemeProviderProps {
  children: React.ReactNode
}

export const ThemeProvider: React.FC<ThemeProviderProps> = ({ children }) => {
  // Get initial theme from localStorage or default to 'light'
  const [mode, setMode] = useState<PaletteMode>(() => {
    const saved = localStorage.getItem('theme-mode')
    return (saved as PaletteMode) || 'light'
  })

  // Save theme to localStorage whenever it changes
  useEffect(() => {
    localStorage.setItem('theme-mode', mode)
  }, [mode])

  const toggleTheme = () => {
    setMode((prevMode) => (prevMode === 'light' ? 'dark' : 'light'))
  }

  const setThemeMode = (newMode: PaletteMode) => {
    setMode(newMode)
  }

  const theme = useMemo(() => getTheme(mode), [mode])

  const value = useMemo(
    () => ({
      mode,
      toggleTheme,
      setThemeMode,
    }),
    [mode]
  )

  return (
    <ThemeContext.Provider value={value}>
      <MuiThemeProvider theme={theme}>
        <CssBaseline />
        {children}
      </MuiThemeProvider>
    </ThemeContext.Provider>
  )
}
