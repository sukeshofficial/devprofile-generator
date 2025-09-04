/*
# DevProfile Database Schema

1. New Tables
   - `users` - User accounts with GitHub/LinkedIn integration
   - `repos` - Cached repository data with analysis results
   - `resumes` - Generated resumes with multiple formats
   - `shared_links` - Public shareable resume links

2. Security
   - Enable RLS on all tables
   - Add policies for authenticated users to access their own data
   - Public access for shared resume links

3. Features
   - UUID primary keys for security
   - JSONB for flexible data storage
   - Automatic timestamps
   - Cascade deletes for data consistency
*/

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Users table for authentication and profile data
CREATE TABLE IF NOT EXISTS users (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  github_id text UNIQUE,
  linkedin_id text UNIQUE,
  email text,
  name text,
  avatar_url text,
  github_username text,
  github_token_encrypted text, -- Note: encrypt in production
  linkedin_token_encrypted text, -- Note: encrypt in production
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

-- Repository data cache
CREATE TABLE IF NOT EXISTS repos (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid REFERENCES users(id) ON DELETE CASCADE,
  repo_name text NOT NULL,
  repo_full_name text NOT NULL,
  stars int DEFAULT 0,
  forks int DEFAULT 0,
  languages jsonb DEFAULT '[]'::jsonb,
  description text,
  readme text,
  html_url text,
  analysis_data jsonb DEFAULT '{}'::jsonb,
  fetched_at timestamptz DEFAULT now(),
  UNIQUE(user_id, repo_full_name)
);

-- Generated resumes
CREATE TABLE IF NOT EXISTS resumes (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid REFERENCES users(id) ON DELETE CASCADE,
  title text NOT NULL,
  json_resume jsonb NOT NULL,
  html text,
  pdf_url text,
  skills jsonb DEFAULT '[]'::jsonb,
  bullets jsonb DEFAULT '[]'::jsonb,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

-- Shared resume links
CREATE TABLE IF NOT EXISTS shared_links (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  resume_id uuid REFERENCES resumes(id) ON DELETE CASCADE,
  slug text UNIQUE NOT NULL,
  public boolean DEFAULT true,
  view_count int DEFAULT 0,
  expires_at timestamptz NULL,
  created_at timestamptz DEFAULT now()
);

-- Enable Row Level Security
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE repos ENABLE ROW LEVEL SECURITY;
ALTER TABLE resumes ENABLE ROW LEVEL SECURITY;
ALTER TABLE shared_links ENABLE ROW LEVEL SECURITY;

-- RLS Policies for users table
CREATE POLICY "Users can read own data"
  ON users
  FOR SELECT
  TO authenticated
  USING (auth.uid()::text = github_id OR auth.uid()::text = id::text);

CREATE POLICY "Users can update own data"
  ON users
  FOR UPDATE
  TO authenticated
  USING (auth.uid()::text = github_id OR auth.uid()::text = id::text);

CREATE POLICY "Users can insert own data"
  ON users
  FOR INSERT
  TO authenticated
  WITH CHECK (auth.uid()::text = github_id OR auth.uid()::text = id::text);

-- RLS Policies for repos table
CREATE POLICY "Users can read own repos"
  ON repos
  FOR SELECT
  TO authenticated
  USING (user_id IN (
    SELECT id FROM users WHERE auth.uid()::text = github_id OR auth.uid()::text = id::text
  ));

CREATE POLICY "Users can manage own repos"
  ON repos
  FOR ALL
  TO authenticated
  USING (user_id IN (
    SELECT id FROM users WHERE auth.uid()::text = github_id OR auth.uid()::text = id::text
  ));

-- RLS Policies for resumes table
CREATE POLICY "Users can read own resumes"
  ON resumes
  FOR SELECT
  TO authenticated
  USING (user_id IN (
    SELECT id FROM users WHERE auth.uid()::text = github_id OR auth.uid()::text = id::text
  ));

CREATE POLICY "Users can manage own resumes"
  ON resumes
  FOR ALL
  TO authenticated
  USING (user_id IN (
    SELECT id FROM users WHERE auth.uid()::text = github_id OR auth.uid()::text = id::text
  ));

-- RLS Policies for shared_links table
CREATE POLICY "Public can read public shared links"
  ON shared_links
  FOR SELECT
  TO anon, authenticated
  USING (public = true AND (expires_at IS NULL OR expires_at > now()));

CREATE POLICY "Users can manage own shared links"
  ON shared_links
  FOR ALL
  TO authenticated
  USING (resume_id IN (
    SELECT r.id FROM resumes r 
    JOIN users u ON r.user_id = u.id 
    WHERE auth.uid()::text = u.github_id OR auth.uid()::text = u.id::text
  ));

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_users_github_id ON users(github_id);
CREATE INDEX IF NOT EXISTS idx_repos_user_id ON repos(user_id);
CREATE INDEX IF NOT EXISTS idx_repos_fetched_at ON repos(fetched_at);
CREATE INDEX IF NOT EXISTS idx_resumes_user_id ON resumes(user_id);
CREATE INDEX IF NOT EXISTS idx_shared_links_slug ON shared_links(slug);
CREATE INDEX IF NOT EXISTS idx_shared_links_expires_at ON shared_links(expires_at);

-- Functions for automatic timestamp updates
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers for automatic timestamp updates
CREATE TRIGGER update_users_updated_at 
    BEFORE UPDATE ON users 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_resumes_updated_at 
    BEFORE UPDATE ON resumes 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();