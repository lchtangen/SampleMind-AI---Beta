'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { useAuthStore } from '@/store/useAuthStore'
import { Upload, BarChart3, Music2, TrendingUp, Activity, Calendar } from 'lucide-react'
import { Card, CardHeader, CardTitle, CardDescription, CardContent, Spinner, Button, Badge } from '@/components'
import Navbar from '@/components/layout/Navbar'

export default function DashboardPage() {
  const { user, isAuthenticated, isLoading, fetchUser } = useAuthStore()
  const router = useRouter()

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push('/login')
    } else if (!user) {
      fetchUser()
    }
  }, [isAuthenticated, isLoading, user, router, fetchUser])

  if (isLoading || !user) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <Spinner size="lg" label="Loading dashboard..." />
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Welcome Section */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Welcome back, {user.username}! 👋</h1>
          <p className="text-gray-600 mt-1">Here&apos;s what&apos;s happening with your audio projects</p>
        </div>
        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Card variant="bordered" className="hover:shadow-md transition-shadow">
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Total Uploads</p>
                  <p className="text-3xl font-bold text-gray-900 mt-2">{user.total_uploads}</p>
                  <p className="text-xs text-green-600 mt-1 flex items-center gap-1">
                    <TrendingUp size={12} />
                    All time
                  </p>
                </div>
                <div className="p-3 bg-blue-100 rounded-xl">
                  <Upload className="h-8 w-8 text-blue-600" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card variant="bordered" className="hover:shadow-md transition-shadow">
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Analyses</p>
                  <p className="text-3xl font-bold text-gray-900 mt-2">{user.total_analyses}</p>
                  <p className="text-xs text-blue-600 mt-1 flex items-center gap-1">
                    <Activity size={12} />
                    Completed
                  </p>
                </div>
                <div className="p-3 bg-purple-100 rounded-xl">
                  <BarChart3 className="h-8 w-8 text-purple-600" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card variant="bordered" className="hover:shadow-md transition-shadow">
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Status</p>
                  <div className="mt-2">
                    <Badge variant={user.is_active ? 'success' : 'error'} size="lg">
                      {user.is_active ? 'Active' : 'Inactive'}
                    </Badge>
                  </div>
                  <p className="text-xs text-gray-500 mt-2">
                    {user.is_verified ? 'Verified' : 'Not verified'}
                  </p>
                </div>
                <div className="p-3 bg-green-100 rounded-xl">
                  <Music2 className="h-8 w-8 text-green-600" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card variant="bordered" className="hover:shadow-md transition-shadow">
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Member Since</p>
                  <p className="text-lg font-semibold text-gray-900 mt-2">
                    {new Date(user.created_at).toLocaleDateString('en-US', { month: 'short', year: 'numeric' })}
                  </p>
                  <p className="text-xs text-gray-500 mt-1 flex items-center gap-1">
                    <Calendar size={12} />
                    {Math.floor((Date.now() - new Date(user.created_at).getTime()) / (1000 * 60 * 60 * 24))} days
                  </p>
                </div>
                <div className="p-3 bg-indigo-100 rounded-xl">
                  <Calendar className="h-8 w-8 text-indigo-600" />
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Quick Actions */}
        <Card variant="bordered" className="mb-8">
          <CardHeader>
            <CardTitle>Quick Actions</CardTitle>
            <CardDescription>Get started with your audio projects</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Link href="/upload">
                <div className="flex items-center space-x-4 p-4 border-2 border-dashed border-gray-300 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition-all group cursor-pointer">
                  <div className="p-3 bg-blue-100 rounded-lg group-hover:bg-blue-200 transition-colors">
                    <Upload className="h-6 w-6 text-blue-600" />
                  </div>
                  <div className="text-left">
                    <h3 className="font-semibold text-gray-900">Upload Audio</h3>
                    <p className="text-sm text-gray-600">Upload and analyze new audio files</p>
                  </div>
                </div>
              </Link>

              <Link href="/library">
                <div className="flex items-center space-x-4 p-4 border-2 border-dashed border-gray-300 rounded-lg hover:border-purple-500 hover:bg-purple-50 transition-all group cursor-pointer">
                  <div className="p-3 bg-purple-100 rounded-lg group-hover:bg-purple-200 transition-colors">
                    <Music2 className="h-6 w-6 text-purple-600" />
                  </div>
                  <div className="text-left">
                    <h3 className="font-semibold text-gray-900">Browse Library</h3>
                    <p className="text-sm text-gray-600">View your audio files and analyses</p>
                  </div>
                </div>
              </Link>
            </div>
          </CardContent>
        </Card>

        {/* Account Information */}
        <Card variant="bordered">
          <CardHeader>
            <CardTitle>Account Information</CardTitle>
            <CardDescription>Your profile details and settings</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex justify-between items-center py-3 border-b">
                <span className="text-sm text-gray-600">Email</span>
                <span className="font-medium text-gray-900">{user.email}</span>
              </div>
              <div className="flex justify-between items-center py-3 border-b">
                <span className="text-sm text-gray-600">Username</span>
                <span className="font-medium text-gray-900">{user.username}</span>
              </div>
              <div className="flex justify-between items-center py-3 border-b">
                <span className="text-sm text-gray-600">Member Since</span>
                <span className="font-medium text-gray-900">
                  {new Date(user.created_at).toLocaleDateString('en-US', {
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric'
                  })}
                </span>
              </div>
              <div className="flex justify-between items-center py-3 border-b">
                <span className="text-sm text-gray-600">Email Verified</span>
                <Badge variant={user.is_verified ? 'success' : 'warning'}>
                  {user.is_verified ? 'Verified' : 'Not Verified'}
                </Badge>
              </div>
              <div className="flex justify-between items-center py-3">
                <span className="text-sm text-gray-600">Account Status</span>
                <Badge variant={user.is_active ? 'success' : 'error'}>
                  {user.is_active ? 'Active' : 'Inactive'}
                </Badge>
              </div>
            </div>
            <div className="mt-6 pt-6 border-t">
              <Link href="/settings">
                <Button variant="outline" className="w-full">
                  Manage Account Settings
                </Button>
              </Link>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
