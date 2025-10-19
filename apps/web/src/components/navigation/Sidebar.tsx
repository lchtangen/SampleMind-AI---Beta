import React from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import { cn } from '../../lib/utils';
import { 
  LayoutDashboard, 
  Music, 
  Settings, 
  Folder, 
  Zap, 
  Sparkles, 
  BrainCircuit, 
  BarChart2,
  PlusCircle
} from 'lucide-react';
import { Button } from '../ui/button';

export const Sidebar = () => {
  const location = useLocation();
  
  const navItems = [
    {
      name: 'Dashboard',
      icon: LayoutDashboard,
      path: '/dashboard',
    },
    {
      name: 'Library',
      icon: Music,
      path: '/library',
    },
    {
      name: 'Projects',
      icon: Folder,
      path: '/projects',
    },
    {
      name: 'AI Tools',
      icon: Sparkles,
      path: '/ai-tools',
    },
    {
      name: 'Analytics',
      icon: BarChart2,
      path: '/analytics',
    },
    {
      name: 'Settings',
      icon: Settings,
      path: '/settings',
    },
  ];

  return (
    <div className="flex flex-col h-full">
      {/* Logo */}
      <div className="flex items-center justify-center p-6 mb-6">
        <div className="flex items-center space-x-2">
          <BrainCircuit className="h-8 w-8 text-cyber-primary" />
          <span className="text-xl font-bold bg-gradient-to-r from-cyber-primary to-cyber-accent bg-clip-text text-transparent">
            SAMPLEMIND
          </span>
        </div>
      </div>
      
      {/* Navigation */}
      <nav className="flex-1 px-3 space-y-1">
        {navItems.map((item) => {
          const isActive = location.pathname.startsWith(item.path);
          return (
            <NavLink
              key={item.path}
              to={item.path}
              className={cn(
                'flex items-center px-4 py-3 rounded-lg text-sm font-medium transition-colors',
                'group relative overflow-hidden',
                isActive 
                  ? 'bg-cyber-primary/10 text-cyber-highlight' 
                  : 'text-cyber-primary/80 hover:bg-cyber-primary/5 hover:text-cyber-highlight',
                'transition-all duration-200',
                'before:absolute before:left-0 before:top-0 before:bottom-0 before:w-1',
                isActive 
                  ? 'before:bg-cyber-primary before:opacity-100' 
                  : 'before:bg-cyber-primary/0 before:opacity-0',
                'before:transition-all before:duration-300',
                'hover:before:opacity-100',
                'after:absolute after:inset-0 after:bg-cyber-primary/5',
                'after:opacity-0 hover:after:opacity-100',
                'after:transition-opacity after:duration-200',
              )}
            >
              <item.icon 
                className={cn(
                  'h-5 w-5 mr-3',
                  isActive ? 'text-cyber-primary' : 'text-cyber-primary/70'
                )} 
              />
              <span>{item.name}</span>
              
              {/* Glow effect on hover */}
              <span className={cn(
                'absolute inset-0 rounded-md',
                'bg-gradient-to-r from-cyber-primary/20 to-transparent',
                'opacity-0 group-hover:opacity-100',
                'transition-opacity duration-300',
                '-z-10'
              )} />
            </NavLink>
          );
        })}
      </nav>
      
      {/* Create New Button */}
      <div className="p-4 mt-auto">
        <Button 
          className={cn(
            'w-full bg-cyber-primary/10 hover:bg-cyber-primary/20',
            'text-cyber-primary hover:text-cyber-highlight',
            'border border-cyber-primary/30 hover:border-cyber-primary/50',
            'transition-all duration-200',
            'group relative overflow-hidden',
            'shadow-cyber-glow hover:shadow-cyber-glow-hover',
          )}
        >
          <PlusCircle className="h-4 w-4 mr-2" />
          <span>New Project</span>
          
          {/* Animated background */}
          <span className={cn(
            'absolute inset-0 bg-gradient-to-r from-cyber-primary/10 to-cyber-secondary/10',
            'opacity-0 group-hover:opacity-100',
            'transition-opacity duration-500',
            '-z-10'
          )} />
        </Button>
      </div>
      
      {/* User Profile */}
      <div className="p-4 border-t border-cyber-primary/10">
        <div className="flex items-center space-x-3">
          <div className="h-9 w-9 rounded-full bg-cyber-primary/10 flex items-center justify-center">
            <span className="text-cyber-primary text-sm font-medium">U</span>
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-cyber-primary truncate">User Name</p>
            <p className="text-xs text-cyber-primary/60 truncate">Free Plan</p>
          </div>
        </div>
      </div>
    </div>
  );
};
