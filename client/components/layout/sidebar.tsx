"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { 
  LayoutDashboard, 
  FileText, 
  Eye, 
  BarChart3, 
  Settings, 
  LogOut,
  ChevronLeft,
  GraduationCap
} from "lucide-react"
import { useAuthStore } from "@/lib/store"

const sidebarItems = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/exams", label: "Exams", icon: FileText },
  { href: "/proctoring", label: "Proctoring", icon: Eye },
  { href: "/analytics", label: "Analytics", icon: BarChart3 },
  { href: "/settings", label: "Settings", icon: Settings },
]

export function Sidebar() {
  const pathname = usePathname()
  const { user, logout } = useAuthStore()

  return (
    <aside className={cn(
      "fixed left-0 top-0 z-40 h-screen border-r bg-card transition-all duration-300",
      "w-64"
    )}>
      <div className="flex h-full flex-col">
        {/* Logo */}
        <div className="flex h-16 items-center border-b px-6">
          <Link href="/dashboard" className="flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary">
              <GraduationCap className="h-5 w-5 text-primary-foreground" />
            </div>
            <span className="text-xl font-bold">SecureExam</span>
          </Link>
        </div>

        {/* Navigation */}
        <nav className="flex-1 space-y-1 p-4">
          {sidebarItems.map((item) => {
            const Icon = item.icon
            const isActive = pathname.startsWith(item.href)
            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                  isActive
                    ? "bg-primary text-primary-foreground"
                    : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
                )}
              >
                <Icon className="h-5 w-5" />
                {item.label}
              </Link>
            )
          })}
        </nav>

        {/* User */}
        <div className="border-t p-4">
          <div className="mb-3 flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-full bg-primary text-sm font-medium">
              {user?.fullName?.[0] || user?.email[0]}
            </div>
            <div className="flex-1 overflow-hidden">
              <p className="truncate text-sm font-medium">{user?.fullName || user?.email}</p>
              <p className="truncate text-xs text-muted-foreground capitalize">
                {user?.role}
              </p>
            </div>
          </div>
          <Button
            variant="ghost"
            className="w-full justify-start text-muted-foreground"
            onClick={logout}
          >
            <LogOut className="mr-2 h-4 w-4" />
            Sign Out
          </Button>
        </div>
      </div>
    </aside>
  )
}