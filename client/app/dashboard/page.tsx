"use client"

import { useEffect } from "react"
import Link from "next/link"
import { 
  FileText, 
  Users, 
  CheckCircle2, 
  Clock, 
  TrendingUp,
  AlertTriangle,
  Plus,
  ArrowRight
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { useAuthStore, useExamStore } from "@/lib/store"
import { formatDate, formatScore } from "@/lib/utils"

export default function DashboardPage() {
  const { user } = useAuthStore()
  const { stats, fetchStats, isLoading } = useExamStore()

  useEffect(() => {
    fetchStats()
  }, [fetchStats])

  const statCards = [
    {
      title: "Total Exams",
      value: stats?.totalExams || "—",
      icon: FileText,
      description: "All time",
    },
    {
      title: "Active Sessions",
      value: stats?.totalSessions || "—",
      icon: Clock,
      description: "In progress",
    },
    {
      title: "Completion Rate",
      value: `${stats?.completionRate.toFixed(0) || 0}%`,
      icon: CheckCircle2,
      description: "This month",
    },
    {
      title: "Average Score",
      value: formatScore(stats?.avgScore || 0),
      icon: TrendingUp,
      description: "Across all exams",
    },
  ]

  return (
    <div className="space-y-6">
      {/* Welcome */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Welcome back, {user?.fullName || user?.username || "User"}</h1>
          <p className="text-muted-foreground">Here&apos;s what&apos;s happening with your exams today.</p>
        </div>
        <Link href="/exams/new">
          <Button>
            <Plus className="mr-2 h-4 w-4" />
            Create Exam
          </Button>
        </Link>
      </div>

      {/* Stats Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {statCards.map((stat, i) => (
          <Card key={i} className="card-hover">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                {stat.title}
              </CardTitle>
              <stat.icon className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stat.value}</div>
              <p className="text-xs text-muted-foreground">{stat.description}</p>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Main Content */}
      <div className="grid gap-6 lg:grid-cols-2">
        {/* Recent Exams */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <div>
              <CardTitle>Recent Exams</CardTitle>
              <CardDescription>Your latest exam activity</CardDescription>
            </div>
            <Link href="/exams">
              <Button variant="ghost" size="sm">
                View All
                <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            </Link>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {stats?.exams?.slice(0, 5).map((exam) => (
                <Link
                  key={exam.examId}
                  href={`/exams/${exam.examId}`}
                  className="flex items-center justify-between rounded-lg border p-3 transition-colors hover:bg-accent"
                >
                  <div className="space-y-1">
                    <p className="font-medium">Exam #{exam.examId}</p>
                    <p className="text-sm text-muted-foreground">
                      {exam.completedSessions} completed
                    </p>
                  </div>
                  <div className="text-right">
                    <div className="font-medium">{formatScore(exam.avgScore)}</div>
                    <p className="text-sm text-muted-foreground">
                      {exam.passRate.toFixed(0)}% pass
                    </p>
                  </div>
                </Link>
              )) || (
                <p className="text-center text-muted-foreground py-8">
                  No exams yet. Create your first exam to get started.
                </p>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Alerts */}
        <Card>
          <CardHeader>
            <CardTitle>Recent Alerts</CardTitle>
            <CardDescription>Students with suspicious activity</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {/* Demo alert */}
              <div className="flex items-start gap-3 rounded-lg border border-destructive/20 bg-destructive/5 p-3">
                <AlertTriangle className="h-5 w-5 text-destructive" />
                <div className="flex-1 space-y-1">
                  <p className="font-medium text-destructive">Multiple faces detected</p>
                  <p className="text-sm text-muted-foreground">
                    Student #42 - Exam #3 - 2 persons in frame
                  </p>
                  <p className="text-xs text-muted-foreground">2 hours ago</p>
                </div>
                <Button variant="ghost" size="sm">
                  Review
                </Button>
              </div>

              <div className="flex items-start gap-3 rounded-lg border border-warning/20 bg-warning/5 p-3">
                <AlertTriangle className="h-5 w-5 text-warning" />
                <div className="flex-1 space-y-1">
                  <p className="font-medium text-warning">Gaze away detected</p>
                  <p className="text-sm text-muted-foreground">
                    Student #18 - Exam #1 - Looking away repeatedly
                  </p>
                  <p className="text-xs text-muted-foreground">5 hours ago</p>
                </div>
                <Button variant="ghost" size="sm">
                  Review
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}