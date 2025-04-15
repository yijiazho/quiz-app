# Implementation Tickets – QuizForge

## Epic: Textbook Upload & Processing

### `UPLOAD-001` – File Upload UI (Frontend)
- Drag-and-drop file input
- Accept only PDF, DOCX, TXT
- Show upload progress

### `UPLOAD-002` – File Upload API (Backend)
- POST `/upload` endpoint
- Virus scan, size validation

### `UPLOAD-003` – Data Storage (Backend)
- Choose proper database to store the uploaded files
- Update the backend endpoint to store the file in the database
- Support extracting the file from the database

### `UPLOAD-004` – File Parser Service (Backend)
- Extract structured text from files
- Remove formatting noise
- Segment by chapters/sections

### `UPLOAD-005` – Parser Caching Service (Backend)
- Implement caching for parsed file content
- Use FastAPI cache with Redis or in-memory storage
- Cache invalidation on file updates/deletions
- Configure cache expiration policies
- Add cache status monitoring

---

## Epic: AI/NLP Quiz Generation

### `AI-001` – Concept & Topic Extraction
- Keyphrase extraction using NLP tools
- Handle long content

### `AI-002` – Question Generator (MCQ + T/F)
- Use transformer models
- Generate distractors
- Filter poor questions

### `AI-003` – Answer & Explanation Generator
- Generate correct answers and short explanations

---

## Epic: Quiz Interaction & Review

### `QUIZ-001` – Quiz Generation UI (Frontend)
- Select chapters/sections
- Choose number and type of questions

### `QUIZ-002` – Take Quiz UI (Frontend)
- Navigate through questions
- Submit answers

### `QUIZ-003` – Quiz Submit & Score (Backend)
- Compare answers
- Return score and correct answers

### `QUIZ-004` – Review Mode UI (Frontend)
- Highlight correct/incorrect
- Show explanations

---

## Epic: User Accounts & Auth

### `AUTH-001` – Signup/Login UI (Frontend)
- Email/password and OAuth

### `AUTH-002` – Auth API & JWT (Backend)
- JWT-based session handling

---

## Epic: Infrastructure & DevOps

### `INFRA-001` – Docker Setup
- Dockerfile for frontend, backend, NLP services

### `INFRA-002` – Deploy to Cloud
- Deploy backend + frontend
- HTTPS and domain config
