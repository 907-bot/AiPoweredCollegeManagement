"use client"

import { useState } from "react"
import Link from "next/link"
import { Menu, Bell, Search } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { useUIStore } from "@/lib/store"

export function Header() {
  const { toggleSidebar } = useUIStore()
  const [showSearch, setShowSearch] = useState(false)

  return (
    <header className="sticky top-0 z-30 flex h-16 items-center gap-4 border-b bg-card/95 px-6 backdrop-blur">
      <Button variant="ghost" size="icon" onClick={toggleSidebar}>
        <Menu className="h-5 w-5" />
      </Button>

      <div className="flex-1">
        {showSearch ? (
          <div className="relative max-w-md animate-fade-in">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <Input
              placeholder="Search exams, students..."
              className="pl-10"
              autoFocus
              onBlur={() => setShowSearch(false)}
            />
          </div>
        ) : (
          <Button
            variant="ghost"
            className="justify-start text-muted-foreground"
            onClick={() => setShowSearch(true)}
          >
            <Search className="mr-2 h-4 w-4" />
            <span className="text-sm">Search...</span>
          </Button>
        )}
      </div>

      <div className="flex items-center gap-2">
        <Button variant="ghost" size="icon" className="relative">
          <Bell className="h-5 w-5" />
          <span className="absolute right-1.5 top-1.5 h-2 w-2 rounded-full bg-destructive" />
        </Button>
      </div>
    </header>
  )
}