'use client';

import React, { useState } from 'react';
import {
  Sparkles,
  Play,
  Layers,
  Activity,
  Zap,
  Coins,
  ShieldCheck,
  FileCheck,
  Clock,
  Plus,
  Inbox,
  X,
  TrendingUp,
  BarChart2
} from 'lucide-react';

interface GenerationJob {
  id: string;
  program: string;
  status: 'En cours' | 'Terminé' | 'Échoué' | 'En attente';
  progress: number;
  chaptersCount: number;
  duration: string;
  createdAt: string;
}

export default function GenerationIAPage() {
  const [activeTab, setActiveTab] = useState<'Tokens' | 'Coûts' | 'Qualité' | 'Couverture' | 'Rapports'>('Tokens');
  const [jobs, setJobs] = useState<GenerationJob[]>([]);
  const [isLaunchModalOpen, setIsLaunchModalOpen] = useState(false);

  // New Job state
  const [selectedProgram, setSelectedProgram] = useState('Terminale S1 - Mathématiques');
  const [targetChapters, setTargetChapters] = useState('5');

  const handleLaunchGeneration = (e: React.FormEvent) => {
    e.preventDefault();
    const newJob: GenerationJob = {
      id: `job-${Date.now()}`,
      program: selectedProgram,
      status: 'En cours',
      progress: 15,
      chaptersCount: Number(targetChapters),
      duration: '0m 45s',
      createdAt: 'À l’instant'
    };
    setJobs([newJob, ...jobs]);
    setIsLaunchModalOpen(false);
  };

  return (
    <div className="max-w-7xl mx-auto space-y-8 animate-in fade-in duration-300">
      {/* Header */}
      <div className="rounded-3xl bg-slate-900 p-6 sm:p-8 text-white shadow-xl space-y-3 border border-slate-800 relative overflow-hidden flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div className="space-y-3 max-w-3xl">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/20 text-indigo-300 text-xs font-semibold border border-indigo-400/30">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Pipeline RAG & Autogénération</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight">
            Génération IA
          </h1>
          <p className="text-slate-300 text-xs sm:text-sm">
            Lancer et suivre les jobs de génération de contenu, surveiller la consommation de tokens et la qualité des contenus générés.
          </p>
        </div>

        {/* Main Action Button */}
        <button
          onClick={() => setIsLaunchModalOpen(true)}
          className="px-6 py-3.5 rounded-2xl bg-indigo-600 hover:bg-indigo-700 text-white font-black text-xs flex items-center justify-center gap-2 shadow-lg hover:shadow-xl transition-all shrink-0 cursor-pointer"
        >
          <Play className="w-4 h-4 fill-white" />
          <span>Lancer une génération</span>
        </button>
      </div>

      {/* Analysis Tabs */}
      <div className="bg-white rounded-3xl p-6 border border-slate-200 shadow-2xs space-y-6">
        <div className="flex items-center gap-2 p-1.5 bg-slate-100 rounded-2xl overflow-x-auto">
          {(['Tokens', 'Coûts', 'Qualité', 'Couverture', 'Rapports'] as const).map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-5 py-2.5 rounded-xl text-xs font-extrabold transition-all whitespace-nowrap ${
                activeTab === tab
                  ? 'bg-white text-indigo-700 shadow-xs'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              {tab}
            </button>
          ))}
        </div>

        {/* Tab Detail Contents */}
        {activeTab === 'Tokens' && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 animate-in fade-in duration-200">
            <div className="p-5 rounded-2xl bg-slate-50 border border-slate-200 space-y-2">
              <span className="text-xs font-bold text-slate-500 uppercase">Tokens Consommés (Aujourd'hui)</span>
              <div className="text-2xl font-black text-slate-900">248,500 Tokens</div>
              <p className="text-[11px] text-emerald-600 font-semibold">Prompt: 180k | Completion: 68.5k</p>
            </div>
            <div className="p-5 rounded-2xl bg-slate-50 border border-slate-200 space-y-2">
              <span className="text-xs font-bold text-slate-500 uppercase">Tokens Mignons / Job</span>
              <div className="text-2xl font-black text-slate-900">14,200 Tokens</div>
              <p className="text-[11px] text-slate-500 font-medium">Moyenne par leçon générée</p>
            </div>
            <div className="p-5 rounded-2xl bg-slate-50 border border-slate-200 space-y-2">
              <span className="text-xs font-bold text-slate-500 uppercase">Efficacité du Context RAG</span>
              <div className="text-2xl font-black text-emerald-600">96.4%</div>
              <p className="text-[11px] text-slate-500 font-medium">Recherche vectorielle Qdrant</p>
            </div>
          </div>
        )}

        {activeTab === 'Coûts' && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 animate-in fade-in duration-200">
            <div className="p-5 rounded-2xl bg-slate-50 border border-slate-200 space-y-2">
              <span className="text-xs font-bold text-slate-500 uppercase">Coût Total (Mois en cours)</span>
              <div className="text-2xl font-black text-slate-900">42.80 $</div>
              <p className="text-[11px] text-emerald-600 font-semibold">Budget max alloué: 150.00 $</p>
            </div>
            <div className="p-5 rounded-2xl bg-slate-50 border border-slate-200 space-y-2">
              <span className="text-xs font-bold text-slate-500 uppercase">Coût Moyen / Cours</span>
              <div className="text-2xl font-black text-slate-900">0.12 $</div>
              <p className="text-[11px] text-slate-500 font-medium">Génération + validation RAG</p>
            </div>
            <div className="p-5 rounded-2xl bg-slate-50 border border-slate-200 space-y-2">
              <span className="text-xs font-bold text-slate-500 uppercase">Projection Fin de Mois</span>
              <div className="text-2xl font-black text-indigo-600">65.00 $</div>
              <p className="text-[11px] text-slate-500 font-medium">Respect des limites budgétaires</p>
            </div>
          </div>
        )}

        {activeTab === 'Qualité' && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 animate-in fade-in duration-200">
            <div className="p-5 rounded-2xl bg-slate-50 border border-slate-200 space-y-2">
              <span className="text-xs font-bold text-slate-500 uppercase">Score de Conformité JS/BAC</span>
              <div className="text-2xl font-black text-emerald-600">98.2%</div>
              <p className="text-[11px] text-slate-500 font-medium">Contrôle syntaxique & KaTeX</p>
            </div>
            <div className="p-5 rounded-2xl bg-slate-50 border border-slate-200 space-y-2">
              <span className="text-xs font-bold text-slate-500 uppercase">Taux d'Approbation Enseignant</span>
              <div className="text-2xl font-black text-slate-900">94.5%</div>
              <p className="text-[11px] text-slate-500 font-medium">Validation sans modification majeure</p>
            </div>
            <div className="p-5 rounded-2xl bg-slate-50 border border-slate-200 space-y-2">
              <span className="text-xs font-bold text-slate-500 uppercase">Signalisations Hallucination</span>
              <div className="text-2xl font-black text-slate-900">0.2%</div>
              <p className="text-[11px] text-emerald-600 font-semibold">Taux extrêmement bas</p>
            </div>
          </div>
        )}

        {activeTab === 'Couverture' && (
          <div className="p-5 rounded-2xl bg-slate-50 border border-slate-200 space-y-4 animate-in fade-in duration-200">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-slate-700 uppercase">Couverture des Programmes Sénégal</span>
              <span className="text-xs font-extrabold text-indigo-600">84% Réalisé</span>
            </div>
            <div className="w-full bg-slate-200 rounded-full h-3 overflow-hidden">
              <div className="bg-indigo-600 h-full rounded-full" style={{ width: '84%' }}></div>
            </div>
            <p className="text-xs text-slate-500">
              Couverture actuelle : 100% Terminale S1, 90% Terminale S2, 75% 3ème (BFEM).
            </p>
          </div>
        )}

        {activeTab === 'Rapports' && (
          <div className="p-5 rounded-2xl bg-slate-50 border border-slate-200 space-y-2 animate-in fade-in duration-200">
            <h4 className="text-xs font-extrabold text-slate-900">Rapports Hebdomadaires d'Autogénération</h4>
            <p className="text-xs text-slate-500">
              Tous les rapports d'audit de génération sont générés et archivés chaque dimanche à minuit.
            </p>
          </div>
        )}
      </div>

      {/* Jobs Table Section */}
      <div className="bg-white rounded-3xl p-6 sm:p-8 border border-slate-200 shadow-2xs space-y-6">
        <div className="flex items-center justify-between">
          <h2 className="text-base font-extrabold text-slate-900 flex items-center gap-2">
            <Activity className="w-5 h-5 text-indigo-600" />
            Tableau des travaux (Jobs)
          </h2>
          <span className="text-xs text-slate-500 font-bold">
            {jobs.length} Job{jobs.length > 1 ? 's' : ''} en cours / récent{jobs.length > 1 ? 's' : ''}
          </span>
        </div>

        {jobs.length === 0 ? (
          /* Default state specified in specs: "Aucun job trouvé" */
          <div className="py-12 text-center space-y-4 border border-dashed border-slate-200 rounded-2xl bg-slate-50/50">
            <div className="w-16 h-16 rounded-full bg-slate-100 text-slate-400 flex items-center justify-center mx-auto">
              <Inbox className="w-8 h-8" />
            </div>
            <div className="space-y-1">
              <h3 className="text-base font-extrabold text-slate-900">Aucun job trouvé</h3>
              <p className="text-xs text-slate-500 max-w-sm mx-auto">
                Aucun travail de génération n'est en cours pour le moment. Cliquez sur "Lancer une génération" pour démarrer un job.
              </p>
            </div>
            <button
              onClick={() => setIsLaunchModalOpen(true)}
              className="px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-extrabold text-xs inline-flex items-center gap-2 transition-colors cursor-pointer"
            >
              <Play className="w-4 h-4 fill-white" />
              Lancer une génération
            </button>
          </div>
        ) : (
          <div className="overflow-x-auto rounded-2xl border border-slate-200">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 border-b border-slate-200 text-slate-500 font-bold uppercase tracking-wider">
                <tr>
                  <th className="p-4">Programme</th>
                  <th className="p-4">Statut</th>
                  <th className="p-4">Progression</th>
                  <th className="p-4">Chapitres</th>
                  <th className="p-4">Durée</th>
                  <th className="p-4 text-right">Créé</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 font-medium text-slate-700">
                {jobs.map((job) => (
                  <tr key={job.id} className="hover:bg-slate-50 transition-colors">
                    <td className="p-4 font-bold text-slate-900">{job.program}</td>
                    <td className="p-4">
                      <span className="px-3 py-1 rounded-full text-[11px] font-extrabold bg-blue-100 text-blue-800 border border-blue-200 inline-flex items-center gap-1.5">
                        <span className="w-1.5 h-1.5 rounded-full bg-blue-600 animate-ping"></span>
                        {job.status}
                      </span>
                    </td>
                    <td className="p-4">
                      <div className="flex items-center gap-3">
                        <div className="w-24 bg-slate-100 rounded-full h-2 overflow-hidden">
                          <div className="bg-indigo-600 h-full" style={{ width: `${job.progress}%` }}></div>
                        </div>
                        <span className="font-extrabold text-slate-900 text-[11px]">{job.progress}%</span>
                      </div>
                    </td>
                    <td className="p-4 font-bold text-slate-700">{job.chaptersCount} chapitres</td>
                    <td className="p-4 text-slate-500 font-semibold">{job.duration}</td>
                    <td className="p-4 text-right text-slate-400 font-medium">{job.createdAt}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Launch Generation Modal */}
      {isLaunchModalOpen && (
        <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-3xl max-w-lg w-full p-6 sm:p-8 space-y-6 shadow-2xl border border-slate-200 animate-in zoom-in-95 duration-200">
            <div className="flex items-center justify-between pb-4 border-b border-slate-100">
              <div className="flex items-center gap-3">
                <div className="p-3 rounded-2xl bg-indigo-50 text-indigo-600 border border-indigo-200">
                  <Play className="w-5 h-5 fill-indigo-600" />
                </div>
                <h3 className="text-base font-extrabold text-slate-900">Lancer un Job de Génération IA</h3>
              </div>
              <button
                onClick={() => setIsLaunchModalOpen(false)}
                className="p-2 rounded-full hover:bg-slate-100 text-slate-400 hover:text-slate-600 transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleLaunchGeneration} className="space-y-4">
              <div>
                <label className="text-xs font-extrabold text-slate-700 block mb-1">Programme Cible</label>
                <select
                  value={selectedProgram}
                  onChange={(e) => setSelectedProgram(e.target.value)}
                  className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3.5 py-2.5 text-xs text-slate-800 focus:bg-white"
                >
                  <option value="Terminale S1 - Mathématiques">Terminale S1 - Mathématiques</option>
                  <option value="Terminale S2 - Mathématiques">Terminale S2 - Mathématiques</option>
                  <option value="Première S1/S2 - Mathématiques">Première S1/S2 - Mathématiques</option>
                  <option value="3ème (BFEM) - Mathématiques">3ème (BFEM) - Mathématiques</option>
                </select>
              </div>

              <div>
                <label className="text-xs font-extrabold text-slate-700 block mb-1">Nombre de chapitres à générer</label>
                <input
                  type="number"
                  min="1"
                  max="20"
                  value={targetChapters}
                  onChange={(e) => setTargetChapters(e.target.value)}
                  className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3.5 py-2.5 text-xs text-slate-800 focus:bg-white"
                />
              </div>

              <div className="pt-4 border-t border-slate-100 flex items-center justify-end gap-3">
                <button
                  type="button"
                  onClick={() => setIsLaunchModalOpen(false)}
                  className="px-4 py-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 font-extrabold text-xs transition-colors"
                >
                  Annuler
                </button>
                <button
                  type="submit"
                  className="px-5 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-black text-xs transition-colors flex items-center gap-2"
                >
                  <Play className="w-3.5 h-3.5 fill-white" />
                  Démarrer le job
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
