/**
 * Sidebar Component
 * 
 * Modern sidebar navigation with glassmorphism effect
 */

import { Link, useLocation } from 'react-router-dom';
import {
  LayoutDashboard,
  Music,
  Library,
  Wand2,
  Radio,
  ChevronLeft,
  ChevronRight,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { useAppStore } from '@/store/appStore';
import { cn } from '@/lib/utils';

interface NavItem {
  path: string;
  icon: React.ComponentType<{ className?: string }>;
  label: string;
  badge?: string;
}

const navItems: NavItem[] = [
  { path: '/', icon: LayoutDashboard, label: 'Dashboard' },
  { path: '/analyze', icon: Music, label: 'Analyze' },
  { path: '/library', icon: Library, label: 'Library' },
  { path: '/generate', icon: Wand2, label: 'Generate', badge: 'New' },
  { path: '/streaming', icon: Radio, label: 'Streaming', badge: 'Beta' },
];

export function Sidebar() {
  const location = useLocation();
  const { sidebarOpen, toggleSidebar } = useAppStore((state) => ({
    sidebarOpen: state.ui.sidebarOpen,
    toggleSidebar: state.toggleSidebar,
  }));

  const isActive = (path: string) => location.pathname === path;

  return (
    <>
      {/* Overlay for mobile */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/50 backdrop-blur-sm lg:hidden"
          onClick={toggleSidebar}
        />
      )}

      {/* Sidebar */}
      <aside
        className={cn(
          'fixed left-0 top-16 z-40 h-[calc(100vh-4rem)] border-r border-white/10 bg-slate-900/80 backdrop-blur-xl transition-all duration-300',
          sidebarOpen ? 'w-64' : 'w-20',
          'lg:translate-x-0',
          !sidebarOpen && 'max-lg:-translate-x-full'
        )}
      >
        <div className="flex h-full flex-col">
          {/* Navigation */}
          <nav className="flex-1 space-y-1 p-4">
            {navItems.map((item) => {
              const Icon = item.icon;
              const active = isActive(item.path);

              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={cn(
                    'group relative flex items-center gap-3 rounded-lg px-3 py-2 transition-all',
                    active
                      ? 'bg-gradient-to-r from-purple-500/20 via-blue-500/20 to-cyan-500/20 text-white shadow-lg shadow-purple-500/10'
                      : 'text-slate-400 hover:bg-white/5 hover:text-white'
                  )}
                >
                  {/* Active indicator */}
                  {active && (
                    <span className="absolute left-0 top-1/2 h-8 w-1 -translate-y-1/2 rounded-r-full bg-gradient-to-b from-purple-500 via-blue-500 to-cyan-500" />
                  )}

                  <Icon className={cn('h-5 w-5 flex-shrink-0', active && 'text-cyan-400')} />

                  {sidebarOpen && (
                    <>
                      <span className="flex-1 font-medium">{item.label}</span>
                      {item.badge && (
                        <Badge
                          variant="secondary"
                          className="bg-gradient-to-r from-purple-500 to-cyan-500 text-xs text-white"
                        >
                          {item.badge}
                        </Badge>
                      )}
                    </>
                  )}

                  {/* Tooltip for collapsed state */}
                  {!sidebarOpen && (
                    <div className="absolute left-full ml-2 hidden rounded-lg bg-slate-800 px-3 py-1.5 text-sm text-white shadow-lg group-hover:block">
                      {item.label}
                      {item.badge && (
                        <Badge className="ml-2 bg-purple-500 text-xs">{item.badge}</Badge>
                      )}
                    </div>
                  )}
                </Link>
              );
            })}
          </nav>

          {/* Footer */}
          <div className="border-t border-white/10 p-4">
            <Button
              variant="ghost"
              size={sidebarOpen ? 'default' : 'icon'}
              onClick={toggleSidebar}
              className="w-full text-slate-400 hover:bg-white/5 hover:text-white"
            >
              {sidebarOpen ? (
                <>
                  <ChevronLeft className="mr-2 h-4 w-4" />
                  Collapse
                </>
              ) : (
                <ChevronRight className="h-4 w-4" />
              )}
            </Button>
          </div>

          {/* AI Status Indicator */}
          {sidebarOpen && (
            <div className="border-t border-white/10 p-4">
              <div className="flex items-center gap-3 rounded-lg bg-gradient-to-r from-purple-500/10 via-blue-500/10 to-cyan-500/10 p-3">
                <div className="relative">
                  <div className="h-3 w-3 rounded-full bg-green-500 pulse-glow" />
                </div>
                <div className="flex-1">
                  <p className="text-xs font-medium text-white">AI Models</p>
                  <p className="text-xs text-slate-400">All systems operational</p>
                </div>
              </div>
            </div>
          )}
        </div>
      </aside>

      {/* Spacer to prevent content overlap */}
      <div className={cn('transition-all duration-300', sidebarOpen ? 'lg:w-64' : 'lg:w-20')} />
    </>
  );
}