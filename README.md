# 💼 DevProfile Generator

An AI-powered web application that helps developers extract skills from their GitHub repositories, receive learning suggestions, match with relevant job roles, and create professional portfolios — now with full authentication, caching, and export capabilities!

---

## 🚀 Features

### 🔐 Authentication & User Management
- **JWT Authentication** - Secure user registration and login
- **GitHub OAuth** - One-click authentication with GitHub
- **User Profiles** - Save and manage your analyses
- **Session Management** - Persistent login sessions

### 📊 Advanced Analysis
- **Smart Skill Extraction** - AI-powered analysis of README files
- **Interactive Dashboard** - Visual charts and progress tracking
- **Skill Categorization** - Organized by programming languages, frameworks, databases, tools, and cloud services
- **Progress Bars** - Visual skill proficiency indicators

### 🎯 Career Development
- **Job Matching** - AI-powered job recommendations
- **Learning Suggestions** - Personalized skill improvement recommendations
- **YouTube Integration** - Curated learning resources
- **Company Insights** - Logo integration and company information

### 📱 Export & Portfolio
- **PDF Export** - Professional analysis reports
- **HTML Portfolio** - Static portfolio websites
- **React Portfolio** - Full React/Vite projects with charts
- **Shareable Links** - Public portfolio sharing

### ⚡ Performance & Caching
- **Redis Caching** - Fast GitHub API responses
- **AI Result Caching** - Reduced API costs and faster responses
- **Database Integration** - Supabase cloud database
- **Dark Mode** - Professional UI with theme switching

### 🎨 Enhanced UI/UX
- **Interactive Charts** - Radar charts and skill visualizations
- **Responsive Design** - Mobile-first approach
- **Dark Mode Toggle** - Professional theme switching
- **Loading States** - Smooth user experience

---

## 🛠️ Tech Stack

| Layer      | Tech                         |
|------------|------------------------------|
| Frontend   | HTML + Tailwind CSS + Chart.js |
| Backend    | Python, FastAPI              |
| Database   | Supabase (PostgreSQL)        |
| Caching    | Redis                        |
| Authentication | JWT + GitHub OAuth        |
| AI/LLM     | OpenRouter (GPT, LLaMA)      |
| Export     | ReportLab, React/Vite        |
| Templating | Jinja2                       |
| Extras     | YouTube embedding, Clearbit logos |

---

## 📁 Project Structure

```
devprofile-project/
│
├── main.py                     # FastAPI backend logic
├── requirements.txt            # Dependencies
│
├── templates/                  # Frontend UI templates (Jinja2 + Tailwind)
│   ├── index.html              # Home page with GitHub input form
│   ├── readmes.html            # Displays README file contents
│   ├── skills.html             # Shows extracted skills
│   ├── suggestions.html        # Skill gap suggestions + YouTube previews
│   └── jobmatch.html           # Matched job roles with company logos
│
└── README.md                   # You're reading it!
```

---

## ⚙️ Setup Instructions

### Prerequisites
- Python 3.8+
- Redis server
- Supabase account
- GitHub OAuth app (optional)

### 1. Clone the Repository
```bash
git clone https://github.com/sukeshofficial/devprofile-project.git
cd devprofile-project/backend
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set Up Database (Supabase)
1. Create a new project at [supabase.com](https://supabase.com)
2. Go to SQL Editor and run the schema from `setup_database.sql`
3. Get your project URL and anon key from Settings > API

### 5. Set Up Redis
```bash
# Install Redis (Ubuntu/Debian)
sudo apt-get install redis-server

# Install Redis (macOS)
brew install redis

# Start Redis
redis-server
```

### 6. Configure Environment Variables
Create a `.env` file in the backend directory:
```env
# API Keys
OPENROUTER_API_KEY=your_openrouter_api_key_here

# JWT Settings
SECRET_KEY=your_secret_key_change_in_production
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Database Settings
SUPABASE_URL=your_supabase_url_here
SUPABASE_KEY=your_supabase_anon_key_here

# Redis Settings
REDIS_URL=redis://localhost:6379

# GitHub OAuth (Optional)
GITHUB_CLIENT_ID=your_github_client_id_here
GITHUB_CLIENT_SECRET=your_github_client_secret_here

# App Settings
DEBUG=False
```

### 7. Run the Application
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 8. Visit the Application
Open your browser at: [http://localhost:8000](http://localhost:8000)

### 9. Set Up GitHub OAuth (Optional)
1. Go to GitHub Settings > Developer settings > OAuth Apps
2. Create a new OAuth App
3. Set Authorization callback URL to: `http://localhost:8000/auth/github/callback`
4. Add Client ID and Secret to your `.env` file

---

## 🔐 API Keys Required

| Service       | Usage                          | Key Name               |
|---------------|--------------------------------|------------------------|
| GitHub API    | Fetch profile & README files   | `token` (user provided)|
| OpenRouter    | Skill & job suggestions        | `OPENROUTER_API_KEY`   |
| YouTube Embed | Preview video suggestions      | (no API needed)        |

👉 Set `OPENROUTER_API_KEY` as an environment variable or directly in `main.py` for dev use.

---

## 📬 Author

Made by 
- [Sukesh](https://github.com/sukeshofficial)
- [Mahima](https://github.com/mahima-jayshri)    
- [Davidson](https://github.com/Davidson-T)    

Feel free to ⭐️ the repo if it helped you!
