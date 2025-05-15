'use client'

import React, { useState, useCallback, useEffect } from 'react'
import { useDropzone } from 'react-dropzone'

// API base URL - can be adjusted based on environment
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function FileUpload() {
  const [file, setFile] = useState<File | null>(null)
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)
  const [apiAvailable, setApiAvailable] = useState<boolean | null>(null)

  // Check if API is available on component mount
  useEffect(() => {
    const checkApiStatus = async () => {
      try {
        console.log('Checking API status at:', API_URL);
        // Try the root endpoint first
        const response = await fetch(`${API_URL}/`, {
          method: 'GET',
          headers: {
            'Accept': 'application/json',
          },
        });
        
        if (response.ok) {
          console.log('API is available');
          setApiAvailable(true);
          setError(null);
        } else {
          console.warn('API returned error status:', response.status);
          setApiAvailable(false);
          setError('API server is not responding correctly. Please ensure the backend server is running.');
        }
      } catch (err) {
        console.error('API connection error:', err);
        setApiAvailable(false);
        setError('Cannot connect to the backend server. Please ensure it is running.');
      }
    };

    // Check immediately and then every 5 seconds
    checkApiStatus();
    const intervalId = setInterval(checkApiStatus, 5000);
    
    // Cleanup the interval on unmount
    return () => clearInterval(intervalId);
  }, []);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      const file = acceptedFiles[0]
      
      // Check file type
      if (file.type !== 'application/pdf' && 
          !file.name.endsWith('.docx') && 
          !file.name.endsWith('.doc') &&
          !file.name.endsWith('.txt')) { 
        setError('Please upload a PDF, DOCX, or TXT file')
        return
      }
      
      // Check file size (max 10MB)
      if (file.size > 10 * 1024 * 1024) {
        setError('File size should be less than 10MB')
        return
      }
      
      setFile(file)
      setError(null)
      setSuccess(null)
    }
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'application/msword': ['.doc'],
      'text/plain': ['.txt']
    },
    maxFiles: 1,
    multiple: false,
    disabled: !apiAvailable
  })

  const handleUpload = async () => {
    if (!file || !apiAvailable) return
    
    setUploading(true)
    setError(null)
    setSuccess(null)
    
    try {
      const formData = new FormData()
      formData.append('file', file)
      
      const uploadUrl = `${API_URL}/api/upload/`;
      console.log('Starting file upload:', {
        url: uploadUrl,
        fileName: file.name,
        fileType: file.type,
        fileSize: file.size
      });
      
      const response = await fetch(uploadUrl, {
        method: 'POST',
        body: formData
      });
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => null);
        throw new Error(errorData?.detail || `Upload failed with status: ${response.status}`);
      }
      
      const data = await response.json();
      console.log('Upload successful:', data);
      
      // Set success message
      setSuccess('File uploaded successfully!')
      
      // Reset file selection after successful upload
      setFile(null)
    } catch (err) {
      console.error('Upload error:', err);
      
      if (err instanceof Error) {
        if (err.message.includes('Failed to fetch') || err.message.includes('NetworkError')) {
          setError('Network error: Cannot connect to the server. Please ensure the backend is running.');
          setApiAvailable(false);
        } else {
          setError(err.message);
        }
      } else {
        setError('Failed to upload file. Please try again.');
      }
    } finally {
      setUploading(false)
    }
  }

  return (
    <div className="mt-8">
      {/* API status indicator */}
      {apiAvailable === false && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-md">
          <p className="text-sm text-red-600 font-medium">
            ⚠️ Cannot connect to the backend server
          </p>
          <p className="text-xs text-red-500 mt-1">
            Please make sure the backend server is running at {API_URL}
          </p>
          <p className="text-xs text-red-500 mt-1">
            Run the start_servers.bat or test_backend.bat script to start the backend.
          </p>
        </div>
      )}
      
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-lg p-6 text-center cursor-pointer transition-colors ${
          isDragActive ? 'border-primary-500 bg-primary-50' : 
          !apiAvailable ? 'border-gray-200 bg-gray-50 cursor-not-allowed' :
          'border-gray-300 hover:border-primary-400'
        }`}
      >
        <input {...getInputProps()} />
        {file ? (
          <div className="space-y-4">
            <p className="text-sm text-gray-600">
              Selected file: <span className="font-medium">{file.name}</span>
            </p>
            <button
              onClick={(e) => {
                e.stopPropagation();
                handleUpload();
              }}
              disabled={uploading || !apiAvailable}
              className={`w-full py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white ${
                uploading || !apiAvailable
                  ? 'bg-gray-400 cursor-not-allowed'
                  : 'bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500'
              }`}
            >
              {uploading ? 'Uploading...' : 'Upload'}
            </button>
          </div>
        ) : (
          <div>
            <p className="text-sm text-gray-600">
              {isDragActive
                ? 'Drop the file here'
                : !apiAvailable
                ? 'File upload is unavailable (backend server not connected)'
                : 'Drag and drop a PDF, DOCX, or TXT file here, or click to select a file'}
            </p>
            <p className="mt-1 text-xs text-gray-500">
              Supported formats: PDF, DOCX, TXT (max 10MB)
            </p>
          </div>
        )}
      </div>
      
      {error && (
        <p className="mt-2 text-sm text-red-600">{error}</p>
      )}
      
      {success && (
        <p className="mt-2 text-sm text-green-600">{success}</p>
      )}
    </div>
  )
} 