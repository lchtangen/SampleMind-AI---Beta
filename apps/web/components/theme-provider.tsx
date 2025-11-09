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
