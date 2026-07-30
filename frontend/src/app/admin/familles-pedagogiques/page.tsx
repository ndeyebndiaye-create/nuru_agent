'use client';

import React, { useState } from 'react';
import { Layers, Brain, Code, CheckCircle2, Save, Sparkles, BookOpen } from 'lucide-react';

export default function FamillesPedagogiquesPage() {
  const [families, setFamilies] = useState([
    {
      id: 'alg-ana',
      name: 'Algèbre & Analyse',
      dcaRatio: '50% Découvrir / 35% Comprendre / 15% Approfondir',
      blocks: 'Définitions, Théorèmes, Propriétés, Exemples guidés, KaTeX Math Formulas',
      katexSupport: 'Complet (Limites, Intégrales, Logarithmes)',
      status: 'Actif'
    },
    {
      id: 'geom',
      name: 'Géométrie Vectorielle & Spatiale',
      dcaRatio: '40% Découvrir / 40% Comprendre / 20% Approfondir',
      blocks: 'Figures 2D/3D, Repères Orthonormés, Produit Scalaire, Exemples',
      katexSupport: 'Complet (Vecteurs, Matrices, Systèmes)',
      status: 'Actif'
    },
    {
      id: 'stat-prob',
      name: 'Statistiques & Probabilités',
      dcaRatio: '45% Découvrir / 40% Comprendre / 15% Approfondir',
      blocks: 'Tableaux de données, Loi Binomiale, Schéma de Bernoulli, Graphiques',
      katexSupport: 'Complet (Combinaisons, Intégration Continue)',
      status: 'Actif'
    }
  ]);

  return (
    <div className="max-w-7xl mx-auto space-y-8 animate-in fade-in duration-300">
      {/* Header */}
      <div className="rounded-3xl bg-slate-900 p-6 sm:p-8 text-white shadow-xl space-y-3 border border-slate-800 relative overflow-hidden">
        <div className="absolute right-0 top-0 translate-x-12 -translate-y-12 w-64 h-64 bg-purple-500/10 rounded-full blur-3xl pointer-events-none"></div>
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-purple-500/20 text-purple-300 text-xs font-semibold border border-purple-400/30">
          <Layers className="w-3.5 h-3.5" />
          <span>Ingénierie Pédagogique</span>
        </div>
        <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight">
          Familles Pédagogiques
        </h1>
        <p className="text-slate-300 text-xs sm:text-sm max-w-3xl">
          Ratios DCA (Découvrir, Comprendre, Approfondir), types de blocs et rendu KaTeX par famille de matière.
        </p>
      </div>

      {/* Cards List */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {families.map((f) => (
          <div key={f.id} className="bg-white rounded-3xl p-6 border border-slate-200 shadow-2xs space-y-4 hover:shadow-md transition-shadow">
            <div className="flex items-center justify-between">
              <span className="text-xs font-extrabold px-3 py-1 rounded-full bg-purple-50 text-purple-800 border border-purple-200">
                {f.name}
              </span>
              <span className="text-[10px] font-extrabold text-emerald-600 uppercase">{f.status}</span>
            </div>

            <div className="space-y-3 pt-2">
              <div>
                <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block">Ratios DCA</span>
                <p className="text-xs font-bold text-slate-800">{f.dcaRatio}</p>
              </div>

              <div>
                <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block">Types de Blocs</span>
                <p className="text-xs text-slate-600">{f.blocks}</p>
              </div>

              <div>
                <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block">Support KaTeX</span>
                <p className="text-xs text-slate-600">{f.katexSupport}</p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
