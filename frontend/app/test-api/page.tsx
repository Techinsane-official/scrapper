'use client'

import { useState } from 'react'
import { api } from '@/lib/api'
import Cookies from 'js-cookie'

export default function TestApiPage() {
  const [results, setResults] = useState<any>({})
  const [loading, setLoading] = useState(false)

  const testEndpoints = async () => {
    setLoading(true)
    const testResults: any = {}
    
    try {
      // Test 1: Health check (no auth required)
      console.log('Testing health endpoint...')
      const healthResponse = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/health`)
      testResults.health = {
        status: healthResponse.status,
        data: await healthResponse.json()
      }
    } catch (error: any) {
      testResults.health = { error: error.message }
    }

    try {
      // Test 2: Root endpoint (no auth required)
      console.log('Testing root endpoint...')
      const rootResponse = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/`)
      testResults.root = {
        status: rootResponse.status,
        data: await rootResponse.json()
      }
    } catch (error: any) {
      testResults.root = { error: error.message }
    }

    try {
      // Test 3: Register endpoint
      console.log('Testing register endpoint...')
      const registerResponse = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: 'test@example.com',
          password: 'password123',
          full_name: 'Test User'
        })
      })
      testResults.register = {
        status: registerResponse.status,
        data: await registerResponse.json()
      }
    } catch (error: any) {
      testResults.register = { error: error.message }
    }

    try {
      // Test 4: Login endpoint
      console.log('Testing login endpoint...')
      const loginResponse = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: 'test@example.com',
          password: 'password123'
        })
      })
      const loginData = await loginResponse.json()
      testResults.login = {
        status: loginResponse.status,
        data: loginData
      }

      // Store token if login successful
      if (loginData.access_token) {
        Cookies.set('access_token', loginData.access_token, { expires: 7 })
        console.log('Token stored:', loginData.access_token)
      }
    } catch (error: any) {
      testResults.login = { error: error.message }
    }

    try {
      // Test 5: Protected endpoint with token
      const token = Cookies.get('access_token')
      console.log('Testing protected endpoint with token:', token)
      
      const protectedResponse = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/dashboard/stats`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        }
      })
      testResults.protected = {
        status: protectedResponse.status,
        data: await protectedResponse.json()
      }
    } catch (error: any) {
      testResults.protected = { error: error.message }
    }

    setResults(testResults)
    setLoading(false)
  }

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">API Connection Test</h1>
        
        <div className="mb-6">
          <button
            onClick={testEndpoints}
            disabled={loading}
            className="bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700 disabled:opacity-50"
          >
            {loading ? 'Testing...' : 'Test All Endpoints'}
          </button>
        </div>

        <div className="space-y-6">
          {Object.entries(results).map(([endpoint, result]: [string, any]) => (
            <div key={endpoint} className="bg-white shadow rounded-lg p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4 capitalize">
                {endpoint} Endpoint
              </h2>
              <div className="bg-gray-100 p-4 rounded-md">
                <pre className="text-sm overflow-auto">
                  {JSON.stringify(result, null, 2)}
                </pre>
              </div>
            </div>
          ))}
        </div>

        <div className="mt-8 bg-blue-50 border border-blue-200 rounded-md p-4">
          <h3 className="text-lg font-medium text-blue-800 mb-2">Debug Info</h3>
          <p className="text-blue-700">
            <strong>API URL:</strong> {process.env.NEXT_PUBLIC_API_URL || 'Not set'}<br/>
            <strong>Token:</strong> {Cookies.get('access_token') ? 'Present' : 'Not found'}<br/>
            <strong>Environment:</strong> {process.env.NODE_ENV}
          </p>
        </div>
      </div>
    </div>
  )
}
