import { create } from "zustand";
import { persist } from "zustand/middleware";
import type { User, Exam, ExamBrief, ExamSession, TenantStats } from "@/types";
import { api } from "@/lib/api";

interface AuthState {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (data: {
    email: string;
    password: string;
    username?: string;
    fullName?: string;
    role?: string;
  }) => Promise<void>;
  logout: () => void;
  checkAuth: () => Promise<void>;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      isLoading: false,
      isAuthenticated: false,

      login: async (email: string, password: string) => {
        set({ isLoading: true });
        try {
          await api.login({ email, password });
          const user = await api.getCurrentUser();
          set({ user, isAuthenticated: true, isLoading: false });
        } catch (error) {
          set({ isLoading: false });
          throw error;
        }
      },

      register: async (data) => {
        set({ isLoading: true });
        try {
          await api.register(data);
          await api.login({ email: data.email, password: data.password });
          const user = await api.getCurrentUser();
          set({ user, isAuthenticated: true, isLoading: false });
        } catch (error) {
          set({ isLoading: false });
          throw error;
        }
      },

      logout: () => {
        api.logout();
        set({ user: null, isAuthenticated: false });
      },

      checkAuth: async () => {
        const token = api.getToken();
        if (!token) {
          set({ isAuthenticated: false, user: null });
          return;
        }
        try {
          const user = await api.getCurrentUser();
          set({ user, isAuthenticated: true });
        } catch {
          api.logout();
          set({ user: null, isAuthenticated: false });
        }
      },
    }),
    {
      name: "auth-storage",
      partialize: (state) => ({
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);

interface ExamState {
  exams: ExamBrief[];
  currentExam: Exam | null;
  currentSession: ExamSession | null;
  sessions: ExamSession[];
  stats: TenantStats | null;
  isLoading: boolean;
  fetchExams: (params?: { status?: string; page?: number; pageSize?: number }) => Promise<void>;
  fetchExam: (id: number) => Promise<void>;
  createExam: (data: Parameters<typeof api.createExam>[0]) => Promise<Exam>;
  updateExam: (id: number, data: Parameters<typeof api.updateExam>[1]) => Promise<void>;
  deleteExam: (id: number) => Promise<void>;
  startSession: (examId: number) => Promise<void>;
  submitSession: (examId: number, answers: Parameters<typeof api.submitExamSession>[1]) => Promise<void>;
  fetchStats: () => Promise<void>;
}

export const useExamStore = create<ExamState>()((set, get) => ({
  exams: [],
  currentExam: null,
  currentSession: null,
  sessions: [],
  stats: null,
  isLoading: false,

  fetchExams: async (params) => {
    set({ isLoading: true });
    try {
      const response = await api.getExams(params);
      set({ exams: response.items, isLoading: false });
    } catch (error) {
      set({ isLoading: false });
      throw error;
    }
  },

  fetchExam: async (id) => {
    set({ isLoading: true });
    try {
      const exam = await api.getExam(id);
      set({ currentExam: exam, isLoading: false });
    } catch (error) {
      set({ isLoading: false });
      throw error;
    }
  },

  createExam: async (data) => {
    set({ isLoading: true });
    try {
      const exam = await api.createExam(data);
      const exams = [...get().exams, exam];
      set({ exams, currentExam: exam, isLoading: false });
      return exam;
    } catch (error) {
      set({ isLoading: false });
      throw error;
    }
  },

  updateExam: async (id, data) => {
    set({ isLoading: true });
    try {
      const exam = await api.updateExam(id, data);
      const exams = get().exams.map((e) => (e.id === id ? exam : e));
      set({ exams, currentExam: exam, isLoading: false });
    } catch (error) {
      set({ isLoading: false });
      throw error;
    }
  },

  deleteExam: async (id) => {
    set({ isLoading: true });
    try {
      await api.deleteExam(id);
      const exams = get().exams.filter((e) => e.id !== id);
      set({ exams, isLoading: false });
    } catch (error) {
      set({ isLoading: false });
      throw error;
    }
  },

  startSession: async (examId) => {
    set({ isLoading: true });
    try {
      const session = await api.startExamSession(examId);
      set({ currentSession: session, isLoading: false });
    } catch (error) {
      set({ isLoading: false });
      throw error;
    }
  },

  submitSession: async (examId, answers) => {
    set({ isLoading: true });
    try {
      const session = await api.submitExamSession(examId, answers);
      set({ currentSession: session, isLoading: false });
    } catch (error) {
      set({ isLoading: false });
      throw error;
    }
  },

  fetchStats: async () => {
    try {
      const stats = await api.getTenantAnalytics();
      set({ stats });
    } catch (error) {
      console.error("Failed to fetch stats:", error);
    }
  },
}));

// UI State
interface UIState {
  sidebarOpen: boolean;
  toggleSidebar: () => void;
  setSidebarOpen: (open: boolean) => void;
  toasts: { id: string; message: string; type: "success" | "error" | "info" }[];
  addToast: (message: string, type: "success" | "error" | "info") => void;
  removeToast: (id: string) => void;
}

export const useUIStore = create<UIState>()((set) => ({
  sidebarOpen: true,
  toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
  setSidebarOpen: (open) => set({ sidebarOpen: open }),
  toasts: [],
  addToast: (message, type) =>
    set((state) => ({
      toasts: [...state.toasts, { id: Math.random().toString(36), message, type }],
    })),
  removeToast: (id) =>
    set((state) => ({
      toasts: state.toasts.filter((t) => t.id !== id),
    })),
}));