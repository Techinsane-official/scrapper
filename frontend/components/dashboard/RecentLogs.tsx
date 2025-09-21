'use client'

import { formatDistanceToNow } from 'date-fns'
import {
  InformationCircleIcon,
  ExclamationTriangleIcon,
  XCircleIcon,
  BugAntIcon,
} from '@heroicons/react/24/outline'

interface Log {
  id: string
  level: string
  message: string
  component: string
  created_at: string
}

interface RecentLogsProps {
  logs: Log[]
}

function getLogIcon(level: string) {
  switch (level.toLowerCase()) {
    case 'error':
      return <XCircleIcon className="h-4 w-4 text-red-500" />
    case 'warning':
      return <ExclamationTriangleIcon className="h-4 w-4 text-yellow-500" />
    case 'debug':
      return <BugAntIcon className="h-4 w-4 text-gray-500" />
    default:
      return <InformationCircleIcon className="h-4 w-4 text-blue-500" />
  }
}

function getLogBadge(level: string) {
  const baseClasses = 'badge text-xs'
  switch (level.toLowerCase()) {
    case 'error':
      return `${baseClasses} badge-error`
    case 'warning':
      return `${baseClasses} badge-warning`
    case 'debug':
      return `${baseClasses} badge-gray`
    default:
      return `${baseClasses} badge-info`
  }
}

export function RecentLogs({ logs }: RecentLogsProps) {
  return (
    <div className="card">
      <div className="px-6 py-4 border-b border-gray-200">
        <h3 className="text-lg font-medium text-gray-900">Recent Logs</h3>
      </div>
      <div className="divide-y divide-gray-200 max-h-96 overflow-y-auto">
        {logs.length === 0 ? (
          <div className="p-6 text-center text-gray-500">
            No recent logs available.
          </div>
        ) : (
          logs.map((log) => (
            <div key={log.id} className="p-4">
              <div className="flex items-start space-x-3">
                {getLogIcon(log.level)}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center space-x-2 mb-1">
                    <span className={getLogBadge(log.level)}>
                      {log.level}
                    </span>
                    <span className="text-xs text-gray-500">{log.component}</span>
                  </div>
                  <p className="text-sm text-gray-900 break-words">
                    {log.message}
                  </p>
                  <p className="text-xs text-gray-500 mt-1">
                    {formatDistanceToNow(new Date(log.created_at), { addSuffix: true })}
                  </p>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}
