'use client'

import { useState, useEffect, FormEvent } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { useAuthStore } from '@/store/useAuthStore'
import { toast } from 'react-hot-toast'

// Password strength calculation
const calculatePasswordStrength = (password: string): { score: number; label: string; color: string; feedback: string } => {
  let score = 0
  
  if (password.length >= 8) score++
  if (password.length >= 12) score++
  if (/[a-z]/.test(password)) score++
  if (/[A-Z]/.test(password)) score++
  if (/[0-9]/.test(password)) score++
  if (/[^a-zA-Z0-9]/.test(password)) score++
  
  let label = 'Very Weak'
  let color = 'bg-red-500'
  let feedback = 'Too weak'
  
  if (score >= 6) {
    label = 'Strong'
    color = 'bg-green-500'
    feedback = 'Great password!'
  } else if (score >= 4) {
    label = 'Good'
    color = 'bg-yellow-500'
    feedback = 'Add special characters for better security'
  } else if (score >= 3) {
    label = 'Fair'
    color = 'bg-orange-500'
    feedback = 'Add uppercase letters and numbers'
  } else if (score >= 1) {
    label = 'Weak'
    color = 'bg-red-400'
    feedback = 'Make it longer and add variety'
  }
  
  return { score, label, color, feedback }
}

export default function RegisterPage() {
  const [email, setEmail] = useState('')
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [agreedToTerms, setAgreedToTerms] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [passwordStrength, setPasswordStrength] = useState({ score: 0, label: '', color: '', feedback: '' })
  const { register } = useAuthStore()
  const router = useRouter()
  
  // Update password strength when password changes
  useEffect(() => {
    if (password) {
      setPasswordStrength(calculatePasswordStrength(password))
    } else {
      setPasswordStrength({ score: 0, label: '', color: '', feedback: '' })
    }
  }, [password])

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()

    if (password !== confirmPassword) {
      toast.error('Passwords do not match')
      return
    }

    if (password.length < 8) {
      toast.error('Password must be at least 8 characters')
      return
    }
    
    if (passwordStrength.score < 3) {
      toast.error('Please use a stronger password')
      return
    }
    
    if (!agreedToTerms) {
      toast.error('You must agree to the Terms of Service and Privacy Policy')
      return
    }

    setIsLoading(true)

    try {
      // FUTURE FEATURE v1.1+: Add email verification flow
      // After successful registration, send verification email
      // and redirect to email-verification-pending page
      
      await register(email, username, password)
      toast.success('Account created successfully!')
      router.push('/dashboard')
    } catch (error) {
      const err = error as { response?: { data?: { detail?: string } } }
      const errorMsg = err.response?.data?.detail || 'Registration failed. Please try again.'
      toast.error(errorMsg)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 px-4 py-12">
      <div className="max-w-md w-full space-y-8">
        <div className="text-center">
          <h1 className="text-4xl font-bold text-gray-900">SampleMind AI</h1>
          <p className="mt-2 text-gray-600">AI-Powered Music Production</p>
        </div>

        <div className="bg-white p-8 rounded-2xl shadow-xl">
          <h2 className="text-2xl font-semibold text-gray-900 mb-6">Create your account</h2>
          
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                Email Address
              </label>
              <input
                id="email"
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                placeholder="your@email.com"
                disabled={isLoading}
              />
            </div>

            <div>
              <label htmlFor="username" className="block text-sm font-medium text-gray-700 mb-2">
                Username
              </label>
              <input
                id="username"
                type="text"
                required
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                placeholder="Choose a username"
                disabled={isLoading}
                minLength={3}
                maxLength={50}
                pattern="[a-zA-Z0-9_]+"
                title="Username can only contain letters, numbers, and underscores"
              />
              <p className="mt-1 text-xs text-gray-500">3-50 characters, letters, numbers, and underscores only</p>
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
                Password
              </label>
              <input
                id="password"
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                placeholder="Create a strong password"
                disabled={isLoading}
                minLength={8}
              />
              
              {/* Password Strength Indicator */}
              {password && (
                <div className="mt-3">
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-xs font-medium text-gray-700">Password Strength:</span>
                    <span className="text-xs font-semibold" style={{ color: passwordStrength.score >= 4 ? '#10b981' : passwordStrength.score >= 3 ? '#f59e0b' : '#ef4444' }}>
                      {passwordStrength.label}
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
                    <div 
                      className={`h-full transition-all duration-300 ${passwordStrength.color}`}
                      style={{ width: `${(passwordStrength.score / 6) * 100}%` }}
                    />
                  </div>
                  <p className="mt-1 text-xs text-gray-600">{passwordStrength.feedback}</p>
                </div>
              )}
              
              <p className="mt-2 text-xs text-gray-500">Minimum 8 characters. Include uppercase, lowercase, number, and special characters.</p>
            </div>

            <div>
              <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-700 mb-2">
                Confirm Password
              </label>
              <input
                id="confirmPassword"
                type="password"
                required
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                placeholder="Confirm your password"
                disabled={isLoading}
              />
              {confirmPassword && password !== confirmPassword && (
                <p className="mt-1 text-xs text-red-600">Passwords do not match</p>
              )}
              {confirmPassword && password === confirmPassword && (
                <p className="mt-1 text-xs text-green-600">✓ Passwords match</p>
              )}
            </div>
            
            {/* Terms of Service Checkbox */}
            <div className="flex items-start">
              <input
                id="terms"
                type="checkbox"
                checked={agreedToTerms}
                onChange={(e) => setAgreedToTerms(e.target.checked)}
                className="mt-1 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded cursor-pointer flex-shrink-0"
                disabled={isLoading}
                required
              />
              <label htmlFor="terms" className="ml-2 block text-sm text-gray-700 cursor-pointer">
                I agree to the{' '}
                <Link href="/terms" className="text-blue-600 hover:text-blue-700 font-medium" target="_blank">
                  Terms of Service
                </Link>
                {' '}and{' '}
                <Link href="/privacy" className="text-blue-600 hover:text-blue-700 font-medium" target="_blank">
                  Privacy Policy
                </Link>
              </label>
            </div>
            
            {/* FUTURE FEATURE v1.1+: Add CAPTCHA protection for bot prevention */}

            <button
              type="submit"
              disabled={isLoading}
              className="w-full bg-blue-600 text-white py-3 px-4 rounded-lg font-semibold hover:bg-blue-700 focus:ring-4 focus:ring-blue-300 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
            >
              {isLoading ? 'Creating account...' : 'Create account'}
            </button>
          </form>

          <div className="mt-6 text-center">
            <p className="text-sm text-gray-600">
              Already have an account?{' '}
              <Link href="/login" className="text-blue-600 hover:text-blue-700 font-medium">
                Sign in
              </Link>
            </p>
          </div>
        </div>

        <div className="text-center text-sm text-gray-500">
          <p>© 2025 SampleMind AI. All rights reserved.</p>
        </div>
      </div>
    </div>
  )
}
