'use client';

import React, { useState } from 'react';
import {
  BookOpen,
  Archive,
  Search,
  Filter,
  History,
  CheckCircle2,
  AlertCircle,
  Clock,
  ChevronRight,
  Eye,
  FileText,
  X
} from 'lucide-react';

interface LessonPublication {
  id: string;
  title: string;
  lang: string;
  duration: string;
  subject: string;
  level: string;
  date: string;
  status: 'Publiée' | 'Archivée';
  revisionsCount: number;
  author: string;
}

export default function PublicationsPage() {
  const initialLessons: LessonPublication[] = [
    {
      id: 'pub-1',
      title: 'Géométrie Vectorielle dans l’Espace',
      lang: 'FR',
      duration: '12 min',
      subject: 'Mathématiques',
      level: 'Terminale S1',
      date: '2026-07-25',
      status: 'Publiée',
      revisionsCount: 3,
      author: 'Prof. Diop'
    },
    {
      id: 'pub-2',
      title: 'Fonctions Logarithmes Néperiens & Propriétés',
      lang: 'FR',
      duration: '15 min',
      subject: 'Mathématiques',
      level: 'Terminale S2',
      date: '2026-07-24',
      status: 'Publiée',
      revisionsCount: 2,
      author: 'Prof. Ndiaye'
    },
    {
      id: 'pub-3',
      title: 'Schéma de Bernoulli & Loi Binomiale',
      lang: 'FR',
      duration: '10 min',
      subject: 'Mathématiques',
      level: 'Terminale S1',
      date: '2026-07-22',
      status: 'Publiée',
      revisionsCount: 4,
      author: 'RAG IA'
    },
    {
      id: 'pub-4',
      title: 'Théorème de Thalès et Applications Pratiques',
      lang: 'FR',
      duration: '8 min',
      subject: 'Mathématiques',
      level: '3ème (BFEM)',
      date: '2026-07-20',
      status: 'Publiée',
      revisionsCount: 1,
      author: 'Prof. Sow'
    },
    {
      id: 'pub-5',
      title: 'Équations Différentielles du Premier Ordre',
      lang: 'FR',
      duration: '14 min',
      subject: 'Mathématiques',
      level: 'Terminale S1',
      date: '2026-07-18',
      status: 'Publiée',
      revisionsCount: 5,
      author: 'RAG IA'
    },
    {
      id: 'pub-6',
      title: 'Nombres Complexes & Transformations du Plan',
      lang: 'FR',
      duration: '20 min',
      subject: 'Mathématiques',
      level: 'Terminale S1',
      date: '2026-07-15',
      status: 'Publiée',
      revisionsCount: 2,
      author: 'Prof. Diop'
    },
    {
      id: 'pub-7',
      title: 'Suites Numériques & Récurrence',
      lang: 'FR',
      duration: '10 min',
      subject: 'Mathématiques',
      level: 'Première S1/S2',
      date: '2026-07-10',
      status: 'Publiée',
      revisionsCount: 1,
      author: 'Prof. Fall'
    }
  ];

  const [lessons, setLessons] = useState<LessonPublication[]>(initialLessons);
  const [statusFilter, setStatusFilter] = useState<'Tous' | 'Publiée' | 'Archivée'>('Tous');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedHistoryLesson, setSelectedHistoryLesson] = useState<LessonPublication | null>(null);

  // Toggle archive status
  const handleToggleArchive = (id: string) => {
    setLessons((prev) =>
      prev.map((item) => {
        if (item.id === id) {
          const newStatus = item.status === 'Publiée' ? 'Archivée' : 'Publiée';
          return { ...item, status: newStatus };
        }
        return item;
      })
    );
  };

  // KPIs calculations
  const totalPublished = lessons.filter((l) => l.status === 'Publiée').length;
  const totalArchived = lessons.filter((l) => l.status === 'Archivée').length;
  const publishedThisWeek = 0;
  const needsAttention = 0;

  // Filtered dataset
  const filteredLessons = lessons.filter((lesson) => {
    const matchesStatus = statusFilter === 'Tous' || lesson.status === statusFilter;
    const matchesSearch = lesson.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                          lesson.subject.toLowerCase().includes(searchQuery.toLowerCase()) ||
                          lesson.level.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesStatus && matchesSearch;
  });

  return (
    <div className="max-w-7xl mx-auto space-y-8 animate-in fade-in duration-300">
      {/* Header */}
      <div className="rounded-3xl bg-slate-900 p-6 sm:p-8 text-white shadow-xl space-y-3 border border-slate-800 relative overflow-hidden">
        <div className="absolute right-0 top-0 translate-x-12 -translate-y-12 w-64 h-64 bg-blue-500/10 rounded-full blur-3xl pointer-events-none"></div>
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/20 text-blue-300 text-xs font-semibold border border-blue-400/30">
          <BookOpen className="w-3.5 h-3.5" />
          <span>Workflow Éditorial</span>
        </div>
        <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight">
          Gestion des Publications
        </h1>
        <p className="text-slate-300 text-xs sm:text-sm max-w-3xl">
          Gérer les leçons publiées et archivées, contrôler leur statut et suivre l'historique des modifications apportées aux contenus.
        </p>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6">
        <div className="bg-white rounded-3xl p-5 border border-slate-200 shadow-2xs space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">Leçons publiées</span>
            <div className="p-2 rounded-xl bg-emerald-50 text-emerald-600">
              <CheckCircle2 className="w-5 h-5" />
            </div>
          </div>
          <div className="text-3xl font-black text-slate-900">{totalPublished}</div>
          <p className="text-[11px] text-emerald-700 font-semibold flex items-center gap-1">
            <span>En ligne sur la plateforme</span>
          </p>
        </div>

        <div className="bg-white rounded-3xl p-5 border border-slate-200 shadow-2xs space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">Leçons archivées</span>
            <div className="p-2 rounded-xl bg-slate-100 text-slate-600">
              <Archive className="w-5 h-5" />
            </div>
          </div>
          <div className="text-3xl font-black text-slate-900">{totalArchived}</div>
          <p className="text-[11px] text-slate-500 font-medium">Masquées du catalogue</p>
        </div>

        <div className="bg-white rounded-3xl p-5 border border-slate-200 shadow-2xs space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">Publiées cette semaine</span>
            <div className="p-2 rounded-xl bg-blue-50 text-blue-600">
              <Clock className="w-5 h-5" />
            </div>
          </div>
          <div className="text-3xl font-black text-slate-900">{publishedThisWeek}</div>
          <p className="text-[11px] text-slate-500 font-medium">Sept derniers jours</p>
        </div>

        <div className="bg-white rounded-3xl p-5 border border-slate-200 shadow-2xs space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">Nécessitent attention</span>
            <div className="p-2 rounded-xl bg-amber-50 text-amber-600">
              <AlertCircle className="w-5 h-5" />
            </div>
          </div>
          <div className="text-3xl font-black text-slate-900">{needsAttention}</div>
          <p className="text-[11px] text-slate-500 font-medium">Signalements ou révisions</p>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="bg-white rounded-3xl p-6 border border-slate-200 shadow-2xs space-y-4">
        <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-4">
          {/* Filter buttons by status */}
          <div className="flex items-center gap-1.5 p-1.5 bg-slate-100 rounded-2xl shrink-0">
            {(['Tous', 'Publiée', 'Archivée'] as const).map((filter) => (
              <button
                key={filter}
                onClick={() => setStatusFilter(filter)}
                className={`px-4 py-2 rounded-xl text-xs font-extrabold transition-all ${
                  statusFilter === filter
                    ? 'bg-white text-slate-900 shadow-xs'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                {filter}
              </button>
            ))}
          </div>

          {/* Text search input */}
          <div className="relative flex-1 max-w-md">
            <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Rechercher par titre, matière ou niveau..."
              className="w-full bg-slate-50 border border-slate-200 rounded-2xl pl-10 pr-4 py-2.5 text-xs text-slate-800 focus:bg-white focus:border-blue-500 focus:ring-2 focus:ring-blue-100 outline-none transition-all"
            />
          </div>
        </div>

        {/* Data Table */}
        <div className="overflow-x-auto rounded-2xl border border-slate-200">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 border-b border-slate-200 text-slate-500 font-bold uppercase tracking-wider">
              <tr>
                <th className="p-4">Titre (Langue & Durée)</th>
                <th className="p-4">Matière</th>
                <th className="p-4">Niveau</th>
                <th className="p-4">Date</th>
                <th className="p-4">Statut</th>
                <th className="p-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 font-medium text-slate-700">
              {filteredLessons.length === 0 ? (
                <tr>
                  <td colSpan={6} className="p-8 text-center text-slate-400 font-bold">
                    Aucune leçon trouvée pour cette recherche.
                  </td>
                </tr>
              ) : (
                filteredLessons.map((lesson) => (
                  <tr key={lesson.id} className="hover:bg-slate-50/80 transition-colors">
                    <td className="p-4 font-bold text-slate-900">
                      <div className="space-y-0.5">
                        <div className="flex items-center gap-2">
                          <span className="text-slate-900">{lesson.title}</span>
                        </div>
                        <div className="flex items-center gap-2 text-[11px] font-semibold text-slate-400">
                          <span className="px-1.5 py-0.2 rounded bg-slate-100 text-slate-600 border border-slate-200">
                            {lesson.lang}
                          </span>
                          <span>• {lesson.duration}</span>
                          <span>• Auteur : {lesson.author}</span>
                        </div>
                      </div>
                    </td>
                    <td className="p-4 font-semibold text-slate-700">{lesson.subject}</td>
                    <td className="p-4">
                      <span className="px-2.5 py-1 rounded-lg bg-emerald-50 text-emerald-800 font-extrabold text-[11px] border border-emerald-200">
                        {lesson.level}
                      </span>
                    </td>
                    <td className="p-4 text-slate-500 font-medium">{lesson.date}</td>
                    <td className="p-4">
                      <span
                        className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-[11px] font-extrabold border ${
                          lesson.status === 'Publiée'
                            ? 'bg-emerald-100 text-emerald-800 border-emerald-300'
                            : 'bg-slate-100 text-slate-600 border-slate-300'
                        }`}
                      >
                        <span
                          className={`w-1.5 h-1.5 rounded-full ${
                            lesson.status === 'Publiée' ? 'bg-emerald-600' : 'bg-slate-400'
                          }`}
                        />
                        {lesson.status}
                      </span>
                    </td>
                    <td className="p-4 text-right">
                      <div className="flex items-center justify-end gap-2">
                        <button
                          onClick={() => setSelectedHistoryLesson(lesson)}
                          className="px-3 py-1.5 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold text-xs flex items-center gap-1.5 transition-colors border border-slate-200"
                          title="Consulter l'historique"
                        >
                          <History className="w-3.5 h-3.5 text-slate-500" />
                          <span>Historique</span>
                        </button>

                        <button
                          onClick={() => handleToggleArchive(lesson.id)}
                          className={`px-3 py-1.5 rounded-xl font-bold text-xs flex items-center gap-1.5 transition-colors border ${
                            lesson.status === 'Publiée'
                              ? 'bg-rose-50 hover:bg-rose-100 text-rose-700 border-rose-200'
                              : 'bg-emerald-50 hover:bg-emerald-100 text-emerald-700 border-emerald-200'
                          }`}
                        >
                          <Archive className="w-3.5 h-3.5" />
                          <span>{lesson.status === 'Publiée' ? 'Archiver' : 'Restaurer'}</span>
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* History Modal */}
      {selectedHistoryLesson && (
        <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-3xl max-w-2xl w-full p-6 sm:p-8 space-y-6 shadow-2xl border border-slate-200 animate-in zoom-in-95 duration-200">
            <div className="flex items-center justify-between pb-4 border-b border-slate-100">
              <div className="flex items-center gap-3">
                <div className="p-3 rounded-2xl bg-blue-50 text-blue-600 border border-blue-200">
                  <History className="w-6 h-6" />
                </div>
                <div>
                  <h3 className="text-base font-extrabold text-slate-900">Historique des révisions</h3>
                  <p className="text-xs text-slate-500">{selectedHistoryLesson.title}</p>
                </div>
              </div>
              <button
                onClick={() => setSelectedHistoryLesson(null)}
                className="p-2 rounded-full hover:bg-slate-100 text-slate-400 hover:text-slate-600 transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="space-y-4 max-h-96 overflow-y-auto pr-2">
              <div className="p-4 rounded-2xl bg-slate-50 border border-slate-200 space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-black text-slate-900">Version 3.0 (Actuelle)</span>
                  <span className="text-[11px] text-slate-400 font-medium">Hier, 15:30 par {selectedHistoryLesson.author}</span>
                </div>
                <p className="text-xs text-slate-600">
                  Mise à jour des figures vectorielles et ajouts d'exercices type BAC 2026.
                </p>
              </div>

              <div className="p-4 rounded-2xl bg-slate-50/60 border border-slate-100 space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-black text-slate-700">Version 2.0</span>
                  <span className="text-[11px] text-slate-400 font-medium">12/07/2026 par RAG IA</span>
                </div>
                <p className="text-xs text-slate-500">
                  Enrichissement automatique des formules Latex KaTeX et cibles cognitives.
                </p>
              </div>

              <div className="p-4 rounded-2xl bg-slate-50/40 border border-slate-100 space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-black text-slate-600">Version 1.0 (Création)</span>
                  <span className="text-[11px] text-slate-400 font-medium">{selectedHistoryLesson.date}</span>
                </div>
                <p className="text-xs text-slate-400">
                  Importation initiale du chapitre depuis le programme JS/BAC officiel.
                </p>
              </div>
            </div>

            <div className="pt-4 border-t border-slate-100 flex justify-end">
              <button
                onClick={() => setSelectedHistoryLesson(null)}
                className="px-5 py-2 rounded-xl bg-slate-900 hover:bg-slate-800 text-white font-extrabold text-xs transition-colors"
              >
                Fermer
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
