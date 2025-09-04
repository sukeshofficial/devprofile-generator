/**
 * Dashboard page for authenticated users
 * 
 * Main workspace where users can import GitHub data, view analysis results,
 * and navigate to resume/portfolio generation features.
 */

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import GitHubImport from '../components/GitHubImport';
import { useAuth } from '../contexts/AuthContext';
import { BarChart3, FileText, Globe, TrendingUp } from 'lucide-react';

const DashboardPage = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [importedData, setImportedData] = useState(null);
  const [activeTab, setActiveTab] = useState('import');

  const handleImportComplete = (data) => {
    setImportedData(data);
    setActiveTab('results');
  };

  const handleCreateResume = () => {
    navigate('/resume', { state: { importedData } });
  };

  const handleCreatePortfolio = () => {
    navigate('/portfolio', { state: { importedData } });
  };

  if (!user) {
    navigate('/');
    return null;
  }

  const renderImportTab = () => (
    <GitHubImport onImportComplete={handleImportComplete} />
  );

  const renderResultsTab = () => {
    if (!importedData) {
      return (
        <div className="text-center py-12">
          <p className="text-gray-600">No analysis data available. Please import your GitHub repositories first.</p>
          <button
            onClick={() => setActiveTab('import')}
            className="btn-primary mt-4"
          >
            Import GitHub Data
          </button>
        </div>
      );
    }

    // Aggregate skills from all repositories
    const allSkills = importedData.skills.reduce((acc, repoSkills) => {
      return [...acc, ...repoSkills.skills, ...repoSkills.tools];
    }, []);
    const uniqueSkills = [...new Set(allSkills)];

    return (
      <div className="space-y-8">
        {/* Analysis Summary */}
        <div className="grid md:grid-cols-4 gap-6">
          <div className="card text-center">
            <div className="text-3xl font-bold text-primary-600 mb-2">
              {importedData.repos.length}
            </div>
            <div className="text-gray-600">Repositories Analyzed</div>
          </div>
          
          <div className="card text-center">
            <div className="text-3xl font-bold text-green-600 mb-2">
              {uniqueSkills.length}
            </div>
            <div className="text-gray-600">Skills Extracted</div>
          </div>
          
          <div className="card text-center">
            <div className="text-3xl font-bold text-blue-600 mb-2">
              {importedData.bullets.length}
            </div>
            <div className="text-gray-600">Resume Bullets</div>
          </div>
          
          <div className="card text-center">
            <div className="text-3xl font-bold text-purple-600 mb-2">
              {importedData.repos.reduce((sum, repo) => sum + repo.stars, 0)}
            </div>
            <div className="text-gray-600">Total Stars</div>
          </div>
        </div>

        {/* Skills Overview */}
        <div className="card">
          <h3 className="text-xl font-semibold text-gray-900 mb-6 flex items-center">
            <BarChart3 className="text-primary-600 mr-2" size={20} />
            Extracted Skills
          </h3>
          
          <div className="flex flex-wrap gap-2">
            {uniqueSkills.slice(0, 20).map((skill, index) => (
              <span
                key={index}
                className="bg-primary-100 text-primary-800 px-3 py-2 rounded-full text-sm font-medium"
              >
                {skill}
              </span>
            ))}
            {uniqueSkills.length > 20 && (
              <span className="text-gray-500 px-3 py-2">
                +{uniqueSkills.length - 20} more
              </span>
            )}
          </div>
        </div>

        {/* Repository Analysis */}
        <div className="card">
          <h3 className="text-xl font-semibold text-gray-900 mb-6">Repository Analysis</h3>
          
          <div className="space-y-4">
            {importedData.repos.map((repo, index) => (
              <div key={index} className="border border-gray-200 rounded-lg p-4">
                <div className="flex items-start justify-between mb-2">
                  <div>
                    <h4 className="font-semibold text-gray-900">{repo.name}</h4>
                    <p className="text-sm text-gray-600">{repo.description}</p>
                  </div>
                  <div className="flex items-center space-x-2 text-sm text-gray-500">
                    <Star size={14} />
                    <span>{repo.stars}</span>
                  </div>
                </div>
                
                <div className="flex flex-wrap gap-1 mt-2">
                  {repo.languages.slice(0, 5).map((lang, langIndex) => (
                    <span
                      key={langIndex}
                      className="bg-gray-100 text-gray-700 px-2 py-1 rounded text-xs"
                    >
                      {lang}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Action Buttons */}
        <div className="grid md:grid-cols-2 gap-6">
          <div className="card text-center">
            <FileText className="w-16 h-16 text-primary-600 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-gray-900 mb-2">Create Resume</h3>
            <p className="text-gray-600 mb-6">
              Generate an ATS-friendly PDF resume with AI-powered bullet points
            </p>
            <button
              onClick={handleCreateResume}
              className="btn-primary w-full"
            >
              Create Resume
            </button>
          </div>
          
          <div className="card text-center">
            <Globe className="w-16 h-16 text-secondary-600 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-gray-900 mb-2">Generate Portfolio</h3>
            <p className="text-gray-600 mb-6">
              Create a complete Next.js portfolio website ready for deployment
            </p>
            <button
              onClick={handleCreatePortfolio}
              className="bg-gradient-to-r from-secondary-600 to-purple-600 text-white py-3 px-6 rounded-lg font-semibold hover:from-secondary-700 hover:to-purple-700 transition-all duration-200 w-full"
            >
              Generate Portfolio
            </button>
          </div>
        </div>
      </div>
    );
  };

  const tabs = [
    { id: 'import', label: 'Import Data', icon: Github },
    { id: 'results', label: 'Analysis Results', icon: TrendingUp }
  ];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="text-center mb-12">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">Dashboard</h1>
        <p className="text-xl text-gray-600">
          Analyze your GitHub repositories and create professional career assets
        </p>
      </div>

      {/* Tabs */}
      <div className="mb-8">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex justify-center space-x-8">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`py-4 px-6 border-b-2 font-medium text-sm flex items-center space-x-2 transition-colors ${
                  activeTab === tab.id
                    ? 'border-primary-500 text-primary-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <tab.icon size={18} />
                <span>{tab.label}</span>
              </button>
            ))}
          </nav>
        </div>
      </div>

      {/* Tab Content */}
      <div className="animate-fade-in">
        {activeTab === 'import' && renderImportTab()}
        {activeTab === 'results' && renderResultsTab()}
      </div>
    </div>
  );
};

export default DashboardPage;