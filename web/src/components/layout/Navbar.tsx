/**
 * Navbar Component
 * 
 * Modern navigation bar with glassmorphism effect and AI theme
 */

import { Menu, Moon, Sun, Bell, Settings, User } from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import { useAppStore } from '@/store/appStore';

export function Navbar() {
  const { sidebarOpen, toggleSidebar, theme, setTheme } = useAppStore((state) => ({
    sidebarOpen: state.ui.sidebarOpen,
    toggleSidebar: state.toggleSidebar,
    theme: state.ui.theme,
    setTheme: state.setTheme,
  }));

  const toggleTheme = () => {
    setTheme(theme === 'dark' ? 'light' : 'dark');
  };

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 h-16 border-b border-white/10 bg-slate-900/80 backdrop-blur-xl">
      <div className="flex h-full items-center justify-between px-4">
        {/* Left Section */}
        <div className="flex items-center gap-4">
          <Button
            variant="ghost"
            size="icon"
            onClick={toggleSidebar}
            className="text-white hover:bg-white/10"
          >
            <Menu className="h-5 w-5" />
          </Button>

          <div className="flex items-center gap-3">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-purple-500 via-blue-500 to-cyan-500 shadow-lg shadow-purple-500/20">
              <span className="text-sm font-bold text-white">SM</span>
            </div>
            <div>
              <h1 className="text-lg font-bold gradient-text">SampleMind AI</h1>
              <p className="text-xs text-slate-400">Audio Intelligence Platform</p>
            </div>
          </div>
        </div>

        {/* Right Section */}
        <div className="flex items-center gap-2">
          {/* Theme Toggle */}
          <Button
            variant="ghost"
            size="icon"
            onClick={toggleTheme}
            className="text-white hover:bg-white/10"
          >
            {theme === 'dark' ? (
              <Sun className="h-5 w-5" />
            ) : (
              <Moon className="h-5 w-5" />
            )}
          </Button>

          {/* Notifications */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button
                variant="ghost"
                size="icon"
                className="relative text-white hover:bg-white/10"
              >
                <Bell className="h-5 w-5" />
                <Badge className="absolute -top-1 -right-1 h-5 w-5 rounded-full p-0 text-xs">
                  3
                </Badge>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-80 bg-slate-800 border-white/10">
              <DropdownMenuLabel className="text-white">Notifications</DropdownMenuLabel>
              <DropdownMenuSeparator className="bg-white/10" />
              <DropdownMenuItem className="text-slate-300 hover:bg-white/10">
                <div className="flex flex-col gap-1">
                  <span className="font-medium">Analysis Complete</span>
                  <span className="text-xs text-slate-400">Your track "Summer Vibes" has been analyzed</span>
                </div>
              </DropdownMenuItem>
              <DropdownMenuItem className="text-slate-300 hover:bg-white/10">
                <div className="flex flex-col gap-1">
                  <span className="font-medium">New Feature Available</span>
                  <span className="text-xs text-slate-400">Check out our new AI-powered stem separation</span>
                </div>
              </DropdownMenuItem>
              <DropdownMenuItem className="text-slate-300 hover:bg-white/10">
                <div className="flex flex-col gap-1">
                  <span className="font-medium">System Update</span>
                  <span className="text-xs text-slate-400">SampleMind AI v7.0 is now available</span>
                </div>
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>

          {/* Settings */}
          <Button
            variant="ghost"
            size="icon"
            className="text-white hover:bg-white/10"
          >
            <Settings className="h-5 w-5" />
          </Button>

          {/* User Menu */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button
                variant="ghost"
                size="icon"
                className="rounded-full text-white hover:bg-white/10"
              >
                <Avatar className="h-8 w-8">
                  <AvatarImage src="/avatar.jpg" alt="User" />
                  <AvatarFallback className="bg-gradient-to-br from-purple-500 to-cyan-500 text-white">
                    <User className="h-4 w-4" />
                  </AvatarFallback>
                </Avatar>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-56 bg-slate-800 border-white/10">
              <DropdownMenuLabel className="text-white">My Account</DropdownMenuLabel>
              <DropdownMenuSeparator className="bg-white/10" />
              <DropdownMenuItem className="text-slate-300 hover:bg-white/10">
                Profile
              </DropdownMenuItem>
              <DropdownMenuItem className="text-slate-300 hover:bg-white/10">
                Settings
              </DropdownMenuItem>
              <DropdownMenuItem className="text-slate-300 hover:bg-white/10">
                Billing
              </DropdownMenuItem>
              <DropdownMenuSeparator className="bg-white/10" />
              <DropdownMenuItem className="text-red-400 hover:bg-red-500/10">
                Sign Out
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>
    </nav>
  );
}