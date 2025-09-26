'use client'

import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Dialog, Transition } from '@headlessui/react'
import { Fragment } from 'react'
import { XMarkIcon } from '@heroicons/react/24/outline'
import { useMutation, useQueryClient } from 'react-query'
import toast from 'react-hot-toast'
import { api } from '@/lib/api'

const createJobSchema = z.object({
  name: z.string().min(1, 'Job name is required'),
  description: z.string().optional(),
  retailer: z.enum(['amazon'], { required_error: 'Please select a retailer' }),
  category: z.string().optional(),
  search_query: z.string().optional(),
  max_pages: z.number().min(1).max(50),
}).refine((data) => data.category || data.search_query, {
  message: "Either category or search query must be provided",
  path: ["category"],
})

type CreateJobForm = z.infer<typeof createJobSchema>

interface CreateJobModalProps {
  isOpen: boolean
  onClose: () => void
}

const retailers = [
  { value: 'amazon', label: 'Amazon', description: 'Scrape products from Amazon' },
]

const amazonCategories = [
  { value: 'electronics', label: 'Electronics' },
  { value: 'home', label: 'Home & Kitchen' },
  { value: 'fashion', label: 'Fashion' },
  { value: 'books', label: 'Books' },
  { value: 'sports', label: 'Sports & Outdoors' },
]

