export type UserRole = 'student' | 'teacher' | 'parent' | 'admin';

export type GradeLevel = 
  | '6ème'
  | '5ème'
  | '4ème'
  | '3ème (BFEM)'
  | 'Seconde S'
  | 'Première S1/S2'
  | 'Terminale S1'
  | 'Terminale S2';

export interface Subject {
  id: string;
  name: string;
  iconName: string;
  isFunctional: boolean; // Only Math is true
  color: string;
  gradient: string;
  chapterCount: number;
  description: string;
}

export interface Chapter {
  id: string;
  name: string;
  subjectId: string;
  gradeLevel: GradeLevel;
  description: string;
  conceptCount: number;
  masteryPercentage?: number;
  category: 'Analyse' | 'Géométrie' | 'Algèbre' | 'Probabilités' | 'Statistiques';
}

export interface Concept {
  id: string;
  chapterId: string;
  title: string;
  description: string;
  masteryScore: number;
  attempts: number;
  hasCourse: boolean;
  hasExercises: boolean;
  hasQuiz: boolean;
}

export interface Course {
  id: string;
  conceptId: string;
  title: string;
  chapterName: string;
  gradeLevel: GradeLevel;
  readTimeMinutes: number;
  summary: string;
  contentMarkdown: string;
  keyFormulas: string[];
  isPublished: boolean;
}

export interface Exercise {
  id: string;
  conceptId: string;
  title: string;
  chapterName: string;
  difficulty: 'facile' | 'moyen' | 'difficile';
  points: number;
  statementMarkdown: string;
  hints: string[];
  solutionMarkdown: string;
}

export interface QuizChoice {
  id: string;
  text: string;
}

export interface QuizQuestion {
  id: string;
  question: string;
  choices: QuizChoice[];
  correctChoiceId: string;
  explanation: string;
}

export interface Quiz {
  id: string;
  conceptId: string;
  title: string;
  chapterName: string;
  questions: QuizQuestion[];
  timeLimitSeconds?: number;
}

export interface Badge {
  id: string;
  label: string;
  description: string;
  icon: string;
  unlockedAt?: string;
  category: 'mastery' | 'streak' | 'challenge' | 'social';
}
