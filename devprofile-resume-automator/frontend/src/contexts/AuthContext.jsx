/**
 * Authentication context for managing user state
 * 
 * Provides authentication state management, GitHub OAuth integration,
 * and user session handling throughout the application.
 */

import React, { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check for existing session on app load
    const token = localStorage.getItem('devprofile_token');
    const userData = localStorage.getItem('devprofile_user');
    
    if (token && userData) {
      try {
        const parsedUser = JSON.parse(userData);
        setUser(parsedUser);
      } catch (error) {
        console.error('Failed to parse stored user data:', error);
        localStorage.removeItem('devprofile_token');
        localStorage.removeItem('devprofile_user');
      }
    }
    
    setLoading(false);
  }, []);

  const login = async () => {
    try {
      // Redirect to GitHub OAuth
      window.location.href = 'http://localhost:8000/api/auth/github/login';
    } catch (error) {
      console.error('Login failed:', error);
      throw error;
    }
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem('devprofile_token');
    localStorage.removeItem('devprofile_user');
  };

  const updateUser = (userData) => {
    setUser(userData);
    localStorage.setItem('devprofile_user', JSON.stringify(userData));
  };

  const setAuthToken = (token) => {
    localStorage.setItem('devprofile_token', token);
  };

  const getAuthToken = () => {
    return localStorage.getItem('devprofile_token');
  };

  const value = {
    user,
    loading,
    login,
    logout,
    updateUser,
    setAuthToken,
    getAuthToken
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};