/**
 * Resume Preview component for displaying formatted resume
 * 
 * Shows a preview of the generated resume with options to download PDF,
 * share publicly, or export in different formats.
 */

import React, { useState } from 'react';
import { Download, Share2, FileText, ExternalLink, Copy, Check } from 'lucide-react';
import axios from 'axios';

const ResumePreview = ({ resumeData }) => {
  const [loading, setLoading] = useState(false);
  const [shareUrl, setShareUrl] = useState('');
  const [copied, setCopied] = useState(false);
  const [error, setError] = useState('');

  const handleDownloadPDF = async () => {
    setLoading(true);
    setError('');

    try {
      const response = await axios.post(
        'http://localhost:8000/api/resume/pdf',
        resumeData,
        {
          responseType: 'blob',
          headers: {
            'Content-Type': 'application/json'
          }
        }
      );

      // Create download link
      const blob = new Blob([response.data], { type: 'application/pdf' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `${resumeData.profile.name.replace(' ', '_')}_resume.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);

    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to generate PDF');
    } finally {
      setLoading(false);
    }
  };

  const handleShareResume = async () => {
    setLoading(true);
    setError('');

    try {
      const response = await axios.post(
        'http://localhost:8000/api/resume/share',
        resumeData
      );

      setShareUrl(response.data.url);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create shareable link');
    } finally {
      setLoading(false);
    }
  };

  const handleCopyUrl = async () => {
    try {
      await navigator.clipboard.writeText(shareUrl);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy URL');
    }
  };

  const handleDownloadJSON = async () => {
    try {
      const response = await axios.post(
        'http://localhost:8000/api/resume/json',
        resumeData
      );

      const blob = new Blob([JSON.stringify(response.data, null, 2)], { 
        type: 'application/json' 
      });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `${resumeData.profile.name.replace(' ', '_')}_resume.json`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);

    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to generate JSON');
    }
  };

  // Group bullets by project
  const projectGroups = resumeData.bullets.reduce((groups, bullet) => {
    const project = bullet.project || 'Other';
    if (!groups[project]) {
      groups[project] = [];
    }
    groups[project].push(bullet);
    return groups;
  }, {});

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* Header */}
      <div className="text-center">
        <h2 className="text-3xl font-bold text-gray-900 mb-4">Resume Preview</h2>
        <p className="text-gray-600">Review your resume and export when ready</p>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-700">{error}</p>
        </div>
      )}

      {/* Action Buttons */}
      <div className="flex flex-wrap justify-center gap-4">
        <button
          onClick={handleDownloadPDF}
          disabled={loading}
          className="btn-primary flex items-center"
        >
          {loading ? (
            <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
          ) : (
            <Download className="mr-2" size={20} />
          )}
          Download PDF
        </button>

        <button
          onClick={handleDownloadJSON}
          className="btn-secondary flex items-center"
        >
          <FileText className="mr-2" size={20} />
          Export JSON
        </button>

        <button
          onClick={handleShareResume}
          disabled={loading}
          className="bg-green-600 text-white py-3 px-6 rounded-lg font-semibold hover:bg-green-700 transition-colors flex items-center"
        >
          <Share2 className="mr-2" size={20} />
          Create Share Link
        </button>
      </div>

      {/* Share URL */}
      {shareUrl && (
        <div className="card bg-green-50 border border-green-200">
          <h3 className="text-lg font-semibold text-green-900 mb-4">Shareable Resume Link</h3>
          <div className="flex items-center space-x-2">
            <input
              type="text"
              value={shareUrl}
              readOnly
              className="input-field flex-1 bg-white"
            />
            <button
              onClick={handleCopyUrl}
              className="bg-green-600 text-white px-4 py-3 rounded-lg hover:bg-green-700 transition-colors flex items-center"
            >
              {copied ? <Check size={20} /> : <Copy size={20} />}
            </button>
            <a
              href={shareUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="bg-blue-600 text-white px-4 py-3 rounded-lg hover:bg-blue-700 transition-colors"
            >
              <ExternalLink size={20} />
            </a>
          </div>
          <p className="text-sm text-green-700 mt-2">
            This link can be shared publicly and will remain active for 30 days.
          </p>
        </div>
      )}

      {/* Resume Preview */}
      <div className="card bg-white shadow-2xl">
        <div className="max-w-none">
          {/* Header */}
          <div className="text-center border-b-2 border-gray-800 pb-4 mb-6">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              {resumeData.profile.name}
            </h1>
            <div className="text-gray-600 space-x-2">
              {resumeData.profile.email && <span>{resumeData.profile.email}</span>}
              {resumeData.profile.phone && <span>| {resumeData.profile.phone}</span>}
              {resumeData.profile.location && <span>| {resumeData.profile.location}</span>}
              {resumeData.profile.github_url && <span>| {resumeData.profile.github_url}</span>}
            </div>
          </div>

          {/* Summary */}
          {resumeData.profile.summary && (
            <div className="mb-6">
              <h2 className="text-lg font-bold text-gray-900 mb-3 uppercase border-b border-gray-800">
                Professional Summary
              </h2>
              <p className="text-gray-700 leading-relaxed">
                {resumeData.profile.summary}
              </p>
            </div>
          )}

          {/* Skills */}
          {resumeData.skills.length > 0 && (
            <div className="mb-6">
              <h2 className="text-lg font-bold text-gray-900 mb-3 uppercase border-b border-gray-800">
                Technical Skills
              </h2>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                {resumeData.skills.map((skill, index) => (
                  <div key={index} className="text-gray-700">
                    {skill}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Projects & Experience */}
          {Object.keys(projectGroups).length > 0 && (
            <div className="mb-6">
              <h2 className="text-lg font-bold text-gray-900 mb-3 uppercase border-b border-gray-800">
                Projects & Experience
              </h2>
              {Object.entries(projectGroups).map(([projectName, projectBullets]) => (
                <div key={projectName} className="mb-4">
                  <h3 className="text-base font-bold text-gray-900 mb-2">
                    {projectName}
                  </h3>
                  <ul className="space-y-1">
                    {projectBullets.map((bullet, index) => (
                      <li key={index} className="text-gray-700 ml-4 relative">
                        <span className="absolute -ml-4">•</span>
                        {bullet.text}
                      </li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Tips */}
      <div className="bg-blue-50 border border-blue-200 rounded-xl p-6">
        <h3 className="text-lg font-semibold text-blue-900 mb-3">
          Resume Tips
        </h3>
        <ul className="space-y-2 text-blue-800 text-sm">
          <li>• Keep your resume to one page for most positions</li>
          <li>• Use action verbs and quantify results when possible</li>
          <li>• Tailor your skills and bullets to match job descriptions</li>
          <li>• Use ATS-friendly formatting (avoid graphics and complex layouts)</li>
        </ul>
      </div>
    </div>
  );
};

export default ResumePreview;