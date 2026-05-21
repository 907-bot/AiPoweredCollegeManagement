"use client"

import { useEffect, useState } from "react"
import Link from "next/link"
import { 
  FileText, 
  Plus, 
  Search, 
  Filter,
  MoreHorizontal,
  Clock,
  Users,
  Play,
  Pencil,
  Trash2,
  Eye
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { useExamStore } from "@/lib/store"
import { formatDate, formatDuration } from "@/lib/utils"
import type { ExamBrief } from "@/types"

const statusColors = {
  draft: "bg-muted text-muted-foreground",
  published: "bg-blue-500/20 text-blue-400",
  active: "bg-green-500/20 text-green-400",
  completed: "bg-purple-500/20 text-purple-400",
  archived: "bg-muted text-muted-foreground",
} as const

export default function ExamsPage() {
  const { exams, fetchExams, isLoading, deleteExam } = useExamStore()
  const [search, setSearch] = useState("")
  const [filter, setFilter] = useState<string>("")

  useEffect(() => {
    fetchExams({ status: filter || undefined })
  }, [fetchExams, filter])

  const filteredExams = exams.filter((exam) =>
    exam.title.toLowerCase().includes(search.toLowerCase())
  )

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Exams</h1>
          <p className="text-muted-foreground">Manage your examinations</p>
        </div>
        <Link href="/exams/new">
          <Button>
            <Plus className="mr-2 h-4 w-4" />
            Create Exam
          </Button>
        </Link>
      </div>

      {/* Filters */}
      <div className="flex gap-4">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            placeholder="Search exams..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-10"
          />
        </div>
        <div className="flex gap-2">
          <Button
            variant={filter === "" ? "secondary" : "outline"}
            size="sm"
            onClick={() => setFilter("")}
          >
            All
          </Button>
          <Button
            variant={filter === "active" ? "secondary" : "outline"}
            size="sm"
            onClick={() => setFilter("active")}
          >
            Active
          </Button>
          <Button
            variant={filter === "published" ? "secondary" : "outline"}
            size="sm"
            onClick={() => setFilter("published")}
          >
            Published
          </Button>
          <Button
            variant={filter === "draft" ? "secondary" : "outline"}
            size="sm"
            onClick={() => setFilter("draft")}
          >
            Draft
          </Button>
        </div>
      </div>

      {/* Exams Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {filteredExams.map((exam) => (
          <Card key={exam.id} className="card-hover group">
            <CardHeader className="pb-3">
              <div className="flex items-start justify-between">
                <div className="space-y-1">
                  <CardTitle className="line-clamp-1">{exam.title}</CardTitle>
                  <CardDescription className="flex items-center gap-2">
                    <Clock className="h-3 w-3" />
                    {formatDuration(exam.durationMinutes)}
                  </CardDescription>
                </div>
                <div className="flex items-center gap-1">
                  <span
                    className={`inline-flex items-center rounded-full px-2 py-1 text-xs font-medium capitalize ${
                      statusColors[exam.status]
                    }`}
                  >
                    {exam.status}
                  </span>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="flex items-center justify-between text-sm text-muted-foreground">
                <span>{formatDate(exam.createdAt)}</span>
                <div className="flex gap-1 opacity-0 transition-opacity group-hover:opacity-100">
                  <Button variant="ghost" size="icon" className="h-8 w-8">
                    <Eye className="h-4 w-4" />
                  </Button>
                  <Button variant="ghost" size="icon" className="h-8 w-8">
                    <Pencil className="h-4 w-4" />
                  </Button>
                  {(exam.status === "draft" || exam.status === "archived") && (
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-8 w-8 text-destructive"
                      onClick={() => deleteExam(exam.id)}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>
        ))}

        {filteredExams.length === 0 && (
          <div className="col-span-full">
            <Card className="py-12">
              <CardContent className="flex flex-col items-center justify-center text-center">
                <FileText className="h-12 w-12 text-muted-foreground" />
                <h3 className="mt-4 text-lg font-medium">No exams found</h3>
                <p className="mt-1 text-muted-foreground">
                  {search ? "Try adjusting your search" : "Create your first exam to get started"}
                </p>
                {!search && (
                  <Link href="/exams/new">
                    <Button className="mt-4">
                      <Plus className="mr-2 h-4 w-4" />
                      Create Exam
                    </Button>
                  </Link>
                )}
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </div>
  )
}