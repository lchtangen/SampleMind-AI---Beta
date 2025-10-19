import React, { useState, useEffect } from 'react';
import { Search, Bell, Settings, Menu, X, Sun, Moon, Zap } from 'lucide-react';
import { Input } from '../ui/input';
import { Button } from '../ui/button';
import { cn } from '../../lib/utils';

export const TopBar = ({ 
  isSidebarOpen, 
  onToggleSidebar 
}: { 
  isSidebarOpen: boolean; 
  onToggleSidebar: () => void 
}) => {
  const [isScrolled, setIsScrolled] = useState(false);
  const [darkMode, setDarkMode] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  
  // Handle scroll effect for the top bar
  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 10);
    };
    
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);
  
  // Toggle dark mode
  const toggleDarkMode = () => {
    setDarkMode(!darkMode);
    document.documentElement.classList.toggle('dark', !darkMode);
  };
  
  return (
    <header className={cn(
      'sticky top-0 z-40 w-full border-b',
      'bg-cyber-glass-dark/80 backdrop-blur-md',
      'border-cyber-primary/10',
      'transition-all duration-300',
      isScrolled ? 'py-2' : 'py-3',
    )}>
      <div className="container flex items-center justify-between h-14 px-4">
        {/* Left section */}
        <div className="flex items-center space-x-2
        ">
          <Button
            variant="ghost"
            size="icon"
            onClick={onToggleSidebar}
            className={cn(
              'text-cyber-primary hover:bg-cyber-primary/10',
              'h-9 w-9 rounded-lg',
              'transition-all duration-200',
              'relative overflow-hidden',
              'group'
            )}
          >
            {isSidebarOpen ? (
              <X className="h-5 w-5 transition-transform duration-200" />
            ) : (
              <Menu className="h-5 w-5 transition-transform duration-200" />
            )}
            
            {/* Hover effect */}
            <span className={cn(
              'absolute inset-0 bg-cyber-primary/5',
              'opacity-0 group-hover:opacity-100',
              'transition-opacity duration-200',
              'rounded-lg',
              'scale-90 group-hover:scale-100',
              'transform-gpu'
            )} />
          </Button>
          
          <div className="relative hidden md:block">
            <Search className={cn(
              'absolute left-3 top-1/2 -translate-y-1/2',
              'h-4 w-4 text-cyber-primary/60',
              'pointer-events-none'
            )} />
            <Input
              type="search"
              placeholder="Search samples, projects, or tools..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className={cn(
                'pl-10 pr-4 py-1.5 h-9 w-64',
                'bg-cyber-glass-dark/50 border-cyber-primary/20',
                'text-cyber-primary placeholder-cyber-primary/50',
                'focus-visible:ring-2 focus-visible:ring-cyber-primary/50',
                'transition-all duration-200',
                'hover:border-cyber-primary/40',
                'focus:w-80',
                'rounded-xl'
              )}
            />
          </div>
        </div>
        
        {/* Right section */}
        <div className="flex items-center space-x-2">
          {/* AI Assistant Button */}
          <Button
            variant="outline"
            className={cn(
              'hidden md:flex items-center space-x-2',
              'bg-cyber-primary/10 border-cyber-primary/20',
              'text-cyber-primary hover:text-cyber-highlight',
              'hover:bg-cyber-primary/20 hover:border-cyber-primary/40',
              'transition-all duration-200',
              'group relative overflow-hidden',
              'rounded-xl px-4 py-1.5 h-9',
              'shadow-cyber-glow hover:shadow-cyber-glow-hover',
              'animate-pulse-slow'
            )}
          >
            <Zap className="h-4 w-4 fill-current text-cyber-accent" />
            <span>AI Assistant</span>
            
            {/* Animated background */}
            <span className={cn(
              'absolute inset-0 bg-gradient-to-r from-cyber-primary/10 via-cyber-accent/10 to-cyber-secondary/10',
              'opacity-0 group-hover:opacity-100',
              'transition-opacity duration-500',
              '-z-10'
            )} />
          </Button>
          
          {/* Notifications */}
          <Button
            variant="ghost"
            size="icon"
            className={cn(
              'text-cyber-primary hover:bg-cyber-primary/10',
              'h-9 w-9 rounded-lg',
              'relative',
              'group'
            )}
          >
            <Bell className="h-5 w-5" />
            <span className={cn(
              'absolute top-1 right-1 h-2 w-2',
              'bg-cyber-error rounded-full',
              'ring-2 ring-cyber-darker',
              'animate-ping-slow'
            )} />
            
            {/* Hover effect */}
            <span className={cn(
              'absolute inset-0 bg-cyber-primary/5',
              'opacity-0 group-hover:opacity-100',
              'transition-opacity duration-200',
              'rounded-lg',
              'scale-90 group-hover:scale-100',
              'transform-gpu'
            )} />
          </Button>
          
          {/* Theme Toggle */}
          <Button
            variant="ghost"
            size="icon"
            onClick={toggleDarkMode}
            className={cn(
              'text-cyber-primary hover:bg-cyber-primary/10',
              'h-9 w-9 rounded-lg',
              'group'
            )}
          >
            {darkMode ? (
              <Sun className="h-5 w-5" />
            ) : (
              <Moon className="h-5 w-5" />
            )}
            
            {/* Hover effect */}
            <span className={cn(
              'absolute inset-0 bg-cyber-primary/5',
              'opacity-0 group-hover:opacity-100',
              'transition-opacity duration-200',
              'rounded-lg',
              'scale-90 group-hover:scale-100',
              'transform-gpu'
            )} />
          </Button>
          
          {/* User Menu */}
          <Button
            variant="ghost"
            size="icon"
            className={cn(
              'h-9 w-9 rounded-full',
              'bg-cyber-primary/10 hover:bg-cyber-primary/20',
              'border border-cyber-primary/20',
              'text-cyber-primary',
              'transition-all duration-200',
              'group relative overflow-hidden'
            )}
          >
            <span className="text-sm font-medium">U</span>
            
            {/* Hover effect */}
            <span className={cn(
              'absolute inset-0 bg-cyber-primary/5',
              'opacity-0 group-hover:opacity-100',
              'transition-opacity duration-200',
              'rounded-full',
              'scale-90 group-hover:scale-100',
              'transform-gpu'
            )} />
          </Button>
        </div>
      </div>
    </header>
  );
};
