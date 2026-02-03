import type { Metadata, Viewport } from 'next';
import { Inter } from 'next/font/google';
import dynamic from 'next/dynamic';
import { ThemeProvider } from '@/components/theme-provider';
import './globals.css';
import { AuthProvider } from '@/contexts/AuthContext';
import { NotificationProvider } from '@/contexts/NotificationContext';

// Dynamic imports for performance
const CommandPalette = dynamic(() => import('@/components/ui/CommandPalette'), {
  ssr: false,
});
const FeedbackWidget = dynamic(() => import('@/components/feedback/FeedbackWidget').then(mod => ({ default: mod.FeedbackWidget })), {
  ssr: false,
});

// Optimize font loading with display: 'swap' and preload
const inter = Inter({ 
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-inter',
  preload: true,
});

export const metadata: Metadata = {
  title: 'SampleMind AI',
  description: 'AI-Powered Music Production Platform',
  metadataBase: new URL(process.env.NEXT_PUBLIC_APP_URL || 'http://localhost:3000'),
  openGraph: {
    title: 'SampleMind AI - Next Generation Music Production',
    description: 'Experience AI-powered music creation with neuro-audio processing',
    type: 'website',
    locale: 'en_US',
  },
  icons: {
    icon: [
      { url: '/favicon.ico', sizes: 'any' },
      { url: '/favicon-16x16.png', sizes: '16x16', type: 'image/png' },
      { url: '/favicon-32x32.png', sizes: '32x32', type: 'image/png' },
    ],
    apple: '/apple-touch-icon.png',
  },
  manifest: '/site.webmanifest',
};

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
  maximumScale: 1,
  userScalable: false,
  themeColor: [
    { media: '(prefers-color-scheme: light)', color: '#f5f5f7' },
    { media: '(prefers-color-scheme: dark)', color: '#1c1c1e' },
  ],
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={`${inter.variable}`} suppressHydrationWarning>
      <head>
        {/* Preload critical assets */}
        <link
          rel="preload"
          href={`${process.env.NEXT_PUBLIC_BASE_PATH || ''}/_next/static/media/${inter.variable.split(' ')[1]}.woff2`}
          as="font"
          type="font/woff2"
          crossOrigin="anonymous"
        />
        <meta name="theme-color" content="#f5f5f7" media="(prefers-color-scheme: light)" />
        <meta name="theme-color" content="#1c1c1e" media="(prefers-color-scheme: dark)" />
      </head>
      <body className={`${inter.className} bg-background-primary text-text-primary antialiased`}>
        <ThemeProvider
          attribute="class"
          defaultTheme="system"
          enableSystem
          disableTransitionOnChange
        >
          <NotificationProvider>
            <AuthProvider>
              <CommandPalette />
              <FeedbackWidget />
              {children}
            </AuthProvider>
          </NotificationProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
