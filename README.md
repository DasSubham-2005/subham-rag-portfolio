# Subham Das —  Portfolio

A modern, responsive personal portfolio built with React, Vite and FastAPI, featuring an integrated RAG-powered portfolio assistant.

## ✨ Features

- Responsive single-page portfolio
- Dark / light mode
- Projects, Skills, Experience, Education and Certificates
- Resume download
- Contact form with email notification
- Admin CMS for managing portfolio content
- Project and media management
- JWT-protected admin panel
- **Talk to Subham AI** — RAG-powered portfolio assistant
- API rate limiting for the public AI assistant

## 🤖 Talk to Subham AI

The assistant answers questions using information from the portfolio knowledge base.

### RAG Flow

```text
Visitor Question
       ↓
React / Vite
       ↓
FastAPI Backend
       ↓
Retrieve Portfolio Knowledge
       ↓
ChromaDB + all-MiniLM-L6-v2
       ↓
GPT-OSS-120B via Groq
       ↓
Grounded AI Answer
```

The detailed workflow diagram is available here:

![Portfolio RAG Workflow](docs/portfolio-rag-workflow.png)

## 🛠️ Tech Stack

### Frontend
- React
- Vite
- CSS
- Lucide React

### Backend
- Python
- FastAPI
- Uvicorn
- SQLAlchemy
- JWT Authentication
- SlowAPI

### AI / RAG
- ChromaDB
- Sentence Transformers
- all-MiniLM-L6-v2
- OpenAI GPT-OSS-120B via Groq

### Database
- SQLite for local development
- PostgreSQL-ready for production

### Email
- Gmail SMTP

## 📁 Project Structure

```text
subham-rag-portfolio/
├── assets/
├── backend/
│   ├── app/
│   ├── uploads/
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   ├── public/
│   └── package.json
├── docs/
│   └── portfolio-rag-workflow.png
├── README.md
├── .gitignore
├── start_backend.ps1
└── start_frontend.ps1
```

## ▶️ Run Locally

### Backend

```powershell
cd "C:\Users\rocky\OneDrive\Desktop\subham-rag-portfolio\backend"
.\venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload
```

Backend:

```text
http://127.0.0.1:8000
```

API docs:

```text
http://127.0.0.1:8000/docs
```

### Frontend

Open another terminal:

```powershell
cd "C:\Users\rocky\OneDrive\Desktop\subham-rag-portfolio\frontend"
npm run dev
```

Frontend:

```text
http://localhost:5173
```

## 🔐 Environment

Keep API keys, email credentials and other secrets inside `backend/.env`.

Never commit `.env` to GitHub.

## 👨‍💻 Author

**Subham Das**

AI/ML Engineer | Data Scientist | Data Analyst

GitHub: `DasSubham-2005`  
LinkedIn: `subham-das-a316422b`

---

**Built with AI, ML & curiosity.**
