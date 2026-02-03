'use client';

import { useState } from 'react';
import Link from 'next/link';
import {
  User,
  Key,
  Sliders,
  Cloud,
  ChevronRight,
  Lock,
  Database,
  Bell,
  Shield
} from 'lucide-react';

interface SettingsSection {
  title: string;
  description: string;
  href: string;
  icon: React.ReactNode;
  badge?: string;
}

const settingsSections: SettingsSection[] = [
  {
    title: 'Profile',
    description: 'Manage your account information',
    href: '/settings/profile',
    icon: <User className="w-5 h-5" />,
  },
  {
    title: 'Preferences',
    description: 'Customize your analysis and UI settings',
    href: '/settings/preferences',
    icon: <Sliders className="w-5 h-5" />,
  },
  {
    title: 'API Keys',
    description: 'Manage API keys for external access',
    href: '/settings/api-keys',
    icon: <Key className="w-5 h-5" />,
  },
  {
    title: 'Cloud Sync',
    description: 'Configure cloud synchronization settings',
    href: '/settings/cloud',
    icon: <Cloud className="w-5 h-5" />,
  },
  {
    title: 'Notifications',
    description: 'Manage notification preferences',
    href: '/settings/notifications',
    icon: <Bell className="w-5 h-5" />,
  },
  {
    title: 'Storage',
    description: 'View storage usage and management',
    href: '/settings/storage',
    icon: <Database className="w-5 h-5" />,
  },
  {
    title: 'Privacy',
    description: 'Control privacy and data settings',
    href: '/settings/privacy',
    icon: <Shield className="w-5 h-5" />,
  },
  {
    title: 'Security',
    description: 'Manage password and security options',
    href: '/settings/security',
    icon: <Lock className="w-5 h-5" />,
  },
];

export default function SettingsPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Header */}
        <div className="mb-12">
          <h1 className="text-4xl font-bold text-white mb-2">Settings</h1>
          <p className="text-slate-400">
            Manage your account, preferences, and configuration
          </p>
        </div>

        {/* Settings Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {settingsSections.map((section) => (
            <Link
              key={section.href}
              href={section.href}
              className="group relative overflow-hidden rounded-lg bg-slate-800/50 backdrop-blur border border-slate-700/50 hover:border-slate-600 transition-all duration-300 hover:shadow-lg hover:shadow-blue-500/10"
            >
              {/* Background gradient on hover */}
              <div className="absolute inset-0 bg-gradient-to-br from-blue-500/5 to-purple-500/5 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />

              <div className="relative p-6">
                {/* Icon and Badge */}
                <div className="flex items-start justify-between mb-4">
                  <div className="w-12 h-12 rounded-lg bg-blue-500/10 border border-blue-500/30 flex items-center justify-center text-blue-400 group-hover:bg-blue-500/20 transition-colors">
                    {section.icon}
                  </div>
                  {section.badge && (
                    <span className="text-xs font-semibold px-2 py-1 rounded-full bg-amber-500/20 text-amber-300">
                      {section.badge}
                    </span>
                  )}
                </div>

                {/* Content */}
                <h3 className="text-lg font-semibold text-white mb-2 group-hover:text-blue-400 transition-colors">
                  {section.title}
                </h3>
                <p className="text-sm text-slate-400 mb-4">
                  {section.description}
                </p>

                {/* Arrow */}
                <div className="flex items-center text-blue-400 text-sm font-medium">
                  View Settings
                  <ChevronRight className="w-4 h-4 ml-2 group-hover:translate-x-1 transition-transform" />
                </div>
              </div>
            </Link>
          ))}
        </div>

        {/* Help Section */}
        <div className="mt-12 p-6 rounded-lg bg-slate-800/50 backdrop-blur border border-slate-700/50">
          <h3 className="text-lg font-semibold text-white mb-2">Need Help?</h3>
          <p className="text-slate-400 text-sm">
            Check our documentation or contact support for assistance with your settings.
          </p>
        </div>
      </div>
    </div>
  );
}
