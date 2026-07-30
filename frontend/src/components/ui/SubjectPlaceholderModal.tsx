'use client';

import React from 'react';
import { Subject } from '@/types';
import { Lock, Sparkles, X, BookOpen, Calculator } from 'lucide-react';

interface SubjectPlaceholderModalProps {
  subject: Subject | null;
  onClose: () => void;
}

export const SubjectPlaceholderModal: React.FC<SubjectPlaceholderModalProps> = ({ subject, onClose }) => {
  if (!subject) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 backdrop-blur-sm p-4 animate-in fade-in duration-200">
      <div className="bg-white rounded-2xl max-w-lg w-full shadow-2xl border border-slate-100 overflow-hidden relative">
        {/* Header gradient banner */}
        <div className="bg-gradient-to-r from-slate-900 via-slate-800 to-indigo-950 text-white p-6 relative">
          <button
            onClick={onClose}
            className="absolute top-4 right-4 text-slate-400 hover:text-white bg-slate-800/60 rounded-full p-1.5 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
          
          <div className="flex items-center gap-3 mb-2">
            <div className="w-10 h-10 rounded-xl bg-amber-500/20 text-amber-400 flex items-center justify-center border border-amber-500/30">
              <Lock className="w-5 h-5" />
            </div>
            <div>
              <span className="text-xs uppercase tracking-wider text-amber-400 font-semibold">
                Placeholder Kartable
              </span>
              <h3 className="text-xl font-bold text-white">{subject.name}</h3>
            </div>
          </div>
          <p className="text-slate-300 text-sm">{subject.description}</p>
        </div>

        {/* Content */}
        <div className="p-6 space-y-4">
          <div className="p-4 bg-amber-50 rounded-xl border border-amber-200 flex items-start gap-3">
            <Sparkles className="w-5 h-5 text-amber-600 shrink-0 mt-0.5" />
            <div className="text-sm text-amber-900 leading-relaxed">
              <strong className="font-semibold block mb-1">NURU est 100% spécialisé en Mathématiques</strong>
              Afin d’offrir une expérience identique à Kartable, cette matière est affichée dans le catalogue mais reste désactivée. Tous les modules de génération RAG, cours, exercices et quiz sont actuellement concentrés sur le programme de <strong>Mathématiques</strong>.
            </div>
          </div>

          <div className="space-y-2 text-sm text-slate-600">
            <p className="font-medium text-slate-800">Ce que vous pouvez explorer actuellement :</p>
            <ul className="space-y-1.5 list-disc list-inside pl-2">
              <li>Cours complets de Mathématiques (Terminale S1)</li>
              <li>Exercices guidés par l’IA NURU</li>
              <li>Quiz d’évaluation auto-corrigés avec KaTeX</li>
              <li>Génération de cours pour enseignants (RAG)</li>
            </ul>
          </div>

          {/* Action buttons */}
          <div className="pt-2 flex items-center justify-end gap-3">
            <button
              onClick={onClose}
              className="px-4 py-2 text-sm font-medium text-slate-600 hover:text-slate-900 transition-colors"
            >
              Fermer
            </button>
            <a
              href="/matieres/mathematiques"
              onClick={onClose}
              className="px-5 py-2.5 rounded-xl text-sm font-semibold bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-lg shadow-blue-500/25 hover:opacity-95 transition-all flex items-center gap-2"
            >
              <Calculator className="w-4 h-4" />
              Aller aux Mathématiques
            </a>
          </div>
        </div>
      </div>
    </div>
  );
};
