'use client'

import { Home } from 'lucide-react'

export default function TestLucidePage() {
  return (
    <div className="container py-10">
      <h1 className="text-2xl font-bold mb-4">Test Lucide React</h1>
      <div className="flex items-center gap-2">
        <Home size={24} />
        <span>Home Icon</span>
      </div>
    </div>
  )
} 