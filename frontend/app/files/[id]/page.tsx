'use client'

import { useEffect, useState } from 'react'
import { useParams } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { AlertCircle, Download, FileText, Trash2 } from 'lucide-react'
import { formatDistanceToNow } from 'date-fns'

interface FileMetadata {
  file_id: string
  filename: string
  title: string
  description: string
  content_type: string
  file_size: number
  created_at: string
  updated_at: string
}

interface ParsedContent {
  title: string
  content: string
  sections: Array<{
    title: string
    content: string
    level: number
  }>
  metadata: Record<string, any>
}

export default function FileViewPage() {
  const params = useParams()
  const [fileMetadata, setFileMetadata] = useState<FileMetadata | null>(null)
  const [parsedContent, setParsedContent] = useState<ParsedContent | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchFileData = async () => {
      try {
        // Fetch file metadata
        const metadataResponse = await fetch(`/api/upload/files/${params.id}`)
        if (!metadataResponse.ok) {
          throw new Error('Failed to fetch file metadata')
        }
        const metadata = await metadataResponse.json()
        setFileMetadata(metadata)

        // Fetch parsed content
        const contentResponse = await fetch(`/api/upload/files/${params.id}/parsed`)
        if (contentResponse.ok) {
          const content = await contentResponse.json()
          setParsedContent(content)
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An error occurred')
      } finally {
        setLoading(false)
      }
    }

    fetchFileData()
  }, [params.id])

  const handleDownload = async () => {
    try {
      const response = await fetch(`/api/upload/files/${params.id}/download`)
      if (!response.ok) {
        throw new Error('Download failed')
      }
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = fileMetadata?.filename || 'downloaded-file'
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Download failed')
    }
  }

  const handleDelete = async () => {
    if (!confirm('Are you sure you want to delete this file?')) return

    try {
      const response = await fetch(`/api/upload/files/${params.id}`, {
        method: 'DELETE',
      })
      if (!response.ok) {
        throw new Error('Delete failed')
      }
      // Redirect to home page after successful deletion
      window.location.href = '/'
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Delete failed')
    }
  }

  if (loading) {
    return <div className="container mx-auto py-8">Loading...</div>
  }

  if (error) {
    return (
      <div className="container mx-auto py-8">
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>Error</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      </div>
    )
  }

  if (!fileMetadata) {
    return <div className="container mx-auto py-8">File not found</div>
  }

  return (
    <div className="container mx-auto py-8">
      <Card className="mb-8">
        <CardHeader className="flex flex-row items-center justify-between">
          <div>
            <CardTitle>{fileMetadata.title || fileMetadata.filename}</CardTitle>
            <CardDescription>
              Uploaded {formatDistanceToNow(new Date(fileMetadata.created_at))} ago
            </CardDescription>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" onClick={handleDownload}>
              <Download className="mr-2 h-4 w-4" />
              Download
            </Button>
            <Button variant="destructive" onClick={handleDelete}>
              <Trash2 className="mr-2 h-4 w-4" />
              Delete
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="font-medium">File Type:</span> {fileMetadata.content_type}
            </div>
            <div>
              <span className="font-medium">Size:</span>{' '}
              {(fileMetadata.file_size / 1024).toFixed(2)} KB
            </div>
            {fileMetadata.description && (
              <div className="col-span-2">
                <span className="font-medium">Description:</span> {fileMetadata.description}
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {parsedContent && (
        <Tabs defaultValue="content">
          <TabsList>
            <TabsTrigger value="content">
              <FileText className="mr-2 h-4 w-4" />
              Content
            </TabsTrigger>
            <TabsTrigger value="sections">Sections</TabsTrigger>
            <TabsTrigger value="metadata">Metadata</TabsTrigger>
          </TabsList>
          <TabsContent value="content" className="mt-4">
            <Card>
              <CardContent className="p-6">
                <pre className="whitespace-pre-wrap">{parsedContent.content}</pre>
              </CardContent>
            </Card>
          </TabsContent>
          <TabsContent value="sections" className="mt-4">
            <div className="space-y-4">
              {parsedContent.sections.map((section, index) => (
                <Card key={index}>
                  <CardHeader>
                    <CardTitle className="text-lg">{section.title}</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <pre className="whitespace-pre-wrap">{section.content}</pre>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>
          <TabsContent value="metadata" className="mt-4">
            <Card>
              <CardContent className="p-6">
                <pre className="whitespace-pre-wrap">
                  {JSON.stringify(parsedContent.metadata, null, 2)}
                </pre>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      )}
    </div>
  )
} 