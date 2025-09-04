# 💼 DevProfile Resume & Portfolio Automator

An AI-powered MVP that automatically creates ATS-friendly resumes and developer portfolios from GitHub + LinkedIn data, using OpenRouter LLMs for skill extraction and STAR bullet generation.

## 🚀 Features

- 🔐 GitHub & LinkedIn OAuth integration
- 📊 AI-powered skill extraction from repositories
- 🎯 Job matching with gap analysis
- 📝 STAR-format bullet generation
- 📄 PDF resume export (ATS-friendly)
- 🌐 Shareable resume links
- 💼 Next.js portfolio generator
- 🧪 Comprehensive test suite

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| Frontend | React + TailwindCSS (Vite) |
| Backend | Python + FastAPI |
| AI/LLM | OpenRouter-compatible models |
| Database | Supabase (PostgreSQL) |
| PDF Export | WeasyPrint |
| Auth | GitHub OAuth + LinkedIn OAuth |
| Testing | pytest + pytest-asyncio |
| CI/CD | GitHub Actions |

## 📁 Project Structure

```
devprofile-resume-automator/
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI application
│   │   ├── api/                    # API route handlers
│   │   ├── services/               # Business logic services
│   │   ├── db/                     # Database schema
│   │   ├── utils/                  # Utilities and prompts
│   │   └── templates/              # HTML templates
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/             # React components
│   │   ├── pages/                  # Page components
│   │   └── App.jsx                 # Main app component
│   └── package.json
├── .github/workflows/              # CI/CD workflows
└── README.md
```

## ⚙️ Setup Instructions

### Prerequisites

- Python 3.9+
- Node.js 18+
- Supabase account
- OpenRouter API key
- GitHub OAuth app
- LinkedIn OAuth app (optional)

### 1. Clone and Setup

```bash
git clone <repository-url>
cd devprofile-resume-automator
```

### 2. Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Environment Configuration

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

Required environment variables:
- `SUPABASE_URL` and `SUPABASE_ANON_KEY`
- `OPENROUTER_API_KEY`
- `GITHUB_CLIENT_ID` and `GITHUB_CLIENT_SECRET`
- `JWT_SECRET`

### 4. Database Setup

1. Create a new Supabase project
2. Run the schema in Supabase SQL editor:
   ```bash
   cat backend/app/db/schema.sql
   ```

### 5. OAuth Setup

#### GitHub OAuth App
1. Go to GitHub Settings → Developer settings → OAuth Apps
2. Create new OAuth App with:
   - Authorization callback URL: `http://localhost:8000/api/auth/github/callback`

#### LinkedIn OAuth App (Optional)
1. Go to LinkedIn Developer Portal
2. Create new app with:
   - Redirect URL: `http://localhost:8000/api/auth/linkedin/callback`

### 6. Run Backend

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 7. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

## 🧪 Testing

### Run Backend Tests
```bash
cd backend
pytest -v
```

### Run Frontend Tests
```bash
cd frontend
npm test
```

## 🚀 Deployment

### Backend (Railway/Render)

1. **Railway**:
   ```bash
   railway login
   railway init
   railway add
   railway deploy
   ```

2. **Render**:
   - Connect GitHub repository
   - Set build command: `pip install -r requirements.txt`
   - Set start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Frontend (Vercel)

```bash
cd frontend
vercel --prod
```

## 📖 API Documentation

### Health Check
```bash
curl http://localhost:8000/health
```

### GitHub Import
```bash
curl "http://localhost:8000/api/github/user/octocat/repos?limit=5"
```

### Skill Extraction
```bash
curl -X POST http://localhost:8000/api/ai/extract-skills \
  -H "Content-Type: application/json" \
  -d '{"repos": [...]}'
```

### Generate Resume PDF
```bash
curl -X POST http://localhost:8000/api/resume/pdf \
  -H "Content-Type: application/json" \
  -d '{"profile": {...}, "bullets": [...]}' \
  --output resume.pdf
```

## 🎯 Manual Testing Scenarios

1. **GitHub Import**: Enter username → see top 5 repos with README snippets
2. **Skill Analysis**: Click "Analyze Skills" → view extracted skills and tools
3. **Job Matching**: Paste job description → see match score and gaps
4. **Bullet Generation**: Generate bullets → see 6-8 STAR-format bullets
5. **PDF Export**: Export PDF → download ATS-friendly resume
6. **Share Resume**: Create shareable link → public URL serves resume

## 🔧 Development

### Adding New AI Prompts

1. Add prompt template to `backend/app/utils/prompts.py`
2. Update OpenRouter client in `backend/app/services/openrouter_client.py`
3. Add corresponding API route
4. Write tests

### Database Migrations

Run new SQL migrations in Supabase SQL editor or use migration tools.

## 📝 License

MIT License - see LICENSE file for details.

## 👥 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open Pull Request

## 🆘 Troubleshooting

### Common Issues

1. **OAuth Callback Errors**: Verify callback URLs match exactly
2. **PDF Generation Fails**: Ensure WeasyPrint dependencies are installed
3. **OpenRouter API Errors**: Check API key and rate limits
4. **Database Connection**: Verify Supabase credentials and network access

### Support

- Check GitHub Issues for known problems
- Review API documentation for endpoint details
- Verify environment variables are set correctly