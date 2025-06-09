'use client'

import React from 'react'

interface File {
  file_id: string;
  filename: string;
  content_type: string;
  file_size: number;
  upload_time: string;
  last_accessed: string | null;
  title: string | null;
  description: string | null;
  is_parsed: boolean;
  parsed_contents_count: number;
}

interface FilesListProps {
  files: File[];
}

export default function FilesList({ files }: FilesListProps) {
  console.log('FilesList received files:', files);
  console.log('Files type:', typeof files);
  console.log('Is array?', Array.isArray(files));
  console.log('Length:', files?.length);

  if (!files || files.length === 0) {
    console.log('No files to display');
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">No files uploaded yet. Go to the Upload page to add your first document.</p>
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              File Name
            </th>
            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Type
            </th>
            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Size
            </th>
            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Upload Date
            </th>
            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Status
            </th>
            <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
              Actions
            </th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {files.map((file) => {
            console.log('Rendering file:', file);
            return (
              <tr key={file.file_id}>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm font-medium text-gray-900">{file.filename}</div>
                  {file.title && (
                    <div className="text-sm text-gray-500">{file.title}</div>
                  )}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm text-gray-500">{file.content_type}</div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm text-gray-500">
                    {(file.file_size / 1024).toFixed(1)} KB
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm text-gray-500">
                    {new Date(file.upload_time).toLocaleDateString()}
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm text-gray-500">
                    {file.is_parsed ? 'Parsed' : 'Not Parsed'}
                    {file.parsed_contents_count > 0 && ` (${file.parsed_contents_count})`}
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
            );
          })}
        </tbody>
      </table>
    </div>
  );
} 