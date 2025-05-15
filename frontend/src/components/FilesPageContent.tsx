'use client'

import React from 'react'
import FileList from './FileList'

interface FilesPageContentProps {
  initialFiles: any[];
}

export default function FilesPageContent({ initialFiles }: FilesPageContentProps) {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl w-full space-y-8">
        <div>
          <h1 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Uploaded Files
          </h1>
          <p className="mt-2 text-center text-sm text-gray-600">
            View and manage your uploaded files
          </p>
        </div>
        <FileList initialFiles={initialFiles} />
      </div>
    </div>
  );
} 