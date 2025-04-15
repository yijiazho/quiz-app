export default function Home() {
  return (
    <div className="container py-8">
      <h1 className="text-4xl font-bold mb-6">Welcome to QuizForge</h1>
      <p className="text-lg text-muted-foreground mb-4">
        Create and manage quizzes from your documents with ease.
      </p>
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        <div className="rounded-lg border p-4">
          <h2 className="text-xl font-semibold mb-2">Upload Documents</h2>
          <p className="text-muted-foreground">
            Upload your PDF, DOCX, TXT, or CSV files to create quizzes.
          </p>
        </div>
        <div className="rounded-lg border p-4">
          <h2 className="text-xl font-semibold mb-2">Generate Questions</h2>
          <p className="text-muted-foreground">
            Automatically generate quiz questions from your documents.
          </p>
        </div>
        <div className="rounded-lg border p-4">
          <h2 className="text-xl font-semibold mb-2">Manage Files</h2>
          <p className="text-muted-foreground">
            View and manage your uploaded documents and quizzes.
          </p>
        </div>
      </div>
    </div>
  )
} 