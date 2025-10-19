// Button props
export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'default' | 'destructive' | 'outline' | 'secondary' | 'ghost' | 'link' | 'primary'
  size?: 'default' | 'sm' | 'lg' | 'icon'
  isLoading?: boolean
  asChild?: boolean
}

// Card props
export interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  className?: string
  asChild?: boolean
}

export interface CardHeaderProps extends React.HTMLAttributes<HTMLDivElement> {
  className?: string
}

export interface CardTitleProps extends React.HTMLAttributes<HTMLHeadingElement> {
  className?: string
}

export interface CardDescriptionProps extends React.HTMLAttributes<HTMLParagraphElement> {
  className?: string
}

export interface CardContentProps extends React.HTMLAttributes<HTMLDivElement> {
  className?: string
}

// Toast/Sonner props
export interface ToasterProps extends React.HTMLAttributes<HTMLDivElement> {
  position?: 'top-left' | 'top-center' | 'top-right' | 'bottom-left' | 'bottom-center' | 'bottom-right'
  toastOptions?: object
  richColors?: boolean
}

// Theme provider props
export interface ThemeProviderProps {
  children: React.ReactNode
  defaultTheme?: string
  storageKey?: string
  attribute?: string | boolean
  enableSystem?: boolean
  disableTransitionOnChange?: boolean
}

// Audio types
export interface AudioFile {
  id: string
  name: string
  url: string
  duration: number
  size: number
  type: string
  tags: string[]
  createdAt: string
  updatedAt: string
}

// Project types
export interface Project {
  id: string
  name: string
  description?: string
  bpm: number
  key: string
  createdAt: string
  updatedAt: string
  audioFiles: AudioFile[]
}

// API response types
export interface ApiResponse<T> {
  data: T
  message?: string
  success: boolean
  error?: string
}

// User types
export interface User {
  id: string
  name: string
  email: string
  avatar?: string
  createdAt: string
  updatedAt: string
}

// AI Model types
export interface AIModel {
  id: string
  name: string
  description: string
  version: string
  isActive: boolean
  createdAt: string
}

// Error boundary props
export interface ErrorBoundaryProps {
  children: React.ReactNode
  fallback?: React.ReactNode
}

export interface ErrorBoundaryState {
  hasError: boolean
  error?: Error
}

// Form field props
export interface FormFieldProps {
  name: string
  label: string
  description?: string
  error?: string
  className?: string
  required?: boolean
  children: React.ReactNode
}
