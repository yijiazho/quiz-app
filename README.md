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
- Next.js
- React
- TypeScript
- Tailwind CSS

### Backend
- FastAPI
- SQLAlchemy
- Python virtual environment
- Transformers (for AI/NLP)

## Getting Started

### Prerequisites
- Node.js (v18 or higher)
- Python (v3.10 or higher)
- npm or yarn

### Setup

#### Option 1: Using the QuizForge Launcher

##### Windows
The easiest way to run QuizForge on Windows is by using the launcher:

```
quizforge.bat
```

##### macOS/Linux
For macOS and Linux users, use the shell script:

```bash
./quizforge.sh
```

The launcher will open an interactive, color-coded menu with the following options:
1. Start both frontend and backend
2. Start backend only
3. Start frontend only
4. Install dependencies
5. Update dependencies
6. Run tests
7. Clean up (stop all servers)
0. Exit

The launcher will:
- Properly handle virtual environments
- Install and update dependencies as needed
- Start servers with the correct configurations
- Provide visual feedback and status information
- Automatically clean up resources when done

For first-time use, you should:
1. Select option 4 to install all dependencies
2. Then select option 1 to start both servers

#### Option 2: Manual Setup

##### Frontend Setup
1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the development server:
   ```bash
   npm run dev
   ```

##### Backend Setup
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create a virtual environment:
   ```bash
   python -m venv venv
   ```
3. Activate the virtual environment:
   - Windows:
     ```bash
     venv\Scripts\activate.bat
     ```
   - macOS/Linux:
     ```bash
     source venv/bin/activate
     ```
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Start the backend server:
   ```bash
   uvicorn main:app --reload --port 8000
   ```

## Environment Variables

Create a `.env` file in both the frontend and backend directories with the following variables:

### Frontend (.env)
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Backend (.env)
```
DATABASE_URL=postgresql://user:password@localhost:5432/quizforge
SECRET_KEY=your-secret-key

# OpenAI API Key (Required for AI features)
OPENAI_API_KEY=your_openai_api_key_here
```

## Development

### Running Tests
- Frontend tests:
  ```bash
  cd frontend
  npm test
  ```
- Backend tests:
  ```bash
  cd backend
  source venv/bin/activate  # or venv\Scripts\activate.bat on Windows
  pytest
  ```

### Code Style
- Frontend: ESLint and Prettier
- Backend: Black and isort

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
│   ├── tsconfig.json
│   ├── tailwind.config.js
│   └── postcss.config.js
├── backend/                   # Backend application
│   ├── app/
│   │   ├── api/               # API endpoints
│   │   ├── core/              # Core functionality
│   │   ├── models/            # Database models
│   │   └── services/          # Services
│   ├── main.py                # Main application entry point
│   ├── venv/                  # Python virtual environment
│   └── requirements.txt       # Python dependencies
├── quizforge.bat              # Interactive launcher script (Windows)
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

## Troubleshooting

### Backend Server Issues
- If you see `ModuleNotFoundError: No module named 'requests'` - use the QuizForge launcher to install dependencies or make sure to activate the virtual environment manually.
- The backend may take up to 10-15 seconds to fully initialize.
- If you see `Connection refused` errors, ensure:
  1. The Python virtual environment is properly activated
  2. The backend server is running at http://127.0.0.1:8000
  3. No firewall or antivirus is blocking the connection
- The frontend will automatically detect when the backend becomes available.

### Frontend Issues
- If you see package dependency errors, use the QuizForge launcher to install dependencies or run `npm install` in the frontend directory.
- The frontend application includes a built-in status indicator that will show when the backend is not connected.

## Testing

### Backend Tests
Run the test script to verify the API endpoints:
```
cd backend
venv\Scripts\activate.bat  # On Windows
python test_api_connection.py
```

Or simply use option 6 in the QuizForge launcher.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Running Tests

Tests should be run from the project root (`quiz-app`). For example:

```sh
python -m pytest backend/tests -v
```

This ensures that the `app` module is correctly importable.