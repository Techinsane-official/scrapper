import { cookies } from 'next/headers'
import { api } from './api'

export async function getServerSession() {
  try {
    const cookieStore = cookies()
    const token = cookieStore.get('access_token')?.value
    
    if (!token) {
      return null
    }

    // Verify token by making a request to the API
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/auth/me`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    })

    if (!response.ok) {
      return null
    }

    const user = await response.json()
    return { user, token }
  } catch (error) {
    console.error('Error getting server session:', error)
    return null
  }
}
