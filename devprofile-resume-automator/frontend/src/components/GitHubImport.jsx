/**
 * GitHub Import component for repository selection and analysis
 * 
 * Handles GitHub authentication, repository fetching, and selection
 * for skill extraction and resume generation.
 */

import React, { useState } from 'react';
import { Github, Search, CheckCircle, AlertCircle } from 'lucide-react';
import axios from 'axios';

const GitHubImport = ({ onImportComplete }) => {
  const [username, setUsername] = useState('');
  const [loading, setLoading] = useState(false);
  const [repos, setRepos] = useState([]);
  const [selectedRepos, setSelectedRepos] = useState([]);
  const [error, setError] = useState('');
  const [step, setStep] = useState('input'); // input, repos, analyzing

  const handleFetchRepos = async (e) => {
    e.preventDefault();
    if (!username.trim()) return;

    setLoading(true);
    setError('');

    try {
      const response = await axios.get(
        `http://localhost:8000/api/github/user/${username}/repos?limit=10`
      );
      
      setRepos(response.data.repos);
      setStep('repos');
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to fetch repositories');
    } finally {
      setLoading(false);
    }
  };

  const handleRepoToggle = (repoName) => {
    setSelectedRepos(prev => 
      prev.includes(repoName)
        ? prev.filter(name => name !== repoName)
        : [...prev, repoName]
    );
  };

  const handleAnalyzeRepos = async () => {
    if (selectedRepos.length === 0) {
      setError('Please select at least one repository');
      return;
    }

    setLoading(true);
    setStep('analyzing');

    try {
      // Filter selected repositories
      const selectedRepoData = repos.filter(repo => 
        selectedRepos.includes(repo.name)
      );

      // Extract skills using AI
      const skillsResponse = await axios.post(
        'http://localhost:8000/api/ai/extract-skills',
        { repos: selectedRepoData }
      );

      // Generate bullets
      const bulletsResponse = await axios.post(
        'http://localhost:8000/api/ai/generate-bullets',
        {
          projects: selectedRepoData,
          context: { username }
        }
      );

      // Call completion callback
      onImportComplete({
        repos: selectedRepoData,
        skills: skillsResponse.data,
        bullets: bulletsResponse.data.bullets,
        username
      });

    } catch (err) {
      setError(err.response?.data?.detail || 'Analysis failed');
      setStep('repos');
    } finally {
      setLoading(false);
    }
  };

  const renderInputStep = () => (
    <div className="card max-w-md mx-auto">
      <div className="text-center mb-6">
        <div className="w-16 h-16 bg-gradient-to-r from-primary-500 to-secondary-500 rounded-full flex items-center justify-center mx-auto mb-4">
          <Github className="text-white" size={32} />
        </div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Import from GitHub</h2>
        <p className="text-gray-600">Enter your GitHub username to analyze your repositories</p>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
          <div className="flex items-center">
            <AlertCircle className="text-red-500 mr-2" size={20} />
            <p className="text-red-700">{error}</p>
          </div>
        </div>
      )}

      <form onSubmit={handleFetchRepos} className="space-y-4">
        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-2">
            GitHub Username
          </label>
          <input
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            placeholder="Enter your GitHub username"
            className="input-field"
            required
          />
        </div>

        <button
          type="submit"
          disabled={loading}
          className="btn-primary w-full"
        >
          {loading ? (
            <div className="flex items-center justify-center">
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
              Fetching Repositories...
            </div>
          ) : (
            <div className="flex items-center justify-center">
              <Search className="mr-2" size={20} />
              Fetch Repositories
            </div>
          )}
        </button>
      </form>
    </div>
  );

  const renderReposStep = () => (
    <div className="max-w-4xl mx-auto">
      <div className="text-center mb-8">
        <h2 className="text-3xl font-bold text-gray-900 mb-4">Select Repositories</h2>
        <p className="text-gray-600">Choose repositories to analyze for skill extraction</p>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
          <div className="flex items-center">
            <AlertCircle className="text-red-500 mr-2" size={20} />
            <p className="text-red-700">{error}</p>
          </div>
        </div>
      )}

      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4 mb-8">
        {repos.map((repo) => (
          <div
            key={repo.name}
            className={`border-2 rounded-lg p-4 cursor-pointer transition-all duration-200 ${
              selectedRepos.includes(repo.name)
                ? 'border-primary-500 bg-primary-50'
                : 'border-gray-200 hover:border-gray-300'
            }`}
            onClick={() => handleRepoToggle(repo.name)}
          >
            <div className="flex items-start justify-between mb-2">
              <h3 className="font-semibold text-gray-900">{repo.name}</h3>
              {selectedRepos.includes(repo.name) && (
                <CheckCircle className="text-primary-500" size={20} />
              )}
            </div>
            
            <p className="text-sm text-gray-600 mb-3">
              {repo.description || 'No description available'}
            </p>
            
            <div className="flex items-center justify-between text-xs text-gray-500">
              <div className="flex flex-wrap gap-1">
                {repo.languages.slice(0, 3).map((lang) => (
                  <span key={lang} className="bg-gray-100 px-2 py-1 rounded">
                    {lang}
                  </span>
                ))}
              </div>
              <div className="flex items-center space-x-2">
                <span>⭐ {repo.stars}</span>
                <span>🍴 {repo.forks}</span>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="text-center space-y-4">
        <p className="text-sm text-gray-600">
          Selected {selectedRepos.length} of {repos.length} repositories
        </p>
        
        <div className="flex justify-center space-x-4">
          <button
            onClick={() => setStep('input')}
            className="btn-secondary"
          >
            Back
          </button>
          
          <button
            onClick={handleAnalyzeRepos}
            disabled={selectedRepos.length === 0 || loading}
            className="btn-primary"
          >
            {loading ? (
              <div className="flex items-center">
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                Analyzing...
              </div>
            ) : (
              `Analyze ${selectedRepos.length} Repositories`
            )}
          </button>
        </div>
      </div>
    </div>
  );

  const renderAnalyzingStep = () => (
    <div className="card max-w-md mx-auto text-center">
      <div className="w-16 h-16 bg-gradient-to-r from-primary-500 to-secondary-500 rounded-full flex items-center justify-center mx-auto mb-6">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-white"></div>
      </div>
      
      <h2 className="text-2xl font-bold text-gray-900 mb-4">Analyzing Repositories</h2>
      <p className="text-gray-600 mb-6">
        Our AI is extracting skills and generating resume bullets from your selected repositories.
        This may take a few moments.
      </p>
      
      <div className="space-y-2 text-sm text-gray-500">
        <div className="flex items-center justify-center">
          <CheckCircle className="text-green-500 mr-2" size={16} />
          <span>Fetching repository content</span>
        </div>
        <div className="flex items-center justify-center">
          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-primary-500 mr-2"></div>
          <span>Extracting technical skills</span>
        </div>
        <div className="flex items-center justify-center text-gray-400">
          <div className="w-4 h-4 border-2 border-gray-300 rounded-full mr-2"></div>
          <span>Generating resume bullets</span>
        </div>
      </div>
    </div>
  );

  return (
    <div className="py-12">
      {step === 'input' && renderInputStep()}
      {step === 'repos' && renderReposStep()}
      {step === 'analyzing' && renderAnalyzingStep()}
    </div>
  );
};

export default GitHubImport;