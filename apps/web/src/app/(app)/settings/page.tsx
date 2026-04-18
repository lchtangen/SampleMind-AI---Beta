/**
 * @fileoverview Settings page for the SampleMind AI app shell.
 *
 * Vertical category nav (Profile, API Keys, Cloud Sync, Preferences) with
 * a right-side content panel showing profile form fields and save button.
 *
 * @module app/(app)/settings/page
 */

'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  User,
  KeyRound,
  Cloud,
  SlidersHorizontal,
  Save,
} from 'lucide-react';

// ─── Animation variants ──────────────────────────────────────────────────────

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.08, delayChildren: 0.1 },
  },
};

const itemVariants = {
  hidden: { opacity: 0, y: 16 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.4, ease: [0.4, 0, 0.2, 1] } },
};

// ─── Static data ─────────────────────────────────────────────────────────────

interface SettingsCategory {
  id: string;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
}

const CATEGORIES: SettingsCategory[] = [
  { id: 'profile', label: 'Profile', icon: User },
  { id: 'api-keys', label: 'API Keys', icon: KeyRound },
  { id: 'cloud-sync', label: 'Cloud Sync', icon: Cloud },
  { id: 'preferences', label: 'Preferences', icon: SlidersHorizontal },
];

// ─── Page Component ──────────────────────────────────────────────────────────

export default function SettingsPage() {
  const [activeCategory, setActiveCategory] = useState('profile');
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="flex flex-col lg:flex-row gap-6"
    >
      {/* ── Category Nav ──────────────────────────────────────────────── */}
      <motion.nav variants={itemVariants} className="lg:w-56 flex-shrink-0">
        <div className="glass rounded-glass p-2 flex flex-row lg:flex-col gap-1">
          {CATEGORIES.map((cat) => {
            const isActive = activeCategory === cat.id;
            return (
              <button
                key={cat.id}
                onClick={() => setActiveCategory(cat.id)}
                className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium
                            transition-all duration-200 w-full text-left
                            ${isActive
                              ? 'bg-cyber-cyan/10 text-cyber-cyan'
                              : 'text-text-secondary hover:text-text-primary hover:bg-glass-light'
                            }`}
              >
                <cat.icon className={`h-4 w-4 ${isActive ? 'text-cyber-cyan' : 'text-text-tertiary'}`} />
                <span className="hidden lg:inline">{cat.label}</span>
              </button>
            );
          })}
        </div>
      </motion.nav>

      {/* ── Content Area ──────────────────────────────────────────────── */}
      <motion.div variants={itemVariants} className="flex-1 glass rounded-glass p-6 space-y-6">
        {activeCategory === 'profile' && (
          <>
            <div>
              <h2 className="text-lg font-semibold text-text-primary mb-1">Profile</h2>
              <p className="text-sm text-text-tertiary">Manage your account information</p>
            </div>

            {/* Name field */}
            <div className="space-y-1.5">
              <label htmlFor="settings-name" className="text-xs font-medium text-text-secondary uppercase tracking-wider">
                Display Name
              </label>
              <input
                id="settings-name"
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Your name"
                className="w-full px-4 py-2.5 rounded-glass-sm bg-dark-400 border border-glass-border
                           text-text-primary placeholder-text-tertiary text-sm outline-none
                           focus:border-cyber-cyan/50 focus:shadow-glow-cyan transition-all duration-200"
              />
            </div>

            {/* Email field */}
            <div className="space-y-1.5">
              <label htmlFor="settings-email" className="text-xs font-medium text-text-secondary uppercase tracking-wider">
                Email Address
              </label>
              <input
                id="settings-email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@example.com"
                className="w-full px-4 py-2.5 rounded-glass-sm bg-dark-400 border border-glass-border
                           text-text-primary placeholder-text-tertiary text-sm outline-none
                           focus:border-cyber-cyan/50 focus:shadow-glow-cyan transition-all duration-200"
              />
            </div>

            {/* Save */}
            <div className="pt-2">
              <button
                className="px-6 py-2.5 rounded-glass-sm font-semibold text-sm
                           bg-gradient-to-r from-cyber-cyan to-cyber-purple text-white
                           hover:shadow-glow-cyan transition-shadow duration-300
                           flex items-center gap-2"
              >
                <Save className="h-4 w-4" />
                Save Changes
              </button>
            </div>
          </>
        )}

        {activeCategory === 'api-keys' && (
          <div className="py-12 text-center">
            <KeyRound className="h-10 w-10 text-text-tertiary/30 mx-auto mb-3" />
            <p className="text-text-secondary font-medium">API Key Management</p>
            <p className="text-sm text-text-tertiary mt-1">Configure provider keys for AI services</p>
          </div>
        )}

        {activeCategory === 'cloud-sync' && (
          <div className="py-12 text-center">
            <Cloud className="h-10 w-10 text-text-tertiary/30 mx-auto mb-3" />
            <p className="text-text-secondary font-medium">Cloud Sync Settings</p>
            <p className="text-sm text-text-tertiary mt-1">Multi-device Supabase Realtime sync configuration</p>
          </div>
        )}

        {activeCategory === 'preferences' && (
          <div className="py-12 text-center">
            <SlidersHorizontal className="h-10 w-10 text-text-tertiary/30 mx-auto mb-3" />
            <p className="text-text-secondary font-medium">Preferences</p>
            <p className="text-sm text-text-tertiary mt-1">Theme, analysis defaults, and notification settings</p>
          </div>
        )}
      </motion.div>
    </motion.div>
  );
}
