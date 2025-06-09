import { NextResponse } from 'next/server'
import { cookies } from 'next/headers'

export async function GET() {
  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
  const cookieStore = cookies()
  const token = cookieStore.get('token')?.value

  if (!token) {
    return NextResponse.json(
      { error: 'Authentication required' },
      { status: 401 }
    )
  }

  try {
    const response = await fetch(`${API_URL}/api/files/`, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Accept': 'application/json',
      },
    })

    if (!response.ok) {
      const errorText = await response.text()
      return NextResponse.json(
        { error: `Failed to fetch files: ${response.status} ${errorText}` },
        { status: response.status }
      )
    }

    const data = await response.json()
    return NextResponse.json(data)
  } catch (error) {
    console.error('Error fetching files:', error)
    return NextResponse.json(
      { error: 'Failed to fetch files' },
      { status: 500 }
    )
  }
} 