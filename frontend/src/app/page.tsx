import FileUpload from '@/components/FileUpload'

export default function Home() {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h1 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            QuizForge
          </h1>
          <p className="mt-2 text-center text-sm text-gray-600">
            Upload your textbooks and let AI generate quizzes for you
          </p>
        </div>
        <FileUpload />
      </div>
    </div>
  )
} 