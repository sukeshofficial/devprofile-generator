-- DevProfile Generator Database Schema for Supabase
-- Run this in your Supabase SQL editor

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    full_name VARCHAR(255),
    github_username VARCHAR(100),
    avatar_url TEXT,
    password_hash VARCHAR(255),
    role VARCHAR(20) DEFAULT 'user' CHECK (role IN ('user', 'admin')),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Analyses table
CREATE TABLE IF NOT EXISTS analyses (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    github_username VARCHAR(100) NOT NULL,
    selected_repos JSONB DEFAULT '[]',
    extracted_skills JSONB DEFAULT '[]',
    job_matches JSONB DEFAULT '[]',
    skill_suggestions JSONB DEFAULT '[]',
    is_public BOOLEAN DEFAULT false,
    public_link VARCHAR(255) UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Portfolio exports table
CREATE TABLE IF NOT EXISTS portfolio_exports (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    analysis_id UUID REFERENCES analyses(id) ON DELETE CASCADE,
    export_type VARCHAR(20) NOT NULL CHECK (export_type IN ('html', 'react', 'pdf')),
    export_url TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- User sessions table (for JWT token management)
CREATE TABLE IF NOT EXISTS user_sessions (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    token_hash VARCHAR(255) NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Skills table (for better skill management)
CREATE TABLE IF NOT EXISTS skills (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    category VARCHAR(50) NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- User skills table (many-to-many relationship)
CREATE TABLE IF NOT EXISTS user_skills (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    skill_id UUID REFERENCES skills(id) ON DELETE CASCADE,
    proficiency_level INTEGER DEFAULT 1 CHECK (proficiency_level BETWEEN 1 AND 5),
    years_experience DECIMAL(3,1),
    last_used TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, skill_id)
);

-- Job opportunities table
CREATE TABLE IF NOT EXISTS job_opportunities (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    company VARCHAR(255) NOT NULL,
    description TEXT,
    required_skills JSONB DEFAULT '[]',
    location VARCHAR(255),
    remote BOOLEAN DEFAULT false,
    salary_min INTEGER,
    salary_max INTEGER,
    experience_level VARCHAR(20) DEFAULT 'mid' CHECK (experience_level IN ('junior', 'mid', 'senior', 'lead')),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_github_username ON users(github_username);
CREATE INDEX IF NOT EXISTS idx_analyses_user_id ON analyses(user_id);
CREATE INDEX IF NOT EXISTS idx_analyses_github_username ON analyses(github_username);
CREATE INDEX IF NOT EXISTS idx_analyses_created_at ON analyses(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_portfolio_exports_user_id ON portfolio_exports(user_id);
CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id ON user_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_sessions_expires_at ON user_sessions(expires_at);
CREATE INDEX IF NOT EXISTS idx_skills_name ON skills(name);
CREATE INDEX IF NOT EXISTS idx_skills_category ON skills(category);
CREATE INDEX IF NOT EXISTS idx_user_skills_user_id ON user_skills(user_id);
CREATE INDEX IF NOT EXISTS idx_job_opportunities_company ON job_opportunities(company);
CREATE INDEX IF NOT EXISTS idx_job_opportunities_experience_level ON job_opportunities(experience_level);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_analyses_updated_at BEFORE UPDATE ON analyses
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_job_opportunities_updated_at BEFORE UPDATE ON job_opportunities
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert some sample skills
INSERT INTO skills (name, category, description) VALUES
('Python', 'programming_languages', 'High-level programming language'),
('JavaScript', 'programming_languages', 'Web programming language'),
('TypeScript', 'programming_languages', 'Typed superset of JavaScript'),
('React', 'frameworks', 'JavaScript library for building user interfaces'),
('Vue.js', 'frameworks', 'Progressive JavaScript framework'),
('Angular', 'frameworks', 'Platform for building mobile and desktop web applications'),
('Django', 'frameworks', 'High-level Python web framework'),
('Flask', 'frameworks', 'Lightweight Python web framework'),
('Express.js', 'frameworks', 'Web application framework for Node.js'),
('MySQL', 'databases', 'Open-source relational database management system'),
('PostgreSQL', 'databases', 'Advanced open-source relational database'),
('MongoDB', 'databases', 'NoSQL document database'),
('Redis', 'databases', 'In-memory data structure store'),
('Docker', 'tools', 'Containerization platform'),
('Kubernetes', 'tools', 'Container orchestration system'),
('Git', 'tools', 'Version control system'),
('AWS', 'cloud_services', 'Amazon Web Services cloud platform'),
('Azure', 'cloud_services', 'Microsoft cloud computing platform'),
('GCP', 'cloud_services', 'Google Cloud Platform')
ON CONFLICT (name) DO NOTHING;

-- Insert some sample job opportunities
INSERT INTO job_opportunities (title, company, description, required_skills, location, remote, salary_min, salary_max, experience_level) VALUES
('Full Stack Developer', 'TechCorp', 'Build and maintain web applications using modern technologies', '["Python", "JavaScript", "React", "PostgreSQL"]', 'San Francisco, CA', true, 80000, 120000, 'mid'),
('Backend Engineer', 'DataFlow Inc', 'Design and implement scalable backend systems', '["Python", "Django", "PostgreSQL", "Docker"]', 'New York, NY', true, 90000, 130000, 'senior'),
('Frontend Developer', 'WebCraft', 'Create beautiful and responsive user interfaces', '["JavaScript", "React", "TypeScript", "CSS"]', 'Austin, TX', false, 70000, 110000, 'mid'),
('DevOps Engineer', 'CloudScale', 'Manage infrastructure and deployment pipelines', '["Docker", "Kubernetes", "AWS", "Terraform"]', 'Seattle, WA', true, 100000, 150000, 'senior'),
('Data Scientist', 'AnalyticsPro', 'Analyze data and build machine learning models', '["Python", "R", "PostgreSQL", "Machine Learning"]', 'Boston, MA', true, 85000, 125000, 'mid')
ON CONFLICT DO NOTHING;
