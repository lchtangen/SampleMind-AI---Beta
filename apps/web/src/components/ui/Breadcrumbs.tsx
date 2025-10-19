/**
 * GLASS BREADCRUMBS COMPONENT
 * Navigation breadcrumbs with separators
 */

'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';
import { ChevronRight } from 'lucide-react';

export interface BreadcrumbItem {
  label: string;
  href?: string;
  onClick?: () => void;
}

interface BreadcrumbsProps {
  items: BreadcrumbItem[];
  className?: string;
}

export const Breadcrumbs: React.FC<BreadcrumbsProps> = ({ items, className }) => {
  return (
    <nav aria-label="Breadcrumb" className={cn('flex items-center gap-2', className)}>
      {items.map((item, index) => {
        const isLast = index === items.length - 1;
        
        return (
          <React.Fragment key={index}>
            <motion.div
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.05 }}
            >
              {isLast ? (
                <span className="text-sm font-medium text-text-primary">
                  {item.label}
                </span>
              ) : item.href ? (
                <a
                  href={item.href}
                  className="text-sm font-medium text-text-secondary hover:text-cyber-blue transition-colors"
                >
                  {item.label}
                </a>
              ) : (
                <button
                  onClick={item.onClick}
                  className="text-sm font-medium text-text-secondary hover:text-cyber-blue transition-colors"
                >
                  {item.label}
                </button>
              )}
            </motion.div>
            
            {!isLast && (
              <ChevronRight className="w-4 h-4 text-text-tertiary" />
            )}
          </React.Fragment>
        );
      })}
    </nav>
  );
};

Breadcrumbs.displayName = 'Breadcrumbs';
