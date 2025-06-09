'use client'

import { useEffect, useState } from 'react'

export default function TestAPI() {
  const [apiUrl, setApiUrl] = useState<string>('');
  const [response, setResponse] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Log the API URL from environment
    const envApiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    setApiUrl(envApiUrl);
    console.log('API URL from environment:', envApiUrl);

    async function testApi() {
      try {
        const url = `${envApiUrl}/api/files/`;
        console.log('Testing API endpoint:', url);
        
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
          throw new Error(`HTTP error! status: ${res.status}`);
        }

        const data = await res.json();
        console.log('Response data:', data);
        setResponse(data);
      } catch (err) {
        console.error('API test error:', err);
        setError(err instanceof Error ? err.message : 'Unknown error occurred');
      } finally {
        setLoading(false);
      }
    }

    testApi();
  }, []);

  if (loading) {
    return (
      <div className="p-4">
        <h2 className="text-xl font-bold mb-4">API Test</h2>
        <p>Loading...</p>
      </div>
    );
  }

  return (
    <div className="p-4">
      <h2 className="text-xl font-bold mb-4">API Test</h2>
      
      <div className="mb-4">
        <h3 className="font-semibold">API URL Configuration:</h3>
        <pre className="bg-gray-100 p-2 rounded">{apiUrl}</pre>
      </div>

      {error ? (
        <div className="mb-4">
          <h3 className="font-semibold text-red-600">Error:</h3>
          <pre className="bg-red-50 p-2 rounded text-red-700">{error}</pre>
        </div>
      ) : (
        <div className="mb-4">
          <h3 className="font-semibold">Response:</h3>
          <pre className="bg-gray-100 p-2 rounded overflow-auto max-h-96">
            {JSON.stringify(response, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
} 