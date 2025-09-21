'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from 'react-query'
import { api } from '@/lib/api'
import toast from 'react-hot-toast'
import { 
  PlusIcon, 
  PlayIcon, 
  StopIcon, 
  TrashIcon,
  ArrowPathIcon,
  ClockIcon,
  CheckCircleIcon,
  XCircleIcon
} from '@heroicons/react/24/outline'

export default function JobsPage() {
  const [showCreateForm, setShowCreateForm] = useState(false)
  const [newJob, setNewJob] = useState({
    url: '',
    job_type: 'amazon_product',
    max_pages: 1,
    keywords: ''
  })
  const queryClient = useQueryClient()

  const { data: jobs, isLoading, error } = useQuery('jobs', api.getJobs, {
    onError: (err: any) => {
      console.error('Error fetching jobs:', err)
      toast.error('Failed to load jobs')
    }
  })

  const createJobMutation = useMutation(api.createJob, {
    onSuccess: () => {
      queryClient.invalidateQueries('jobs')
      toast.success('Job created successfully!')
      setShowCreateForm(false)
      setNewJob({ url: '', job_type: 'amazon_product', max_pages: 1, keywords: '' })
    },
    onError: (err: any) => {
      toast.error(err.response?.data?.detail || 'Failed to create job')
    }
  })

  const handleCreateJob = (e: React.FormEvent) => {
    e.preventDefault()
    if (!newJob.url.trim()) {
      toast.error('Please enter a URL')
      return
    }
    createJobMutation.mutate(newJob)
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircleIcon className="h-5 w-5 text-green-500" />
      case 'running':
        return <ArrowPathIcon className="h-5 w-5 text-blue-500 animate-spin" />
      case 'failed':
        return <XCircleIcon className="h-5 w-5 text-red-500" />
      default:
        return <ClockIcon className="h-5 w-5 text-yellow-500" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800'
      case 'running':
        return 'bg-blue-100 text-blue-800'
      case 'failed':
        return 'bg-red-100 text-red-800'
      default:
        return 'bg-yellow-100 text-yellow-800'
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <ArrowPathIcon className="h-8 w-8 animate-spin text-primary-500" />
        <p className="ml-3 text-lg text-gray-600">Loading jobs...</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900">Scraping Jobs</h1>
        <button
          onClick={() => setShowCreateForm(!showCreateForm)}
          className="btn-primary"
        >
          <PlusIcon className="h-5 w-5 mr-2" />
          Create New Job
        </button>
      </div>

      {showCreateForm && (
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-xl font-semibold mb-4">Create New Scraping Job</h2>
          <form onSubmit={handleCreateJob} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Target URL
              </label>
              <input
                type="url"
                value={newJob.url}
                onChange={(e) => setNewJob({ ...newJob, url: e.target.value })}
                placeholder="https://amazon.com/product/..."
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                required
              />
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Job Type
                </label>
                <select
                  value={newJob.job_type}
                  onChange={(e) => setNewJob({ ...newJob, job_type: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                >
                  <option value="amazon_product">Amazon Product</option>
                  <option value="amazon_search">Amazon Search</option>
                  <option value="general_scrape">General Scrape</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Max Pages
                </label>
                <input
                  type="number"
                  min="1"
                  max="10"
                  value={newJob.max_pages}
                  onChange={(e) => setNewJob({ ...newJob, max_pages: parseInt(e.target.value) })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                />
              </div>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Keywords (optional)
              </label>
              <input
                type="text"
                value={newJob.keywords}
                onChange={(e) => setNewJob({ ...newJob, keywords: e.target.value })}
                placeholder="Search keywords..."
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
            </div>
            
            <div className="flex space-x-3">
              <button
                type="submit"
                disabled={createJobMutation.isLoading}
                className="btn-primary"
              >
                {createJobMutation.isLoading ? 'Creating...' : 'Create Job'}
              </button>
              <button
                type="button"
                onClick={() => setShowCreateForm(false)}
                className="btn-secondary"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      <div className="bg-white shadow rounded-lg">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-medium text-gray-900">All Jobs</h2>
        </div>
        
        {error ? (
          <div className="p-6 text-center text-red-600">
            Failed to load jobs. Please try again.
          </div>
        ) : jobs?.length === 0 ? (
          <div className="p-6 text-center text-gray-500">
            No jobs found. Create your first scraping job to get started.
          </div>
        ) : (
          <div className="divide-y divide-gray-200">
            {jobs?.map((job: any) => (
              <div key={job.id} className="p-6 hover:bg-gray-50">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4">
                    {getStatusIcon(job.status)}
                    <div>
                      <h3 className="text-sm font-medium text-gray-900">
                        {job.url.length > 60 ? `${job.url.substring(0, 60)}...` : job.url}
                      </h3>
                      <p className="text-sm text-gray-500">
                        {job.job_type} • {job.max_pages} page{job.max_pages > 1 ? 's' : ''}
                        {job.keywords && ` • Keywords: ${job.keywords}`}
                      </p>
                      <p className="text-xs text-gray-400">
                        Created: {new Date(job.created_at).toLocaleString()}
                      </p>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-3">
                    <span className={`px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(job.status)}`}>
                      {job.status}
                    </span>
                    
                    {job.status === 'running' && (
                      <button className="text-red-600 hover:text-red-800">
                        <StopIcon className="h-5 w-5" />
                      </button>
                    )}
                    
                    {job.status === 'pending' && (
                      <button className="text-green-600 hover:text-green-800">
                        <PlayIcon className="h-5 w-5" />
                      </button>
                    )}
                    
                    <button className="text-red-600 hover:text-red-800">
                      <TrashIcon className="h-5 w-5" />
                    </button>
                  </div>
                </div>
                
                {job.status === 'completed' && (
                  <div className="mt-3 text-sm text-gray-600">
                    ✅ Scraped {job.products_count || 0} products
                  </div>
                )}
                
                {job.status === 'failed' && job.error_message && (
                  <div className="mt-3 text-sm text-red-600">
                    ❌ Error: {job.error_message}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
