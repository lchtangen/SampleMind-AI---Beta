/**
 * @fileoverview Unified App Shell layout for all authenticated pages.
 *
 * Wraps dashboard, library, upload, search, analytics, settings, collections,
 * gallery, and generate pages with a persistent sidebar + top bar.
 *
 * Uses Next.js 15 Route Groups — the `(app)` folder does NOT appear in the URL.
 * Pages inside this group automatically get the sidebar/topbar chrome.
 *
 * Layout hierarchy:
 *   RootLayout → (app)/layout → page content
 *
 * @module app/(app)/layout
 */

'use client';

import { useState, useCallback } from 'react';
import { usePathname, useRouter } from 'next/navigation';
import Link from 'next/link';
import { motion, AnimatePresence } from 'framer-motion';
import {
  LayoutDashboard,
  Music2,
  Upload,
  Search,
  BarChart3,
  Settings,
  FolderOpen,
  Sparkles,
  Sliders,
  ChevronLeft,
  ChevronRight,
  LogOut,
  User,
  Bell,
  Command,
  Gauge,
  AudioWaveform,
} from 'lucide-react';
import { useAuthContext } from '@/contexts/AuthContext';
import ProtectedRoute from '@/components/ProtectedRoute';

// ─── Navigation items ────────────────────────────────────────────────────────

interface NavItem {
  /** Display label */
  label: string;
  /** Route path */
  href: string;
  /** Lucide icon component */
  icon: React.ComponentType<{ className?: string }>;
  /** Optional badge count */
  badge?: number;
  /** Group divider label (shown above this item) */
  group?: string;
}

const NAV_ITEMS: NavItem[] = [
  { label: 'Dashboard',   href: '/dashboard',   icon: LayoutDashboard, group: 'Main' },
  { label: 'Library',     href: '/library',     icon: Music2 },
  { label: 'Upload',      href: '/upload',      icon: Upload },
  { label: 'Search',      href: '/search',      icon: Search },
  { label: 'Analytics',   href: '/analytics',   icon: BarChart3, group: 'Tools' },
  { label: 'Effects',     href: '/effects',     icon: Sliders },
  { label: 'Generate',    href: '/generate',    icon: Sparkles },
  { label: 'Collections', href: '/collections', icon: FolderOpen },
  { label: 'Gallery',     href: '/gallery',     icon: AudioWaveform },
  { label: 'Settings',    href: '/settings',    icon: Settings, group: 'Account' },
];

// ─── Sidebar Component ───────────────────────────────────────────────────────

function AppSidebar({
  collapsed,
  onToggle,
}: {
  collapsed: boolean;
  onToggle: () => void;
}) {
  const pathname = usePathname();

  return (
    <motion.aside
      initial={false}
      animate={{ width: collapsed ? 72 : 256 }}
      transition={{ duration: 0.25, ease: [0.4, 0, 0.2, 1] }}
      className="fixed left-0 top-0 bottom-0 z-40 flex flex-col
                 bg-dark-600/80 backdrop-blur-xl border-r border-glass-border"
    >
      {/* ── Logo ─────────────────────────────────────────────────────── */}
      <div className="flex items-center h-16 px-4 border-b border-glass-border">
        <Link href="/dashboard" className="flex items-center gap-3 group">
          <div className="h-9 w-9 rounded-lg bg-gradient-to-br from-cyber-cyan to-cyber-purple
                          flex items-center justify-center shadow-glow-cyan
                          group-hover:shadow-glow-purple transition-shadow duration-300">
            <span className="text-white font-bold text-lg">SM</span>
          </div>
          <AnimatePresence>
            {!collapsed && (
              <motion.span
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -10 }}
                className="text-lg font-bold bg-gradient-to-r from-cyber-cyan to-cyber-purple
                           bg-clip-text text-transparent whitespace-nowrap"
              >
                SampleMind
              </motion.span>
            )}
          </AnimatePresence>
        </Link>
      </div>

      {/* ── Navigation Links ─────────────────────────────────────────── */}
      <nav className="flex-1 overflow-y-auto py-4 px-2 space-y-1">
        {NAV_ITEMS.map((item, i) => {
          const isActive =
            pathname === item.href || pathname.startsWith(item.href + '/');

          return (
            <div key={item.href}>
              {/* Group divider label */}
              {item.group && !collapsed && (
                <p className="px-3 pt-4 pb-1 text-[10px] uppercase tracking-widest
                              text-text-tertiary font-semibold">
                  {item.group}
                </p>
              )}
              {item.group && collapsed && i > 0 && (
                <div className="mx-auto my-2 w-6 border-t border-glass-border" />
              )}

              <Link
                href={item.href}
                className={`
                  group relative flex items-center gap-3 rounded-lg px-3 py-2.5
                  text-sm font-medium transition-all duration-200
                  ${isActive
                    ? 'bg-cyber-cyan/10 text-cyber-cyan shadow-inner'
                    : 'text-text-secondary hover:text-text-primary hover:bg-glass-light'
                  }
                `}
              >
                {/* Active indicator bar */}
                {isActive && (
                  <motion.div
                    layoutId="sidebar-active"
                    className="absolute left-0 top-1 bottom-1 w-[3px] rounded-full
                               bg-gradient-to-b from-cyber-cyan to-cyber-purple"
                    transition={{ type: 'spring', stiffness: 500, damping: 35 }}
                  />
                )}

                <item.icon
                  className={`h-5 w-5 flex-shrink-0 transition-colors
                    ${isActive ? 'text-cyber-cyan' : 'text-text-tertiary group-hover:text-text-secondary'}
                  `}
                />

                <AnimatePresence>
                  {!collapsed && (
                    <motion.span
                      initial={{ opacity: 0, x: -8 }}
                      animate={{ opacity: 1, x: 0 }}
                      exit={{ opacity: 0, x: -8 }}
                      className="truncate"
                    >
                      {item.label}
                    </motion.span>
                  )}
                </AnimatePresence>

                {/* Badge */}
                {item.badge && item.badge > 0 && (
                  <span className="ml-auto text-[10px] font-bold bg-cyber-magenta/20
                                   text-cyber-magenta px-1.5 py-0.5 rounded-full">
                    {item.badge}
                  </span>
                )}

                {/* Hover tooltip when collapsed */}
                {collapsed && (
                  <div className="absolute left-full ml-2 px-2 py-1 rounded-md
                                  bg-dark-300 text-text-primary text-xs whitespace-nowrap
                                  opacity-0 group-hover:opacity-100 pointer-events-none
                                  transition-opacity z-50 shadow-glass-sm">
                    {item.label}
                  </div>
                )}
              </Link>
            </div>
          );
        })}
      </nav>

      {/* ── Collapse toggle ──────────────────────────────────────────── */}
      <div className="px-2 py-3 border-t border-glass-border">
        <button
          onClick={onToggle}
          className="w-full flex items-center justify-center gap-2 rounded-lg px-3 py-2
                     text-text-tertiary hover:text-text-secondary hover:bg-glass-light
                     transition-colors text-sm"
          aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        >
          {collapsed ? (
            <ChevronRight className="h-4 w-4" />
          ) : (
            <>
              <ChevronLeft className="h-4 w-4" />
              <span>Collapse</span>
            </>
          )}
        </button>
      </div>
    </motion.aside>
  );
}

