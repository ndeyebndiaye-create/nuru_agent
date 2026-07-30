'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { useAuth } from '@/context/AuthContext';
import { generateStudentQuiz, submitQuizEvaluation } from '@/lib/api';
import { MarkdownViewer } from '@/components/math/MarkdownViewer';
import { useParams } from 'next/navigation';
import {
  HelpCircle,
  ArrowLeft,
  CheckCircle2,
  XCircle,
  AlertCircle,
  ChevronRight,
  Brain,
  Loader2
} from 'lucide-react';

export default function QuizPage() {
  const { user } = useAuth();
  const params = useParams();
  const concept = typeof params.id === 'string' ? decodeURIComponent(params.id).replace(/-/g, ' ') : 'Quiz Général';
  
  const [quiz, setQuiz] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  const [selectedChoices, setSelectedChoices] = useState<Record<number, string>>({});
  const [isSubmitted, setIsSubmitted] = useState(false);

  useEffect(() => {
    generateStudentQuiz({ concept, num_questions: 3 })
      .then(res => {
        setQuiz(res);
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        setLoading(false);
      });
  }, [concept]);

  const handleSelectChoice = (questionIdx: number, choiceId: string) => {
    if (isSubmitted) return;
    setSelectedChoices(prev => ({
      ...prev,
      [questionIdx]: choiceId
    }));
  };

  const calculateScore = () => {
    let score = 0;
    quiz.questions.forEach((q: any, idx: number) => {
      if (selectedChoices[idx] === q.correct_answer) score += 1;
    });
    return score;
  };

  const handleSubmit = async () => {
    if (Object.keys(selectedChoices).length < quiz.questions.length) {
      alert("Veuillez répondre à toutes les questions avant de soumettre.");
      return;
    }

    setIsSubmitted(true);

    if (user?.id) {
      try {
        await submitQuizEvaluation({
          user_id: user.id,
          concept: concept,
          questions: quiz.questions,
          student_answers: Object.entries(selectedChoices).map(([qIdx, ans]) => ({
            question_id: quiz.questions[Number(qIdx)].id,
            selected_choice: ans,
            is_correct: quiz.questions[Number(qIdx)].correct_answer === ans
          }))
        });
      } catch (err) {
        console.error(err);
      }
    }
  };

  if (loading) {
    return <div className="p-12 flex justify-center"><Loader2 className="w-8 h-8 animate-spin text-emerald-600" /></div>;
  }

  if (!quiz || !quiz.questions) {
    return <div className="p-12 text-center text-slate-500">Erreur lors de la génération du quiz.</div>;
  }

  return (
    <div className="max-w-3xl mx-auto space-y-6 animate-in fade-in duration-200 p-8">
      <div className="flex items-center justify-between">
        <Link
          href="/"
          className="text-xs font-bold text-slate-600 hover:text-slate-900 flex items-center gap-1.5"
        >
          <ArrowLeft className="w-4 h-4 text-emerald-600" />
          Retour au Tableau de bord
        </Link>
        <span className="text-xs font-extrabold px-3 py-1 rounded-full bg-emerald-100 text-emerald-800">
          +{quiz.questions.length * 10} XP à gagner
        </span>
      </div>

      <div className="bg-white rounded-3xl p-6 sm:p-8 border border-slate-200 shadow-2xs space-y-8">
        <div className="space-y-1 border-b border-slate-100 pb-4 flex justify-between items-center">
          <div>
            <span className="text-[10px] font-extrabold uppercase px-2.5 py-0.5 rounded bg-emerald-100 text-emerald-800">
              Quiz d'évaluation Rapide
            </span>
            <h1 className="text-xl sm:text-2xl font-extrabold text-slate-900 mt-2">
              {quiz.chapitre || concept}
            </h1>
          </div>
          <div className="w-12 h-12 rounded-full bg-slate-50 border border-slate-200 flex items-center justify-center text-slate-400">
            <HelpCircle className="w-6 h-6" />
          </div>
        </div>

        <div className="space-y-10">
          {quiz.questions.map((q: any, qIdx: number) => {
            const isCorrect = selectedChoices[qIdx] === q.correct_answer;
            const hasAnswered = !!selectedChoices[qIdx];
            
            return (
              <div key={q.id || qIdx} className="space-y-4">
                <div className="flex gap-4">
                  <div className="w-8 h-8 rounded-full bg-emerald-600 text-white flex items-center justify-center font-bold text-sm shrink-0">
                    {qIdx + 1}
                  </div>
                  <div className="space-y-4 flex-1">
                    <h3 className="text-sm font-bold text-slate-800">
                      <MarkdownViewer content={q.question} />
                    </h3>
                    
                    <div className="space-y-2">
                      {q.choices.map((choice: any) => {
                        const isSelected = selectedChoices[qIdx] === choice.id;
                        const isCorrectChoice = choice.id === q.correct_answer;
                        
                        let buttonStateClass = "bg-white border-slate-200 hover:border-emerald-300 hover:bg-slate-50 text-slate-700";
                        
                        if (isSelected && !isSubmitted) {
                          buttonStateClass = "bg-emerald-50 border-emerald-500 text-emerald-900 ring-2 ring-emerald-100";
                        } else if (isSubmitted) {
                          if (isCorrectChoice) {
                            buttonStateClass = "bg-emerald-50 border-emerald-500 text-emerald-900";
                          } else if (isSelected && !isCorrectChoice) {
                            buttonStateClass = "bg-rose-50 border-rose-500 text-rose-900";
                          } else {
                            buttonStateClass = "bg-white border-slate-200 text-slate-400 opacity-50";
                          }
                        }

                        return (
                          <button
                            key={choice.id}
                            onClick={() => handleSelectChoice(qIdx, choice.id)}
                            disabled={isSubmitted}
                            className={`w-full text-left p-4 rounded-2xl border transition-all flex items-center justify-between ${buttonStateClass}`}
                          >
                            <div className="flex items-center gap-3">
                              <span className="w-6 h-6 rounded-full border border-current flex items-center justify-center text-[10px] font-bold">
                                {choice.id}
                              </span>
                              <span className="text-sm font-medium"><MarkdownViewer content={choice.text} /></span>
                            </div>
                            
                            {isSubmitted && isCorrectChoice && <CheckCircle2 className="w-5 h-5 text-emerald-500" />}
                            {isSubmitted && isSelected && !isCorrectChoice && <XCircle className="w-5 h-5 text-rose-500" />}
                          </button>
                        );
                      })}
                    </div>

                    {isSubmitted && (
                      <div className={`p-4 rounded-2xl text-xs flex gap-3 items-start border ${isCorrect ? 'bg-emerald-50 border-emerald-200 text-emerald-900' : 'bg-amber-50 border-amber-200 text-amber-900'}`}>
                        {isCorrect ? <CheckCircle2 className="w-5 h-5 text-emerald-600 shrink-0" /> : <AlertCircle className="w-5 h-5 text-amber-600 shrink-0" />}
                        <div className="space-y-1">
                          <p className="font-bold">{isCorrect ? 'Bonne réponse !' : 'Réponse incorrecte.'}</p>
                          <div className="opacity-90">
                            <MarkdownViewer content={q.explanation || 'Veuillez revoir cette notion dans le cours.'} />
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        <div className="pt-8 border-t border-slate-100 flex justify-end">
          {!isSubmitted ? (
            <button
              onClick={handleSubmit}
              disabled={Object.keys(selectedChoices).length < quiz.questions.length}
              className="px-8 py-3 bg-slate-900 hover:bg-slate-800 text-white text-sm font-bold rounded-2xl transition-all shadow-xs flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Soumettre mes réponses
              <ChevronRight className="w-4 h-4" />
            </button>
          ) : (
            <div className="w-full flex items-center justify-between p-4 rounded-2xl bg-emerald-50 border border-emerald-200">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-emerald-200 text-emerald-800 flex items-center justify-center font-black">
                  {calculateScore()}/{quiz.questions.length}
                </div>
                <div>
                  <p className="text-sm font-bold text-emerald-900">Évaluation terminée</p>
                  <p className="text-xs text-emerald-700">Vos résultats ont été enregistrés.</p>
                </div>
              </div>
              <Link
                href="/"
                className="px-6 py-2 bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold rounded-xl transition-all shadow-xs"
              >
                Retour au Tableau
              </Link>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
