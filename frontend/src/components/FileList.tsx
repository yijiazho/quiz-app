'use client'

import React, { useState } from 'react'

// API base URL - can be adjusted based on environment
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

console.log('FileList component loaded, API_URL:', API_URL);

interface ParsedContent {
  content_id: string;
  file_id: string;
  content_type: string;
  parsed_text: string;
  content_metadata: {
    file_size: number;
    encoding?: string;
  };
  parse_time: string;
  last_updated: string;
}

interface ParsedContentsResponse {
  total: number;
  contents: ParsedContent[];
}

interface FileListProps {
  initialFiles: ParsedContent[];
}

export default function FileList({ initialFiles }: FileListProps) {
  const [files, setFiles] = useState<ParsedContent[]>(initialFiles);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleDelete = async (fileId: string) => {
    if (!confirm('Are you sure you want to delete this file?')) {
      return;
    }

    try {
      const response = await fetch(`${API_URL}/api/upload/files/${fileId}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        throw new Error('Failed to delete file');
      }

      // Update the local state
      setFiles(files.filter(file => file.file_id !== fileId));
    } catch (err) {
      console.error('Error deleting file:', err);
      setError('Failed to delete file. Please try again later.');
    }
  };

  const handleDownload = async (fileId: string) => {
    try {
      const response = await fetch(`${API_URL}/api/upload/files/${fileId}/download`);
      if (!response.ok) {
        throw new Error('Failed to download file');
      }

      // Create a blob from the response
      const blob = await response.blob();
      
      // Create a download link
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `file_${fileId}`; // We don't have filename in parsed content
      document.body.appendChild(a);
      a.click();
      
      // Cleanup
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      console.error('Error downloading file:', err);
      setError('Failed to download file. Please try again later.');
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4 bg-red-50 border border-red-200 rounded-md">
        <p className="text-sm text-red-600">{error}</p>
      </div>
    );
  }

  if (files.length === 0) {
    return (
      <div className="text-center py-8">
        <p className="text-gray-500">No files uploaded yet. Go to the Upload page to add your first document.</p>
      </div>
    );
  }

  return (
    <div className="mt-8">
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                File ID
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Type
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Size
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Parsed
              </th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {files.map((file) => (
              <tr key={file.content_id}>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm font-medium text-gray-900">{file.file_id}</div>
                  <div className="text-sm text-gray-500">
                    {file.parsed_text.substring(0, 50)}...
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm text-gray-500">{file.content_type}</div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm text-gray-500">
                    {(file.content_metadata.file_size / 1024).toFixed(1)} KB
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm text-gray-500">
                    {new Date(file.parse_time).toLocaleDateString()}
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                  <button
                    onClick={() => handleDownload(file.file_id)}
                    className="text-primary-600 hover:text-primary-900 mr-4"
                  >
                    Download
                  </button>
                  <button
                    onClick={() => handleDelete(file.file_id)}
                    className="text-red-600 hover:text-red-900"
                  >
                    Delete
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
} 