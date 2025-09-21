'use client'

import { DashboardStats } from '@/lib/api'
import {
  DocumentTextIcon,
  PlayIcon,
  CheckCircleIcon,
  XCircleIcon,
  ChartBarIcon,
  UsersIcon,
} from '@heroicons/react/24/outline'

interface StatsCardsProps {
  stats: DashboardStats
}

export function StatsCards({ stats }: StatsCardsProps) {
  const cards = [
    {
      name: 'Total Jobs',
      value: stats.total_jobs,
      icon: DocumentTextIcon,
      color: 'text-blue-600',
      bgColor: 'bg-blue-100',
    },
    {
      name: 'Active Jobs',
      value: stats.active_jobs,
      icon: PlayIcon,
      color: 'text-yellow-600',
      bgColor: 'bg-yellow-100',
    },
    {
      name: 'Completed Jobs',
      value: stats.completed_jobs,
      icon: CheckCircleIcon,
      color: 'text-green-600',
      bgColor: 'bg-green-100',
    },
    {
      name: 'Failed Jobs',
      value: stats.failed_jobs,
      icon: XCircleIcon,
      color: 'text-red-600',
      bgColor: 'bg-red-100',
    },
    {
      name: 'Total Products',
      value: stats.total_products.toLocaleString(),
      icon: ChartBarIcon,
      color: 'text-purple-600',
      bgColor: 'bg-purple-100',
    },
    {
      name: 'Success Rate',
      value: `${stats.success_rate}%`,
      icon: UsersIcon,
      color: 'text-indigo-600',
      bgColor: 'bg-indigo-100',
    },
  ]

  return (
    <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6">
      {cards.map((card) => (
        <div key={card.name} className="card p-5">
          <div className="flex items-center">
            <div className={`p-2 rounded-lg ${card.bgColor}`}>
              <card.icon className={`h-6 w-6 ${card.color}`} />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">{card.name}</p>
              <p className="text-2xl font-semibold text-gray-900">{card.value}</p>
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}