export function CreateJobModal({ isOpen, onClose }: CreateJobModalProps) {
  const [jobType, setJobType] = useState<'category' | 'search'>('category')
  const queryClient = useQueryClient()

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
    watch,
  } = useForm<CreateJobForm>({
    resolver: zodResolver(createJobSchema),
    defaultValues: {
      retailer: 'amazon',
      max_pages: 5,
    },
  })

  const createJobMutation = useMutation(api.createJob, {
    onSuccess: () => {
      toast.success('Scraping job created successfully!')
      queryClient.invalidateQueries('recent-jobs')
      queryClient.invalidateQueries('dashboard')
      reset()
      onClose()
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to create job')
    },
  })

  const onSubmit = (data: CreateJobForm) => {
    // For now, we'll create a simple product scraping job
    // In the future, this can be enhanced to support different job types
    const jobData = {
      url: data.category || data.search_query || 'https://www.amazon.com/s?k=electronics',
      job_type: 'product',
      max_pages: data.max_pages,
      keywords: data.search_query || 'electronics'
    }
    createJobMutation.mutate(jobData)
  }

  const handleClose = () => {
    reset()
    onClose()
  }

  return (
    <Transition appear show={isOpen} as={Fragment}>
      <Dialog as="div" className="relative z-50" onClose={handleClose}>
        <Transition.Child
          as={Fragment}
          enter="ease-out duration-300"
          enterFrom="opacity-0"
          enterTo="opacity-100"
          leave="ease-in duration-200"
          leaveFrom="opacity-100"
          leaveTo="opacity-0"
        >
          <div className="fixed inset-0 bg-black bg-opacity-25" />
        </Transition.Child>

        <div className="fixed inset-0 overflow-y-auto">
          <div className="flex min-h-full items-center justify-center p-4 text-center">
            <Transition.Child
              as={Fragment}
              enter="ease-out duration-300"
              enterFrom="opacity-0 scale-95"
              enterTo="opacity-100 scale-100"
              leave="ease-in duration-200"
              leaveFrom="opacity-100 scale-100"
              leaveTo="opacity-0 scale-95"
            >
              <Dialog.Panel className="w-full max-w-md transform overflow-hidden rounded-2xl bg-white p-6 text-left align-middle shadow-xl transition-all">
                <div className="flex items-center justify-between mb-4">
                  <Dialog.Title as="h3" className="text-lg font-medium leading-6 text-gray-900">
                    Create New Scraping Job
                  </Dialog.Title>
                  <button
                    type="button"
                    className="text-gray-400 hover:text-gray-600"
                    onClick={handleClose}
                  >
                    <XMarkIcon className="h-6 w-6" />
                  </button>
                </div>

                <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
                  {/* Job Name */}
                  <div>
                    <label htmlFor="name" className="label">
                      Job Name *
                    </label>
                    <input
                      {...register('name')}
                      type="text"
                      className="input"
                      placeholder="Enter job name"
                    />
                    {errors.name && (
                      <p className="mt-1 text-sm text-red-600">{errors.name.message}</p>
                    )}
                  </div>

                  {/* Description */}
                  <div>
                    <label htmlFor="description" className="label">
                      Description
                    </label>
                    <textarea
                      {...register('description')}
                      rows={3}
                      className="input"
                      placeholder="Enter job description (optional)"
                    />
                  </div>

                  {/* Retailer */}
                  <div>
                    <label htmlFor="retailer" className="label">
                      Retailer *
                    </label>
                    <select {...register('retailer')} className="input">
                      {retailers.map((retailer) => (
                        <option key={retailer.value} value={retailer.value}>
                          {retailer.label}
                        </option>
                      ))}
                    </select>
                    {errors.retailer && (
                      <p className="mt-1 text-sm text-red-600">{errors.retailer.message}</p>
                    )}
                  </div>

                  {/* Job Type */}
                  <div>
                    <label className="label">Scraping Type *</label>
                    <div className="space-y-2">
                      <label className="flex items-center">
                        <input
                          type="radio"
                          value="category"
                          checked={jobType === 'category'}
                          onChange={(e) => setJobType(e.target.value as 'category')}
                          className="mr-2"
                        />
                        <span className="text-sm">Scrape by Category</span>
                      </label>
                      <label className="flex items-center">
                        <input
                          type="radio"
                          value="search"
                          checked={jobType === 'search'}
                          onChange={(e) => setJobType(e.target.value as 'search')}
                          className="mr-2"
                        />
                        <span className="text-sm">Scrape by Search Query</span>
                      </label>
                    </div>
                  </div>

                  {/* Category or Search Query */}
                  {jobType === 'category' ? (
                    <div>
                      <label htmlFor="category" className="label">
                        Category *
                      </label>
                      <select {...register('category')} className="input">
                        <option value="">Select a category</option>
                        {amazonCategories.map((category) => (
                          <option key={category.value} value={category.value}>
                            {category.label}
                          </option>
                        ))}
                      </select>
                      {errors.category && (
                        <p className="mt-1 text-sm text-red-600">{errors.category.message}</p>
                      )}
                    </div>
                  ) : (
                    <div>
                      <label htmlFor="search_query" className="label">
                        Search Query *
                      </label>
                      <input
                        {...register('search_query')}
                        type="text"
                        className="input"
                        placeholder="Enter search terms"
                      />
                      {errors.search_query && (
                        <p className="mt-1 text-sm text-red-600">{errors.search_query.message}</p>
                      )}
                    </div>
                  )}

                  {/* Max Pages */}
                  <div>
                    <label htmlFor="max_pages" className="label">
                      Maximum Pages *
                    </label>
                    <input
                      {...register('max_pages', { valueAsNumber: true })}
                      type="number"
                      min="1"
                      max="50"
                      className="input"
                    />
                    {errors.max_pages && (
                      <p className="mt-1 text-sm text-red-600">{errors.max_pages.message}</p>
                    )}
                    <p className="mt-1 text-xs text-gray-500">
                      Maximum number of pages to scrape (1-50)
                    </p>
                  </div>

                  {/* Actions */}
                  <div className="flex justify-end space-x-3 pt-4">
                    <button
                      type="button"
                      onClick={handleClose}
                      className="btn-outline btn-md"
                    >
                      Cancel
                    </button>
                    <button
                      type="submit"
                      disabled={createJobMutation.isLoading}
                      className="btn-primary btn-md"
                    >
                      {createJobMutation.isLoading ? 'Creating...' : 'Create Job'}
                    </button>
                  </div>
                </form>
              </Dialog.Panel>
            </Transition.Child>
          </div>
        </div>
      </Dialog>
    </Transition>
  )
}
