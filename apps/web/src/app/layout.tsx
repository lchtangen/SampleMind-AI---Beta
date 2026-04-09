import type { Metadata, Viewport } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import { ThemeProvider } from '@/components/theme-provider';
import { Toaster } from '@/components/ui/sonner';
import { cn } from '@/lib/utils';
import { AnalyticsProvider } from '@/components/analytics-provider';
import QueryProvider from '@/components/providers/QueryProvider';

export const metadata: Metadata = {
  title: 'SampleMind AI - Next-Gen Music Production',
  description: 'AI-powered audio intelligence for professional music production',
  keywords: ['AI music', 'audio production', 'sample analysis', 'music technology'],
};

// Next.js 15: viewport is a separate export
export const viewport: Viewport = {
  themeColor: [
    { media: '(prefers-color-scheme: light)', color: '#f0f0ff' },
    { media: '(prefers-color-scheme: dark)', color: '#0a0a1a' },
  ],
  width: 'device-width',
  initialScale: 1,
  maximumScale: 1,
};

const inter = Inter({ 
  subsets: ['latin'],
  variable: '--font-sans',
  display: 'swap',
});

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning className={inter.variable}>
      <head>
        <link rel="icon" href="/favicon.ico" sizes="any" />
        <link rel="apple-touch-icon" href="/apple-icon.png" />
      </head>
      <body className={cn(
        "min-h-screen bg-dark-500 font-sans antialiased",
        "text-text-primary",
        inter.variable
      )}>
        <QueryProvider>
        <AnalyticsProvider>
          <ThemeProvider
            attribute="class"
            defaultTheme="dark"
            enableSystem={false}
            disableTransitionOnChange
          >
          <div className="relative min-h-screen overflow-hidden">
            {/* Animated background elements */}
            <div className="fixed inset-0 -z-10">
              <div className="absolute inset-0 bg-dark-500" />
              <div className="absolute inset-0 grid-pattern opacity-5" />
              <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,hsl(220,90%,30%)_0%,transparent_70%)] opacity-20" />
            </div>
            
            {/* Main content */}
            <div className="relative z-10">
              {children}
            </div>
            
            {/* Global UI Elements */}
            <Toaster 
              position="top-center" 
              richColors
              toastOptions={{
                classNames: {
                  toast: 'glass border border-glass-border',
                  title: 'font-semibold',
                  description: 'text-text-secondary',
                },
              }}
            />
          </div>
        </ThemeProvider>
        </AnalyticsProvider>
        </QueryProvider>
      </body>
    </html>
  );
}
