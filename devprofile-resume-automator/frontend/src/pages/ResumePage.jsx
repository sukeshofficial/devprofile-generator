/**
 * Resume page for editing and generating resumes
 * 
 * Provides interface for editing resume content and generating
 * PDF exports with preview functionality.
 */

import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import ResumeEditor from '../components/ResumeEditor';
import ResumePreview from '../components/ResumePreview';
import { useAuth } from '../contexts/AuthContext';
import { FileText, Edit, Eye } from 'lucide-react';

const ResumePage = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [resumeData, setResumeData] = useState(null);
  const [activeView, setActiveView] = useState('edit');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!user) {
      navigate('/');
      return;
    }

    // Get imported data from navigation state
    const importedData = location.state?.importedData;
    if (importedData) {
      // Transform imported data to resume format
      const transformedData = transformImportedData(importedData);
      setResumeData(transformedData);
    } else {
      // Load default/empty resume data
      setResumeData(getDefaultResumeData());
    }
  }, [user, location.state, navigate]);

  const transformImportedData = (importedData) => {
    // Extract unique skills from all repositories
    const allSkills = importedData.skills.reduce((acc, repoSkills) => {
      return [...acc, ...repoSkills.skills, ...repoSkills.tools];
    }, []);
    const uniqueSkills = [...new Set(allSkills)];

    return {
      profile: {
        name: user.name || user.username,
        email: user.email || '',
        phone: '',
        location: '',
        github_url: `https://github.com/${user.username}`,
        linkedin_url: '',
        summary: `Experienced developer with expertise in ${uniqueSkills.slice(0, 3).join(', ')} and other modern technologies. Passionate about building scalable applications and contributing to open-source projects.`
      },
      skills: uniqueSkills,
      bullets: importedData.bullets || []
    };
  };

  const getDefaultResumeData = () => {
    return {
      profile: {
        name: user?.name || user?.username || '',
        email: user?.email || '',
        phone: '',
        location: '',
        github_url: user?.username ? `https://github.com/${user.username}` : '',
        linkedin_url: '',
        summary: ''
      },
      skills: [],
      bullets: []
    };
  };

  const handleSaveResume = (data) => {
    setResumeData(data);
    setActiveView('preview');
  };

  const handlePreviewResume = (data) => {
    setResumeData(data);
    setActiveView('preview');
  };

  if (!resumeData) {
    return (
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading resume data...</p>
        </div>
      </div>
    );
  }

  const views = [
    { id: 'edit', label: 'Edit Resume', icon: Edit },
    { id: 'preview', label: 'Preview & Export', icon: Eye }
  ];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="text-center mb-12">
        <h1 className="text-4xl font-bold text-gray-900 mb-4 flex items-center justify-center">
          <FileText className="text-primary-600 mr-3" size={36} />
          Resume Builder
        </h1>
        <p className="text-xl text-gray-600">
          Create and customize your professional resume
        </p>
      </div>

      {/* View Tabs */}
      <div className="mb-8">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex justify-center space-x-8">
            {views.map((view) => (
              <button
                key={view.id}
                onClick={() => setActiveView(view.id)}
                className={`py-4 px-6 border-b-2 font-medium text-sm flex items-center space-x-2 transition-colors ${
                  activeView === view.id
                    ? 'border-primary-500 text-primary-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <view.icon size={18} />
                <span>{view.label}</span>
              </button>
            ))}
          </nav>
        </div>
      </div>

      {/* Content */}
      <div className="animate-fade-in">
        {activeView === 'edit' && (
          <ResumeEditor
            initialData={resumeData}
            onSave={handleSaveResume}
            onPreview={handlePreviewResume}
          />
        )}
        
        {activeView === 'preview' && (
          <ResumePreview resumeData={resumeData} />
        )}
      </div>

      {/* Quick Actions */}
      {activeView === 'preview' && (
        <div className="mt-12 bg-gradient-to-r from-primary-600 to-secondary-600 rounded-2xl p-8 text-white">
          <div className="text-center mb-8">
            <h2 className="text-2xl font-bold mb-4">What's Next?</h2>
            <p className="text-blue-100">Your resume is ready! Here are some next steps:</p>
          </div>
          
          <div className="grid md:grid-cols-3 gap-6">
            <div className="text-center">
              <Globe className="w-12 h-12 mx-auto mb-4 text-blue-200" />
              <h3 className="font-semibold mb-2">Create Portfolio</h3>
              <p className="text-blue-100 text-sm mb-4">
                Generate a complete portfolio website
              </p>
              <button
                onClick={handleCreatePortfolio}
                className="bg-white text-primary-600 px-4 py-2 rounded-lg font-medium hover:bg-gray-100 transition-colors"
              >
                Generate Portfolio
              </button>
            </div>
            
            <div className="text-center">
              <TrendingUp className="w-12 h-12 mx-auto mb-4 text-blue-200" />
              <h3 className="font-semibold mb-2">Job Matching</h3>
              <p className="text-blue-100 text-sm mb-4">
                Find jobs that match your skills
              </p>
              <button className="bg-white text-primary-600 px-4 py-2 rounded-lg font-medium hover:bg-gray-100 transition-colors">
                Coming Soon
              </button>
            </div>
            
            <div className="text-center">
              <FileText className="w-12 h-12 mx-auto mb-4 text-blue-200" />
              <h3 className="font-semibold mb-2">Cover Letters</h3>
              <p className="text-blue-100 text-sm mb-4">
                Generate tailored cover letters
              </p>
              <button className="bg-white text-primary-600 px-4 py-2 rounded-lg font-medium hover:bg-gray-100 transition-colors">
                Coming Soon
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ResumePage;