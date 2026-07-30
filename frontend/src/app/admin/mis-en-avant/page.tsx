'use client';

import React, { useState } from 'react';
import {
  Star,
  Plus,
  Search,
  Filter,
  Calendar,
  Layers,
  Trash2,
  CheckCircle2,
  Clock,
  AlertCircle,
  Inbox,
  X
} from 'lucide-react';

interface FeaturedContent {
  id: string;
  title: string;
  category: 'Accueil' | 'Matière';
  subject: string;
  level: string;
  status: 'Actives' | 'Planifiées' | 'Expirées';
  startDate: string;
  endDate: string;
}

export default function MisEnAvantPage() {
  const [featuredItems, setFeaturedItems] = useState<FeaturedContent[]>([
    {
      id: 'feat-1',
      title: 'Géométrie Vectorielle dans l’Espace (Méthode & Exercices)',
      category: 'Accueil',
      subject: 'Mathématiques',
      level: 'Terminale S1',
      status: 'Actives',
      startDate: '2026-07-20',
      endDate: '2026-08-20'
    },
    {
      id: 'feat-2',
      title: 'Révisions Intensives BFEM : Théorème de Thalès',
      category: 'Matière',
      subject: 'Mathématiques',
      level: '3ème (BFEM)',
      status: 'Actives',
      startDate: '2026-07-15',
      endDate: '2026-08-15'
    },
    {
      id: 'feat-3',
      title: 'Préparation BAC S1/S2 : Nombres Complexes & Probabilités',
      category: 'Accueil',
      subject: 'Mathématiques',
      level: 'Terminale S1',
      status: 'Planifiées',
      startDate: '2026-08-01',
      endDate: '2026-09-01'
    },
    {
      id: 'feat-4',
      title: 'Guide complet des Équations Différentielles',
      category: 'Matière',
      subject: 'Mathématiques',
      level: 'Terminale S2',
      status: 'Expirées',
      startDate: '2026-06-01',
      endDate: '2026-07-01'
    }
  ]);

  const [statusFilter, setStatusFilter] = useState<'Tous' | 'Actives' | 'Planifiées' | 'Expirées'>('Tous');
  const [categoryFilter, setCategoryFilter] = useState<'Toutes catégories' | 'Accueil' | 'Matière'>('Toutes catégories');
  const [searchQuery, setSearchQuery] = useState('');
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);

  // New item form state
  const [newTitle, setNewTitle] = useState('');
  const [newCategory, setNewCategory] = useState<'Accueil' | 'Matière'>('Accueil');
  const [newLevel, setNewLevel] = useState('Terminale S1');

  // KPIs
  const totalActive = featuredItems.filter((item) => item.status === 'Actives').length;
  const totalPlanned = featuredItems.filter((item) => item.status === 'Planifiées').length;
  const totalExpired = featuredItems.filter((item) => item.status === 'Expirées').length;

  // Filter dataset
  const filteredItems = featuredItems.filter((item) => {
    const matchesStatus = statusFilter === 'Tous' || item.status === statusFilter;
    const matchesCategory = categoryFilter === 'Toutes catégories' || item.category === categoryFilter;
    const matchesSearch = item.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                          item.level.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesStatus && matchesCategory && matchesSearch;
  });

  const handleRemove = (id: string) => {
    setFeaturedItems((prev) => prev.filter((item) => item.id !== id));
  };

  const handleAddLesson = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTitle.trim()) return;
    const newItem: FeaturedContent = {
      id: `feat-${Date.now()}`,
      title: newTitle.trim(),
      category: newCategory,
      subject: 'Mathématiques',
      level: newLevel,
      status: 'Actives',
      startDate: new Date().toISOString().split('T')[0],
      endDate: '2026-09-01'
    };
    setFeaturedItems([newItem, ...featuredItems]);
    setNewTitle('');
    setIsAddModalOpen(false);
  };

  return (
    <div className="max-w-7xl mx-auto space-y-8 animate-in fade-in duration-300">
      {/* Header */}
      <div className="rounded-3xl bg-slate-900 p-6 sm:p-8 text-white shadow-xl space-y-3 border border-slate-800 relative overflow-hidden flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div className="space-y-3 max-w-3xl">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-amber-500/20 text-amber-300 text-xs font-semibold border border-amber-400/30">
            <Star className="w-3.5 h-3.5 fill-amber-300" />
            <span>Mise en Avant & Carrousel</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight">
            Contenu Mis en Avant
          </h1>
          <p className="text-slate-300 text-xs sm:text-sm">
            Gérer les leçons mises en avant sur la page d'accueil et dans les espaces de matières pour maximiser l'engagement des élèves.
          </p>
        </div>

        {/* Main Action Button */}
        <button
          onClick={() => setIsAddModalOpen(true)}
          className="px-6 py-3.5 rounded-2xl bg-amber-500 hover:bg-amber-600 text-slate-950 font-black text-xs flex items-center justify-center gap-2 shadow-lg hover:shadow-xl transition-all shrink-0 cursor-pointer"
        >
          <Plus className="w-4 h-4 stroke-[3]" />
          <span>Ajouter une leçon</span>
        </button>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-3xl p-6 border border-slate-200 shadow-2xs space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">Actives</span>
            <span className="p-2 rounded-xl bg-emerald-50 text-emerald-600">
              <CheckCircle2 className="w-5 h-5" />
            </span>
          </div>
          <div className="text-3xl font-black text-slate-900">{totalActive}</div>
          <p className="text-[11px] text-emerald-700 font-semibold">Affichées actuellement</p>
        </div>

        <div className="bg-white rounded-3xl p-6 border border-slate-200 shadow-2xs space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">Planifiées</span>
            <span className="p-2 rounded-xl bg-blue-50 text-blue-600">
              <Clock className="w-5 h-5" />
            </span>
          </div>
          <div className="text-3xl font-black text-slate-900">{totalPlanned}</div>
          <p className="text-[11px] text-blue-700 font-semibold">Début automatique à venir</p>
        </div>

        <div className="bg-white rounded-3xl p-6 border border-slate-200 shadow-2xs space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">Expirées</span>
            <span className="p-2 rounded-xl bg-slate-100 text-slate-600">
              <AlertCircle className="w-5 h-5" />
            </span>
          </div>
          <div className="text-3xl font-black text-slate-900">{totalExpired}</div>
          <p className="text-[11px] text-slate-500 font-medium">Fin de mise en avant</p>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="bg-white rounded-3xl p-6 border border-slate-200 shadow-2xs space-y-4">
        <div className="flex flex-col md:flex-row items-stretch md:items-center justify-between gap-4">
          {/* Status filters */}
          <div className="flex items-center gap-1.5 p-1.5 bg-slate-100 rounded-2xl shrink-0 overflow-x-auto">
            {(['Tous', 'Actives', 'Planifiées', 'Expirées'] as const).map((status) => (
              <button
                key={status}
                onClick={() => setStatusFilter(status)}
                className={`px-4 py-2 rounded-xl text-xs font-extrabold transition-all whitespace-nowrap ${
                  statusFilter === status
                    ? 'bg-white text-slate-900 shadow-xs'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                {status}
              </button>
            ))}
          </div>

          {/* Category filters */}
          <div className="flex items-center gap-1.5 p-1.5 bg-slate-100 rounded-2xl shrink-0">
            {(['Toutes catégories', 'Accueil', 'Matière'] as const).map((cat) => (
              <button
                key={cat}
                onClick={() => setCategoryFilter(cat)}
                className={`px-3.5 py-1.5 rounded-xl text-xs font-extrabold transition-all ${
                  categoryFilter === cat
                    ? 'bg-amber-500 text-slate-950 shadow-xs'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                {cat}
              </button>
            ))}
          </div>

          {/* Text search */}
          <div className="relative flex-1 max-w-xs">
            <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Rechercher une leçon..."
              className="w-full bg-slate-50 border border-slate-200 rounded-2xl pl-10 pr-4 py-2 text-xs text-slate-800 focus:bg-white focus:border-amber-500 focus:ring-2 focus:ring-amber-100 outline-none transition-all"
            />
          </div>
        </div>
      </div>

      {/* Cards List / Empty State */}
      {filteredItems.length === 0 ? (
        <div className="bg-white rounded-3xl p-12 border border-slate-200 text-center space-y-4 shadow-2xs">
          <div className="w-16 h-16 rounded-full bg-slate-100 text-slate-400 flex items-center justify-center mx-auto">
            <Inbox className="w-8 h-8" />
          </div>
          <div className="space-y-1">
            <h3 className="text-base font-extrabold text-slate-900">Aucune leçon mise en avant</h3>
            <p className="text-xs text-slate-500 max-w-sm mx-auto">
              Aucun contenu ne correspond actuellement aux filtres sélectionnés. Cliquez sur "Ajouter une leçon" pour mettre en avant du contenu.
            </p>
          </div>
          <button
            onClick={() => setIsAddModalOpen(true)}
            className="px-5 py-2.5 rounded-xl bg-slate-900 hover:bg-slate-800 text-white font-extrabold text-xs inline-flex items-center gap-2 transition-colors"
          >
            <Plus className="w-4 h-4" />
            Ajouter une leçon
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {filteredItems.map((item) => (
            <div key={item.id} className="bg-white rounded-3xl p-6 border border-slate-200 shadow-2xs hover:shadow-md transition-all space-y-4">
              <div className="flex items-start justify-between gap-4">
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="text-[10px] font-extrabold px-2.5 py-0.5 rounded-full bg-amber-100 text-amber-900 uppercase">
                      Catégorie : {item.category}
                    </span>
                    <span className="text-[11px] font-extrabold px-2.5 py-0.5 rounded-md bg-emerald-50 text-emerald-800 border border-emerald-200">
                      {item.level}
                    </span>
                  </div>
                  <h3 className="text-sm font-extrabold text-slate-900 leading-snug">{item.title}</h3>
                </div>

                <button
                  onClick={() => handleRemove(item.id)}
                  className="p-2 rounded-xl text-slate-400 hover:text-rose-600 hover:bg-rose-50 transition-colors"
                  title="Retirer des contenus mis en avant"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>

              <div className="flex items-center justify-between text-xs pt-3 border-t border-slate-100">
                <div className="flex items-center gap-1.5 text-slate-500 font-medium">
                  <Calendar className="w-3.5 h-3.5" />
                  <span>Du {item.startDate} au {item.endDate}</span>
                </div>

                <span
                  className={`px-3 py-1 rounded-full text-[11px] font-extrabold border ${
                    item.status === 'Actives'
                      ? 'bg-emerald-100 text-emerald-800 border-emerald-300'
                      : item.status === 'Planifiées'
                      ? 'bg-blue-100 text-blue-800 border-blue-300'
                      : 'bg-slate-100 text-slate-600 border-slate-300'
                  }`}
                >
                  {item.status}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Add Featured Lesson Modal */}
      {isAddModalOpen && (
        <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-3xl max-w-lg w-full p-6 sm:p-8 space-y-6 shadow-2xl border border-slate-200 animate-in zoom-in-95 duration-200">
            <div className="flex items-center justify-between pb-4 border-b border-slate-100">
              <div className="flex items-center gap-3">
                <div className="p-3 rounded-2xl bg-amber-50 text-amber-600 border border-amber-200">
                  <Star className="w-5 h-5 fill-amber-500" />
                </div>
                <h3 className="text-base font-extrabold text-slate-900">Mettre une leçon en avant</h3>
              </div>
              <button
                onClick={() => setIsAddModalOpen(false)}
                className="p-2 rounded-full hover:bg-slate-100 text-slate-400 hover:text-slate-600 transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleAddLesson} className="space-y-4">
              <div>
                <label className="text-xs font-extrabold text-slate-700 block mb-1">Titre de la leçon</label>
                <input
                  type="text"
                  required
                  value={newTitle}
                  onChange={(e) => setNewTitle(e.target.value)}
                  placeholder="ex: Problème d'Analyse BAC S1 2026"
                  className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3.5 py-2.5 text-xs text-slate-800 focus:bg-white focus:border-amber-500 outline-none"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-xs font-extrabold text-slate-700 block mb-1">Catégorie</label>
                  <select
                    value={newCategory}
                    onChange={(e) => setNewCategory(e.target.value as any)}
                    className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-xs text-slate-800"
                  >
                    <option value="Accueil">Accueil</option>
                    <option value="Matière">Matière</option>
                  </select>
                </div>

                <div>
                  <label className="text-xs font-extrabold text-slate-700 block mb-1">Niveau</label>
                  <select
                    value={newLevel}
                    onChange={(e) => setNewLevel(e.target.value)}
                    className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-xs text-slate-800"
                  >
                    <option value="Terminale S1">Terminale S1</option>
                    <option value="Terminale S2">Terminale S2</option>
                    <option value="Première S1/S2">Première S1/S2</option>
                    <option value="3ème (BFEM)">3ème (BFEM)</option>
                  </select>
                </div>
              </div>

              <div className="pt-4 border-t border-slate-100 flex items-center justify-end gap-3">
                <button
                  type="button"
                  onClick={() => setIsAddModalOpen(false)}
                  className="px-4 py-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 font-extrabold text-xs transition-colors"
                >
                  Annuler
                </button>
                <button
                  type="submit"
                  className="px-5 py-2 rounded-xl bg-amber-500 hover:bg-amber-600 text-slate-950 font-black text-xs transition-colors"
                >
                  Valider
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
