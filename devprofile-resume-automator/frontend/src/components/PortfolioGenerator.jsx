/**
 * Portfolio Generator component for creating Next.js portfolio sites
 * 
 * Generates downloadable Next.js portfolio projects based on user
 * profile data and GitHub repositories.
 */

import React, { useState } from 'react';
import { Download, Globe, Code, Palette, Zap } from 'lucide-react';
import axios from 'axios';

const PortfolioGenerator = ({ profileData }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [generatedUrl, setGeneratedUrl] = useState('');

  const handleGeneratePortfolio = async () => {
    setLoading(true);
    setError('');

    try {
      const response = await axios.post(
        'http://localhost:8000/api/portfolio/generate',
        { profile: profileData },
        {
          responseType: 'blob',
          headers: {
            'Content-Type': 'application/json'
          }
        }
      );

      // Create download link
      const blob = new Blob([response.data], { type: 'application/zip' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `${profileData.name.replace(' ', '_')}_portfolio.zip`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);

      setGeneratedUrl(url);

    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to generate portfolio');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* Header */}
      <div className="text-center">
        <h2 className="text-3xl font-bold text-gray-900 mb-4">
          <Globe className="inline text-primary-600 mr-3" size={32} />
          Portfolio Generator
        </h2>
        <p className="text-xl text-gray-600">
          Create a professional Next.js portfolio website from your GitHub data
        </p>
      </div>

      {/* Features */}
      <div className="grid md:grid-cols-3 gap-6">
        <div className="card text-center">
          <div className="w-16 h-16 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full flex items-center justify-center mx-auto mb-4">
            <Code className="text-white" size={24} />
          </div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Next.js + TypeScript</h3>
          <p className="text-gray-600 text-sm">
            Modern React framework with TypeScript for type safety and performance
          </p>
        </div>

        <div className="card text-center">
          <div className="w-16 h-16 bg-gradient-to-r from-green-500 to-teal-500 rounded-full flex items-center justify-center mx-auto mb-4">
            <Palette className="text-white" size={24} />
          </div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Responsive Design</h3>
          <p className="text-gray-600 text-sm">
            Mobile-first design that looks great on all devices and screen sizes
          </p>
        </div>

        <div className="card text-center">
          <div className="w-16 h-16 bg-gradient-to-r from-orange-500 to-red-500 rounded-full flex items-center justify-center mx-auto mb-4">
            <Zap className="text-white" size={24} />
          </div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Deploy Ready</h3>
          <p className="text-gray-600 text-sm">
            Optimized for Vercel deployment with one-click setup and custom domain support
          </p>
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-700">{error}</p>
        </div>
      )}

      {/* Portfolio Preview */}
      <div className="card">
        <h3 className="text-xl font-semibold text-gray-900 mb-6">Portfolio Preview</h3>
        
        <div className="bg-gray-100 rounded-lg p-6 mb-6">
          <div className="bg-white rounded-lg shadow-lg overflow-hidden">
            {/* Mock browser header */}
            <div className="bg-gray-200 px-4 py-2 flex items-center space-x-2">
              <div className="flex space-x-1">
                <div className="w-3 h-3 bg-red-400 rounded-full"></div>
                <div className="w-3 h-3 bg-yellow-400 rounded-full"></div>
                <div className="w-3 h-3 bg-green-400 rounded-full"></div>
              </div>
              <div className="flex-1 bg-white rounded px-3 py-1 text-sm text-gray-600">
                {profileData.name.toLowerCase().replace(' ', '')}.vercel.app
              </div>
            </div>
            
            {/* Mock portfolio content */}
            <div className="p-8">
              <div className="text-center mb-8">
                <div className="w-24 h-24 bg-gradient-to-r from-primary-500 to-secondary-500 rounded-full mx-auto mb-4"></div>
                <h1 className="text-2xl font-bold text-gray-900 mb-2">
                  {profileData.name}
                </h1>
                <p className="text-gray-600">Full Stack Developer</p>
              </div>
              
              <div className="grid md:grid-cols-2 gap-6">
                <div className="bg-gray-50 rounded-lg p-4">
                  <h3 className="font-semibold text-gray-900 mb-2">About</h3>
                  <p className="text-gray-600 text-sm">
                    {profileData.summary || 'Passionate developer with experience in modern web technologies.'}
                  </p>
                </div>
                
                <div className="bg-gray-50 rounded-lg p-4">
                  <h3 className="font-semibold text-gray-900 mb-2">Skills</h3>
                  <div className="flex flex-wrap gap-1">
                    {profileData.skills.slice(0, 6).map((skill, index) => (
                      <span key={index} className="bg-primary-100 text-primary-800 text-xs px-2 py-1 rounded">
                        {skill}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* What's Included */}
        <div className="bg-blue-50 rounded-lg p-6 mb-6">
          <h4 className="font-semibold text-blue-900 mb-3">What's Included:</h4>
          <ul className="space-y-2 text-blue-800 text-sm">
            <li>• Complete Next.js 14 project with TypeScript</li>
            <li>• Responsive design with Tailwind CSS</li>
            <li>• About, Projects, and Contact pages</li>
            <li>• SEO-optimized with meta tags</li>
            <li>• Ready for Vercel deployment</li>
            <li>• GitHub integration and project showcase</li>
          </ul>
        </div>

        {/* Generate Button */}
        <div className="text-center">
          <button
            onClick={handleGeneratePortfolio}
            disabled={loading}
            className="btn-primary text-lg px-8 py-4"
          >
            {loading ? (
              <div className="flex items-center">
                <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-white mr-3"></div>
                Generating Portfolio...
              </div>
            ) : (
              <div className="flex items-center">
                <Download className="mr-3" size={24} />
                Generate Portfolio Zip
              </div>
            )}
          </button>
        </div>
      </div>

      {/* Deployment Instructions */}
      <div className="card">
        <h3 className="text-xl font-semibold text-gray-900 mb-4">Deployment Instructions</h3>
        
        <div className="space-y-6">
          <div>
            <h4 className="font-semibold text-gray-900 mb-2 flex items-center">
              <Zap className="text-primary-600 mr-2" size={18} />
              Quick Deploy to Vercel
            </h4>
            <div className="bg-gray-50 rounded-lg p-4">
              <code className="text-sm text-gray-700">
                # Extract the zip file<br/>
                unzip portfolio.zip<br/>
                cd portfolio<br/><br/>
                # Install dependencies<br/>
                npm install<br/><br/>
                # Deploy to Vercel<br/>
                npx vercel --prod
              </code>
            </div>
          </div>

          <div>
            <h4 className="font-semibold text-gray-900 mb-2">Local Development</h4>
            <div className="bg-gray-50 rounded-lg p-4">
              <code className="text-sm text-gray-700">
                npm run dev<br/>
                # Open http://localhost:3000
              </code>
            </div>
          </div>

          <div>
            <h4 className="font-semibold text-gray-900 mb-2">Customization</h4>
            <p className="text-gray-600 text-sm">
              The generated portfolio is fully customizable. Edit the pages in the <code>pages/</code> 
              directory, modify styles, add new sections, or integrate with a CMS.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PortfolioGenerator;