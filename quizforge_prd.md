# Product Requirements Document (PRD)

## Product Name: QuizForge *(working title)*

### 1. Overview

**Purpose:**  
QuizForge is an AI-powered web application that allows users to upload textbook content and automatically generates quizzes to help with studying, reviewing, or teaching. The app supports various question formats and adapts to different levels of difficulty.

**Target Users:**  
- Students (middle school to university)  
- Teachers and tutors  
- Self-learners  
- Educational content creators

**Goals:**  
- Simplify the process of studying textbooks  
- Provide high-quality, auto-generated quizzes from any text  
- Help users retain knowledge more effectively

### 2. Key Features

#### 2.1. Content Ingestion
- File upload: Accepts PDF, DOCX, TXT
- Text input: Paste content directly
- Automatic content parsing:
  - Detects headings, subheadings, paragraphs
  - Segments content into logical sections

#### 2.2. Quiz Generation
- Question types:
  - Multiple Choice
  - True/False
  - Short Answer
  - Fill-in-the-Blank
- Customization:
  - Choose number of questions
  - Select difficulty: Easy, Medium, Hard
  - Select specific chapters or topics
- AI-generated answer key with explanations

#### 2.3. AI/NLP Engine
- Key concept extraction
- Sentence classification and transformation into questions
- Distractor generation for MCQs
- Bloom’s taxonomy-based difficulty scaling

#### 2.4. Quiz Interaction & Review
- Take quizzes in-app
- Real-time feedback or summary feedback mode
- Review mode:
  - Correct/incorrect indicators
  - Explanations and reference to original content

#### 2.5. User Features
- User accounts (signup/login)
- Quiz history and progress tracking
- Save/export quizzes as PDF or shareable links

#### 2.6. Admin Dashboard *(optional MVP feature)*
- Review/edit auto-generated quizzes
- Manage flagged questions
- Create reusable quizzes for class distribution

### 3. User Flows

1. Upload Flow: Upload File → Process Text → View Chapters → Generate Quiz  
2. Quiz Flow: Generate Quiz → Take Quiz → Submit → View Score → Review Answers  
3. Custom Flow: Select Topics/Chapters → Choose Type/Difficulty → Generate Quiz

### 4. Technical Requirements

#### Frontend:
- React.js or Vue.js
- Responsive UI (mobile-first)
- Quiz components with timers, scores, navigation

#### Backend:
- Node.js / Python (Flask or FastAPI)
- REST API for quiz generation, file processing, auth
- AI/NLP module integration (Hugging Face transformers, spaCy)

#### AI/NLP Stack:
- Pre-trained language models for:
  - Topic/keyphrase extraction
  - Question generation
  - Answer and distractor generation

#### Database:
- PostgreSQL or MongoDB
- Stores user data, files, quizzes, and scores

#### File Storage:
- AWS S3 or Firebase Storage

### 5. Non-Functional Requirements

- **Performance:** Quiz generation in < 10 seconds
- **Scalability:** Handle large files and 10k+ users
- **Security:** File scanning, data encryption, OAuth
- **Accessibility:** WCAG-compliant design

### 6. Milestones & Timeline (MVP)

| Phase | Milestone                             | Duration |
|-------|----------------------------------------|----------|
| 1     | Requirements Finalization              | 1 week   |
| 2     | UI/UX Design                           | 2 weeks  |
| 3     | Backend & AI Model Prototyping         | 3 weeks  |
| 4     | Frontend Implementation                | 3 weeks  |
| 5     | Integration & Testing                  | 2 weeks  |
| 6     | Beta Launch                            | 1 week   |

### 7. Future Enhancements

- Flashcard mode from generated content
- Voice input & audio-based quizzes
- Multilingual quiz support
- Gamified learning leaderboard
- Classroom integration (Google Classroom, LMS APIs)
