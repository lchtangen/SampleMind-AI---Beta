import React from 'react';
import { cn } from '@/lib/utils';
import { Loader2 } from 'lucide-react';

export interface SpinnerProps {
  size?: 'sm' | 'md' | 'lg' | 'xl';
  color?: 'blue' | 'gray' | 'white';
  label?: string;
  className?: string;
}

const Spinner: React.FC<SpinnerProps> = ({
  size = 'md',
  color = 'blue',
  label,
  className,
}) => {
  const sizes = {
    sm: 16,
    md: 24,
    lg: 32,
    xl: 48,
  };

  const colors = {
    blue: 'text-blue-600',
    gray: 'text-gray-600',
    white: 'text-white',
  };

  return (
    <div className={cn('flex flex-col items-center justify-center gap-3', className)}>
      <Loader2 
        className={cn('animate-spin', colors[color])} 
        size={sizes[size]}
      />
      {label && (
        <p className={cn('text-sm font-medium', colors[color])}>{label}</p>
      )}
    </div>
  );
};

export default Spinner;
