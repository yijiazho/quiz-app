'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/button'
import { FileText, Home, Plus, Settings, LogIn, UserPlus } from 'lucide-react'

const navigation = [
  { name: 'Home', href: '/', icon: Home },
  { name: 'Files', href: '/files', icon: FileText },
  { name: 'Upload', href: '/upload', icon: Plus },
  { name: 'Settings', href: '/settings', icon: Settings },
]

const authNavigation = [
  { name: 'Login', href: '/login', icon: LogIn },
  { name: 'Register', href: '/register', icon: UserPlus },
]

export function Navigation() {
  const pathname = usePathname()

  return (
    <nav className="flex items-center gap-6">
      <div className="flex items-center gap-1">
        {navigation.map((item) => {
          const isActive = pathname === item.href
          return (
            <Link key={item.name} href={item.href}>
              <Button
                variant={isActive ? 'default' : 'ghost'}
                className={cn(
                  'relative h-9 w-full justify-start px-3',
                  isActive && 'bg-accent text-accent-foreground'
                )}
              >
                <item.icon className="mr-2 h-4 w-4" />
                {item.name}
              </Button>
            </Link>
          )
        })}
      </div>
      <div className="flex items-center gap-1">
        {authNavigation.map((item) => {
          const isActive = pathname === item.href
          return (
            <Link key={item.name} href={item.href}>
              <Button
                variant={isActive ? 'default' : 'secondary'}
                className={cn(
                  'relative h-9 w-full justify-start px-3',
                  isActive && 'bg-accent text-accent-foreground'
                )}
              >
                <item.icon className="mr-2 h-4 w-4" />
                {item.name}
              </Button>
            </Link>
          )
        })}
      </div>
    </nav>
  )
} 