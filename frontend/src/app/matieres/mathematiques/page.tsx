'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { MATH_CHAPTERS } from '@/lib/mockData';
import { MathRenderer } from '@/components/math/MathRenderer';
import {
  Calculator,
  BookOpen,
  CheckCircle2,
  HelpCircle,
  Sparkles,
  ArrowRight,
  TrendingUp,
  Brain
} from 'lucide-react';

export default function MathematiquesPage() {
  const [selectedCategory, setSelectedCategory] = useState<string>('Tous');

  const categories = ['Tous', 'Analyse', 'Géométrie', 'Probabilités'];

  const filteredChapters = selectedCategory === 'Tous'
    ? MATH_CHAPTERS
    : MATH_CHAPTERS.filter((c) => c.category === selectedCategory);

  return (
    <div className="max-w-7xl mx-auto space-y-8 animate-in fade-in duration-300">
      {/* Header Banner */}
      <div className="rounded-3xl bg-gradient-to-r from-blue-900 via-indigo-900 to-slate-900 p-6 sm:p-8 text-white shadow-xl space-y-4 border border-blue-800">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="space-y-2">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/20 text-blue-300 text-xs font-semibold border border-blue-400/30">
              <Calculator className="w-3.5 h-3.5" />
              <span>Spécialité NURU Active</span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight">
              Mathématiques - Terminale S1
            </h1>
            <p className="text-slate-300 text-xs sm:text-sm max-w-2xl">
              Accédez aux cours structurés, formules KaTeX (<MathRenderer formula="\int f(x) dx" />), séries d’exercices et quiz d’évaluation.
            </p>
          </div>

          <div className="bg-white/10 backdrop-blur-md p-4 rounded-2xl border border-white/10 text-center shrink-0">
            <div className="text-2xl font-black text-blue-400">14</div>
            <div className="text-xs text-slate-300 font-medium">Chapitres au total</div>
          </div>
        </div>

        {/* Categories Filter Tabs */}
        <div className="flex items-center gap-2 pt-2 overflow-x-auto">
          {categories.map((cat) => (
            <button
              key={cat}
              onClick={() => setSelectedCategory(cat)}
              className={`px-4 py-2 rounded-xl text-xs font-bold transition-all shrink-0 ${
                selectedCategory === cat
                  ? 'bg-blue-600 text-white shadow-md shadow-blue-600/30'
                  : 'bg-white/10 text-slate-300 hover:bg-white/20'
              }`}
            >
              {cat}
            </button>
          ))}
        </div>
      </div>

      {/* Chapters Grid */}
      <div className="space-y-4">
        <h2 className="text-lg font-extrabold text-slate-900 flex items-center gap-2">
          <BookOpen className="w-5 h-5 text-blue-600" />
          Liste des Chapitres ({filteredChapters.length})
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {filteredChapters.map((chap) => (
            <div
              key={chap.id}
              className="bg-white rounded-3xl p-6 border border-slate-200 shadow-xs hover:shadow-lg transition-all space-y-6 flex flex-col justify-between"
            >
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-[10px] font-extrabold uppercase px-2.5 py-1 rounded bg-blue-50 text-blue-700 border border-blue-100">
                    {chap.category}
                  </span>
                  <div className="flex items-center gap-1.5 text-xs font-bold text-emerald-600 bg-emerald-50 px-3 py-1 rounded-full border border-emerald-200">
                    <TrendingUp className="w-3.5 h-3.5" />
                    <span>{chap.masteryPercentage}% Maîtrisé</span>
                  </div>
                </div>

                <h3 className="text-lg font-bold text-slate-900">
                  {chap.name}
                </h3>
                <p className="text-xs text-slate-600 leading-relaxed">
                  {chap.description}
                </p>

                {/* Progress bar */}
                <div className="space-y-1 pt-1">
                  <div className="w-full bg-slate-100 rounded-full h-2 overflow-hidden">
                    <div
                      className="bg-gradient-to-r from-blue-600 to-indigo-600 h-full rounded-full"
                      style={{ width: `${chap.masteryPercentage}%` }}
                    ></div>
                  </div>
                </div>
              </div>

              {/* Action Buttons for Course, Exercise, Quiz */}
              <div className="pt-4 border-t border-slate-100 grid grid-cols-3 gap-2 text-center">
                <Link
                  href="/cours/cours-logarithme-neperien"
                  className="p-2.5 rounded-xl bg-blue-50 hover:bg-blue-100 text-blue-700 font-bold text-xs transition-colors flex items-center justify-center gap-1.5"
                >
                  <BookOpen className="w-3.5 h-3.5" />
                  <span>Cours</span>
                </Link>
                <Link
                  href="/exercices/exo-log-1"
                  className="p-2.5 rounded-xl bg-emerald-50 hover:bg-emerald-100 text-emerald-700 font-bold text-xs transition-colors flex items-center justify-center gap-1.5"
                >
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  <span>Exercices</span>
                </Link>
                <Link
                  href="/quiz/quiz-log-1"
                  className="p-2.5 rounded-xl bg-indigo-50 hover:bg-indigo-100 text-indigo-700 font-bold text-xs transition-colors flex items-center justify-center gap-1.5"
                >
                  <HelpCircle className="w-3.5 h-3.5" />
                  <span>Quiz</span>
                </Link>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
