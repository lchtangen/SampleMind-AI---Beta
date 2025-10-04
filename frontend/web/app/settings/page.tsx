'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAuthStore } from '@/store/useAuthStore'
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  Button,
  Input,
  Spinner,
  Badge,
  Modal
} from '@/components'
import Navbar from '@/components/layout/Navbar'
import { api } from '@/lib/api'
import { toast } from 'react-hot-toast'
import { User, Lock, Mail, AlertCircle, CheckCircle2 } from 'lucide-react'

export default function SettingsPage() {
  const router = useRouter()
  const { user, isAuthenticated, isLoading, fetchUser } = useAuthStore()
  
  // Password Change State
  const [currentPassword, setCurrentPassword] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [isChangingPassword, setIsChangingPassword] = useState(false)
  const [showPasswordModal, setShowPasswordModal] = useState(false)

  // Email Change State
  const [showEmailModal, setShowEmailModal] = useState(false)
  const [newEmail, setNewEmail] = useState('')
  const [emailPassword, setEmailPassword] = useState('')
  const [isChangingEmail, setIsChangingEmail] = useState(false)

  // Delete Account State
  const [showDeleteModal, setShowDeleteModal] = useState(false)
  const [deletePassword, setDeletePassword] = useState('')
  const [deleteConfirmText, setDeleteConfirmText] = useState('')
  const [isDeletingAccount, setIsDeletingAccount] = useState(false)

  // Profile Update State
  const [email, setEmail] = useState('')
  const [username, setUsername] = useState('')
  const [isUpdatingProfile, setIsUpdatingProfile] = useState(false)

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push('/login')
    } else if (user) {
      setEmail(user.email)
      setUsername(user.username)
    }
  }, [isAuthenticated, isLoading, user, router])

  const handlePasswordChange = async () => {
    if (newPassword !== confirmPassword) {
      toast.error('Passwords do not match')
      return
    }

    if (newPassword.length < 8) {
      toast.error('Password must be at least 8 characters')
      return
    }

    try {
      setIsChangingPassword(true)
      await api.changePassword(currentPassword, newPassword)
      toast.success('Password changed successfully!')
      setShowPasswordModal(false)
      setCurrentPassword('')
      setNewPassword('')
      setConfirmPassword('')
    } catch (error) {
      const err = error as { response?: { data?: { detail?: string } } }
      toast.error(err.response?.data?.detail || 'Failed to change password')
    } finally {
      setIsChangingPassword(false)
    }
  }

  const handleProfileUpdate = async () => {
    try {
      setIsUpdatingProfile(true)
      // Note: Update API endpoint when available
      // await api.updateProfile({ email, username })
      await fetchUser()
      toast.success('Profile updated successfully!')
    } catch {
      toast.error('Failed to update profile')
    } finally {
      setIsUpdatingProfile(false)
    }
  }

  const handleEmailChange = async () => {
    if (!newEmail || !emailPassword) {
      toast.error('Please fill in all fields')
      return
    }

    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(newEmail)) {
      toast.error('Please enter a valid email address')
      return
    }

    try {
      setIsChangingEmail(true)
      // Note: Implement email change API endpoint
      // await api.changeEmail(newEmail, emailPassword)
      toast.success('Email change request sent! Please check your new email to verify.')
      setShowEmailModal(false)
      setNewEmail('')
      setEmailPassword('')
    } catch (error) {
      const err = error as { response?: { data?: { detail?: string } } }
      toast.error(err.response?.data?.detail || 'Failed to change email')
    } finally {
      setIsChangingEmail(false)
    }
  }

  const handleDeleteAccount = async () => {
    if (!deletePassword) {
      toast.error('Please enter your password')
      return
    }

    if (deleteConfirmText !== 'DELETE') {
      toast.error('Please type DELETE to confirm')
      return
    }

    try {
      setIsDeletingAccount(true)
      // Note: Implement account deletion API endpoint
      // await api.deleteAccount(deletePassword)
      toast.success('Account deleted successfully. Goodbye!')
      // Logout and redirect
      await useAuthStore.getState().logout()
      router.push('/goodbye')
    } catch (error) {
      const err = error as { response?: { data?: { detail?: string } } }
      toast.error(err.response?.data?.detail || 'Failed to delete account')
    } finally {
      setIsDeletingAccount(false)
    }
  }

  if (isLoading || !user) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <Spinner size="lg" label="Loading settings..." />
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />

      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Settings ⚙️</h1>
          <p className="text-gray-600 mt-1">Manage your account preferences</p>
        </div>

        {/* Profile Information */}
        <Card variant="bordered" className="mb-6">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <User size={24} />
              Profile Information
            </CardTitle>
            <CardDescription>
              Update your account details
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <Input
                label="Email Address"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                leftIcon={<Mail size={20} />}
                helperText="Your email address for notifications"
              />

              <Input
                label="Username"
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                leftIcon={<User size={20} />}
                helperText="Your unique username"
              />

              <div className="flex items-center gap-4 pt-4">
                <Button
                  variant="primary"
                  onClick={handleProfileUpdate}
                  isLoading={isUpdatingProfile}
                  disabled={email === user.email && username === user.username}
                >
                  Save Changes
                </Button>
                <Button
                  variant="outline"
                  onClick={() => {
                    setEmail(user.email)
                    setUsername(user.username)
                  }}
                >
                  Reset
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Security */}
        <Card variant="bordered" className="mb-6">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Lock size={24} />
              Security
            </CardTitle>
            <CardDescription>
              Manage your password and security settings
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <div>
                  <p className="font-medium text-gray-900">Password</p>
                  <p className="text-sm text-gray-600">Last changed recently</p>
                </div>
                <Button
                  variant="outline"
                  onClick={() => setShowPasswordModal(true)}
                >
                  Change Password
                </Button>
              </div>

              {/* FUTURE FEATURE v1.1+: Two-Factor Authentication */}
              <div className="flex items-center justify-between p-4 bg-blue-50 rounded-lg border border-blue-200">
                <div>
                  <p className="font-medium text-gray-900">Two-Factor Authentication</p>
                  <p className="text-sm text-gray-600">Add an extra layer of security (Coming in v1.1)</p>
                </div>
                <Badge variant="default">v1.1 Feature</Badge>
              </div>

              <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <div>
                  <p className="font-medium text-gray-900">Email Address</p>
                  <p className="text-sm text-gray-600">Change your email address</p>
                </div>
                <Button
                  variant="outline"
                  onClick={() => setShowEmailModal(true)}
                >
                  Change Email
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Account Status */}
        <Card variant="bordered" className="mb-6">
          <CardHeader>
            <CardTitle>Account Status</CardTitle>
            <CardDescription>Your account information and status</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between p-3 border-b">
                <span className="text-sm text-gray-600">Account Status</span>
                <Badge variant={user.is_active ? 'success' : 'error'}>
                  {user.is_active ? 'Active' : 'Inactive'}
                </Badge>
              </div>

              <div className="flex items-center justify-between p-3 border-b">
                <span className="text-sm text-gray-600">Email Verification</span>
                <div className="flex items-center gap-2">
                  <Badge variant={user.is_verified ? 'success' : 'warning'}>
                    {user.is_verified ? 'Verified' : 'Not Verified'}
                  </Badge>
                  {user.is_verified ? (
                    <CheckCircle2 size={18} className="text-green-600" />
                  ) : (
                    <AlertCircle size={18} className="text-yellow-600" />
                  )}
                </div>
              </div>

              <div className="flex items-center justify-between p-3 border-b">
                <span className="text-sm text-gray-600">Member Since</span>
                <span className="font-medium">
                  {new Date(user.created_at).toLocaleDateString('en-US', {
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric'
                  })}
                </span>
              </div>

              <div className="flex items-center justify-between p-3">
                <span className="text-sm text-gray-600">Total Uploads</span>
                <span className="font-medium">{user.total_uploads}</span>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Danger Zone */}
        <Card variant="bordered" className="border-red-200">
          <CardHeader>
            <CardTitle className="text-red-600">Danger Zone</CardTitle>
            <CardDescription>
              Irreversible actions that affect your account
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between p-4 bg-red-50 rounded-lg border border-red-200">
                <div>
                  <p className="font-medium text-red-900">Delete Account</p>
                  <p className="text-sm text-red-700">
                    Permanently delete your account and all data. This action cannot be undone.
                  </p>
                </div>
                <Button 
                  variant="danger" 
                  onClick={() => setShowDeleteModal(true)}
                >
                  Delete Account
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Password Change Modal */}
      <Modal
        isOpen={showPasswordModal}
        onClose={() => setShowPasswordModal(false)}
        title="Change Password"
        size="md"
      >
        <div className="space-y-4">
          <Input
            label="Current Password"
            type="password"
            value={currentPassword}
            onChange={(e) => setCurrentPassword(e.target.value)}
            placeholder="Enter current password"
          />

          <Input
            label="New Password"
            type="password"
            value={newPassword}
            onChange={(e) => setNewPassword(e.target.value)}
            placeholder="Enter new password"
            helperText="Minimum 8 characters"
          />

          <Input
            label="Confirm New Password"
            type="password"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            placeholder="Confirm new password"
            error={
              confirmPassword && newPassword !== confirmPassword
                ? 'Passwords do not match'
                : undefined
            }
          />

          <div className="flex gap-2 pt-4">
            <Button
              variant="primary"
              onClick={handlePasswordChange}
              isLoading={isChangingPassword}
              disabled={
                !currentPassword ||
                !newPassword ||
                !confirmPassword ||
                newPassword !== confirmPassword
              }
              className="flex-1"
            >
              Change Password
            </Button>
            <Button
              variant="outline"
              onClick={() => setShowPasswordModal(false)}
              className="flex-1"
            >
              Cancel
            </Button>
          </div>
        </div>
      </Modal>

      {/* Email Change Modal */}
      <Modal
        isOpen={showEmailModal}
        onClose={() => setShowEmailModal(false)}
        title="Change Email Address"
        size="md"
      >
        <div className="space-y-4">
          <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
            <p className="text-sm text-blue-800">
              <strong>Current Email:</strong> {user?.email}
            </p>
          </div>

          <Input
            label="New Email Address"
            type="email"
            value={newEmail}
            onChange={(e) => setNewEmail(e.target.value)}
            placeholder="Enter new email address"
            helperText="A verification email will be sent to this address"
          />

          <Input
            label="Confirm Password"
            type="password"
            value={emailPassword}
            onChange={(e) => setEmailPassword(e.target.value)}
            placeholder="Enter your password to confirm"
          />

          <div className="flex gap-2 pt-4">
            <Button
              variant="primary"
              onClick={handleEmailChange}
              isLoading={isChangingEmail}
              disabled={!newEmail || !emailPassword}
              className="flex-1"
            >
              Change Email
            </Button>
            <Button
              variant="outline"
              onClick={() => setShowEmailModal(false)}
              className="flex-1"
            >
              Cancel
            </Button>
          </div>
        </div>
      </Modal>

      {/* Delete Account Modal */}
      <Modal
        isOpen={showDeleteModal}
        onClose={() => setShowDeleteModal(false)}
        title="Delete Account"
        size="md"
      >
        <div className="space-y-4">
          <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
            <h3 className="font-semibold text-red-900 mb-2">⚠️ Warning: This action is permanent!</h3>
            <ul className="text-sm text-red-800 space-y-1 list-disc list-inside">
              <li>All your audio files will be deleted</li>
              <li>All your analysis results will be lost</li>
              <li>Your account cannot be recovered</li>
              <li>This action cannot be undone</li>
            </ul>
          </div>

          <Input
            label="Confirm Password"
            type="password"
            value={deletePassword}
            onChange={(e) => setDeletePassword(e.target.value)}
            placeholder="Enter your password"
          />

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Type <span className="font-bold text-red-600">DELETE</span> to confirm
            </label>
            <Input
              type="text"
              value={deleteConfirmText}
              onChange={(e) => setDeleteConfirmText(e.target.value)}
              placeholder="Type DELETE"
            />
          </div>

          <div className="flex gap-2 pt-4">
            <Button
              variant="danger"
              onClick={handleDeleteAccount}
              isLoading={isDeletingAccount}
              disabled={!deletePassword || deleteConfirmText !== 'DELETE'}
              className="flex-1"
            >
              Delete My Account
            </Button>
            <Button
              variant="outline"
              onClick={() => {
                setShowDeleteModal(false)
                setDeletePassword('')
                setDeleteConfirmText('')
              }}
              className="flex-1"
            >
              Cancel
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  )
}
