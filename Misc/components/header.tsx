"use client"

import type React from "react"

import { Button } from "@/components/ui/button"
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetTrigger } from "@/components/ui/sheet"
import { Menu } from "lucide-react"
import Link from "next/link"

export function Header() {
  const navItems = [
    { name: "Features", href: "#features-section" },
    { name: "Pricing", href: "#pricing-section" },
    { name: "Testimonials", href: "#testimonials-section" },
  ]

  const handleScroll = (e: React.MouseEvent<HTMLAnchorElement>, href: string) => {
    e.preventDefault()
    const targetId = href.substring(1)
    const targetElement = document.getElementById(targetId)
    if (targetElement) {
      targetElement.scrollIntoView({ behavior: "smooth" })
    }
  }

  return (
    <header className="w-full py-4 px-6">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        <div className="flex items-center gap-6">
          <div className="flex items-center gap-3">
            <span className="text-foreground text-xl font-semibold neon-text">Pointer</span>
          </div>
          <nav className="hidden md:flex items-center gap-2">
            {navItems.map((item) => (
              <Link
                key={item.name}
                href={item.href}
                onClick={(e) => handleScroll(e, item.href)}
                className="text-muted-foreground hover:text-primary px-4 py-2 rounded-full font-medium transition-all duration-300 hover:neon-glow"
              >
                {item.name}
              </Link>
            ))}
          </nav>
        </div>
        <div className="flex items-center gap-4">
          <Link href="https://vercel.com/home" target="_blank" rel="noopener noreferrer" className="hidden md:block">
            <Button className="bg-secondary text-primary-foreground hover:bg-secondary/90 px-6 py-2 rounded-full font-medium neon-glow-blue transition-all duration-300">
              Try for Free
            </Button>
          </Link>
          <Sheet>
            <SheetTrigger asChild className="md:hidden">
              <Button variant="ghost" size="icon" className="text-foreground">
                <Menu className="h-7 w-7" />
                <span className="sr-only">Toggle navigation menu</span>
              </Button>
            </SheetTrigger>
            <SheetContent side="bottom" className="bg-background border-t border-border text-foreground glassmorphism">
              <SheetHeader>
                <SheetTitle className="text-left text-xl font-semibold text-foreground neon-text">
                  Navigation
                </SheetTitle>
              </SheetHeader>
              <nav className="flex flex-col gap-4 mt-6">
                {navItems.map((item) => (
                  <Link
                    key={item.name}
                    href={item.href}
                    onClick={(e) => handleScroll(e, item.href)}
                    className="text-muted-foreground hover:text-primary justify-start text-lg py-2 transition-colors"
                  >
                    {item.name}
                  </Link>
                ))}
                <Link href="https://vercel.com/home" target="_blank" rel="noopener noreferrer" className="w-full mt-4">
                  <Button className="bg-secondary text-primary-foreground hover:bg-secondary/90 px-6 py-2 rounded-full font-medium neon-glow-blue w-full">
                    Try for Free
                  </Button>
                </Link>
              </nav>
            </SheetContent>
          </Sheet>
        </div>
      </div>
    </header>
  )
}
