"use client"

import * as React from "react"
import { ThemeProvider as NextThemesProvider } from "next-themes"
import { type ThemeProviderProps } from "next-themes/dist/types"

export function ThemeProvider({ children, ...props }: ThemeProviderProps) {
  const [mounted, setMounted] = React.useState(false)

  React.useEffect(() => {
    setMounted(true)
  }, [])

  if (!mounted) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="animate-pulse text-cyan-300">Preparing theme…</div>
      </div>
    )
  }

  return (
    <NextThemesProvider
      disableTransitionOnChange
      enableSystem
      defaultTheme="system"
      {...props}
    >
      {children}
    </NextThemesProvider>
  )
}
