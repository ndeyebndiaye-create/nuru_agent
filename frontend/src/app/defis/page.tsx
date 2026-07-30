'use client';

import React from 'react';
import { BADGES } from '@/lib/mockData';
import {
  Trophy,
  Award,
  Zap,
  Flame,
  Star,
  Users,
  CheckCircle2,
  Lock
} from 'lucide-react';

export default function DefisPage() {
  const leaderboard = [
    { rank: 1, name: 'Amadou Sow', points: '1,890 XP', streak: 12, grade: 'Terminale S1' },
    { rank: 2, name: 'Fatou Ndiaye', points: '1,620 XP', streak: 9, grade: 'Terminale S1' },
    { rank: 3, name: 'Élève NURU (Vous)', points: '1,450 XP', streak: 7, grade: 'Terminale S1', isUser: true },
    { rank: 4, name: 'Moussa Diallo', points: '1,210 XP', streak: 5, grade: 'Terminale S1' },
    { rank: 5, name: 'Awa Camara', points: '980 XP', streak: 4, grade: 'Terminale S1' }
  ];

  return (
    <div className="max-w-7xl mx-auto space-y-8 animate-in fade-in duration-300">
      {/* Header */}
      <div className="space-y-2">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-amber-100 text-amber-800 text-xs font-bold">
          <Trophy className="w-3.5 h-3.5 text-amber-600" />
          <span>Défis & Gamification</span>
        </div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
          Badges, Défis & Classement
        </h1>
        <p className="text-slate-600 text-xs sm:text-sm">
          Gagnez des points XP en résolvant des exercices et montez sur le podium de votre classe.
        </p>
      </div>

      {/* Badges Gallery */}
      <section className="space-y-4">
        <h2 className="text-lg font-extrabold text-slate-900 flex items-center gap-2">
          <Award className="w-5 h-5 text-amber-500" />
          Vos Badges Débloqués & En Cours
        </h2>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {BADGES.map((b) => (
            <div
              key={b.id}
              className={`p-5 rounded-3xl border transition-all flex flex-col justify-between space-y-4 ${
                b.unlockedAt
                  ? 'bg-white border-amber-200 shadow-md shadow-amber-500/5'
                  : 'bg-slate-50 border-slate-200 opacity-60'
              }`}
            >
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <div
                    className={`w-12 h-12 rounded-2xl flex items-center justify-center ${
                      b.unlockedAt
                        ? 'bg-gradient-to-tr from-amber-400 to-orange-500 text-white shadow-md shadow-amber-500/20'
                        : 'bg-slate-200 text-slate-400'
                    }`}
                  >
                    {b.unlockedAt ? <Trophy className="w-6 h-6" /> : <Lock className="w-5 h-5" />}
                  </div>

                  {b.unlockedAt && (
                    <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-700">
                      Débloqué
                    </span>
                  )}
                </div>

                <div>
                  <h3 className="font-bold text-sm text-slate-900">{b.label}</h3>
                  <p className="text-xs text-slate-500 mt-1">{b.description}</p>
                </div>
              </div>

              {b.unlockedAt && (
                <div className="text-[10px] font-semibold text-slate-400 border-t border-slate-100 pt-2">
                  Débloqué le {b.unlockedAt}
                </div>
              )}
            </div>
          ))}
        </div>
      </section>

      {/* Leaderboard & Daily Challenges */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Leaderboard Table */}
        <div className="bg-white rounded-3xl p-6 sm:p-8 border border-slate-200 shadow-xs space-y-4" id="classement">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-bold text-slate-900 flex items-center gap-2">
              <Users className="w-5 h-5 text-blue-600" />
              Classement Général (Terminale S1)
            </h2>
            <span className="text-xs font-bold text-blue-600 bg-blue-50 px-2.5 py-1 rounded-full">
              Semaine 30
            </span>
          </div>

          <div className="space-y-2">
            {leaderboard.map((user) => (
              <div
                key={user.rank}
                className={`p-3.5 rounded-2xl border transition-all flex items-center justify-between ${
                  user.isUser
                    ? 'bg-blue-50/80 border-blue-300 shadow-xs font-bold'
                    : 'bg-white border-slate-100 hover:bg-slate-50'
                }`}
              >
                <div className="flex items-center gap-3">
                  <span
                    className={`w-7 h-7 rounded-xl font-bold text-xs flex items-center justify-center ${
                      user.rank === 1
                        ? 'bg-amber-400 text-white shadow-xs'
                        : user.rank === 2
                        ? 'bg-slate-300 text-slate-800'
                        : user.rank === 3
                        ? 'bg-amber-700 text-white'
                        : 'bg-slate-100 text-slate-600'
                    }`}
                  >
                    #{user.rank}
                  </span>
                  <div>
                    <h4 className="text-xs font-bold text-slate-900">{user.name}</h4>
                    <p className="text-[10px] text-slate-500">{user.grade}</p>
                  </div>
                </div>

                <div className="flex items-center gap-4 text-xs">
                  <span className="flex items-center gap-1 text-slate-600 font-semibold">
                    <Flame className="w-3.5 h-3.5 text-amber-500" /> {user.streak}j
                  </span>
                  <span className="font-extrabold text-blue-600">{user.points}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Daily Challenges */}
        <div className="bg-white rounded-3xl p-6 sm:p-8 border border-slate-200 shadow-xs space-y-4">
          <h2 className="text-lg font-bold text-slate-900 flex items-center gap-2">
            <Zap className="w-5 h-5 text-amber-500" />
            Défis Quotidiens (+150 XP)
          </h2>

          <div className="space-y-3">
            {[
              { title: 'Réussir un Quiz avec au moins 80%', points: '+50 XP', done: true },
              { title: 'Poser 1 question approfondie au Tuteur NURU', points: '+30 XP', done: true },
              { title: 'Compléter 1 série d’exercices sur les limites', points: '+70 XP', done: false }
            ].map((challenge, idx) => (
              <div key={idx} className="p-4 rounded-2xl bg-slate-50 border border-slate-100 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className={`w-6 h-6 rounded-full flex items-center justify-center ${challenge.done ? 'bg-emerald-500 text-white' : 'bg-slate-200 text-slate-400'}`}>
                    <CheckCircle2 className="w-4 h-4" />
                  </div>
                  <div>
                    <h4 className="text-xs font-bold text-slate-900">{challenge.title}</h4>
                    <span className="text-[10px] font-bold text-amber-600">{challenge.points}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
