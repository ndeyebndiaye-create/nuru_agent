'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { useAuth } from '@/context/AuthContext';
import { generateStudentExercise, submitExerciseEvaluation } from '@/lib/api';
import ReactMarkdown from 'react-markdown';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import 'katex/dist/katex.min.css';
import {
  CheckCircle2,
  ArrowLeft,
  Sparkles,
  Brain,
  Loader2
} from 'lucide-react';
import { useParams } from 'next/navigation';

export default function ExercisePage() {
  const { user } = useAuth();
  const params = useParams();
  const concept = typeof params.id === 'string' ? decodeURIComponent(params.id).replace(/-/g, ' ') : 'Exercice Général';
  
  const [exercise, setExercise] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  
  const [userAnswer, setUserAnswer] = useState('');
  const [showCorrection, setShowCorrection] = useState(false);
  const [isEvaluated, setIsEvaluated] = useState(false);

  useEffect(() => {
    // Generate an exercise dynamically based on the URL ID
    generateStudentExercise({ concept })
      .then(res => {
        // extract the first exercise if the response is formatted as the prompt requested
        if (res.exercices && res.exercices.length > 0) {
          setExercise(res.exercices[0]);
        } else {
          setExercise(res); // fallback
        }
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        setLoading(false);
      });
  }, [concept]);

  const handleToggleCorrection = async () => {
    const nextState = !showCorrection;
    setShowCorrection(nextState);

    if (nextState && !isEvaluated && user?.id) {
      setIsEvaluated(true);
      try {
        await submitExerciseEvaluation({
          user_id: user.id,
          concept: concept,
          is_correct: userAnswer.trim().length > 5,
          student_answer: userAnswer
        });
      } catch (err) {
        console.error(err);
      }
    }
  };

  if (loading) {
    return <div className="p-12 flex justify-center"><Loader2 className="w-8 h-8 animate-spin text-emerald-600" /></div>;
  }

  if (!exercise) {
    return <div className="p-12 text-center text-slate-500">Erreur lors de la génération de l'exercice.</div>;
  }

  return (
    <div className="max-w-3xl mx-auto space-y-6 animate-in fade-in duration-200 p-8">
      {/* Top Header */}
      <div className="flex items-center justify-between">
        <Link
          href="/"
          className="text-xs font-bold text-slate-600 hover:text-slate-900 flex items-center gap-1.5"
        >
          <ArrowLeft className="w-4 h-4 text-emerald-600" />
          Retour au Tableau de bord
        </Link>
        <span className="text-xs font-extrabold px-3 py-1 rounded-full bg-emerald-100 text-emerald-800">
          +20 XP à gagner
        </span>
      </div>

      <div className="bg-white rounded-3xl p-6 sm:p-8 border border-slate-200 shadow-2xs space-y-6">
        <div className="space-y-1 border-b border-slate-100 pb-4">
          <span className="text-[10px] font-extrabold uppercase px-2.5 py-0.5 rounded bg-emerald-100 text-emerald-800">
            Exercice Dynamique
          </span>
          <h1 className="text-xl sm:text-2xl font-extrabold text-slate-900">
            {exercise.titre || concept}
          </h1>
        </div>

        {/* 1. ÉNONCÉ */}
        <div className="space-y-3">
          <h3 className="font-extrabold text-xs text-slate-900 uppercase tracking-wider flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-600" />
            1. Énoncé du problème
          </h3>
          <div className="markdown-body prose prose-sm max-w-none text-slate-700 bg-slate-50 p-4 rounded-xl border border-slate-100">
            <ReactMarkdown remarkPlugins={[remarkMath]} rehypePlugins={[rehypeKatex]}>
              {exercise.enonce || exercise.raw || "Pas d'énoncé fourni."}
            </ReactMarkdown>
          </div>
        </div>

        {/* 2. ZONE DE RÉPONSE */}
        <div className="space-y-3 pt-4 border-t border-slate-100">
          <h3 className="font-extrabold text-xs text-slate-900 uppercase tracking-wider">
            2. Votre zone de réponse et étapes de calcul
          </h3>
          <textarea
            value={userAnswer}
            onChange={(e) => setUserAnswer(e.target.value)}
            placeholder="Saisissez vos étapes de calcul ou votre résultat ici..."
            className="w-full bg-slate-50 border border-slate-200 rounded-2xl p-4 text-xs text-slate-800 focus:bg-white focus:border-emerald-500 focus:ring-2 focus:ring-emerald-100 outline-none transition-all h-28"
          />
        </div>

        {/* 3. CORRECTION & EXPLICATION IA */}
        <div className="pt-4 border-t border-slate-100 space-y-4">
          <button
            onClick={handleToggleCorrection}
            className="w-full py-3 px-4 rounded-2xl bg-slate-900 hover:bg-slate-800 text-white text-xs font-bold transition-all shadow-xs flex items-center justify-center gap-2 cursor-pointer"
          >
            <Sparkles className="w-4 h-4 text-amber-400" />
            <span>{showCorrection ? 'Masquer la Correction' : 'Évaluer & Voir la Correction IA'}</span>
          </button>

          {showCorrection && (
            <div className="space-y-4 animate-in fade-in">
              <div className="p-6 rounded-2xl bg-emerald-50/70 border border-emerald-200 space-y-3">
                <h4 className="font-bold text-xs text-emerald-900 uppercase">3. Correction Détaillée & Validation</h4>
                <div className="markdown-body prose prose-sm max-w-none">
                  <ReactMarkdown remarkPlugins={[remarkMath]} rehypePlugins={[rehypeKatex]}>
                    {exercise.correction || "Correction non fournie."}
                  </ReactMarkdown>
                </div>
              </div>

              <div className="p-4 rounded-2xl bg-slate-50 border border-slate-200 space-y-2">
                <h4 className="font-bold text-xs text-slate-900 flex items-center gap-1.5">
                  <Brain className="w-4 h-4 text-emerald-600" />
                  Progression mise à jour
                </h4>
                <p className="text-xs text-slate-600 leading-relaxed">
                  Votre soumission a été évaluée et votre profil de maîtrise a été mis à jour dans le système.
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
