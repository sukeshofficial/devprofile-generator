/**
 * Portfolio page for generating Next.js portfolio websites
 * 
 * Provides interface for creating and downloading complete
 * Next.js portfolio projects based on user data.
 */

import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import PortfolioGenerator from '../components/PortfolioGenerator';
import { useAuth } from '../contexts/AuthContext';
import { Globe } from 'lucide-react';

const PortfolioPage = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [portfolioData, setPortfolioData] = useState(null);

  useEffect(() => {
    if (!user) {
      navigate('/');
      return;
    }

    // Get imported data from navigation state
    const importedData = location.state?.importedData;
    if (importedData) {
      const transformedData = transformToPortfolioData(importedData);
      setPortfolioData(transformedData);
    } else {
      // Load default portfolio data
      setPortfolioData(getDefaultPortfolioData());
    }
  }, [user, location.state, navigate]);

  const transformToPortfolioData = (importedData) => {
    // Extract unique skills
    const allSkills = importedData.skills.reduce((acc, repoSkills) => {
      return [...acc, ...repoSkills.skills, ...repoSkills.tools];
    }, []);
    const uniqueSkills = [...new Set(allSkills)];

    return {
      name: user.name || user.username,
      email: user.email || '',
      github_url: `https://github.com/${user.username}`,
      linkedin_url: '',
      summary: `Experienced developer with expertise in ${uniqueSkills.slice(0, 3).join(', ')} and other modern technologies.`,
      skills: uniqueSkills,
      projects: importedData.repos.map(repo => ({
        name: repo.name,
        description: repo.description,
        technologies: repo.languages,
        github_url: repo.html_url,
        stars: repo.stars,
        forks: repo.forks
      })),
      bullets: importedData.bullets || []
    };
  };

  const getDefaultPortfolioData = () => {
    return {
      name: user?.name || user?.username || 'Developer',
      email: user?.email || '',
      github_url: user?.username ? `https://github.com/${user.username}` : '',
      linkedin_url: '',
      summary: 'Passionate developer building modern web applications.',
      skills: [],
      projects: [],
      bullets: []
    };
  };

  if (!portfolioData) {
    return (
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading portfolio data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="text-center mb-12">
        <h1 className="text-4xl font-bold text-gray-900 mb-4 flex items-center justify-center">
          <Globe className="text-primary-600 mr-3" size={36} />
          Portfolio Generator
        </h1>
        <p className="text-xl text-gray-600">
          Create a professional Next.js portfolio website
        </p>
      </div>

      {/* Portfolio Generator */}
      <PortfolioGenerator profileData={portfolioData} />

      {/* Back to Dashboard */}
      <div className="text-center mt-12">
        <button
          onClick={() => navigate('/dashboard')}
          className="btn-secondary"
        >
          Back to Dashboard
        </button>
      </div>
    </div>
  );
};

export default PortfolioPage;