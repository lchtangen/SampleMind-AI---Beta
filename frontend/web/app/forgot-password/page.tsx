'use client'

import { useState, FormEvent } from 'react'
import Link from 'next/link'
import { toast } from 'react-hot-toast'
import { ArrowLeft, Mail } from 'lucide-react'

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [emailSent, setEmailSent] = useState(false)

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()

    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      toast.error('Please enter a valid email address')
      return
    }

    setIsLoading(true)

    try {
      // Note: Implement password reset API endpoint
      // await api.requestPasswordReset(email)
      
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1500))
      
      setEmailSent(true)
      toast.success('Password reset email sent!')
    } catch (error) {
      const err = error as { response?: { data?: { detail?: string } } }
      toast.error(err.response?.data?.detail || 'Failed to send reset email')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 px-4">
      <div className="max-w-md w-full space-y-8">
        <div className="text-center">
          <h1 className="text-4xl font-bold text-gray-900">SampleMind AI</h1>
          <p className="mt-2 text-gray-600">AI-Powered Music Production</p>
        </div>

        <div className="bg-white p-8 rounded-2xl shadow-xl">
          {!emailSent ? (
            <>
              <div className="mb-6">
                <h2 className="text-2xl font-semibold text-gray-900">Reset your password</h2>
                <p className="text-sm text-gray-600 mt-2">
                  Enter your email address and we'll send you a link to reset your password.
                </p>
              </div>
              
              <form onSubmit={handleSubmit} className="space-y-6">
                <div>
                  <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                    Email Address
                  </label>
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                      <Mail className="h-5 w-5 text-gray-400" />
                    </div>
                    <input
                      id="email"
                      type="email"
                      required
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                      placeholder="your@email.com"
                      disabled={isLoading}
                    />
                  </div>
                </div>

                <button
                  type="submit"
                  disabled={isLoading}
                  className="w-full bg-blue-600 text-white py-3 px-4 rounded-lg font-semibold hover:bg-blue-700 focus:ring-4 focus:ring-blue-300 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                >
                  {isLoading ? 'Sending...' : 'Send Reset Link'}
                </button>
              </form>
            </>
          ) : (
            <div className="text-center space-y-4">
              <div className="flex items-center justify-center mb-4">
                <div className="p-4 bg-green-100 rounded-full">
                  <Mail className="h-12 w-12 text-green-600" />
                </div>
              </div>
              
              <h2 className="text-2xl font-semibold text-gray-900">Check your email</h2>
              <p className="text-gray-600">
                We've sent a password reset link to <strong>{email}</strong>
              </p>
              <p className="text-sm text-gray-500">
                Don't see the email? Check your spam folder or try again.
              </p>
              
              <button
                onClick={() => {
                  setEmailSent(false)
                  setEmail('')
                }}
                className="text-blue-600 hover:text-blue-700 font-medium text-sm"
              >
                Send to a different email
              </button>
            </div>
          )}

          <div className="mt-6 text-center">
            <Link 
              href="/login" 
              className="inline-flex items-center gap-2 text-sm text-gray-600 hover:text-gray-900 font-medium"
            >
              <ArrowLeft size={16} />
              Back to sign in
            </Link>
          </div>
        </div>

        <div className="text-center text-sm text-gray-500">
          <p>© 2025 SampleMind AI. All rights reserved.</p>
        </div>
      </div>
    </div>
  )
}
