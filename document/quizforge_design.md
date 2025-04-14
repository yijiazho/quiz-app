# Technical Design Document QuizForge

## Objective

Design a scalable, secure, and responsive web application that enables users to upload textbooks and generate quizzes powered by AI/NLP.

## High-Level System Architecture

```
Client (Browser/Mobile)
     │
     ▼
Frontend App (React.js)
     │
     ▼
Backend API Gateway (Node.js / FastAPI)
     ├────────────► File Processor (PDF/DOCX/Text Extractor)
     ├────────────► AI/NLP Engine (Quiz Generator Service)
     ├────────────► Auth Service (JWT/OAuth)
     ├────────────► Quiz Manager (CRUD, Results)
     └────────────► DB & Storage Layer
```

## Core Components

### 1. Frontend (React.js / Next.js)

- File Upload Module
- Quiz Builder UI
- Quiz Taker Interface
- Review Dashboard
- Auth Flow (Sign up/Login/Forgot Password)

### 2. Backend API Layer (FastAPI or Node.js/Express)

- Endpoints:
  - `POST /upload`
  - `POST /generate-quiz`
  - `GET /quiz/:id`
  - `POST /quiz/:id/submit`
  - `GET /user/history`

### 3. AI/NLP Engine (Python Microservice)

- Text Segmenter
- Concept Extractor
- Question Generator
- Answer Generator & Distractor Builder
- Quality Filter

### 4. File Processor Service

- Extract text from PDF, DOCX, TXT
- Clean formatting, remove footers/headers
- Identify structure (titles, sections)

### 5. Database Layer (PostgreSQL or MongoDB)

Tables:
- Users
- Documents
- Quizzes
- Results
- Logs

### 6. File & Asset Storage

- S3 or Firebase Storage
- Store textbooks and quiz exports

### 7. Authentication & Security

- JWT-based Auth or OAuth2
- Secure file uploads
- Rate limiting
- HTTPS, CORS, CSP headers

### 8. Deployment & Infrastructure

- Frontend: Vercel / Netlify / S3 + CloudFront
- Backend + AI: Dockerized services
- DB: RDS or MongoDB Atlas
- Storage: S3
- CI/CD: GitHub Actions
- Monitoring: Sentry, Prometheus, Grafana

## Data Flow Example

1. Upload textbook
2. Extract text
3. AI generates quiz
4. Display and take quiz
5. Submit and review
