'use client'

import React from 'react'

interface File {
  id: string;
  file_id: string;
  type: string;
  text: string;
  metadata: {
    file_size: number;
    encoding?: string;
  };
  parsed_at: string;
  updated_at: string;
}

interface FilesListProps {
  files: File[];
}

export default function FilesList({ files }: FilesListProps) {
  if (files.length === 0) {
    return (
      <div className="text-center py-8">
        <p className="text-gray-500">No files uploaded yet. Go to the Upload page to add your first document.</p>
      </div>
    );
  }

  return (
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
            <tr key={file.id}>
              <td className="px-6 py-4 whitespace-nowrap">
                <div className="text-sm font-medium text-gray-900">{file.file_id}</div>
                <div className="text-sm text-gray-500">
                  {file.text.substring(0, 50)}...
                </div>
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                <div className="text-sm text-gray-500">{file.type}</div>
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                <div className="text-sm text-gray-500">
                  {(file.metadata.file_size / 1024).toFixed(1)} KB
                </div>
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                <div className="text-sm text-gray-500">
                  {new Date(file.parsed_at).toLocaleDateString()}
                </div>
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <button
                  onClick={() => window.open(`/api/files/${file.file_id}/download`, '_blank')}
                  className="text-primary-600 hover:text-primary-900 mr-4"
                >
                  Download
                </button>
                <button
                  onClick={() => {
                    if (confirm('Are you sure you want to delete this file?')) {
                      fetch(`/api/files/${file.file_id}`, { method: 'DELETE' })
                        .then(() => window.location.reload())
                        .catch(console.error);
                    }
                  }}
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
  );
} 