/**
 * Main App component with routing
 */

import React from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { Box } from '@mui/material'
import HomePage from './pages/HomePage'

const App: React.FC = () => {
  return (
    <BrowserRouter>
      <Box sx={{ minHeight: '100vh', width: '100%', bgcolor: 'background.default' }}>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Box>
    </BrowserRouter>
  )
}

export default App
