# QuizForge

QuizForge is an AI-powered web application that allows users to upload textbook content and automatically generates quizzes. The application supports various question formats and adapts to different difficulty levels.

## Features

- Drag-and-drop file upload for textbooks
- Support for PDF, DOCX, and TXT formats
- AI-powered quiz generation
- Multiple question formats (multiple choice, true/false, short answer, etc.)
- Difficulty level selection
- User authentication and quiz history

## Tech Stack

### Frontend
- Next.js 14
- React
- TypeScript
- Tailwind CSS
- Shadcn UI

### Backend
- FastAPI
- SQLAlchemy
- Python 3.12
- Transformers (for AI/NLP)

## Getting Started

### Prerequisites
- Docker and Docker Compose (recommended)
- Node.js (v18 or higher) - only needed for local development
- Python 3.12 - only needed for local development
- npm or yarn - only needed for local development
- Git

### Setup

#### Option 1: Using Docker (Recommended)

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/quizforge.git
   cd quizforge
   ```

2. Create a `.env` file in the root directory:
   ```bash
   cp .env.example .env
   ```
   Then edit `.env` with your configuration:
   ```
   DATABASE_URL=sqlite:///quiz_app.db
   SECRET_KEY=your-secret-key
   OPENAI_API_KEY=your_openai_api_key_here
   ```

3. Start the application using Docker Compose:
   ```bash
   docker-compose up -d
   ```

   The application will be available at:
   - Frontend: http://localhost:3000
   - Backend: http://localhost:8000

4. To stop the application:
   ```bash
   docker-compose down
   ```

#### Option 2: Using the macOS Setup Script (Recommended for macOS)

1. Make the setup script executable:
   ```bash
   chmod +x setup_mac.sh
   ```

2. Run the setup script:
   ```bash
   ./setup_mac.sh
   ```

The script will:
- Install Homebrew if not present
- Install Python 3.12 if not present
- Install Node.js if not present
- Set up the backend virtual environment and dependencies
- Set up the frontend dependencies
- Create necessary .env files

#### Option 3: Manual Setup

##### Frontend Setup
1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Create a `.env` file:
   ```bash
   echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env
   ```

4. Start the development server:
   ```bash
   npm run dev
   ```
   The frontend will be available at http://localhost:3000

##### Backend Setup
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment:
   ```bash
   python3.12 -m venv venv
   ```

3. Activate the virtual environment:
   ```bash
   source venv/bin/activate
   ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Create a `.env` file:
   ```bash
   cp .env.example .env
   ```
   Then edit `.env` with your configuration:
   ```
   DATABASE_URL=sqlite:///quiz_app.db
   SECRET_KEY=your-secret-key
   OPENAI_API_KEY=your_openai_api_key_here
   ```

6. Start the backend server:
   ```bash
   uvicorn main:app --reload --port 8000
   ```
   The backend will be available at http://localhost:8000

## Development

### Running Tests
- Using Docker:
  ```bash
  docker-compose run backend pytest
  docker-compose run frontend npm test
  ```

- Local development:
  - Frontend tests:
    ```bash
    cd frontend
    npm test
    ```
  - Backend tests:
    ```bash
    cd backend
    source venv/bin/activate
    pytest
    ```

### Code Style
- Frontend: ESLint and Prettier
- Backend: Black and isort

## Troubleshooting

### Common Issues

1. **Docker Issues**
   ```bash
   # Rebuild containers
   docker-compose build --no-cache
   
   # View logs
   docker-compose logs -f
   
   # Restart containers
   docker-compose restart
   ```

2. **Port Already in Use**
   ```bash
   # Find process using port 3000 (frontend)
   lsof -i :3000
   # Find process using port 8000 (backend)
   lsof -i :8000
   # Kill the process
   kill -9 <PID>
   ```

3. **Node Modules Issues**
   ```bash
   cd frontend
   rm -rf node_modules
   npm install
   ```

