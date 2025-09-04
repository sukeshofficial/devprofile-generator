/**
 * Navigation component with authentication state
 * 
 * Provides main navigation bar with user authentication status,
 * GitHub login, and navigation between different sections.
 */

import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Code, User, FileText, Briefcase, LogOut } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

const Navigation = () => {
  const location = useLocation();
  const { user, logout } = useAuth();
  
  const navItems = [
    { path: '/', label: 'Home', icon: Code },
    { path: '/dashboard', label: 'Dashboard', icon: User, requireAuth: true },
    { path: '/resume', label: 'Resume', icon: FileText, requireAuth: true },
    { path: '/portfolio', label: 'Portfolio', icon: Briefcase, requireAuth: true },
  ];
  
  const isActive = (path) => location.pathname === path;
  
  return (
    <nav className="bg-white/80 backdrop-blur-md border-b border-gray-200 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-r from-primary-500 to-secondary-500 rounded-lg flex items-center justify-center">
              <Code className="text-white" size={20} />
            </div>
            <h1 className="text-xl font-bold bg-gradient-to-r from-primary-600 to-secondary-600 bg-clip-text text-transparent">
              DevProfile
            </h1>
          </Link>
          
          {/* Navigation Links */}
          <div className="hidden md:flex items-center space-x-8">
            {navItems.map(({ path, label, icon: Icon, requireAuth }) => {
              if (requireAuth && !user) return null;
              
              return (
                <Link
                  key={path}
                  to={path}
                  className={`flex items-center space-x-2 px-3 py-2 rounded-lg transition-colors ${
                    isActive(path)
                      ? 'bg-primary-100 text-primary-700'
                      : 'text-gray-600 hover:text-primary-600 hover:bg-gray-100'
                  }`}
                >
                  <Icon size={18} />
                  <span className="font-medium">{label}</span>
                </Link>
              );
            })}
          </div>
          
          {/* User Menu */}
          <div className="flex items-center space-x-4">
            {user ? (
              <div className="flex items-center space-x-3">
                <img
                  src={user.avatar_url}
                  alt={user.name}
                  className="w-8 h-8 rounded-full border-2 border-primary-200"
                />
                <span className="hidden md:block text-sm font-medium text-gray-700">
                  {user.name || user.username}
                </span>
                <button
                  onClick={logout}
                  className="text-gray-600 hover:text-red-600 transition-colors"
                  title="Logout"
                >
                  <LogOut size={18} />
                </button>
              </div>
            ) : (
              <Link
                to="/"
                className="btn-primary text-sm"
              >
                Get Started
              </Link>
            )}
          </div>
        </div>
      </div>
      
      {/* Mobile Navigation */}
      <div className="md:hidden border-t border-gray-200 bg-white/90">
        <div className="px-4 py-2 space-y-1">
          {navItems.map(({ path, label, icon: Icon, requireAuth }) => {
            if (requireAuth && !user) return null;
            
            return (
              <Link
                key={path}
                to={path}
                className={`flex items-center space-x-3 px-3 py-2 rounded-lg transition-colors ${
                  isActive(path)
                    ? 'bg-primary-100 text-primary-700'
                    : 'text-gray-600 hover:text-primary-600 hover:bg-gray-100'
                }`}
              >
                <Icon size={18} />
                <span className="font-medium">{label}</span>
              </Link>
            );
          })}
        </div>
      </div>
    </nav>
  );
};

export default Navigation;