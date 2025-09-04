/**
 * Home page component with GitHub authentication and feature overview
 * 
 * Landing page that introduces the application features and provides
 * GitHub OAuth login functionality.
 */

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Github, Zap, FileText, Briefcase, ArrowRight, Star } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

const HomePage = () => {
  const navigate = useNavigate();
  const { user, login } = useAuth();
  const [loading, setLoading] = useState(false);

  const handleGitHubLogin = async () => {
    setLoading(true);
    try {
      await login();
      navigate('/dashboard');
    } catch (error) {
      console.error('Login failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const features = [
    {
      icon: Github,
      title: 'GitHub Integration',
      description: 'Connect your GitHub account to automatically analyze your repositories and extract technical skills.',
      color: 'from-gray-600 to-gray-800'
    },
    {
      icon: Zap,
      title: 'AI-Powered Analysis',
      description: 'Advanced AI extracts skills, generates STAR-format bullets, and matches you with relevant job opportunities.',
      color: 'from-yellow-500 to-orange-500'
    },
    {
      icon: FileText,
      title: 'ATS-Friendly Resumes',
      description: 'Generate professional, ATS-optimized PDF resumes that pass through applicant tracking systems.',
      color: 'from-blue-500 to-purple-500'
    },
    {
      icon: Briefcase,
      title: 'Portfolio Generation',
      description: 'Create a complete Next.js portfolio website ready for deployment to showcase your projects.',
      color: 'from-green-500 to-teal-500'
    }
  ];

  const stats = [
    { label: 'Resumes Generated', value: '10,000+' },
    { label: 'Skills Extracted', value: '50,000+' },
    { label: 'Job Matches', value: '25,000+' },
    { label: 'Portfolios Created', value: '5,000+' }
  ];

  if (user) {
    return (
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="text-center">
          <div className="w-24 h-24 mx-auto mb-6">
            <img
              src={user.avatar_url}
              alt={user.name}
              className="w-full h-full rounded-full border-4 border-primary-200 shadow-lg"
            />
          </div>
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Welcome back, {user.name || user.username}!
          </h1>
          <p className="text-xl text-gray-600 mb-8">
            Ready to create your next resume or portfolio?
          </p>
          
          <div className="flex justify-center space-x-4">
            <button
              onClick={() => navigate('/dashboard')}
              className="btn-primary flex items-center"
            >
              <ArrowRight className="mr-2" size={20} />
              Go to Dashboard
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="relative overflow-hidden">
      {/* Hero Section */}
      <div className="gradient-bg relative">
        <div className="absolute inset-0 bg-black/20"></div>
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
          <div className="text-center">
            <h1 className="text-4xl md:text-6xl font-bold text-white mb-6 animate-fade-in">
              Transform Your GitHub Into
              <span className="block bg-gradient-to-r from-yellow-300 to-orange-300 bg-clip-text text-transparent">
                Career Success
              </span>
            </h1>
            <p className="text-xl text-white/90 mb-8 max-w-3xl mx-auto animate-slide-up">
              AI-powered resume and portfolio generator that analyzes your GitHub repositories
              to create professional resumes and stunning portfolio websites.
            </p>
            
            <div className="flex flex-wrap justify-center gap-4 text-white/80 mb-8 animate-slide-up">
              <div className="flex items-center space-x-2">
                <Zap size={20} />
                <span>AI-Powered</span>
              </div>
              <div className="flex items-center space-x-2">
                <FileText size={20} />
                <span>ATS-Friendly</span>
              </div>
              <div className="flex items-center space-x-2">
                <Briefcase size={20} />
                <span>Portfolio Ready</span>
              </div>
            </div>

            <button
              onClick={handleGitHubLogin}
              disabled={loading}
              className="bg-white text-primary-600 py-4 px-8 rounded-lg font-semibold text-lg hover:bg-gray-100 transform hover:scale-[1.02] transition-all duration-200 shadow-lg hover:shadow-xl"
            >
              {loading ? (
                <div className="flex items-center">
                  <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary-600 mr-3"></div>
                  Connecting...
                </div>
              ) : (
                <div className="flex items-center">
                  <Github className="mr-3" size={24} />
                  Connect with GitHub
                </div>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="text-center mb-16">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">How It Works</h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Our AI-powered platform transforms your GitHub activity into professional career assets
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
          {features.map((feature, index) => (
            <div key={index} className="card text-center hover:shadow-2xl transition-all duration-300">
              <div className={`w-16 h-16 bg-gradient-to-r ${feature.color} rounded-full flex items-center justify-center mx-auto mb-6`}>
                <feature.icon className="text-white" size={24} />
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-4">{feature.title}</h3>
              <p className="text-gray-600 leading-relaxed">
                {feature.description}
              </p>
            </div>
          ))}
        </div>
      </div>

      {/* Stats Section */}
      <div className="bg-white py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">Trusted by Developers</h2>
            <p className="text-gray-600">Join thousands of developers who've accelerated their careers</p>
          </div>
          
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            {stats.map((stat, index) => (
              <div key={index} className="text-center">
                <div className="text-3xl font-bold text-primary-600 mb-2">{stat.value}</div>
                <div className="text-gray-600">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Process Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="text-center mb-16">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">Simple 4-Step Process</h2>
          <p className="text-gray-600">From GitHub to career success in minutes</p>
        </div>

        <div className="grid md:grid-cols-4 gap-8">
          {[
            { step: '1', title: 'Connect GitHub', desc: 'Authenticate with your GitHub account' },
            { step: '2', title: 'Select Repos', desc: 'Choose repositories to analyze' },
            { step: '3', title: 'AI Analysis', desc: 'Extract skills and generate content' },
            { step: '4', title: 'Export & Share', desc: 'Download resume and portfolio' }
          ].map((item, index) => (
            <div key={index} className="text-center">
              <div className="w-12 h-12 bg-primary-600 text-white rounded-full flex items-center justify-center mx-auto mb-4 font-bold text-lg">
                {item.step}
              </div>
              <h3 className="font-semibold text-gray-900 mb-2">{item.title}</h3>
              <p className="text-gray-600 text-sm">{item.desc}</p>
            </div>
          ))}
        </div>
      </div>

      {/* CTA Section */}
      <div className="bg-gradient-to-r from-primary-600 to-secondary-600 py-16">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl font-bold text-white mb-4">
            Ready to Accelerate Your Career?
          </h2>
          <p className="text-xl text-blue-100 mb-8">
            Join thousands of developers who've transformed their GitHub activity into career opportunities.
          </p>
          
          <button
            onClick={handleGitHubLogin}
            disabled={loading}
            className="bg-white text-primary-600 py-4 px-8 rounded-lg font-semibold text-lg hover:bg-gray-100 transform hover:scale-[1.02] transition-all duration-200 shadow-lg hover:shadow-xl"
          >
            <div className="flex items-center">
              <Github className="mr-3" size={24} />
              Get Started Free
            </div>
          </button>
          
          <p className="text-blue-100 text-sm mt-4">
            No credit card required • Free GitHub analysis • Export ready resumes
          </p>
        </div>
      </div>
    </div>
  );
};

export default HomePage;