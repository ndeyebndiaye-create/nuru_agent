'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { useAuth } from '@/context/AuthContext';
import { fetchChapitres } from '@/lib/api';
import { SubjectPlaceholderModal } from '@/components/ui/SubjectPlaceholderModal';
import {
  Calculator,
  BookOpen,
  Atom,
  Dna,
  Globe,
  Feather,
  Code,
  Lock,
  Sparkles,
  ArrowRight,
  Search,
  Loader2
} from 'lucide-react';
import { GradeLevel, Subject } from '@/types';

const GRADE_LEVELS: GradeLevel[] = [
  'Terminale S1',
  'Terminale S2',
  'Première S1/S2',
  'Seconde S',
  '3ème (BFEM)'
];

export default function MatieresPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedGrade, setSelectedGrade] = useState<GradeLevel>('Terminale S1');
  const [selectedTab, setSelectedTab] = useState<'maths' | 'autres'>('maths');
  const [selectedPlaceholder, setSelectedPlaceholder] = useState<Subject | null>(null);
  
  const [chapitres, setChapitres] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchChapitres().then(data => {
      setChapitres(data.chapitres || []);
      setLoading(false);
    });
  }, []);

  const getSubjectIcon = (iconName: string) => {
    switch (iconName) {
      case 'Calculator': return Calculator;
      case 'BookOpen': return BookOpen;
      case 'Atom': return Atom;
      case 'Dna': return Dna;
      default: return BookOpen;
    }
  };

  const filteredChapters = chapitres.filter((chap) => {
    return chap.toLowerCase().includes(searchQuery.toLowerCase());
  });

  const inactiveSubjects = [
    { id: 'pc', name: 'Physique-Chimie', iconName: 'Atom', isFunctional: false, description: 'Programme complet de Physique-Chimie.' },
    { id: 'svt', name: 'SVT', iconName: 'Dna', isFunctional: false, description: 'Sciences de la Vie et de la Terre.' }
  ];

  return (
    <div className="max-w-7xl mx-auto space-y-8 animate-in fade-in duration-300 p-8">
      {/* 1. En-tête & Barre de Recherche Épurée en Haut */}
      <div className="bg-white rounded-3xl p-6 sm:p-8 border border-slate-200 shadow-2xs space-y-6">
        <div className="space-y-2">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-50 text-emerald-800 text-xs font-bold border border-emerald-200">
            <Sparkles className="w-3.5 h-3.5 text-emerald-600" />
            <span>Programme Officiel du Sénégal (RAG)</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
            Bibliothèque des Cours & Chapitres
          </h1>
          <p className="text-slate-500 text-xs sm:text-sm">
            Ces chapitres sont indexés depuis le programme officiel dans notre base Qdrant.
          </p>
        </div>

        {/* Barre de Recherche minimaliste */}
        <div className="relative">
          <Search className="w-5 h-5 text-slate-400 absolute left-4 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Rechercher un chapitre (ex: Logarithme, Limites...)"
            className="w-full pl-12 pr-4 py-3.5 rounded-2xl bg-slate-50 border border-slate-200 text-xs sm:text-sm text-slate-900 focus:bg-white focus:border-emerald-500 focus:ring-2 focus:ring-emerald-100 outline-none transition-all"
          />
        </div>

        {/* Sélecteur de Niveau Scolaire */}
        <div className="space-y-2 pt-2 border-t border-slate-100">
          <span className="text-[11px] font-extrabold uppercase text-slate-400">Niveau Scolaire :</span>
          <div className="flex items-center gap-2 overflow-x-auto pb-1">
            {GRADE_LEVELS.map((grade) => (
              <button
                key={grade}
                onClick={() => setSelectedGrade(grade)}
                className={`px-4 py-2 rounded-xl text-xs font-bold transition-all shrink-0 ${
                  selectedGrade === grade
                    ? 'bg-emerald-600 text-white shadow-xs'
                    : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                }`}
              >
                {grade}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* 2. Onglets Matières */}
      <div className="flex items-center justify-between border-b border-slate-200 pb-3">
        <div className="flex items-center gap-3">
          <button
            onClick={() => setSelectedTab('maths')}
            className={`text-sm font-extrabold px-4 py-2 rounded-2xl transition-all ${
              selectedTab === 'maths'
                ? 'bg-emerald-600 text-white shadow-2xs'
                : 'text-slate-600 hover:bg-slate-100'
            }`}
          >
            🟢 Mathématiques (Actif)
          </button>

          <button
            onClick={() => setSelectedTab('autres')}
            className={`text-sm font-extrabold px-4 py-2 rounded-2xl transition-all ${
              selectedTab === 'autres'
                ? 'bg-slate-900 text-white shadow-2xs'
                : 'text-slate-500 hover:bg-slate-100'
            }`}
          >
            🔒 Autres Matières (Bientôt)
          </button>
        </div>

        <span className="text-xs font-semibold text-slate-400 hidden sm:inline">
          {selectedTab === 'maths' ? `${filteredChapters.length} chapitres indexés` : '2 matières désactivées'}
        </span>
      </div>

      {/* 3. Section MATHÉMATIQUES (Chapitres réels depuis le RAG) */}
      {selectedTab === 'maths' && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {loading ? (
            <div className="col-span-full flex justify-center py-12">
              <Loader2 className="w-8 h-8 animate-spin text-emerald-600" />
            </div>
          ) : filteredChapters.length === 0 ? (
            <div className="col-span-full text-center py-12 text-slate-500">
              Aucun chapitre trouvé dans la base de données.
            </div>
          ) : (
            filteredChapters.map((chap, index) => (
              <div
                key={index}
                className="bg-white rounded-3xl p-6 border border-slate-200 shadow-2xs hover:border-emerald-300 transition-all flex flex-col justify-between space-y-6"
              >
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div className="w-12 h-12 rounded-2xl bg-emerald-50 text-emerald-700 flex items-center justify-center border border-emerald-100">
                      <Calculator className="w-6 h-6" />
                    </div>
                    <span className="text-[10px] font-extrabold uppercase px-2.5 py-1 rounded bg-emerald-100 text-emerald-800">
                      Mathématiques
                    </span>
                  </div>

                  <div className="space-y-1">
                    <h3 className="text-base font-extrabold text-slate-900">{chap}</h3>
                    <p className="text-xs text-slate-500 line-clamp-2 leading-relaxed">
                      Générez un cours complet, des exercices ou des quiz sur ce chapitre via l'IA NURU.
                    </p>
                  </div>
                </div>

                {/* Bouton Continuer (redirection vers le Dashboard avec ce chapitre en pré-sélectionné) */}
                <Link
                  href={`/?chapitre=${encodeURIComponent(chap)}`}
                  className="w-full py-3 rounded-2xl bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold text-center flex items-center justify-center gap-2 shadow-2xs transition-colors"
                >
                  <span>Générer un cours</span>
                  <ArrowRight className="w-4 h-4" />
                </Link>
              </div>
            ))
          )}
        </div>
      )}

      {/* 4. Section AUTRES MATIÈRES (Désactivées) */}
      {selectedTab === 'autres' && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {inactiveSubjects.map((sub: any) => {
            const Icon = getSubjectIcon(sub.iconName);
            return (
              <div
                key={sub.id}
                onClick={() => setSelectedPlaceholder(sub)}
                className="bg-slate-50 rounded-3xl p-6 border border-slate-200 hover:border-slate-300 transition-all space-y-6 opacity-75 hover:opacity-100 cursor-pointer flex flex-col justify-between"
              >
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div className="w-12 h-12 rounded-2xl bg-slate-200 text-slate-500 flex items-center justify-center">
                      <Icon className="w-6 h-6" />
                    </div>
                    <span className="text-[10px] font-extrabold px-2.5 py-1 rounded bg-amber-100 text-amber-800 border border-amber-200 flex items-center gap-1">
                      <Lock className="w-3 h-3 text-amber-600" />
                      Bientôt disponible
                    </span>
                  </div>

                  <div className="space-y-1">
                    <h3 className="text-base font-extrabold text-slate-800">{sub.name}</h3>
                    <p className="text-xs text-slate-500 leading-relaxed">{sub.description}</p>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Modal pour matière désactivée */}
      <SubjectPlaceholderModal
        subject={selectedPlaceholder as any}
        onClose={() => setSelectedPlaceholder(null)}
      />
    </div>
  );
}
