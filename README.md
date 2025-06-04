# QuizForge

QuizForge is an AI-powered web application that allows users to upload textbook content and automatically generates quizzes. The application supports various question formats, adapts to different difficulty levels, and provides user authentication and quiz management.

## Features

- User registration, login, and JWT-based authentication
- Drag-and-drop file upload for textbooks (PDF, DOCX, TXT, JSON)
- File parsing and metadata management
- AI-powered quiz generation (OpenAI integration)
- Multiple question formats (multiple choice, true/false, short answer, etc.)
- Difficulty level selection
- Quiz CRUD operations (create, list, update, delete)
- User quiz history
- Caching for AI and analysis endpoints
- Pagination, rate limiting, and email support (if configured)

## Tech Stack

### Frontend
- Next.js 14 (App Router)
- React
- TypeScript
- Tailwind CSS
- Shadcn UI, Radix UI
- Zod (form validation)
- React Hook Form

### Backend
- FastAPI
- SQLAlchemy & Alembic (migrations)
- Python 3.12
- Pydantic
- FastAPI-Users (user management)
- FastAPI-JWT-Auth (authentication)
- FastAPI-Mail (email)
- FastAPI-Cache (caching)
- FastAPI-Limiter (rate limiting)
- FastAPI-Pagination (pagination)
- OpenAI (AI quiz generation)
- SQLite (default, with PostgreSQL support)

## Getting Started

### Prerequisites
- Docker and Docker Compose (recommended)
- Node.js (v18 or higher)
- Python 3.12
- npm or yarn
- Git

### Environment Variables

#### Backend (`backend/.env`)
```
DATABASE_URL=sqlite:///quizforge.db
SECRET_KEY=your-secret-key
OPENAI_API_KEY=your_openai_api_key_here
```

#### Frontend (`frontend/.env`)
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Setup

#### Option 1: Using Docker (Recommended)

```bash
git clone https://github.com/yourusername/quizforge.git
cd quizforge
docker-compose up -d
```
- Frontend: http://localhost:3000
- Backend: http://localhost:8000

To stop:
```bash
docker-compose down
```

#### Option 2: macOS Setup Script

```bash
chmod +x setup_mac.sh
./setup_mac.sh
```

#### Option 3: Manual Setup

##### Frontend
```bash
cd frontend
npm install
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env
npm run dev
```

##### Backend
```bash
cd backend
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # or create .env as above
uvicorn main:app --reload --port 8000
```

## Project Structure

```
quiz-app/
├── frontend/                  # Next.js frontend
│   ├── src/
│   │   ├── app/               # App router
│   │   ├── components/        # React components
│   │   └── lib/               # Utilities
│   ├── public/                # Static assets
│   ├── package.json
│   └── .env                   # Frontend env vars
├── backend/                   # FastAPI backend
│   ├── app/
│   │   ├── api/               # API endpoints
│   │   ├── core/              # Core config, db, cache
│   │   ├── models/            # SQLAlchemy models
│   │   └── schemas/           # Pydantic schemas
│   ├── requirements.txt
│   └── .env                   # Backend env vars
├── docker-compose.yml         # Docker Compose config
├── setup_mac.sh               # macOS setup script
└── README.md
```

## API Endpoints

### Auth
- `POST /register` — Register a new user (email, password, full_name)
- `POST /token` — Obtain JWT access token (OAuth2)
- `GET /me` — Get current user info (JWT required)

### Quiz
- `GET /api/quiz/` — List quizzes (pagination supported)
- `POST /api/quiz/` — Create a new quiz
- `GET /api/quiz/{quiz_id}` — Get quiz by ID
- `PUT /api/quiz/{quiz_id}` — Update quiz
- `DELETE /api/quiz/{quiz_id}` — Delete quiz

### AI
- `POST /api/ai/generate` — Generate quiz from content (content, num_questions, difficulty)
- `POST /api/ai/analyze` — Analyze content and extract key concepts

### Upload
- `POST /api/upload/` — Upload a file (PDF, TXT, etc.)
- `GET /api/upload/files` — List uploaded files (pagination)
- `GET /api/upload/{file_id}` — Get file metadata
- `GET /api/upload/{file_id}/download` — Download file
- `DELETE /api/upload/{file_id}` — Delete file
- `PATCH /api/upload/{file_id}` — Update file metadata (title, description)
- `GET /api/upload/parsed-contents` — List parsed contents

### Files
- `GET /api/files/` — List all parsed files
- `GET /api/files/{file_id}` — Get file metadata
- `GET /api/files/{file_id}/content` — Get parsed file content
- `DELETE /api/files/{file_id}` — Delete file

### Root
- `GET /` — Welcome message
- `GET /health` — Health check

## Database

- Default: SQLite (`backend/quizforge.db`)
- PostgreSQL supported (set `DATABASE_URL`)
- Alembic for migrations

## Running Tests

- **Backend:**
  ```bash
  cd backend
  source venv/bin/activate
  pytest
  ```
- **Frontend:**
  ```bash
  cd frontend
  npm test
  ```
- **Docker:**
  ```bash
  docker-compose run backend pytest
  docker-compose run frontend npm test
  ```

## Troubleshooting

- **Port in use:**
  ```bash
  lsof -i :3000  # frontend
  lsof -i :8000  # backend
  kill -9 <PID>
  ```
- **Node modules:**
  ```bash
  cd frontend
  rm -rf node_modules
  npm install
  ```
- **Python venv:**
  ```bash
  cd backend
  rm -rf venv
  python3.12 -m venv venv
  source venv/bin/activate
  pip install -r requirements.txt
  ```
- **Database:**
  ```bash
  cd backend
  rm quizforge.db
  # Will be recreated on next server start
  ```

## Contributing

1. Fork the repository
2. Create a new branch
3. Make your changes
4. Submit a pull request

## License

MIT License. See LICENSE file for details.