'use client'

import { formatDistanceToNow } from 'date-fns'
import {
  InformationCircleIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  XCircleIcon,
} from '@heroicons/react/24/outline'

interface Notification {
  id: string
  title: string
  message: string
  type: string
  created_at: string
}

interface NotificationsProps {
  notifications: Notification[]
}

function getNotificationIcon(type: string) {
  switch (type.toLowerCase()) {
    case 'success':
      return <CheckCircleIcon className="h-5 w-5 text-green-500" />
    case 'warning':
      return <ExclamationTriangleIcon className="h-5 w-5 text-yellow-500" />
    case 'error':
      return <XCircleIcon className="h-5 w-5 text-red-500" />
    default:
      return <InformationCircleIcon className="h-5 w-5 text-blue-500" />
  }
}

function getNotificationBadge(type: string) {
  const baseClasses = 'badge text-xs'
  switch (type.toLowerCase()) {
    case 'success':
      return `${baseClasses} badge-success`
    case 'warning':
      return `${baseClasses} badge-warning`
    case 'error':
      return `${baseClasses} badge-error`
    default:
      return `${baseClasses} badge-info`
  }
}

export function Notifications({ notifications }: NotificationsProps) {
  return (
    <div className="card">
      <div className="px-6 py-4 border-b border-gray-200">
        <h3 className="text-lg font-medium text-gray-900">Notifications</h3>
      </div>
      <div className="divide-y divide-gray-200 max-h-96 overflow-y-auto">
        {notifications.length === 0 ? (
          <div className="p-6 text-center text-gray-500">
            No notifications at this time.
          </div>
        ) : (
          notifications.map((notification) => (
            <div key={notification.id} className="p-4">
              <div className="flex items-start space-x-3">
                {getNotificationIcon(notification.type)}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center space-x-2 mb-1">
                    <span className={getNotificationBadge(notification.type)}>
                      {notification.type}
                    </span>
                  </div>
                  <h4 className="text-sm font-medium text-gray-900">
                    {notification.title}
                  </h4>
                  <p className="text-sm text-gray-600 mt-1">
                    {notification.message}
                  </p>
                  <p className="text-xs text-gray-500 mt-2">
                    {formatDistanceToNow(new Date(notification.created_at), { addSuffix: true })}
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
