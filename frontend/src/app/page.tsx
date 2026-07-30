'use client';

import React, { useEffect, useState } from 'react';
import { useAuth } from '@/context/AuthContext';
import { fetchStudentDashboard, fetchChapitres, generateContent } from '@/lib/api';
import { BookOpen, Trophy, TrendingUp, Sparkles, CheckCircle2, AlertCircle, Loader2 } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import 'katex/dist/katex.min.css';

export default function StudentDashboard() {
  const { user } = useAuth();
  const [dashboard, setDashboard] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  
  // Générateur dynamique
  const [chapitres, setChapitres] = useState<string[]>([]);
  const [selectedChapitre, setSelectedChapitre] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedCours, setGeneratedCours] = useState<any>(null);

  useEffect(() => {
    if (user?.id) {
      fetchStudentDashboard(user.id).then(data => {
        setDashboard(data);
        setLoading(false);
      });
    } else {
      setLoading(false);
    }

    fetchChapitres().then(data => {
      setChapitres(data.chapitres);
      if (data.chapitres.length > 0) setSelectedChapitre(data.chapitres[0]);
    });
  }, [user]);

  const handleGenerateCours = async () => {
    if (!selectedChapitre) return;
    setIsGenerating(true);
    setGeneratedCours(null);
    try {
      const res = await generateContent({
        classe: user?.classe || 'Terminale',
        serie: user?.serie || 'S1',
        chapitre: selectedChapitre,
        content_type: 'cours'
      });
      setGeneratedCours(res);
    } catch (error) {
      alert("Erreur lors de la génération. Veuillez réessayer.");
    } finally {
      setIsGenerating(false);
    }
  };

  if (loading) return <div className="p-8 flex justify-center"><Loader2 className="w-8 h-8 animate-spin text-emerald-600" /></div>;

  return (
    <div className="p-8 max-w-6xl mx-auto space-y-8 animate-in fade-in">
      <header className="flex justify-between items-end border-b border-slate-200 pb-4">
        <div>
          <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">Bonjour, {user?.name || 'Élève'} 👋</h1>
          <p className="text-slate-500 mt-1">
            Classe : {user?.classe || 'Terminale'} {user?.serie || 'S1'} | 
            Niveau global : <span className="font-bold text-emerald-600">{dashboard?.overall_mastery || 0}%</span>
          </p>
        </div>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Stats Rapides */}
        <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm flex items-center gap-4">
          <div className="p-3 bg-emerald-100 rounded-xl text-emerald-600"><CheckCircle2 className="w-6 h-6" /></div>
          <div>
            <p className="text-sm text-slate-500 font-medium">Exercices faits</p>
            <p className="text-2xl font-black text-slate-800">{dashboard?.nb_evaluations || 0}</p>
          </div>
        </div>
        <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm flex items-center gap-4">
          <div className="p-3 bg-amber-100 rounded-xl text-amber-600"><Trophy className="w-6 h-6" /></div>
          <div>
            <p className="text-sm text-slate-500 font-medium">Total XP</p>
            <p className="text-2xl font-black text-slate-800">{dashboard?.total_xp || 0}</p>
          </div>
        </div>
        <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm flex items-center gap-4">
          <div className="p-3 bg-blue-100 rounded-xl text-blue-600"><TrendingUp className="w-6 h-6" /></div>
          <div>
            <p className="text-sm text-slate-500 font-medium">Badges</p>
            <p className="text-2xl font-black text-slate-800">{dashboard?.badges?.length || 0}</p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Générateur IA (Élève) */}
        <section className="lg:col-span-2 space-y-6">
          <div className="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden">
            <div className="p-6 border-b border-slate-100">
              <h2 className="text-lg font-bold text-slate-800 flex items-center gap-2 mb-4">
                <Sparkles className="w-5 h-5 text-emerald-600" />
                Générer un cours IA
              </h2>
              <div className="flex gap-4">
                <select 
                  className="flex-1 rounded-xl border-slate-200 bg-slate-50 text-sm focus:ring-emerald-500"
                  value={selectedChapitre} onChange={(e) => setSelectedChapitre(e.target.value)}
                >
                  {chapitres.map(c => <option key={c} value={c}>{c}</option>)}
                </select>
                <button
                  onClick={handleGenerateCours}
                  disabled={isGenerating || !selectedChapitre}
                  className="px-6 py-2 bg-emerald-600 hover:bg-emerald-700 text-white font-bold rounded-xl transition-all shadow-sm flex items-center gap-2 disabled:opacity-70"
                >
                  {isGenerating ? <Loader2 className="w-4 h-4 animate-spin" /> : <BookOpen className="w-4 h-4" />}
                  Générer
                </button>
              </div>
            </div>

            {/* Affichage du cours généré */}
            {generatedCours && (
              <div className="p-6 bg-slate-50">
                <div className="flex justify-between items-center mb-4">
                  <h3 className="font-bold text-slate-800">Cours : {generatedCours.chapitre}</h3>
                  <span className="text-xs px-2 py-1 bg-emerald-100 text-emerald-800 rounded-lg font-medium">
                    {generatedCours.rag_used ? 'RAG Actif' : 'Base'}
                  </span>
                </div>
                <div className="markdown-body prose max-w-none bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
                  <ReactMarkdown remarkPlugins={[remarkMath]} rehypePlugins={[rehypeKatex]}>
                    {generatedCours.markdown}
                  </ReactMarkdown>
                </div>
                {generatedCours.sources?.length > 0 && (
                  <div className="mt-4 p-4 bg-emerald-50/50 border border-emerald-100 rounded-xl">
                    <h4 className="text-xs font-bold text-emerald-800 mb-2">Sources (Programme Officiel)</h4>
                    <ul className="text-xs text-emerald-700 list-disc pl-4">
                      {generatedCours.sources.map((s: string, i: number) => <li key={i}>{s}</li>)}
                    </ul>
                  </div>
                )}
              </div>
            )}
            
            {!generatedCours && !isGenerating && (
              <div className="p-12 text-center text-slate-400">
                <BookOpen className="w-12 h-12 mx-auto mb-4 opacity-20" />
                <p>Sélectionnez un chapitre pour générer un cours adapté à votre niveau.</p>
              </div>
            )}
          </div>
        </section>

        {/* Maîtrise & Historique */}
        <aside className="space-y-6">
          <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-6">
            <h2 className="text-lg font-bold text-slate-800 mb-4">Maîtrise par chapitre</h2>
            {dashboard?.mastery_map?.length > 0 ? (
              <div className="space-y-4">
                {dashboard.mastery_map.map((item: any, i: number) => (
                  <div key={i} className="space-y-1">
                    <div className="flex justify-between text-sm">
                      <span className="font-medium text-slate-700 truncate">{item.concept}</span>
                      <span className="font-bold text-emerald-600">{Math.round(item.mastery_score * 100)}%</span>
                    </div>
                    <div className="w-full bg-slate-100 rounded-full h-2">
                      <div className="bg-emerald-500 h-2 rounded-full" style={{ width: `${Math.round(item.mastery_score * 100)}%` }} />
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center p-4 text-slate-500 text-sm">
                Aucune donnée d'évaluation pour le moment.
              </div>
            )}
          </div>

          <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-6">
            <h2 className="text-lg font-bold text-slate-800 mb-4">Derniers exercices</h2>
            {dashboard?.history?.length > 0 ? (
              <div className="space-y-3">
                {dashboard.history.slice(0, 5).map((item: any, i: number) => (
                  <div key={i} className="flex justify-between items-center p-3 rounded-xl bg-slate-50 border border-slate-100">
                    <div className="truncate pr-4">
                      <p className="text-sm font-bold text-slate-800 truncate">{item.concept}</p>
                      <p className="text-xs text-slate-500">{new Date(item.created_at).toLocaleDateString()}</p>
                    </div>
                    <span className={`px-2 py-1 text-xs font-bold rounded-lg ${item.is_correct ? 'bg-emerald-100 text-emerald-700' : 'bg-rose-100 text-rose-700'}`}>
                      {item.score}%
                    </span>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center p-4 text-slate-500 text-sm">
                Historique vide.
              </div>
            )}
          </div>
        </aside>
      </div>
    </div>
  );
}
