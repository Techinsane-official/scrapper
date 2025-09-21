import axios from 'axios'
import Cookies from 'js-cookie'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

// Handle different environments
const getApiUrl = () => {
  if (typeof window !== 'undefined') {
    // Client-side: use environment variable or fallback
    return process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
  }
  // Server-side: use environment variable
  return process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
}

// Create axios instance
const apiClient = axios.create({
  baseURL: getApiUrl(),
  timeout: 30000,
})

// Request interceptor to add auth token
apiClient.interceptors.request.use(
  (config) => {
    const token = Cookies.get('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor to handle auth errors
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Clear token and redirect to login
      Cookies.remove('access_token')
      window.location.href = '/auth/login'
    }
    return Promise.reject(error)
  }
)

// Types
export interface User {
  id: string
  email: string
  full_name: string
  role: 'admin' | 'user' | 'viewer'
  is_active: boolean
  created_at: string
  last_login: string
}

export interface ScrapingJob {
  id: string
  name: string
  description?: string
  retailer: string
  category?: string
  search_query?: string
  max_pages: number
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled'
  progress: number
  products_scraped: number
  products_found: number
  error_message?: string
  started_at?: string
  completed_at?: string
  created_at: string
}

export interface Product {
  id: string
  job_id: string
  retailer: string
  external_id: string
  url: string
  title: string
  price?: number
  original_price?: number
  discount_percentage?: number
  rating?: number
  review_count?: number
  availability: string
  brand?: string
  category?: string
  description?: string
  bullet_points: string[]
  specifications: Record<string, string>
  variations: any[]
  images: string[]
  scraped_at: string
  created_at?: string
}

export interface DashboardStats {
  total_jobs: number
  active_jobs: number
  completed_jobs: number
  failed_jobs: number
  total_products: number
  total_users: number
  average_job_duration: number
  success_rate: number
  last_updated?: string
}

export interface DashboardData {
  stats: DashboardStats
  recent_logs: Array<{
    id: string
    level: string
    message: string
    component: string
    created_at: string
  }>
  notifications: Array<{
    id: string
    title: string
    message: string
    type: string
    created_at: string
  }>
}

// API methods
export const api = {
  // Auth
  async login(email: string, password: string) {
    const response = await apiClient.post('/api/auth/login', { email, password })
    const { access_token, user } = response.data
    Cookies.set('access_token', access_token, { expires: 1 }) // 1 day
    return { token: access_token, user }
  },

  async register(email: string, password: string, fullName: string) {
    const response = await apiClient.post('/api/auth/register', {
      email,
      password,
      full_name: fullName,
    })
    return response.data
  },

  async getCurrentUser() {
    const response = await apiClient.get('/api/auth/me')
    return response.data
  },

  async logout() {
    Cookies.remove('access_token')
    await apiClient.post('/api/auth/logout')
  },

  // Jobs
  async getJobs() {
    const response = await apiClient.get('/api/jobs')
    return response.data
  },

  async getJob(jobId: string) {
    const response = await apiClient.get(`/api/jobs/${jobId}`)
    return response.data
  },

  async createJob(jobData: {
    name: string
    description?: string
    retailer: string
    category?: string
    search_query?: string
    max_pages: number
  }) {
    const response = await apiClient.post('/api/jobs', jobData)
    return response.data
  },

  async updateJob(jobId: string, jobData: Partial<ScrapingJob>) {
    const response = await apiClient.put(`/api/jobs/${jobId}`, jobData)
    return response.data
  },

  async deleteJob(jobId: string) {
    const response = await apiClient.delete(`/api/jobs/${jobId}`)
    return response.data
  },

  // Products
  async getJobProducts(jobId: string, limit = 100) {
    const response = await apiClient.get(`/api/products/job/${jobId}?limit=${limit}`)
    return response.data
  },

  async getProduct(productId: string) {
    const response = await apiClient.get(`/api/products/${productId}`)
    return response.data
  },

  async searchProducts(query: string, limit = 50) {
    const response = await apiClient.get(`/api/products/search?query=${encodeURIComponent(query)}&limit=${limit}`)
    return response.data
  },

  // Dashboard
  async getDashboardData() {
    const response = await apiClient.get('/api/dashboard')
    return response.data
  },

  async getDashboardStats() {
    const response = await apiClient.get('/api/dashboard/stats')
    return response.data
  },

  // Users (admin only)
  async getUsers() {
    const response = await apiClient.get('/api/users')
    return response.data
  },

  async updateUser(userId: string, userData: Partial<User>) {
    const response = await apiClient.put(`/api/users/${userId}`, userData)
    return response.data
  },

  async deleteUser(userId: string) {
    const response = await apiClient.delete(`/api/users/${userId}`)
    return response.data
  },
}
