# 💼 DevProfile Generator

An AI-powered web application that helps developers extract skills from their GitHub repositories, receive learning suggestions, match with relevant job roles, and download a LaTeX-based resume — all without writing a single line of JavaScript!

---

## 🚀 Features

- 🔐 GitHub profile integration via token
- 📊 Skill extraction from selected repository README files
- 📚 Missing skill suggestions with real YouTube previews
- 🧠 Job role matching based on skills
- 📄 Resume generation using LaTeX (coming soon)
- 🖥️ Pure HTML + Tailwind CSS frontend (No JavaScript)

---

## 🛠️ Tech Stack

| Layer      | Tech                         |
|------------|------------------------------|
| Frontend   | HTML + Tailwind CSS          |
| Backend    | Python, FastAPI              |
| AI/LLM     | OpenRouter (GPT, LLaMA)      |
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

1. **Clone the repo**
   ```bash
   git clone https://github.com/sukeshofficial/devprofile-project.git
   cd devprofile-project
   ```

2. **Create virtual environment (optional but recommended)**
   ```bash
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the FastAPI server**
   ```bash
   uvicorn main:app --reload
   ```

5. **Visit the app**
   Open your browser at: [http://127.0.0.1:8000](http://127.0.0.1:8000)

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
