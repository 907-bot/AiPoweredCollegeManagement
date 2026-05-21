"use client"

import { useEffect } from "react"
import { useRouter, usePathname } from "next/navigation"
import { cn } from "@/lib/utils"
import { Sidebar } from "@/components/layout/sidebar"
import { Header } from "@/components/layout/header"
import { useAuthStore, useUIStore } from "@/lib/store"

const publicRoutes = ["/login", "/register"]

export function AppLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter()
  const pathname = usePathname()
  const { isAuthenticated, checkAuth } = useAuthStore()
  const { sidebarOpen } = useUIStore()

  const isPublic = publicRoutes.some(route => pathname.startsWith(route))

  useEffect(() => {
    checkAuth()
  }, [checkAuth])

  useEffect(() => {
    if (!isAuthenticated && !isPublic) {
      router.push("/login")
    }
  }, [isAuthenticated, isPublic, router])

  // Show without layout for public pages
  if (isPublic) {
    return <>{children}</>
  }

  if (!isAuthenticated) {
    return null
  }

  return (
    <div className="min-h-screen bg-background">
      <Sidebar />
      <div
        className={cn(
          "transition-all duration-300",
          sidebarOpen ? "ml-64" : "ml-0"
        )}
      >
        <Header />
        <main className="p-6">{children}</main>
      </div>
    </div>
  )
}