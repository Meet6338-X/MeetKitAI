# Full-Stack React + FastAPI Template

> Production-ready web application template with React frontend and FastAPI backend.

## Quick Start

```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

## Structure

```
fullstack-react-fastapi/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── hooks/
│   │   ├── services/
│   │   ├── store/
│   │   └── App.jsx
│   ├── package.json
│   └── vite.config.js
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── core/
│   │   └── main.py
│   ├── tests/
│   └── requirements.txt
├── docker-compose.yml
├── .env.example
└── README.md
```

## Features

- ⚛️ React 18 with Vite
- 🚀 FastAPI with async support
- 🗄️ PostgreSQL database
- 🔐 JWT authentication
- 🐳 Docker & Docker Compose
- 📝 API documentation (Swagger/OpenAPI)
- 🧪 Testing setup (pytest, vitest)
- 🔄 Hot reload development

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | React, Vite, TailwindCSS |
| Backend | FastAPI, SQLAlchemy, Pydantic |
| Database | PostgreSQL |
| Auth | JWT, OAuth2 |
| DevOps | Docker, GitHub Actions |
