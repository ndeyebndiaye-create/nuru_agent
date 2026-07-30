'use client';

import React from 'react';
import Link from 'next/link';
import { MATH_CHAPTERS } from '@/lib/mockData';
import { MathRenderer } from '@/components/math/MathRenderer';
import {
  TrendingUp,
  BarChart2,
  Award,
  AlertTriangle,
  Sparkles,
  History,
  ArrowRight,
  CheckCircle2,
  Target
} from 'lucide-react';

export default function ProgressionPage() {
  const historyLog = [
    { id: '1', date: 'Aujourd’hui, 16:45', type: 'Quiz', title: 'Quiz Logarithmes & Croissances Comparées', score: '3/3 (100%)', badge: 'Maître des Logarithmes' },
    { id: '2', date: 'Hier, 14:20', type: 'Exercice', title: 'Résolution d’Équations Logarithmiques', score: '20 XP', badge: '' },
    { id: '3', date: '25 Juillet 2026', type: 'Cours', title: 'La Fonction Logarithme Néperien', score: 'Lecture validée', badge: '' },
    { id: '4', date: '24 Juillet 2026', type: 'Quiz', title: 'Limites et Asymptotes', score: '4/5 (80%)', badge: '' }
  ];

  return (
    <div className="max-w-7xl mx-auto space-y-8 animate-in fade-in duration-300">
      {/* Page Header */}
      <div className="space-y-2">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-100 text-blue-700 text-xs font-bold">
          <TrendingUp className="w-3.5 h-3.5" />
          <span>Statistiques & Suivi de Maîtrise</span>
        </div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
          Progression Globale en Mathématiques
        </h1>
        <p className="text-slate-600 text-xs sm:text-sm">
          Analyse dynamique de vos compétences calculée par l’Agent de Progression NURU.
        </p>
      </div>

      {/* Top Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-3xl p-6 border border-slate-200 shadow-xs space-y-2">
          <div className="flex items-center justify-between text-slate-500 text-xs font-bold">
            <span>Taux de Maîtrise Global</span>
            <BarChart2 className="w-4 h-4 text-blue-600" />
          </div>
          <div className="text-3xl font-black text-slate-900">78%</div>
          <div className="w-full bg-slate-100 rounded-full h-2 overflow-hidden">
            <div className="bg-blue-600 h-full w-[78%]"></div>
          </div>
        </div>

        <div className="bg-white rounded-3xl p-6 border border-slate-200 shadow-xs space-y-2">
          <div className="flex items-center justify-between text-slate-500 text-xs font-bold">
            <span>Notions Travaillées</span>
            <CheckCircle2 className="w-4 h-4 text-emerald-600" />
          </div>
          <div className="text-3xl font-black text-slate-900">12 / 15</div>
          <p className="text-[11px] text-emerald-600 font-semibold">+3 notions validées cette semaine</p>
        </div>

        <div className="bg-white rounded-3xl p-6 border border-slate-200 shadow-xs space-y-2">
          <div className="flex items-center justify-between text-slate-500 text-xs font-bold">
            <span>Points XP Cumulés</span>
            <Award className="w-4 h-4 text-amber-500" />
          </div>
          <div className="text-3xl font-black text-slate-900">1 450 XP</div>
          <p className="text-[11px] text-amber-600 font-semibold">Niveau 4 : Génie de l'Analyse</p>
        </div>
      </div>

      {/* Next Step AI Recommendation */}
      <div className="p-6 rounded-3xl bg-gradient-to-r from-amber-500/10 via-amber-500/5 to-white border border-amber-200/80 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div className="flex items-start gap-4">
          <div className="w-12 h-12 rounded-2xl bg-amber-500 text-white flex items-center justify-center shrink-0 shadow-md shadow-amber-500/20">
            <Sparkles className="w-6 h-6" />
          </div>
          <div className="space-y-1">
            <span className="text-[10px] font-extrabold uppercase text-amber-800 tracking-wider">
              Prochaine Étape Recommandée par NURU
            </span>
            <h3 className="text-base font-bold text-slate-900">
              Renforcer la notion : Intégration par parties (Intégration & Primitives)
            </h3>
            <p className="text-xs text-slate-600">
              Votre score actuel sur ce chapitre est de 45%. NURU a détecté 2 hésitations lors du dernier exercice.
            </p>
          </div>
        </div>

        <Link
          href="/cours/cours-logarithme-neperien"
          className="px-5 py-2.5 rounded-xl bg-amber-600 hover:bg-amber-700 text-white text-xs font-bold shadow-md shadow-amber-600/20 transition-colors shrink-0"
        >
          Revoir le cours
        </Link>
      </div>

      {/* Chapter Breakdown & History */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left 2 cols: Category Progress Bars */}
        <div className="lg:col-span-2 bg-white rounded-3xl p-6 sm:p-8 border border-slate-200 shadow-xs space-y-6">
          <h2 className="text-lg font-bold text-slate-900 flex items-center gap-2">
            <Target className="w-5 h-5 text-blue-600" />
            Maîtrise par Chapitre
          </h2>

          <div className="space-y-4">
            {MATH_CHAPTERS.map((chap) => (
              <div key={chap.id} className="space-y-1.5 p-3 rounded-2xl bg-slate-50 border border-slate-100">
                <div className="flex items-center justify-between text-xs font-bold text-slate-800">
                  <span>{chap.name}</span>
                  <span className="text-blue-600">{chap.masteryPercentage}%</span>
                </div>
                <div className="w-full bg-slate-200 rounded-full h-2 overflow-hidden">
                  <div
                    className="bg-gradient-to-r from-blue-600 to-indigo-600 h-full rounded-full"
                    style={{ width: `${chap.masteryPercentage}%` }}
                  ></div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Right 1 col: Learning History Log */}
        <div className="bg-white rounded-3xl p-6 border border-slate-200 shadow-xs space-y-4">
          <h2 className="text-base font-bold text-slate-900 flex items-center gap-2" id="historique">
            <History className="w-4 h-4 text-blue-600" />
            Historique Récents
          </h2>

          <div className="space-y-3">
            {historyLog.map((log) => (
              <div key={log.id} className="p-3 rounded-xl bg-slate-50 border border-slate-100 space-y-1">
                <div className="flex items-center justify-between text-[11px] text-slate-400">
                  <span className="font-semibold text-slate-700">{log.type}</span>
                  <span>{log.date}</span>
                </div>
                <h4 className="text-xs font-bold text-slate-900">{log.title}</h4>
                <div className="text-[11px] font-semibold text-blue-600">{log.score}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
