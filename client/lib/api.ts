import type {
  LoginCredentials,
  TokenResponse,
  User,
  Exam,
  ExamBrief,
  ExamSession,
  ExamSessionSubmit,
  BehaviorSummary,
  ExamStats,
  TenantStats,
} from "@/types";

// Configure your backend URL here
const API_BASE = process.env.NEXT_PUBLIC_API_URL || "https://your-backend.onrender.com/api/v1";

class ApiClient {
  private token: string | null = null;

  setToken(token: string | null) {
    this.token = token;
    if (typeof window !== "undefined") {
      if (token) {
        localStorage.setItem("token", token);
      } else {
        localStorage.removeItem("token");
      }
    }
  }

  getToken(): string | null {
    if (this.token) return this.token;
    if (typeof window !== "undefined") {
      return localStorage.getItem("token");
    }
    return null;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const token = this.getToken();
    const headers: HeadersInit = {
      "Content-Type": "application/json",
      ...options.headers,
    };

    if (token) {
      (headers as Record<string, string>)["Authorization"] = `Bearer ${token}`;
    }

    const response = await fetch(`${API_BASE}${endpoint}`, {
      ...options,
      headers,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: "Request failed" }));
      throw new Error(error.detail || error.error);
    }

    if (response.status === 204) {
      return null as T;
    }

    return response.json();
  }

  // Auth
  async login(credentials: LoginCredentials): Promise<TokenResponse> {
    const response = await this.request<TokenResponse>("/auth/login", {
      method: "POST",
      body: JSON.stringify(credentials),
    });
    this.setToken(response.access_token);
    return response;
  }

  async register(data: {
    email: string;
    password: string;
    username?: string;
    fullName?: string;
    role?: string;
  }): Promise<User> {
    return this.request<User>("/auth/register", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  logout() {
    this.setToken(null);
  }

  async getCurrentUser(): Promise<User> {
    return this.request<User>("/users/me");
  }

  // Exams
  async getExams(params?: {
    status?: string;
    page?: number;
    pageSize?: number;
  }): Promise<{ items: ExamBrief[]; total: number }> {
    const searchParams = new URLSearchParams(params as Record<string, string>);
    return this.request<{ items: ExamBrief[]; total: number }>(
      `/exams?${searchParams}`
    );
  }

  async getExam(id: number): Promise<Exam> {
    return this.request<Exam>(`/exams/${id}`);
  }

  async createExam(data: {
    title: string;
    description?: string;
    instructions?: string;
    durationMinutes: number;
    passingScore?: number;
    questions: { id: number; question: string; options: string[]; correct: number }[];
    scheduledAt?: string;
    expiresAt?: string;
  }): Promise<Exam> {
    return this.request<Exam>("/exams", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async updateExam(
    id: number,
    data: Partial<{
      title: string;
      description: string;
      instructions: string;
      durationMinutes: number;
      passingScore: number;
      status: string;
    }>
  ): Promise<Exam> {
    return this.request<Exam>(`/exams/${id}`, {
      method: "PATCH",
      body: JSON.stringify(data),
    });
  }

  async deleteExam(id: number): Promise<void> {
    return this.request<void>(`/exams/${id}`, { method: "DELETE" });
  }

  // Exam Sessions
  async startExamSession(examId: number): Promise<ExamSession> {
    return this.request<ExamSession>(`/exams/${examId}/start`, {
      method: "POST",
    });
  }

  async submitExamSession(
    examId: number,
    data: ExamSessionSubmit
  ): Promise<ExamSession> {
    return this.request<ExamSession>(`/exams/${examId}/submit`, {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async getExamSessions(
    examId: number,
    params?: { page?: number; pageSize?: number }
  ): Promise<{ items: ExamSession[]; total: number }> {
    const searchParams = new URLSearchParams(params as Record<string, string>);
    return this.request<{ items: ExamSession[]; total: number }>(
      `/exams/${examId}/sessions?${searchParams}`
    );
  }

  // Behavior
  async getBehaviorSummary(sessionId: number): Promise<BehaviorSummary> {
    return this.request<BehaviorSummary>(`/sessions/${sessionId}/behavior`);
  }

  // Analytics
  async getExamAnalytics(examId: number): Promise<ExamStats> {
    return this.request<ExamStats>(`/analytics/exams/${examId}`);
  }

  async getTenantAnalytics(): Promise<TenantStats> {
    return this.request<TenantStats>("/analytics/tenant");
  }

  // Health
  async healthCheck(): Promise<{ status: string; timestamp: string }> {
    return this.request<{ status: string; timestamp: string }>("/health");
  }
}

export const api = new ApiClient();