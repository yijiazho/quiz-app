type LogLevel = 'debug' | 'info' | 'warn' | 'error'

interface LogEntry {
  timestamp: string
  level: LogLevel
  message: string
  data?: any
}

class Logger {
  private static instance: Logger
  private logHistory: LogEntry[] = []
  private maxHistorySize = 1000
  private isDevelopment = process.env.NODE_ENV === 'development'

  private constructor() {}

  static getInstance(): Logger {
    if (!Logger.instance) {
      Logger.instance = new Logger()
    }
    return Logger.instance
  }

  private formatMessage(level: LogLevel, message: string, data?: any): LogEntry {
    return {
      timestamp: new Date().toISOString(),
      level,
      message,
      data
    }
  }

  private log(level: LogLevel, message: string, data?: any) {
    const entry = this.formatMessage(level, message, data)
    
    // Add to history
    this.logHistory.push(entry)
    if (this.logHistory.length > this.maxHistorySize) {
      this.logHistory.shift()
    }

    // In development, log to console with appropriate styling
    if (this.isDevelopment) {
      const styles = {
        debug: 'color: #808080',
        info: 'color: #0066cc',
        warn: 'color: #ff9900',
        error: 'color: #cc0000'
      }

      console.log(
        `%c${entry.timestamp} [${level.toUpperCase()}] ${message}`,
        styles[level]
      )
      if (data) {
        console.log(data)
      }
    }

    // In production, only log warnings and errors to console
    else if (level === 'warn' || level === 'error') {
      const consoleMethod = level === 'warn' ? console.warn : console.error
      consoleMethod(`${entry.timestamp} [${level.toUpperCase()}] ${message}`, data)
    }
  }

  debug(message: string, data?: any) {
    this.log('debug', message, data)
  }

  info(message: string, data?: any) {
    this.log('info', message, data)
  }

  warn(message: string, data?: any) {
    this.log('warn', message, data)
  }

  error(message: string, data?: any) {
    this.log('error', message, data)
  }

  getHistory(): LogEntry[] {
    return [...this.logHistory]
  }

  clearHistory() {
    this.logHistory = []
  }
}

export const logger = Logger.getInstance()

// Error boundary logging
export function logError(error: Error, errorInfo: any) {
  logger.error('React Error Boundary caught an error', {
    error: {
      name: error.name,
      message: error.message,
      stack: error.stack
    },
    errorInfo
  })
}

// API error logging
export function logAPIError(endpoint: string, error: any) {
  logger.error(`API Error: ${endpoint}`, {
    endpoint,
    error: error.response ? {
      status: error.response.status,
      statusText: error.response.statusText,
      data: error.response.data
    } : error
  })
}

// Performance logging
export function logPerformance(label: string, duration: number) {
  logger.debug(`Performance: ${label}`, { duration: `${duration}ms` })
} 