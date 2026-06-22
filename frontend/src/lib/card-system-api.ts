const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8080";

export type DocumentRecord = {
  id: string;
  title: string;
  content: string;
  file_path?: string | null;
  created_at?: string;
};

export type KnowledgeCard = {
  id: string;
  document_id?: string;
  title: string;
  summary: string;
  explanation: string;
  example?: string;
  keywords: string[];
  related_concepts?: string[];
  related_points?: string[];
  common_mistakes: string[];
  source_text?: string;
};

export type QuizQuestion = {
  id: string;
  card_id?: string;
  question: string;
  question_type: string;
  options: string[];
  answer: string;
  explanation: string;
  difficulty: string;
  related_card_title?: string;
};

export type AnswerCheckResult = {
  is_correct: boolean;
  correct_answer: string;
  explanation: string;
  feedback: string;
};

export type WrongQuestion = {
  id: string;
  question: string;
  related_knowledge?: string;
  error_count: number;
  explanation: string;
};

export type ReviewTask = {
  day: number;
  topic: string;
  task: string;
  reason: string;
  is_completed: boolean;
};

export type ReviewPlan = {
  id: string;
  weak_points: string[];
  tasks: ReviewTask[];
};

export type StudySummary = {
  document_count: number;
  card_count: number;
  quiz_count: number;
  answer_count: number;
  wrong_count: number;
  accuracy: number;
};

export type AgentTraceItem = {
  step: number;
  name: string;
  status: string;
  detail: string;
};

export type AgentReviewTask = {
  day: number;
  task_title: string;
  task_content: string;
  reason: string;
};

export type AgentReviewPlan = {
  id?: string;
  plan_title: string;
  review_days: number;
  weak_points: string[];
  daily_tasks: AgentReviewTask[];
};

export type AgentAnalyzeResponse = {
  document_id: string;
  agent_name: "CardReviewAgent";
  agent_trace: AgentTraceItem[];
  cards: KnowledgeCard[];
  quizzes: QuizQuestion[];
  review_plan: AgentReviewPlan;
  summary: {
    filename: string;
    learning_goal: string;
    char_count: number;
    rag_chunk_count: number;
    card_count: number;
    quiz_count: number;
    review_days: number;
    memory_status: "saved" | "fallback";
  };
};

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...init?.headers,
    },
  });

  if (!response.ok) {
    const message = await response.text().catch(() => response.statusText);
    throw new Error(message || response.statusText);
  }

  return response.json() as Promise<T>;
}

async function uploadRequest<T>(path: string, formData: FormData): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const message = await response.text().catch(() => response.statusText);
    throw new Error(message || response.statusText);
  }

  return response.json() as Promise<T>;
}

export const cardSystemApi = {
  analyzeStudyFile(formData: FormData) {
    return uploadRequest<AgentAnalyzeResponse>("/card-system/agent/analyze-file", formData);
  },

  createDocument(input: { title?: string | null; content: string; file_path?: string | null }) {
    return request<DocumentRecord>("/card-system/documents", {
      method: "POST",
      body: JSON.stringify(input),
    });
  },

  listDocuments() {
    return request<DocumentRecord[]>("/card-system/documents");
  },

  generateCards(input: { document_id?: string; text?: string; title?: string }) {
    return request<{ document: DocumentRecord; cards: { cards: KnowledgeCard[] } }>("/card-system/cards/generate", {
      method: "POST",
      body: JSON.stringify(input),
    });
  },

  listCards(documentId?: string) {
    const query = documentId ? `?document_id=${encodeURIComponent(documentId)}` : "";
    return request<KnowledgeCard[]>(`/card-system/cards${query}`);
  },

  generateQuiz(input: { card_id?: string }) {
    return request<{ questions: { questions: QuizQuestion[] } }>("/card-system/quiz/generate", {
      method: "POST",
      body: JSON.stringify(input),
    });
  },

  listQuiz(cardId?: string) {
    const query = cardId ? `?card_id=${encodeURIComponent(cardId)}` : "";
    return request<QuizQuestion[]>(`/card-system/quiz${query}`);
  },

  submitQuiz(input: { question_id: string; user_answer: string }) {
    return request<{ result: AnswerCheckResult; record: Record<string, unknown> }>("/card-system/quiz/submit", {
      method: "POST",
      body: JSON.stringify(input),
    });
  },

  listWrongQuestions() {
    return request<WrongQuestion[]>("/card-system/wrong-questions");
  },

  generateReviewPlan(input: { weak_points?: string[]; title?: string }) {
    return request<{ plan: ReviewPlan; record: Record<string, unknown> }>("/card-system/review-plan/generate", {
      method: "POST",
      body: JSON.stringify(input),
    });
  },

  getStudySummary() {
    return request<StudySummary>("/card-system/study-summary");
  },
};
