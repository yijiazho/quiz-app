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

#### Option 1: Using the QuizForge Launcher (Windows)
The easiest way to run QuizForge is by using the launcher:

```
quizforge.bat
```

This will open an interactive, color-coded menu with the following options:
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
   ```
   cd frontend
   ```
2. Install dependencies:
   ```
   npm install
   ```
3. Start the development server:
   ```
   npm run dev
   ```

##### Backend Setup
1. Navigate to the backend directory:
   ```
   cd backend
   ```
2. Create a virtual environment:
   ```
   python -m venv venv
   ```
3. Activate the virtual environment:
   - Windows:
     ```
     venv\Scripts\activate.bat
     ```
   - macOS/Linux:
     ```
     source venv/bin/activate
     ```
4. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
5. Start the development server:
   ```
   uvicorn main:app --reload --host 127.0.0.1 --port 8000
   ```

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
- `POST /api/upload`: Upload a file (PDF, DOCX, or TXT)
  - Request: Multipart form data with `file` field
  - Response: JSON with upload status and file information

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