4. **Python Virtual Environment Issues**
   ```bash
   cd backend
   rm -rf venv
   python3.12 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

5. **Database Issues**
   ```bash
   cd backend
   rm quiz_app.db
   # The database will be recreated on next server start
   ```

6. **macOS-specific Issues**
   - If you get permission errors when running scripts:
     ```bash
     chmod +x setup_mac.sh
     ```
   - If Python 3.12 installation fails:
     ```bash
     brew update
     brew install python@3.12
     ```
   - If you get SSL errors:
     ```bash
     /Applications/Python\ 3.12/Install\ Certificates.command
     ```

## Contributing

1. Fork the repository
2. Create a new branch
3. Make your changes
4. Submit a pull request

## Project Structure

```
quiz-app/
├── frontend/                  # Frontend application
│   ├── src/
│   │   ├── app/               # Next.js app router
│   │   ├── components/        # React components
│   │   └── lib/               # Utility functions
│   ├── public/                # Static assets
│   ├── package.json
│   └── .env                   # Frontend environment variables
├── backend/                   # Backend application
│   ├── app/
│   │   ├── api/              # API endpoints
│   │   ├── core/             # Core functionality
│   │   ├── models/           # Database models
│   │   └── schemas/          # Pydantic schemas
│   ├── requirements.txt
│   └── .env                  # Backend environment variables
├── docker/                    # Docker configuration files
│   ├── frontend/             # Frontend Dockerfile
│   └── backend/              # Backend Dockerfile
├── docker-compose.yml        # Docker Compose configuration
├── setup_mac.sh              # macOS setup script
└── README.md
```

## API Endpoints

### Root Endpoints
- `GET /`: Root endpoint that returns a welcome message
- `GET /health`: Health check endpoint

### Upload API
- `POST /api/upload`: Upload a file (PDF, DOCX, TXT, or JSON)
  - Request: Multipart form data with `file` field
  - Response: JSON with upload status and file information
- `GET /api/upload/files`: List all uploaded files
  - Optional query parameters: `skip` (default: 0), `limit` (default: 100)
  - Response: JSON with an array of file metadata
- `GET /api/upload/files/{file_id}`: Get metadata for a specific file
  - Response: JSON with file metadata (excluding binary content)
- `GET /api/upload/files/{file_id}/download`: Download a specific file
  - Response: File content with appropriate content type
- `DELETE /api/upload/files/{file_id}`: Delete a specific file
  - Response: JSON with deletion status

## Database Integration

QuizForge uses SQLite for storing uploaded files and their metadata. The database integration provides reliable storage with support for both reading and writing operations.

### Database Schema

The main table `uploaded_files` has the following schema:

```
uploaded_files:
- id (primary key, auto-increment)
- file_id (UUID, indexed for quick lookups)
- filename (string, NOT NULL)
- content_type (string, NOT NULL)
- file_size (integer, NOT NULL)
- file_content (BLOB, NOT NULL)
- upload_time (timestamp, default: current time)
- last_accessed (timestamp, nullable)
- title (string, nullable)
- description (text, nullable)
```

### Accessing the Database

#### Using SQLite CLI
```
cd backend
sqlite3 instance/app.db
.tables
SELECT * FROM uploaded_files;
```

#### Using DB Browser for SQLite
1. Download from https://sqlitebrowser.org/
2. Open the database file (located at `backend/instance/app.db`)

### Supported File Operations

- **Upload**: Store files directly in the database as binary blobs
- **List**: Retrieve a paginated list of all files with metadata
- **Metadata**: Get detailed information about a specific file
- **Download**: Retrieve a file's binary content from the database
- **Delete**: Remove a file and its metadata from the database

### Supported File Types

The system currently supports the following file types:
- PDF (`.pdf`)
- Microsoft Word (`.docx`, `.doc`) 
- Plain Text (`.txt`)
- JSON (`.json`)

### Testing Database Operations

You can test the database operations using the provided test script:

```
cd backend
python test_db_operations.py
```

This script performs comprehensive testing of all database operations including uploading, listing, downloading, and deleting files.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Running Tests

Tests should be run from the project root (`quiz-app`). For example:

```sh
python -m pytest backend/tests -v
```

This ensures that the `app` module is correctly importable.