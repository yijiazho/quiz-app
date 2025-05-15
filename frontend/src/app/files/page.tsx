'use client'

import { useEffect, Suspense } from 'react'
import FileList from '../../components/FileList'
import FilesPageContent from '../../components/FilesPageContent'
import FilesList from '../../components/FilesList'

async function getFiles() {
  console.log('=== Starting server-side data fetch ===');
  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  const url = `${API_URL}/api/upload/parsed-contents`;
  console.log('Fetching from URL:', url);

  try {
    const res = await fetch(url, {
      cache: 'no-store',
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
      },
    });

    console.log('Response status:', res.status);
    console.log('Response headers:', Object.fromEntries(res.headers.entries()));

    if (!res.ok) {
      const errorText = await res.text();
      console.error('Error response:', errorText);
      throw new Error(`Failed to fetch files: ${res.status} ${errorText}`);
    }

    const data = await res.json();
    console.log('Fetched data:', data);
    console.log('=== Completed server-side data fetch ===');
    return data;
  } catch (error) {
    console.error('=== Error in server-side data fetch ===');
    console.error('Error:', error);
    console.error('=== End of error log ===');
    throw error;
  }
}

export default async function FilesPage() {
  console.log('=== Rendering FilesPage ===');
  try {
    const data = await getFiles();
    console.log('Data received:', data);

    return (
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold mb-8">Uploaded Files</h1>
        <Suspense fallback={<div>Loading files...</div>}>
          <FilesList files={data.files} />
        </Suspense>
      </div>
    );
  } catch (error) {
    console.error('Error in FilesPage:', error);
    return (
      <div className="flex flex-col items-center justify-center min-h-screen py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-4xl w-full space-y-8">
          <div className="p-4 bg-red-50 border border-red-200 rounded-md">
            <p className="text-sm text-red-600">
              Failed to load files. Please try again later.
            </p>
          </div>
        </div>
      </div>
    );
  }
} 