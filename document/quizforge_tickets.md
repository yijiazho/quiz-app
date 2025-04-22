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

### `AI-001` – Integrated Quiz Generation After Upload
- Automatically generate quiz after file is uploaded and parsed
- Direct integration with local model (e.g., T5, BART)
- Avoid using external APIs
- Save generated quiz to database

### `AI-002` – Local Model Setup for NLP
- Set up and run transformer models locally (T5/BART) using Hugging Face
- Ensure models can run offline once downloaded
- Optimize for CPU or GPU as available

### `AI-003` – Save Parsed Text for Reuse
- Store parsed textbook content in a separate database/table
- Reference it with file/document ID
- Use this as the source for quiz regeneration or review

### `AI-004` – Quiz Generation Endpoint Refactor
- Update quiz generation service to work from parsed text directly
- Support JSON output format
- Handle various question types (MCQ, True/False)

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
