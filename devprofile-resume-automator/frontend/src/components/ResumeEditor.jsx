/**
 * Resume Editor component for customizing resume content
 * 
 * Allows users to edit profile information, skills, and bullet points
 * before generating the final resume PDF.
 */

import React, { useState, useEffect } from 'react';
import { Edit3, Plus, Trash2, Save, Eye } from 'lucide-react';

const ResumeEditor = ({ initialData, onSave, onPreview }) => {
  const [profile, setProfile] = useState({
    name: '',
    email: '',
    phone: '',
    location: '',
    github_url: '',
    linkedin_url: '',
    summary: ''
  });
  
  const [skills, setSkills] = useState([]);
  const [bullets, setBullets] = useState([]);
  const [newSkill, setNewSkill] = useState('');
  const [editingBullet, setEditingBullet] = useState(null);

  useEffect(() => {
    if (initialData) {
      setProfile(prev => ({ ...prev, ...initialData.profile }));
      setSkills(initialData.skills || []);
      setBullets(initialData.bullets || []);
    }
  }, [initialData]);

  const handleProfileChange = (field, value) => {
    setProfile(prev => ({ ...prev, [field]: value }));
  };

  const handleAddSkill = () => {
    if (newSkill.trim() && !skills.includes(newSkill.trim())) {
      setSkills(prev => [...prev, newSkill.trim()]);
      setNewSkill('');
    }
  };

  const handleRemoveSkill = (skillToRemove) => {
    setSkills(prev => prev.filter(skill => skill !== skillToRemove));
  };

  const handleEditBullet = (index, field, value) => {
    setBullets(prev => prev.map((bullet, i) => 
      i === index ? { ...bullet, [field]: value } : bullet
    ));
  };

  const handleAddBullet = () => {
    const newBullet = {
      project: 'New Project',
      text: 'Describe your achievement here using STAR format',
      action: 'Action taken',
      tool: 'Technology used',
      result: 'Quantified result',
      tags: []
    };
    setBullets(prev => [...prev, newBullet]);
  };

  const handleRemoveBullet = (index) => {
    setBullets(prev => prev.filter((_, i) => i !== index));
  };

  const handleSave = () => {
    const resumeData = {
      profile,
      skills,
      bullets
    };
    onSave(resumeData);
  };

  const handlePreview = () => {
    const resumeData = {
      profile,
      skills,
      bullets
    };
    onPreview(resumeData);
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* Header */}
      <div className="text-center">
        <h2 className="text-3xl font-bold text-gray-900 mb-4">Edit Your Resume</h2>
        <p className="text-gray-600">Customize your profile, skills, and experience bullets</p>
      </div>

      {/* Profile Section */}
      <div className="card">
        <h3 className="text-xl font-semibold text-gray-900 mb-6 flex items-center">
          <Edit3 className="text-primary-600 mr-2" size={20} />
          Profile Information
        </h3>
        
        <div className="grid md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Full Name
            </label>
            <input
              type="text"
              value={profile.name}
              onChange={(e) => handleProfileChange('name', e.target.value)}
              className="input-field"
              placeholder="John Doe"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Email
            </label>
            <input
              type="email"
              value={profile.email}
              onChange={(e) => handleProfileChange('email', e.target.value)}
              className="input-field"
              placeholder="john@example.com"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Phone
            </label>
            <input
              type="tel"
              value={profile.phone}
              onChange={(e) => handleProfileChange('phone', e.target.value)}
              className="input-field"
              placeholder="+1 (555) 123-4567"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Location
            </label>
            <input
              type="text"
              value={profile.location}
              onChange={(e) => handleProfileChange('location', e.target.value)}
              className="input-field"
              placeholder="San Francisco, CA"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              GitHub URL
            </label>
            <input
              type="url"
              value={profile.github_url}
              onChange={(e) => handleProfileChange('github_url', e.target.value)}
              className="input-field"
              placeholder="https://github.com/username"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              LinkedIn URL
            </label>
            <input
              type="url"
              value={profile.linkedin_url}
              onChange={(e) => handleProfileChange('linkedin_url', e.target.value)}
              className="input-field"
              placeholder="https://linkedin.com/in/username"
            />
          </div>
        </div>
        
        <div className="mt-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Professional Summary
          </label>
          <textarea
            value={profile.summary}
            onChange={(e) => handleProfileChange('summary', e.target.value)}
            rows={4}
            className="input-field"
            placeholder="Write a brief professional summary highlighting your key strengths and experience..."
          />
        </div>
      </div>

      {/* Skills Section */}
      <div className="card">
        <h3 className="text-xl font-semibold text-gray-900 mb-6">Technical Skills</h3>
        
        <div className="flex gap-2 mb-4">
          <input
            type="text"
            value={newSkill}
            onChange={(e) => setNewSkill(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleAddSkill()}
            className="input-field flex-1"
            placeholder="Add a skill (e.g., React, Python, AWS)"
          />
          <button
            onClick={handleAddSkill}
            className="bg-primary-600 text-white px-4 py-3 rounded-lg hover:bg-primary-700 transition-colors"
          >
            <Plus size={20} />
          </button>
        </div>
        
        <div className="flex flex-wrap gap-2">
          {skills.map((skill, index) => (
            <div
              key={index}
              className="bg-primary-100 text-primary-800 px-3 py-2 rounded-full text-sm font-medium flex items-center"
            >
              <span>{skill}</span>
              <button
                onClick={() => handleRemoveSkill(skill)}
                className="ml-2 text-primary-600 hover:text-primary-800"
              >
                <Trash2 size={14} />
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* Bullets Section */}
      <div className="card">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-xl font-semibold text-gray-900">Experience Bullets</h3>
          <button
            onClick={handleAddBullet}
            className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors flex items-center"
          >
            <Plus className="mr-2" size={16} />
            Add Bullet
          </button>
        </div>
        
        <div className="space-y-4">
          {bullets.map((bullet, index) => (
            <div key={index} className="border border-gray-200 rounded-lg p-4">
              <div className="grid md:grid-cols-2 gap-4 mb-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Project
                  </label>
                  <input
                    type="text"
                    value={bullet.project}
                    onChange={(e) => handleEditBullet(index, 'project', e.target.value)}
                    className="input-field"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Tool/Technology
                  </label>
                  <input
                    type="text"
                    value={bullet.tool}
                    onChange={(e) => handleEditBullet(index, 'tool', e.target.value)}
                    className="input-field"
                  />
                </div>
              </div>
              
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Achievement Description (STAR format)
                </label>
                <textarea
                  value={bullet.text}
                  onChange={(e) => handleEditBullet(index, 'text', e.target.value)}
                  rows={3}
                  className="input-field"
                  placeholder="Describe what you did, how you did it, and the impact/result..."
                />
              </div>
              
              <div className="flex justify-between items-center">
                <div className="text-sm text-gray-500">
                  {bullet.text.length}/200 characters
                </div>
                <button
                  onClick={() => handleRemoveBullet(index)}
                  className="text-red-600 hover:text-red-800 transition-colors"
                >
                  <Trash2 size={16} />
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex justify-center space-x-4">
        <button
          onClick={handlePreview}
          className="btn-secondary flex items-center"
        >
          <Eye className="mr-2" size={20} />
          Preview Resume
        </button>
        
        <button
          onClick={handleSave}
          className="btn-primary flex items-center"
        >
          <Save className="mr-2" size={20} />
          Save & Continue
        </button>
      </div>
    </div>
  );
};

export default ResumeEditor;