// ─── TopBar Component ────────────────────────────────────────────────────────

function AppTopBar({ sidebarCollapsed }: { sidebarCollapsed: boolean }) {
  const pathname = usePathname();
  const { user, logout } = useAuthContext();
  const router = useRouter();

  // Derive page title from pathname
  const pageTitle = NAV_ITEMS.find(
    (item) =>
      pathname === item.href || pathname.startsWith(item.href + '/')
  )?.label ?? 'SampleMind AI';

  return (
    <header
      className="sticky top-0 z-30 h-16 flex items-center justify-between
                 px-6 bg-dark-500/60 backdrop-blur-xl border-b border-glass-border"
      style={{ marginLeft: sidebarCollapsed ? 72 : 256 }}
    >
      {/* Left: breadcrumb / page title */}
      <div className="flex items-center gap-3">
        <h1 className="text-lg font-semibold text-text-primary">{pageTitle}</h1>
      </div>

      {/* Right: actions */}
      <div className="flex items-center gap-4">
        {/* Keyboard shortcut hint */}
        <button
          className="hidden md:flex items-center gap-1.5 px-3 py-1.5 rounded-lg
                     bg-glass-light border border-glass-border text-text-tertiary text-xs
                     hover:text-text-secondary transition-colors"
          onClick={() => {
            // Could trigger command palette
          }}
        >
          <Command className="h-3 w-3" />
          <span>K</span>
        </button>

        {/* Notifications */}
        <button
          className="relative p-2 rounded-lg text-text-tertiary
                     hover:text-text-primary hover:bg-glass-light transition-colors"
          aria-label="Notifications"
        >
          <Bell className="h-5 w-5" />
          <span className="absolute top-1.5 right-1.5 h-2 w-2 rounded-full
                           bg-cyber-magenta animate-pulse" />
        </button>

        {/* User menu */}
        <div className="flex items-center gap-3 pl-3 border-l border-glass-border">
          <div className="h-8 w-8 rounded-full bg-gradient-to-br from-cyber-cyan to-cyber-purple
                          flex items-center justify-center text-xs font-bold text-white">
            {user?.email?.[0]?.toUpperCase() ?? 'U'}
          </div>
          <div className="hidden sm:block">
            <p className="text-sm font-medium text-text-primary leading-tight">
              {user?.full_name || user?.email?.split('@')[0] || 'User'}
            </p>
            <p className="text-[11px] text-text-tertiary leading-tight">Pro Plan</p>
          </div>
          <button
            onClick={async () => {
              await logout();
              router.push('/');
            }}
            className="p-1.5 rounded-md text-text-tertiary hover:text-error
                       hover:bg-error/10 transition-colors"
            aria-label="Logout"
          >
            <LogOut className="h-4 w-4" />
          </button>
        </div>
      </div>
    </header>
  );
}

// ─── App Shell Layout ────────────────────────────────────────────────────────

/**
 * Wraps all authenticated pages with sidebar + topbar chrome.
 *
 * The sidebar is collapsible (state persisted in `localStorage`).
 * The main content area expands/contracts with a smooth animation.
 */
export default function AppShellLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const [collapsed, setCollapsed] = useState(() => {
    if (typeof window === 'undefined') return false;
    return localStorage.getItem('sidebar-collapsed') === 'true';
  });

  const toggle = useCallback(() => {
    setCollapsed((prev) => {
      const next = !prev;
      localStorage.setItem('sidebar-collapsed', String(next));
      return next;
    });
  }, []);

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-dark-500">
        <AppSidebar collapsed={collapsed} onToggle={toggle} />
        <AppTopBar sidebarCollapsed={collapsed} />

        {/* Main content area — shifts right to accommodate sidebar */}
        <motion.main
          initial={false}
          animate={{ marginLeft: collapsed ? 72 : 256 }}
          transition={{ duration: 0.25, ease: [0.4, 0, 0.2, 1] }}
          className="min-h-[calc(100vh-4rem)] p-6"
        >
          {children}
        </motion.main>
      </div>
    </ProtectedRoute>
  );
}
