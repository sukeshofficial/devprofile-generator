/**
 * Main App component for DevProfile Resume Automator
 * 
 * Provides routing and layout for the application with GitHub integration,
 * skill analysis, resume generation, and portfolio creation features.
 */

import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import HomePage from './pages/HomePage';
import DashboardPage from './pages/DashboardPage';
import ResumePage from './pages/ResumePage';
import PortfolioPage from './pages/PortfolioPage';
import Navigation from './components/Navigation';
import { AuthProvider } from './contexts/AuthContext';

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
          <Navigation />
          <main className="flex-1">
            <Routes>
              <Route path="/" element={<HomePage />} />
              <Route path="/dashboard" element={<DashboardPage />} />
              <Route path="/resume" element={<ResumePage />} />
              <Route path="/portfolio" element={<PortfolioPage />} />
            </Routes>
          </main>
          
          {/* Footer */}
          <footer className="bg-white/80 backdrop-blur-md border-t border-gray-200 mt-20">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
              <div className="text-center">
                <p className="text-gray-600 mb-4">DevProfile Resume & Portfolio Automator</p>
                <div className="flex justify-center space-x-6">
                  <a 
                    href="https://github.com/sukeshofficial" 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="text-primary-600 hover:text-primary-700 font-medium transition-colors"
                  >
                    GitHub
                  </a>
                  <a 
                    href="#" 
                    className="text-primary-600 hover:text-primary-700 font-medium transition-colors"
                  >
                    Documentation
                  </a>
                  <a 
                    href="#" 
                    className="text-primary-600 hover:text-primary-700 font-medium transition-colors"
                  >
                    Support
                  </a>
                </div>
              </div>
            </div>
          </footer>
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;