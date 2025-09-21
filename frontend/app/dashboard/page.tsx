'use client'

import { useQuery } from 'react-query'
import { StatsCards } from '@/components/dashboard/StatsCards'
import { RecentJobs } from '@/components/dashboard/RecentJobs'
import { RecentLogs } from '@/components/dashboard/RecentLogs'
import { Notifications } from '@/components/dashboard/Notifications'
import { CreateJobModal } from '@/components/jobs/CreateJobModal'
import { useState } from 'react'
import { PlusIcon } from '@heroicons/react/24/outline'
import { api } from '@/lib/api'

export default function DashboardPage() {
  const [isCreateJobModalOpen, setIsCreateJobModalOpen] = useState(false)

  const { data: dashboardData, isLoading } = useQuery(
    'dashboard',
    () => api.getDashboardData(),
    {
      refetchInterval: 30000, // Refetch every 30 seconds
    }
  )

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600">Welcome to your scraping dashboard</p>
        </div>
        <button
          onClick={() => setIsCreateJobModalOpen(true)}
          className="btn-primary btn-md"
        >
          <PlusIcon className="h-4 w-4 mr-2" />
          New Scraping Job
        </button>
      </div>

      {/* Stats Cards */}
      {dashboardData?.stats && (
        <StatsCards stats={dashboardData.stats} />
      )}

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent Jobs */}
        <div className="lg:col-span-2">
          <RecentJobs />
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Notifications */}
          <Notifications notifications={dashboardData?.notifications || []} />
          
          {/* Recent Logs */}
          <RecentLogs logs={dashboardData?.recent_logs || []} />
        </div>
      </div>

      {/* Create Job Modal */}
      <CreateJobModal
        isOpen={isCreateJobModalOpen}
        onClose={() => setIsCreateJobModalOpen(false)}
      />
    </div>
  )
}
