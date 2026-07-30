// frontend/src/lib/api.ts
// Client API NURU - connecté au backend FastAPI

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080';

// ─────────────────────────────────────── Types
export interface ChatResponse {
  response: string;
  session_id?: string;
  sources?: string[];
  rag_used?: boolean;
  error?: string;
}

export interface GenerateRequest {
  classe: string;
  serie?: string;
  chapitre: string;
  content_type: 'cours' | 'exercices' | 'quiz';
  num_questions?: number;
  difficulty?: string;
}

export interface GenerateResponse {
  content_type: string;
  classe: string;
  chapitre: string;
  serie?: string;
  markdown?: string;
  exercices?: any[];
  questions?: any[];
  sources: string[];
  rag_used: boolean;
  [key: string]: any;
}

export interface ChapitresResponse {
  chapitres: string[];
  classes: string[];
  series: string[];
}

// ─────────────────────────────────────── Auth APIs
export async function loginUserApi(payload: { email: string; password: string }) {
  const res = await fetch(`${API_BASE_URL}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || 'Connexion échouée');
  return data;
}

export async function registerUserApi(payload: {
  email: string;
  password: string;
  name: string;
  role: string;
  classe?: string;
  serie?: string;
  linked_student_identifier?: string;
}) {
  const res = await fetch(`${API_BASE_URL}/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "Erreur lors de l'inscription");
  return data;
}

export async function linkStudentApi(payload: {
  user_id: string;
  role: string;
  student_identifier: string;
}) {
  const res = await fetch(`${API_BASE_URL}/auth/link-student`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || 'Erreur lors de la liaison');
  return data;
}

// ─────────────────────────────────────── Generate API (RAG → Gemini)
export async function generateContent(payload: GenerateRequest): Promise<GenerateResponse> {
  const res = await fetch(`${API_BASE_URL}/generate/content`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Erreur lors de la génération');
  }
  return res.json();
}

export async function fetchChapitres(): Promise<ChapitresResponse> {
  try {
    const res = await fetch(`${API_BASE_URL}/generate/chapitres`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return res.json();
  } catch {
    return {
      chapitres: [
        'Révisions de trigonométrie', 'Dérivabilité', 'Limites et continuité',
        'Fonctions exponentielles', 'Fonctions logarithmes', 'Calcul intégral',
        'Suites numériques', 'Nombres complexes', 'Probabilités', 'Dénombrement',
        'Courbes paramétrées', 'Arithmétique', 'Équations différentielles',
        'Géométrie dans l\'espace', 'Coniques', 'Étude de fonctions',
      ],
      classes: ['Terminale'],
      series: ['S1', 'S2', 'S3', 'L1', 'L2'],
    };
  }
}

// ─────────────────────────────────────── Chatbot API (RAG → Gemini)
export async function sendChatMessage(
  message: string,
  sessionId?: string,
  userId?: string,
  classe?: string,
  chapitre?: string
): Promise<ChatResponse> {
  const res = await fetch(`${API_BASE_URL}/generate/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      message,
      session_id: sessionId || null,
      user_id: userId || null,
      classe: classe || 'Terminale',
      chapitre: chapitre || null,
    }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Le service IA est momentanément indisponible');
  }
  return res.json();
}

// ─────────────────────────────────────── Student APIs
export async function fetchStudentDashboard(userId: string) {
  try {
    const res = await fetch(`${API_BASE_URL}/student/dashboard/${userId}`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return res.json();
  } catch {
    return {
      student_id: userId,
      nb_evaluations: 0,
      total_xp: 0,
      overall_mastery: 0,
      mastery_map: [],
      badges: [],
      history: [],
      recommendations: [],
      is_empty_state: true,
    };
  }
}

export async function generateStudentQuiz(payload: {
  concept: string;
  num_questions?: number;
  difficulty?: string;
}) {
  const res = await fetch(`${API_BASE_URL}/generate/content`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      classe: 'Terminale',
      chapitre: payload.concept,
      content_type: 'quiz',
      num_questions: payload.num_questions || 3,
      difficulty: payload.difficulty || 'intermediate'
    }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Erreur lors de la génération du quiz");
  }
  return res.json();
}

export async function generateStudentExercise(payload: {
  concept: string;
  difficulty?: string;
}) {
  const res = await fetch(`${API_BASE_URL}/generate/content`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      classe: 'Terminale',
      chapitre: payload.concept,
      content_type: 'exercices',
      difficulty: payload.difficulty || 'intermediate',
      num_questions: 1
    }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Erreur lors de la génération de l'exercice");
  }
  return res.json();
}

export async function submitQuizEvaluation(payload: {
  user_id: string;
  concept: string;
  chapitre?: string;
  questions: any[];
  student_answers: any[];
}) {
  const res = await fetch(`${API_BASE_URL}/evaluation/quiz`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error('Erreur correction quiz');
  return res.json();
}

export async function submitExerciseEvaluation(payload: {
  user_id: string;
  concept: string;
  chapitre?: string;
  is_correct: boolean;
  student_answer?: string;
  expected_answer?: string;
}) {
  const res = await fetch(`${API_BASE_URL}/evaluation/exercice`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  if (!res.ok) throw new Error('Erreur correction exercice');
  return res.json();
}

// ─────────────────────────────────────── Teacher APIs
export async function fetchTeacherStudents(teacherId: string) {
  try {
    const res = await fetch(`${API_BASE_URL}/teacher/students/${teacherId}`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return res.json();
  } catch {
    return { teacher_id: teacherId, students: [] };
  }
}

export async function fetchClassStats(teacherId: string) {
  try {
    const res = await fetch(`${API_BASE_URL}/teacher/class-stats/${teacherId}`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return res.json();
  } catch {
    return { teacher_id: teacherId, nb_students: 0, students: [] };
  }
}

// ─────────────────────────────────────── Parent APIs
export async function fetchParentStudents(parentId: string) {
  try {
    const res = await fetch(`${API_BASE_URL}/parent/students/${parentId}`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return res.json();
  } catch {
    return { parent_id: parentId, students: [] };
  }
}

// ─────────────────────────────────────── Admin APIs
export async function fetchAdminStats() {
  try {
    const res = await fetch(`${API_BASE_URL}/admin/stats`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return res.json();
  } catch {
    return { total_users: 0, rag_vectors_count: 2635, courses_count: 32 };
  }
}

export async function fetchAdminUsers() {
  try {
    const res = await fetch(`${API_BASE_URL}/admin/users`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return res.json();
  } catch {
    return { users: [], total: 0 };
  }
}
