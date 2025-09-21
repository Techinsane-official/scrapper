'use client'

import { useQuery } from 'react-query'
import Link from 'next/link'
import { api, ScrapingJob } from '@/lib/api'
import { formatDistanceToNow } from 'date-fns'
import {
  PlayIcon,
  CheckCircleIcon,
  XCircleIcon,
  ClockIcon,
  ArrowTopRightOnSquareIcon,
} from '@heroicons/react/24/outline'

function getStatusIcon(status: ScrapingJob['status']) {
  switch (status) {
    case 'running':
      return <PlayIcon className="h-4 w-4 text-blue-500" />
    case 'completed':
      return <CheckCircleIcon className="h-4 w-4 text-green-500" />
    case 'failed':
      return <XCircleIcon className="h-4 w-4 text-red-500" />
    default:
      return <ClockIcon className="h-4 w-4 text-gray-500" />
  }
}

function getStatusBadge(status: ScrapingJob['status']) {
  const baseClasses = 'badge'
  switch (status) {
    case 'running':
      return `${baseClasses} badge-info`
    case 'completed':
      return `${baseClasses} badge-success`
    case 'failed':
      return `${baseClasses} badge-error`
    case 'cancelled':
      return `${baseClasses} badge-gray`
    default:
      return `${baseClasses} badge-warning`
  }
}

export function RecentJobs() {
  const { data: jobs, isLoading } = useQuery(
    'recent-jobs',
    () => api.getJobs(),
    {
      refetchInterval: 10000, // Refetch every 10 seconds
    }
  )

  if (isLoading) {
    return (
      <div className="card">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">Recent Jobs</h3>
        </div>
        <div className="p-6">
          <div className="animate-pulse space-y-4">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="flex items-center space-x-4">
                <div className="h-4 w-4 bg-gray-200 rounded"></div>
                <div className="flex-1 space-y-2">
                  <div className="h-4 bg-gray-200 rounded w-3/4"></div>
                  <div className="h-3 bg-gray-200 rounded w-1/2"></div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    )
  }

  const recentJobs = jobs?.slice(0, 5) || []

  return (
    <div className="card">
      <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
        <h3 className="text-lg font-medium text-gray-900">Recent Jobs</h3>
        <Link
          href="/dashboard/jobs"
          className="text-sm text-primary-600 hover:text-primary-500 flex items-center"
        >
          View all
          <ArrowTopRightOnSquareIcon className="h-4 w-4 ml-1" />
        </Link>
      </div>
      <div className="divide-y divide-gray-200">
        {recentJobs.length === 0 ? (
          <div className="p-6 text-center text-gray-500">
            No jobs found. Create your first scraping job to get started.
          </div>
        ) : (
          recentJobs.map((job: ScrapingJob) => (
            <div key={job.id} className="p-6 hover:bg-gray-50">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  {getStatusIcon(job.status)}
                  <div>
                    <Link
                      href={`/dashboard/jobs/${job.id}`}
                      className="text-sm font-medium text-gray-900 hover:text-primary-600"
                    >
                      {job.name}
                    </Link>
                    <p className="text-sm text-gray-500">
                      {job.retailer} • {job.products_scraped}/{job.products_found} products
                    </p>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <span className={getStatusBadge(job.status)}>
                    {job.status}
                  </span>
                  {job.progress > 0 && (
                    <div className="w-16 bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-primary-600 h-2 rounded-full"
                        style={{ width: `${job.progress}%` }}
                      ></div>
                    </div>
                  )}
                </div>
              </div>
              <div className="mt-2 text-xs text-gray-500">
                {formatDistanceToNow(new Date(job.created_at), { addSuffix: true })}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}
