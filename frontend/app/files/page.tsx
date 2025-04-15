'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { AlertCircle, FileText, Plus } from 'lucide-react'
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

export default function FilesPage() {
  return (
    <div className="container py-8">
      <h1 className="text-4xl font-bold mb-6">Your Files</h1>
      <p className="text-lg text-muted-foreground mb-4">
        View and manage your uploaded documents and generated quizzes.
      </p>
      <div className="rounded-lg border p-4">
        <p className="text-center text-muted-foreground">
          No files uploaded yet. Go to the Upload page to add your first document.
        </p>
      </div>
    </div>
  )
} 