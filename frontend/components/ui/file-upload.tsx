'use client'

import { useCallback, useState } from 'react'
import { useDropzone } from 'react-dropzone'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/button'
import { Upload, X } from 'lucide-react'

interface FileUploadProps {
  onFileSelect: (files: File[]) => void
  maxSize?: number // in bytes
  accept?: Record<string, string[]>
}

export function FileUpload({ 
  onFileSelect, 
  maxSize = 10 * 1024 * 1024, // 10MB default
  accept = {
    'application/pdf': ['.pdf'],
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
    'text/plain': ['.txt'],
    'text/csv': ['.csv']
  }
}: FileUploadProps) {
  const [files, setFiles] = useState<File[]>([])

  const onDrop = useCallback((acceptedFiles: File[]) => {
    setFiles(acceptedFiles)
    onFileSelect(acceptedFiles)
  }, [onFileSelect])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    maxSize,
    accept,
    multiple: false
  })

  const removeFile = (index: number) => {
    setFiles(files.filter((_, i) => i !== index))
  }

  return (
    <div className="w-full">
      <div
        {...getRootProps()}
        className={cn(
          'relative rounded-lg border-2 border-dashed border-gray-300 p-12 text-center transition-colors',
          isDragActive && 'border-primary bg-primary/5',
          'hover:border-primary hover:bg-primary/5'
        )}
      >
        <input {...getInputProps()} />
        <div className="flex flex-col items-center justify-center gap-4">
          <Upload className="h-8 w-8 text-muted-foreground" />
          {isDragActive ? (
            <p className="text-lg text-muted-foreground">Drop your files here...</p>
          ) : (
            <>
              <p className="text-lg text-muted-foreground">
                Drag and drop your files here, or click to select files
              </p>
              <Button variant="secondary" className="mt-2">
                Select Files
              </Button>
              <p className="text-sm text-muted-foreground">
                Supported formats: PDF, DOCX, TXT, CSV
              </p>
              <p className="text-sm text-muted-foreground">
                Maximum file size: 10MB
              </p>
            </>
          )}
        </div>
      </div>

      {files.length > 0 && (
        <div className="mt-4">
          <h3 className="text-sm font-medium">Selected files:</h3>
          <ul className="mt-2 space-y-2">
            {files.map((file, index) => (
              <li
                key={index}
                className="flex items-center justify-between rounded-md border px-3 py-2"
              >
                <span className="text-sm">
                  {file.name} ({(file.size / 1024 / 1024).toFixed(2)} MB)
                </span>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => removeFile(index)}
                  className="h-8 w-8 p-0"
                >
                  <X className="h-4 w-4" />
                  <span className="sr-only">Remove file</span>
                </Button>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
} 