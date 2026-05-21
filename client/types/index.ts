// User types
export type UserRole = 'admin' | 'teacher' | 'student';

export interface User {
  id: number;
  email: string;
  username?: string;
  fullName?: string;
  role: UserRole;
  department?: string;
  isActive: boolean;
  emailVerified: boolean;
  lastLogin?: string;
  createdAt: string;
  updatedAt: string;
}

// Auth types
export interface LoginCredentials {
  email: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

// Exam types
export type ExamStatus = 'draft' | 'published' | 'active' | 'completed' | 'archived';

export interface Question {
  id: number;
  question: string;
  options: string[];
  correct: number;
}

export interface Exam {
  id: number;
  tenantId: number;
  createdBy?: number;
  title: string;
  description?: string;
  instructions?: string;
  durationMinutes: number;
  passingScore: number;
  questions: Question[];
  shuffleQuestions: boolean;
  shuffleOptions: boolean;
  showResults: boolean;
  status: ExamStatus;
  scheduledAt?: string;
  expiresAt?: string;
  createdAt: string;
  updatedAt: string;
}

export interface ExamBrief {
  id: number;
  title: string;
  status: ExamStatus;
  durationMinutes: number;
  createdAt: string;
}

// Exam Session
export interface ExamSession {
  id: number;
  examId: number;
  userId: number;
  answers?: Record<number, number>;
  score?: number;
  totalCorrect?: number;
  totalQuestions?: number;
  isCompleted: boolean;
  isFlagged: boolean;
  startedAt: string;
  submittedAt?: string;
}

export interface AnswerSubmit {
  questionId: number;
  selectedOption: number;
}

export interface ExamSessionSubmit {
  answers: AnswerSubmit[];
}

// Behavior monitoring
export type EventType =
  | 'face_not_detected'
  | 'multiple_faces'
  | 'gaze_away'
  | 'suspicious_movement'
  | 'object_detected'
  | 'audio_anomaly'
  | 'tab_switch'
  | 'copy_paste_attempt';

export interface BehaviorEvent {
  id: number;
  sessionId: number;
  eventType: EventType;
  severity: number;
  details?: Record<string, unknown>;
  timestamp: string;
}

export interface BehaviorSummary {
  sessionId: number;
  totalEvents: number;
  flagged: boolean;
  avgSeverity: number;
  eventsByType: Record<string, number>;
}

// Analytics
export interface ExamStats {
  examId: number;
  totalSessions: number;
  completedSessions: number;
  avgScore: number;
  passRate: number;
  flaggedSessions: number;
}

export interface TenantStats {
  totalUsers: number;
  totalExams: number;
  totalSessions: number;
  completionRate: number;
  avgScore: number;
  exams: ExamStats[];
}

// API Response types
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
}

export interface ApiError {
  error: string;
  detail?: string;
}

// WebSocket for proctoring
export interface ProctorFrame {
  frame: string; // base64
  sessionId: number;
  timestamp: number;
}