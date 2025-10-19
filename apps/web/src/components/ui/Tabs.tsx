/**
 * GLASS TABS COMPONENT
 * Tabs with animated slider indicator
 */

'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';

export interface Tab {
  id: string;
  label: string;
  icon?: React.ReactNode;
  disabled?: boolean;
}

interface TabsProps {
  tabs: Tab[];
  activeTab: string;
  onChange: (tabId: string) => void;
  className?: string;
}

export const Tabs: React.FC<TabsProps> = ({ tabs, activeTab, onChange, className }) => {
  const [indicatorStyle, setIndicatorStyle] = React.useState({ left: 0, width: 0 });
  const tabsRef = React.useRef<(HTMLButtonElement | null)[]>([]);

  React.useEffect(() => {
    const activeIndex = tabs.findIndex(tab => tab.id === activeTab);
    const activeButton = tabsRef.current[activeIndex];
    
    if (activeButton) {
      setIndicatorStyle({
        left: activeButton.offsetLeft,
        width: activeButton.offsetWidth,
      });
    }
  }, [activeTab, tabs]);

  return (
    <div className={cn('w-full', className)}>
      <div className="relative glass rounded-glass p-1 inline-flex gap-1">
        {tabs.map((tab, index) => (
          <button
            key={tab.id}
            ref={el => tabsRef.current[index] = el}
            className={cn(
              'relative z-10 px-4 py-2 rounded-glass-sm',
              'text-sm font-medium transition-colors duration-fast',
              'flex items-center gap-2',
              'focus:outline-none focus:ring-2 focus:ring-cyber-blue focus:ring-offset-2 focus:ring-offset-dark-500',
              tab.disabled && 'opacity-50 cursor-not-allowed',
              activeTab === tab.id ? 'text-cyber-blue' : 'text-text-secondary hover:text-text-primary'
            )}
            onClick={() => !tab.disabled && onChange(tab.id)}
            disabled={tab.disabled}
          >
            {tab.icon && <span className="w-4 h-4">{tab.icon}</span>}
            {tab.label}
          </button>
        ))}
        
        {/* Animated indicator */}
        <motion.div
          className="absolute bottom-1 h-[calc(100%-8px)] rounded-glass-sm glass-light border border-cyber-blue/30 shadow-glow-blue"
          initial={false}
          animate={{
            left: indicatorStyle.left,
            width: indicatorStyle.width,
          }}
          transition={{
            type: 'spring',
            stiffness: 400,
            damping: 30,
          }}
        />
      </div>
    </div>
  );
};

Tabs.displayName = 'Tabs';
