'use client'

import { useState } from 'react'
import { FileUpload } from '@/components/ui/file-upload'
import { Button } from '@/components/ui/button'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { AlertCircle, CheckCircle2 } from 'lucide-react'
import { Progress } from '@/components/ui/progress'

export default function UploadPage() {
  const [files, setFiles] = useState<File[]>([])
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)

  const handleFileSelect = (selectedFiles: File[]) => {
    setFiles(selectedFiles)
    setError(null)
    setSuccess(false)
    setUploadProgress(0)
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (files.length === 0) {
      setError('Please select a file to upload')
      return
    }

    setUploading(true)
    setError(null)
    setUploadProgress(0)

    const formData = new FormData()
    formData.append('file', files[0])

    // Create a promise wrapper around XMLHttpRequest
    const uploadFile = () => {
      return new Promise((resolve, reject) => {
        const xhr = new XMLHttpRequest()
        
        xhr.upload.addEventListener('progress', (event) => {
          if (event.lengthComputable) {
            const progress = Math.round((event.loaded * 100) / event.total)
            console.log(`Upload progress: ${progress}%`)
            setUploadProgress(progress)
          }
        })

        xhr.addEventListener('load', () => {
          console.log(`Upload completed with status: ${xhr.status}`)
          if (xhr.status >= 200 && xhr.status < 300) {
            try {
              const response = JSON.parse(xhr.responseText)
              console.log('Upload response:', response)
              resolve(response)
            } catch (err) {
              console.error('Error parsing response:', err)
              reject(new Error('Invalid server response'))
            }
          } else {
            console.error('Upload failed with status:', xhr.status)
            let errorMessage = 'Failed to upload file'
            try {
              const errorResponse = JSON.parse(xhr.responseText)
              errorMessage = errorResponse.detail || errorMessage
            } catch (e) {
              console.error('Error parsing error response:', e)
            }
            reject(new Error(errorMessage))
          }
        })

        xhr.addEventListener('error', () => {
          console.error('Upload network error')
          reject(new Error('Network error occurred'))
        })

        xhr.addEventListener('abort', () => {
          console.error('Upload aborted')
          reject(new Error('Upload was aborted'))
        })

        console.log('Starting upload for file:', files[0].name)
        xhr.open('POST', 'http://localhost:8000/api/upload')
        xhr.send(formData)
      })
    }

    try {
      await uploadFile()
      console.log('Upload successful')
      setSuccess(true)
      setFiles([])
      setUploadProgress(100)
    } catch (err) {
      console.error('Upload error:', err)
      setError(err instanceof Error ? err.message : 'An error occurred')
      setUploadProgress(0)
    } finally {
      setUploading(false)
    }
  }

  return (
    <div className="container py-8 max-w-3xl">
      <div className="space-y-6">
        <div>
          <h1 className="text-4xl font-bold mb-2">Upload Documents</h1>
          <p className="text-lg text-muted-foreground">
            Upload your documents to create quizzes. Supported formats: PDF, DOCX, TXT, CSV.
          </p>
        </div>

        {error && (
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertTitle>Error</AlertTitle>
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {success && (
          <Alert>
            <CheckCircle2 className="h-4 w-4" />
            <AlertTitle>Success</AlertTitle>
            <AlertDescription>File uploaded successfully!</AlertDescription>
          </Alert>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          <FileUpload onFileSelect={handleFileSelect} />

          {uploading && (
            <div className="space-y-2">
              <Progress value={uploadProgress} />
              <p className="text-sm text-center text-muted-foreground">
                Uploading... {uploadProgress}%
              </p>
            </div>
          )}

          <Button
            type="submit"
            className="w-full"
            disabled={uploading || files.length === 0}
          >
            {uploading ? 'Uploading...' : 'Upload Document'}
          </Button>
        </form>
      </div>
    </div>
  )
} 