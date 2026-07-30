'use client';

import React, { useState } from 'react';
import {
  ShieldCheck,
  LayoutDashboard,
  Target,
  Sliders,
  CheckCircle2,
  Settings,
  DollarSign,
  PieChart,
  MessageSquare,
  Bell,
  Plus,
  Play,
  Eye,
  AlertTriangle,
  RefreshCw,
  TrendingUp,
  BarChart2,
  Calendar,
  Filter,
  Check,
  Zap,
  Info
} from 'lucide-react';

type SubView =
  | 'Tableau de bord'
  | 'Campagnes'
  | 'Contrôle'
  | 'Revue'
  | 'Configuration'
  | 'Budget'
  | 'Couverture'
  | 'Prompts'
  | 'Notifications';

export default function CentreIAPage() {
  const [activeSubView, setActiveSubView] = useState<SubView>('Tableau de bord');

  // Budget sub-tabs
  const [budgetTab, setBudgetTab] = useState<'Dashboard' | 'Allocations' | 'Projections' | 'ROI'>('Dashboard');

  // Notifications sub-tabs & filters & error state
  const [notifTab, setNotifTab] = useState<'Historique' | 'Préférences'>('Historique');
  const [notifTypeFilter, setNotifTypeFilter] = useState('Tous');
  const [notifStatusFilter, setNotifStatusFilter] = useState('Tous');
  const [startDate, setStartDate] = useState('2026-07-01');
  const [endDate, setEndDate] = useState('2026-07-27');
  const [hasNetworkError, setHasNetworkError] = useState(false);

  // Modals state
  const [showNewCampaignModal, setShowNewCampaignModal] = useState(false);
  const [showNewAllocationModal, setShowNewAllocationModal] = useState(false);

  const subMenuItems: { id: SubView; label: string; icon: any }[] = [
    { id: 'Tableau de bord', label: 'Tableau de bord', icon: LayoutDashboard },
    { id: 'Campagnes', label: 'Campagnes', icon: Target },
    { id: 'Contrôle', label: 'Contrôle', icon: Sliders },
    { id: 'Revue', label: 'Revue', icon: CheckCircle2 },
    { id: 'Configuration', label: 'Configuration', icon: Settings },
    { id: 'Budget', label: 'Budget', icon: DollarSign },
    { id: 'Couverture', label: 'Couverture', icon: PieChart },
    { id: 'Prompts', label: 'Prompts', icon: MessageSquare },
    { id: 'Notifications', label: 'Notifications', icon: Bell }
  ];

  return (
    <div className="max-w-7xl mx-auto space-y-8 animate-in fade-in duration-300">
      {/* Header */}
      <div className="rounded-3xl bg-slate-900 p-6 sm:p-8 text-white shadow-xl space-y-3 border border-slate-800 relative overflow-hidden">
        <div className="absolute right-0 top-0 translate-x-12 -translate-y-12 w-64 h-64 bg-teal-500/10 rounded-full blur-3xl pointer-events-none"></div>
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-teal-500/20 text-teal-300 text-xs font-semibold border border-teal-400/30">
          <ShieldCheck className="w-3.5 h-3.5" />
          <span>Sous-module spécialisé</span>
        </div>
        <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight">
          Centre de Commande IA
        </h1>
        <p className="text-slate-300 text-xs sm:text-sm max-w-3xl">
          Supervision centrale du système d'intelligence artificielle : campagnes, prompts, contrôle budget, file de revue et métriques de couverture.
        </p>
      </div>

      {/* Secondary Dedicated Navigation Menu */}
      <div className="bg-white rounded-3xl p-3 border border-slate-200 shadow-2xs">
        <nav className="flex items-center gap-1.5 overflow-x-auto pb-1">
          {subMenuItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeSubView === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveSubView(item.id)}
                className={`flex items-center gap-2 px-4 py-2.5 rounded-2xl text-xs font-extrabold transition-all whitespace-nowrap ${
                  isActive
                    ? 'bg-teal-600 text-white shadow-md'
                    : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'
                }`}
              >
                <Icon className={`w-4 h-4 ${isActive ? 'text-white' : 'text-slate-400'}`} />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>
      </div>

      {/* SUB-VIEW 1: TABLEAU DE BORD */}
      {activeSubView === 'Tableau de bord' && (
        <div className="space-y-8 animate-in fade-in duration-200">
          {/* KPI Cards */}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="bg-white rounded-3xl p-6 border border-slate-200 shadow-2xs space-y-2">
              <span className="text-xs font-bold text-slate-500 uppercase">Jobs Actifs</span>
              <div className="text-3xl font-black text-slate-900">3</div>
              <p className="text-[11px] text-emerald-600 font-semibold flex items-center gap-1">
                <span className="w-2 h-2 rounded-full bg-emerald-500 animate-ping"></span>
                Génération RAG en cours
              </p>
            </div>

            <div className="bg-white rounded-3xl p-6 border border-slate-200 shadow-2xs space-y-2">
              <span className="text-xs font-bold text-slate-500 uppercase">En Revue</span>
              <div className="text-3xl font-black text-amber-600">8</div>
              <p className="text-[11px] text-slate-500 font-medium">Contenus en attente de validation</p>
            </div>

            <div className="bg-white rounded-3xl p-6 border border-slate-200 shadow-2xs space-y-2">
              <span className="text-xs font-bold text-slate-500 uppercase">Budget Consommé (%)</span>
              <div className="text-3xl font-black text-teal-600">28.5%</div>
              <p className="text-[11px] text-slate-500 font-medium">42.80 $ / 150.00 $ alloués</p>
            </div>

            <div className="bg-white rounded-3xl p-6 border border-slate-200 shadow-2xs space-y-2">
              <span className="text-xs font-bold text-slate-500 uppercase">Alertes Actives</span>
              <div className="text-3xl font-black text-slate-900">0</div>
              <p className="text-[11px] text-emerald-700 font-semibold">Système 100% opérationnel</p>
            </div>
          </div>

          {/* Quick Action Buttons */}
          <div className="bg-white rounded-3xl p-6 border border-slate-200 shadow-2xs space-y-4">
            <h3 className="text-xs font-bold text-slate-500 uppercase tracking-wider">Actions Rapides</h3>
            <div className="flex flex-wrap items-center gap-4">
              <button
                onClick={() => setShowNewCampaignModal(true)}
                className="px-5 py-3 rounded-2xl bg-teal-600 hover:bg-teal-700 text-white font-extrabold text-xs flex items-center gap-2 shadow-sm transition-colors cursor-pointer"
              >
                <Plus className="w-4 h-4" />
                <span>Nouvelle Campagne</span>
              </button>

              <button
                onClick={() => setActiveSubView('Contrôle')}
                className="px-5 py-3 rounded-2xl bg-indigo-600 hover:bg-indigo-700 text-white font-extrabold text-xs flex items-center gap-2 shadow-sm transition-colors cursor-pointer"
              >
                <Play className="w-4 h-4 fill-white" />
                <span>Lancer Génération</span>
              </button>

              <button
                onClick={() => setActiveSubView('Revue')}
                className="px-5 py-3 rounded-2xl bg-slate-900 hover:bg-slate-800 text-white font-extrabold text-xs flex items-center gap-2 shadow-sm transition-colors cursor-pointer"
              >
                <Eye className="w-4 h-4 text-teal-300" />
                <span>Voir la Revue (8)</span>
              </button>
            </div>
          </div>

          {/* Monitoring Charts (Last 7 Days) */}
          <div className="bg-white rounded-3xl p-6 sm:p-8 border border-slate-200 shadow-2xs space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-base font-extrabold text-slate-900">Graphiques de Suivi (7 derniers jours)</h3>
                <p className="text-xs text-slate-500">Volume de génération, taux de validation et coût quotidien.</p>
              </div>
              <span className="text-xs font-extrabold px-3 py-1 rounded-full bg-teal-50 text-teal-800 border border-teal-200">
                Données synchronisées
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {/* Chart 1: Volume */}
              <div className="p-5 rounded-2xl bg-slate-50 border border-slate-200 space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-slate-700">Volume de Génération</span>
                  <span className="text-xs font-extrabold text-teal-600">+18%</span>
                </div>
                <div className="h-28 flex items-end justify-between gap-2 pt-4 border-b border-slate-200 pb-2">
                  {[35, 42, 50, 28, 65, 80, 74].map((v, i) => (
                    <div key={i} className="flex-1 flex flex-col items-center gap-1">
                      <div
                        style={{ height: `${v}%` }}
                        className="w-full bg-teal-500 rounded-t-md hover:bg-teal-600 transition-all"
                        title={`Jour ${i + 1}: ${v} contenus`}
                      />
                      <span className="text-[9px] text-slate-400 font-bold">J{i + 1}</span>
                    </div>
                  ))}
                </div>
                <p className="text-[11px] text-slate-500 font-medium">Moyenne: 53 leçons / jour</p>
              </div>

              {/* Chart 2: Taux de Validation */}
              <div className="p-5 rounded-2xl bg-slate-50 border border-slate-200 space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-slate-700">Taux de Validation</span>
                  <span className="text-xs font-extrabold text-emerald-600">96.8%</span>
                </div>
                <div className="h-28 flex items-end justify-between gap-2 pt-4 border-b border-slate-200 pb-2">
                  [92, 94, 98, 95, 99, 97, 96].map((v, i) =&gt; (
                  {[92, 94, 98, 95, 99, 97, 96].map((v, i) => (
                    <div key={i} className="flex-1 flex flex-col items-center gap-1">
                      <div
                        style={{ height: `${v}%` }}
                        className="w-full bg-emerald-500 rounded-t-md hover:bg-emerald-600 transition-all"
                        title={`Jour ${i + 1}: ${v}%`}
                      />
                      <span className="text-[9px] text-slate-400 font-bold">J{i + 1}</span>
                    </div>
                  ))}
                </div>
                <p className="text-[11px] text-slate-500 font-medium">Validation automatique RAG élevée</p>
              </div>

              {/* Chart 3: Coût Quotidien */}
              <div className="p-5 rounded-2xl bg-slate-50 border border-slate-200 space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-slate-700">Coût Quotidien ($)</span>
                  <span className="text-xs font-extrabold text-indigo-600">1.82 $/j</span>
                </div>
                <div className="h-28 flex items-end justify-between gap-2 pt-4 border-b border-slate-200 pb-2">
                  {[1.2, 1.5, 2.1, 1.1, 2.4, 1.9, 1.8].map((v, i) => (
                    <div key={i} className="flex-1 flex flex-col items-center gap-1">
                      <div
                        style={{ height: `${(v / 3) * 100}%` }}
                        className="w-full bg-indigo-500 rounded-t-md hover:bg-indigo-600 transition-all"
                        title={`Jour ${i + 1}: ${v}$`}
                      />
                      <span className="text-[9px] text-slate-400 font-bold">J{i + 1}</span>
                    </div>
                  ))}
                </div>
                <p className="text-[11px] text-slate-500 font-medium">Stabilité des coûts d'API LLM</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* SUB-VIEW 6: BUDGET */}
      {activeSubView === 'Budget' && (
        <div className="space-y-6 animate-in fade-in duration-200">
          <div className="bg-white rounded-3xl p-6 border border-slate-200 shadow-2xs space-y-6">
            <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-4">
              {/* Budget sub-tabs */}
              <div className="flex items-center gap-1.5 p-1.5 bg-slate-100 rounded-2xl shrink-0">
                {(['Dashboard', 'Allocations', 'Projections', 'ROI'] as const).map((tab) => (
                  <button
                    key={tab}
                    onClick={() => setBudgetTab(tab)}
                    className={`px-4 py-2 rounded-xl text-xs font-extrabold transition-all ${
                      budgetTab === tab
                        ? 'bg-white text-teal-700 shadow-xs'
                        : 'text-slate-600 hover:text-slate-900'
                    }`}
                  >
                    {tab}
                  </button>
                ))}
              </div>

              {/* Action Button: Nouvelle allocation */}
              <button
                onClick={() => setShowNewAllocationModal(true)}
                className="px-5 py-2.5 rounded-xl bg-teal-600 hover:bg-teal-700 text-white font-extrabold text-xs flex items-center justify-center gap-2 shadow-sm transition-colors cursor-pointer"
              >
                <Plus className="w-4 h-4" />
                <span>Nouvelle allocation</span>
              </button>
            </div>

            {/* Budget content according to sub-tab */}
            {budgetTab === 'Dashboard' && (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-2">
                <div className="p-5 rounded-2xl bg-teal-50/50 border border-teal-200 space-y-2">
                  <span className="text-xs font-bold text-teal-800 uppercase">Budget Mensuel Total</span>
                  <div className="text-3xl font-black text-teal-900">150.00 $</div>
                  <p className="text-[11px] text-teal-700 font-semibold">Allocation courante (Juillet 2026)</p>
                </div>
                <div className="p-5 rounded-2xl bg-slate-50 border border-slate-200 space-y-2">
                  <span className="text-xs font-bold text-slate-500 uppercase">Consommé</span>
                  <div className="text-3xl font-black text-slate-900">42.80 $</div>
                  <p className="text-[11px] text-emerald-600 font-semibold">28.5% utilisé</p>
                </div>
                <div className="p-5 rounded-2xl bg-slate-50 border border-slate-200 space-y-2">
                  <span className="text-xs font-bold text-slate-500 uppercase">Solde Restant</span>
                  <div className="text-3xl font-black text-slate-900">107.20 $</div>
                  <p className="text-[11px] text-slate-500 font-medium">Disponible jusqu'au 31 Juillet</p>
                </div>
              </div>
            )}

            {budgetTab === 'Allocations' && (
              <div className="space-y-4 pt-2">
                <h4 className="text-xs font-extrabold text-slate-900 uppercase">Historique des allocations de crédits IA</h4>
                <div className="space-y-3">
                  <div className="p-4 rounded-2xl bg-slate-50 border border-slate-200 flex items-center justify-between">
                    <div>
                      <h5 className="text-xs font-bold text-slate-900">Allocation Mensuelle RAG</h5>
                      <p className="text-[11px] text-slate-500">Créé le 01/07/2026 par Admin</p>
                    </div>
                    <span className="text-sm font-black text-teal-700">150.00 $</span>
                  </div>
                </div>
              </div>
            )}

            {budgetTab === 'Projections' && (
              <div className="p-5 rounded-2xl bg-slate-50 border border-slate-200 space-y-2 pt-2">
                <h4 className="text-xs font-extrabold text-slate-900">Projections de Consommation</h4>
                <p className="text-xs text-slate-600">
                  Basé sur la fréquence actuelle des requêtes RAG, le coût estimé pour le mois prochain est de 65.00 $, restant bien en dessous du plafond.
                </p>
              </div>
            )}

            {budgetTab === 'ROI' && (
              <div className="p-5 rounded-2xl bg-slate-50 border border-slate-200 space-y-2 pt-2">
                <h4 className="text-xs font-extrabold text-slate-900">Calculateur du ROI Pédagogique</h4>
                <p className="text-xs text-slate-600">
                  L'autogénération IA a permis de réduire le temps de production de contenus écrits de 85%, tout en maintenant un taux d'exactitude de 98.2%.
                </p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* SUB-VIEW 9: NOTIFICATIONS */}
      {activeSubView === 'Notifications' && (
        <div className="space-y-6 animate-in fade-in duration-200">
          <div className="bg-white rounded-3xl p-6 border border-slate-200 shadow-2xs space-y-6">
            {/* Tabs */}
            <div className="flex items-center gap-1.5 p-1.5 bg-slate-100 rounded-2xl shrink-0 w-fit">
              {(['Historique', 'Préférences'] as const).map((tab) => (
                <button
                  key={tab}
                  onClick={() => setNotifTab(tab)}
                  className={`px-4 py-2 rounded-xl text-xs font-extrabold transition-all ${
                    notifTab === tab
                      ? 'bg-white text-teal-700 shadow-xs'
                      : 'text-slate-600 hover:text-slate-900'
                  }`}
                >
                  {tab}
                </button>
              ))}
            </div>

            {/* Combined Filters */}
            <div className="p-4 rounded-2xl bg-slate-50 border border-slate-200 space-y-4">
              <div className="flex flex-col md:flex-row items-stretch md:items-center gap-4">
                <div>
                  <label className="text-[11px] font-extrabold text-slate-600 block mb-1">Type d'alerte</label>
                  <select
                    value={notifTypeFilter}
                    onChange={(e) => setNotifTypeFilter(e.target.value)}
                    className="bg-white border border-slate-200 rounded-xl px-3 py-1.5 text-xs text-slate-800"
                  >
                    <option value="Tous">Tous</option>
                    <option value="Budget">Budget</option>
                    <option value="Qualité">Qualité</option>
                    <option value="Système">Système</option>
                  </select>
                </div>

                <div>
                  <label className="text-[11px] font-extrabold text-slate-600 block mb-1">Statut</label>
                  <select
                    value={notifStatusFilter}
                    onChange={(e) => setNotifStatusFilter(e.target.value)}
                    className="bg-white border border-slate-200 rounded-xl px-3 py-1.5 text-xs text-slate-800"
                  >
                    <option value="Tous">Tous</option>
                    <option value="Non lue">Non lue</option>
                    <option value="Lue">Lue</option>
                  </select>
                </div>

                <div>
                  <label className="text-[11px] font-extrabold text-slate-600 block mb-1">Période (Début - Fin)</label>
                  <div className="flex items-center gap-2">
                    <input
                      type="date"
                      value={startDate}
                      onChange={(e) => setStartDate(e.target.value)}
                      className="bg-white border border-slate-200 rounded-xl px-2.5 py-1 text-xs text-slate-800"
                    />
                    <span className="text-xs text-slate-400 font-bold">à</span>
                    <input
                      type="date"
                      value={endDate}
                      onChange={(e) => setEndDate(e.target.value)}
                      className="bg-white border border-slate-200 rounded-xl px-2.5 py-1 text-xs text-slate-800"
                    />
                  </div>
                </div>

                {/* Network error toggle demo button */}
                <div className="md:ml-auto flex items-end">
                  <button
                    onClick={() => setHasNetworkError(!hasNetworkError)}
                    className="text-[11px] font-bold text-slate-500 hover:text-slate-700 underline"
                  >
                    {hasNetworkError ? 'Simuler succès rézo' : 'Simuler erreur rézo'}
                  </button>
                </div>
              </div>
            </div>

            {/* Error Message Box if network error */}
            {hasNetworkError && (
              <div className="p-4 rounded-2xl bg-rose-50 border border-rose-200 text-rose-900 flex items-center justify-between animate-in fade-in">
                <div className="flex items-center gap-3">
                  <AlertTriangle className="w-5 h-5 text-rose-600 shrink-0" />
                  <div>
                    <h4 className="text-xs font-extrabold">Erreur de chargement des notifications</h4>
                    <p className="text-xs">Impossible de se connecter au serveur de notifications. Veuillez vérifier votre réseau.</p>
                  </div>
                </div>
                <button
                  onClick={() => setHasNetworkError(false)}
                  className="px-3 py-1.5 rounded-xl bg-rose-600 hover:bg-rose-700 text-white text-xs font-bold transition-colors flex items-center gap-1"
                >
                  <RefreshCw className="w-3.5 h-3.5" />
                  Réessayer
                </button>
              </div>
            )}

            {/* Notifications List */}
            {!hasNetworkError && (
              <div className="space-y-3">
                {[
                  { id: 1, title: 'Job RAG achevé', type: 'Système', date: '2026-07-27 18:40', status: 'Non lue' },
                  { id: 2, title: 'Seuil de budget mensuel (25%) atteint', type: 'Budget', date: '2026-07-25 10:15', status: 'Lue' },
                  { id: 3, title: 'Validation automatique de 12 exercices', type: 'Qualité', date: '2026-07-22 14:00', status: 'Lue' }
                ].map((n) => (
                  <div key={n.id} className="p-4 rounded-2xl bg-slate-50 border border-slate-100 flex items-center justify-between">
                    <div className="space-y-1">
                      <div className="flex items-center gap-2">
                        <span className="text-[10px] font-extrabold px-2 py-0.5 rounded bg-teal-100 text-teal-800 uppercase">{n.type}</span>
                        <span className="text-xs text-slate-400 font-medium">{n.date}</span>
                      </div>
                      <h4 className="text-xs font-extrabold text-slate-900">{n.title}</h4>
                    </div>
                    <span className="text-[11px] font-bold text-slate-500">{n.status}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* OTHER SUB-VIEWS: Campagnes, Contrôle, Revue, Configuration, Couverture, Prompts */}
      {activeSubView === 'Campagnes' && (
        <div className="bg-white rounded-3xl p-6 border border-slate-200 space-y-4 animate-in fade-in">
          <h3 className="text-base font-extrabold text-slate-900">Campagnes de Génération Planifiées</h3>
          <p className="text-xs text-slate-500">Planification des lots de cours pour la rentrée 2026.</p>
        </div>
      )}

      {activeSubView === 'Contrôle' && (
        <div className="bg-white rounded-3xl p-6 border border-slate-200 space-y-4 animate-in fade-in">
          <h3 className="text-base font-extrabold text-slate-900">Panneau de Contrôle Temps Réel</h3>
          <p className="text-xs text-slate-500">Monitoring de la vitesse et de la latence de l'API LLM.</p>
        </div>
      )}

      {activeSubView === 'Revue' && (
        <div className="bg-white rounded-3xl p-6 border border-slate-200 space-y-4 animate-in fade-in">
          <h3 className="text-base font-extrabold text-slate-900">File de Revue et Modération</h3>
          <p className="text-xs text-slate-500">8 leçons générées en attente de la validation finale de l'administrateur.</p>
        </div>
      )}

      {activeSubView === 'Configuration' && (
        <div className="bg-white rounded-3xl p-6 border border-slate-200 space-y-4 animate-in fade-in">
          <h3 className="text-base font-extrabold text-slate-900">Configuration des API & Clés</h3>
          <p className="text-xs text-slate-500">Gestion des endpoints LLM et paramètres de température.</p>
        </div>
      )}

      {activeSubView === 'Couverture' && (
        <div className="bg-white rounded-3xl p-6 border border-slate-200 space-y-4 animate-in fade-in">
          <h3 className="text-base font-extrabold text-slate-900">Matrice de Couverture Pédagogique</h3>
          <p className="text-xs text-slate-500">Analyse détaillée de la couverture par chapitre et niveau scolaire.</p>
        </div>
      )}

      {activeSubView === 'Prompts' && (
        <div className="bg-white rounded-3xl p-6 border border-slate-200 space-y-4 animate-in fade-in">
          <h3 className="text-base font-extrabold text-slate-900">Bibliothèque de System Prompts RAG</h3>
          <p className="text-xs text-slate-500">Gestion des instructions système pour la génération de cours et quiz.</p>
        </div>
      )}

      {/* Modal: Nouvelle Campagne */}
      {showNewCampaignModal && (
        <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-3xl max-w-md w-full p-6 space-y-4 border border-slate-200 animate-in zoom-in-95">
            <h3 className="text-base font-extrabold text-slate-900">Nouvelle Campagne IA</h3>
            <input type="text" placeholder="Nom de la campagne" className="w-full bg-slate-50 border rounded-xl px-3 py-2 text-xs" />
            <div className="flex justify-end gap-2 pt-2">
              <button onClick={() => setShowNewCampaignModal(false)} className="px-4 py-2 rounded-xl bg-slate-100 text-xs font-bold">Annuler</button>
              <button onClick={() => setShowNewCampaignModal(false)} className="px-4 py-2 rounded-xl bg-teal-600 text-white text-xs font-extrabold">Créer</button>
            </div>
          </div>
        </div>
      )}

      {/* Modal: Nouvelle Allocation */}
      {showNewAllocationModal && (
        <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-3xl max-w-md w-full p-6 space-y-4 border border-slate-200 animate-in zoom-in-95">
            <h3 className="text-base font-extrabold text-slate-900">Nouvelle Allocation Budget</h3>
            <input type="number" placeholder="Montant en USD ($)" className="w-full bg-slate-50 border rounded-xl px-3 py-2 text-xs" />
            <div className="flex justify-end gap-2 pt-2">
              <button onClick={() => setShowNewAllocationModal(false)} className="px-4 py-2 rounded-xl bg-slate-100 text-xs font-bold">Annuler</button>
              <button onClick={() => setShowNewAllocationModal(false)} className="px-4 py-2 rounded-xl bg-teal-600 text-white text-xs font-extrabold">Valider Allocation</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
