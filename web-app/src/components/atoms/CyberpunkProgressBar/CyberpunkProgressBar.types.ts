export type ProgressBarSize = 'sm' | 'md' | 'lg';

export interface CyberpunkProgressBarProps {
  progress: number;
  size?: ProgressBarSize;
  className?: string;
  testId?: string;
}
