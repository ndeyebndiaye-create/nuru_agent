'use client';

import React, { useState } from 'react';
import { Brain, RotateCcw, Save, CheckCircle2, AlertTriangle, ShieldAlert, Sparkles, Info } from 'lucide-react';

export default function CiblesCognitivesPage() {
  // Default values requested by specifications:
  // Découvrir: 50%, Comprendre: 35%, Approfondir: 15%
  // Seuil minimum: 15% (range 5% to 50%)
  const [decouvrir, setDecouvrir] = useState<number>(50);
  const [comprendre, setComprendre] = useState<number>(35);
  const [approfondir, setApprofondir] = useState<number>(15);
  const [seuilMin, setSeuilMin] = useState<number>(15);

  const [savedNotification, setSavedNotification] = useState<boolean>(false);

  const totalSum = decouvrir + comprendre + approfondir;
  const isValidTotal = totalSum === 100;

  const handleReset = () => {
    setDecouvrir(50);
    setComprendre(35);
    setApprofondir(15);
    setSeuilMin(15);
    setSavedNotification(false);
  };

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    if (!isValidTotal) return;
    setSavedNotification(true);
    setTimeout(() => {
      setSavedNotification(false);
    }, 4000);
  };

  return (
    <div className="max-w-5xl mx-auto space-y-8 animate-in fade-in duration-300">
      {/* Header */}
      <div className="rounded-3xl bg-slate-900 p-6 sm:p-8 text-white shadow-xl space-y-3 border border-slate-800 relative overflow-hidden">
        <div className="absolute right-0 top-0 translate-x-12 -translate-y-12 w-64 h-64 bg-emerald-500/10 rounded-full blur-3xl pointer-events-none"></div>
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/20 text-emerald-300 text-xs font-semibold border border-emerald-400/30">
          <Brain className="w-3.5 h-3.5" />
          <span>Matrice de Distribution Taxonomique</span>
        </div>
        <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight">
          Cibles de Distribution Cognitive
        </h1>
        <p className="text-slate-300 text-xs sm:text-sm max-w-3xl">
          Configurer les pourcentages cibles pour chaque niveau cognitif. Ces réglages gouvernent la génération automatique des quiz et exercices par l'IA RAG.
        </p>
      </div>

      {/* Save Notification Toast */}
      {savedNotification && (
        <div className="p-4 rounded-2xl bg-emerald-600 text-white shadow-lg flex items-center justify-between animate-in slide-in-from-top duration-300">
          <div className="flex items-center gap-3">
            <CheckCircle2 className="w-5 h-5 shrink-0 text-emerald-200" />
            <div>
              <p className="text-xs font-extrabold">Cibles cognitives enregistrées avec succès !</p>
              <p className="text-[11px] text-emerald-100">La nouvelle configuration a été enregistrée dans la base système.</p>
            </div>
          </div>
          <button
            onClick={() => setSavedNotification(false)}
            className="text-xs font-bold px-3 py-1 rounded-lg bg-emerald-700 hover:bg-emerald-800 transition-colors"
          >
            Fermer
          </button>
        </div>
      )}

      {/* Validation Banner */}
      <div
        className={`p-5 rounded-2xl border flex items-center justify-between transition-colors ${
          isValidTotal
            ? 'bg-emerald-50 border-emerald-200 text-emerald-900'
            : 'bg-rose-50 border-rose-200 text-rose-900'
        }`}
      >
        <div className="flex items-center gap-3">
          {isValidTotal ? (
            <CheckCircle2 className="w-6 h-6 text-emerald-600 shrink-0" />
          ) : (
            <AlertTriangle className="w-6 h-6 text-rose-600 shrink-0" />
          )}
          <div>
            <h2 className="text-xs font-black uppercase tracking-wider">
              {isValidTotal ? 'Répartition valide (100%)' : 'Répartition invalide (Doit égaler 100%)'}
            </h2>
            <p className="text-xs font-medium mt-0.5">
              Somme actuelle des cibles : <strong className="text-sm font-black">{totalSum}%</strong>
              {!isValidTotal && ` (Ajustement requis : ${100 - totalSum > 0 ? `+${100 - totalSum}` : 100 - totalSum}%)`}
            </p>
          </div>
        </div>

        <span
          className={`text-xs font-extrabold px-3 py-1.5 rounded-xl border ${
            isValidTotal
              ? 'bg-emerald-100 text-emerald-800 border-emerald-300'
              : 'bg-rose-100 text-rose-800 border-rose-300'
          }`}
        >
          {totalSum} / 100%
        </span>
      </div>

      {/* Distribution Visual Breakdown */}
      <div className="bg-white rounded-3xl p-6 border border-slate-200 shadow-2xs space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-xs font-extrabold text-slate-700 uppercase tracking-wider">Aperçu visuel de la répartition</h3>
          <span className="text-xs font-bold text-slate-500">Total : {totalSum}%</span>
        </div>

        <div className="h-5 rounded-full bg-slate-100 overflow-hidden flex p-1 border border-slate-200">
          <div
            style={{ width: `${Math.min(decouvrir, 100)}%` }}
            className="bg-emerald-500 h-full rounded-l-full transition-all duration-300 relative group"
            title={`Découvrir: ${decouvrir}%`}
          />
          <div
            style={{ width: `${Math.min(comprendre, 100)}%` }}
            className="bg-blue-500 h-full transition-all duration-300 relative group"
            title={`Comprendre: ${comprendre}%`}
          />
          <div
            style={{ width: `${Math.min(approfondir, 100)}%` }}
            className="bg-purple-500 h-full rounded-r-full transition-all duration-300 relative group"
            title={`Approfondir: ${approfondir}%`}
          />
        </div>

        <div className="grid grid-cols-3 gap-4 pt-2">
          <div className="flex items-center gap-2">
            <span className="w-3 h-3 rounded-full bg-emerald-500 shrink-0"></span>
            <span className="text-xs font-bold text-slate-700">Découvrir ({decouvrir}%)</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-3 h-3 rounded-full bg-blue-500 shrink-0"></span>
            <span className="text-xs font-bold text-slate-700">Comprendre ({comprendre}%)</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-3 h-3 rounded-full bg-purple-500 shrink-0"></span>
            <span className="text-xs font-bold text-slate-700">Approfondir ({approfondir}%)</span>
          </div>
        </div>
      </div>

      {/* Sliders Form */}
      <form onSubmit={handleSave} className="bg-white rounded-3xl p-6 sm:p-8 border border-slate-200 shadow-2xs space-y-8">
        <div className="space-y-6">
          <h2 className="text-base font-extrabold text-slate-900 flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-emerald-600" />
            Réglage des pourcentages cibles
          </h2>

          {/* Slider 1: Cible Découvrir */}
          <div className="space-y-3 p-5 rounded-2xl bg-slate-50 border border-slate-200">
            <div className="flex items-center justify-between">
              <div>
                <label className="text-sm font-extrabold text-slate-900 flex items-center gap-2">
                  <span className="w-3 h-3 rounded-full bg-emerald-500"></span>
                  Cible Découvrir
                </label>
                <p className="text-xs text-slate-500 mt-0.5">Notions fondamentales, définitions et mémorisation active.</p>
              </div>
              <span className="text-lg font-black text-emerald-600 bg-emerald-50 px-3 py-1 rounded-xl border border-emerald-200">
                {decouvrir}%
              </span>
            </div>
            <input
              type="range"
              min="0"
              max="100"
              value={decouvrir}
              onChange={(e) => setDecouvrir(Number(e.target.value))}
              className="w-full h-2.5 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-emerald-600"
            />
            {decouvrir < seuilMin && (
              <p className="text-[11px] text-amber-700 font-bold flex items-center gap-1">
                <AlertTriangle className="w-3.5 h-3.5" />
                Attention : la cible est inférieure au seuil minimum ({seuilMin}%).
              </p>
            )}
          </div>

          {/* Slider 2: Cible Comprendre */}
          <div className="space-y-3 p-5 rounded-2xl bg-slate-50 border border-slate-200">
            <div className="flex items-center justify-between">
              <div>
                <label className="text-sm font-extrabold text-slate-900 flex items-center gap-2">
                  <span className="w-3 h-3 rounded-full bg-blue-500"></span>
                  Cible Comprendre
                </label>
                <p className="text-xs text-slate-500 mt-0.5">Applications directes des théorèmes et résolution guidée.</p>
              </div>
              <span className="text-lg font-black text-blue-600 bg-blue-50 px-3 py-1 rounded-xl border border-blue-200">
                {comprendre}%
              </span>
            </div>
            <input
              type="range"
              min="0"
              max="100"
              value={comprendre}
              onChange={(e) => setComprendre(Number(e.target.value))}
              className="w-full h-2.5 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-blue-600"
            />
            {comprendre < seuilMin && (
              <p className="text-[11px] text-amber-700 font-bold flex items-center gap-1">
                <AlertTriangle className="w-3.5 h-3.5" />
                Attention : la cible est inférieure au seuil minimum ({seuilMin}%).
              </p>
            )}
          </div>

          {/* Slider 3: Cible Approfondir */}
          <div className="space-y-3 p-5 rounded-2xl bg-slate-50 border border-slate-200">
            <div className="flex items-center justify-between">
              <div>
                <label className="text-sm font-extrabold text-slate-900 flex items-center gap-2">
                  <span className="w-3 h-3 rounded-full bg-purple-500"></span>
                  Cible Approfondir
                </label>
                <p className="text-xs text-slate-500 mt-0.5">Démonstrations avancées, synthèse et problèmes type BAC.</p>
              </div>
              <span className="text-lg font-black text-purple-600 bg-purple-50 px-3 py-1 rounded-xl border border-purple-200">
                {approfondir}%
              </span>
            </div>
            <input
              type="range"
              min="0"
              max="100"
              value={approfondir}
              onChange={(e) => setApprofondir(Number(e.target.value))}
              className="w-full h-2.5 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-purple-600"
            />
            {approfondir < seuilMin && (
              <p className="text-[11px] text-amber-700 font-bold flex items-center gap-1">
                <AlertTriangle className="w-3.5 h-3.5" />
                Attention : la cible est inférieure au seuil minimum ({seuilMin}%).
              </p>
            )}
          </div>

          {/* Secondary Slider: Seuil Minimum */}
          <div className="space-y-3 p-5 rounded-2xl bg-amber-50/50 border border-amber-200">
            <div className="flex items-center justify-between">
              <div>
                <label className="text-sm font-extrabold text-slate-900 flex items-center gap-2">
                  <ShieldAlert className="w-4 h-4 text-amber-600" />
                  Seuil minimum par niveau
                </label>
                <p className="text-xs text-slate-500 mt-0.5">Pourcentage minimum recommandé par niveau avant avertissement (5% à 50%).</p>
              </div>
              <span className="text-base font-black text-amber-700 bg-amber-100 px-3 py-1 rounded-xl border border-amber-300">
                {seuilMin}%
              </span>
            </div>
            <input
              type="range"
              min="5"
              max="50"
              value={seuilMin}
              onChange={(e) => setSeuilMin(Number(e.target.value))}
              className="w-full h-2.5 bg-amber-200 rounded-lg appearance-none cursor-pointer accent-amber-600"
            />
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center justify-between pt-6 border-t border-slate-200">
          <button
            type="button"
            onClick={handleReset}
            className="px-5 py-2.5 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 font-extrabold text-xs flex items-center gap-2 transition-colors border border-slate-300"
          >
            <RotateCcw className="w-4 h-4" />
            Réinitialiser
          </button>

          <button
            type="submit"
            disabled={!isValidTotal}
            className={`px-6 py-2.5 rounded-xl font-extrabold text-xs flex items-center gap-2 shadow-sm transition-all ${
              isValidTotal
                ? 'bg-emerald-600 hover:bg-emerald-700 text-white cursor-pointer hover:shadow-md'
                : 'bg-slate-300 text-slate-500 cursor-not-allowed'
            }`}
          >
            <Save className="w-4 h-4" />
            Enregistrer
          </button>
        </div>
      </form>
    </div>
  );
}
