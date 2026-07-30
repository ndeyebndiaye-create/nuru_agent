'use client';

import React, { useState, useEffect } from 'react';
import { useAuth } from '@/context/AuthContext';
import { fetchChapitres, generateContent } from '@/lib/api';
import { BookOpen, CheckCircle2, HelpCircle, Loader2, Sparkles, Edit2, Check, X, Database } from 'lucide-react';
import { MarkdownViewer } from '@/components/math/MarkdownViewer';

export default function TeacherDashboard() {
  const { user } = useAuth();
  
  const [chapitres, setChapitres] = useState<string[]>([]);
  const [classes, setClasses] = useState<string[]>(['Terminale']);
  const [series, setSeries] = useState<string[]>(['S1', 'S2', 'S3', 'L1', 'L2']);
  
  const [selectedClasse, setSelectedClasse] = useState('Terminale');
  const [selectedSerie, setSelectedSerie] = useState('S1');
  const [selectedChapitre, setSelectedChapitre] = useState('');
  const [contentType, setContentType] = useState<'cours' | 'exercices' | 'quiz'>('cours');
  
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedResult, setGeneratedResult] = useState<any>(null);
  const [isEditing, setIsEditing] = useState(false);
  const [editedContent, setEditedContent] = useState('');

  useEffect(() => {
    fetchChapitres().then((data) => {
      setChapitres(data.chapitres);
      setClasses(data.classes);
      setSeries(data.series);
      if (data.chapitres.length > 0) setSelectedChapitre(data.chapitres[0]);
    });
  }, []);

  const handleGenerate = async () => {
    if (!selectedChapitre) return;
    setIsGenerating(true);
    setGeneratedResult(null);
    setIsEditing(false);
    
    try {
      const res = await generateContent({
        classe: selectedClasse,
        serie: selectedSerie,
        chapitre: selectedChapitre,
        content_type: contentType,
        difficulty: 'intermediate',
        num_questions: 5
      });
      setGeneratedResult(res);
      if (contentType === 'cours' && res.markdown) {
        setEditedContent(res.markdown);
      } else {
        setEditedContent(JSON.stringify(res, null, 2));
      }
    } catch (error) {
      console.error(error);
      alert("Erreur lors de la génération. Vérifiez que l'API et la base Qdrant sont accessibles.");
    } finally {
      setIsGenerating(false);
    }
  };

  const handlePublish = () => {
    // Dans une version complète, on enverrait `editedContent` au backend pour publication
    alert('Contenu publié avec succès aux élèves !');
    setGeneratedResult(null);
  };

  if (user?.role !== 'teacher' && user?.role !== 'admin') {
    return <div className="p-8">Accès réservé aux enseignants.</div>;
  }

  return (
    <div className="p-8 max-w-6xl mx-auto space-y-8 animate-in fade-in">
      <header className="flex justify-between items-end border-b border-slate-200 pb-4">
        <div>
          <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">Espace Enseignant</h1>
          <p className="text-slate-500 mt-1">Générez et validez du contenu pédagogique sur-mesure grâce à l'IA RAG.</p>
        </div>
      </header>

      {/* Configuration de la génération */}
      <section className="bg-white rounded-2xl shadow-sm border border-slate-200 p-6 space-y-6">
        <h2 className="text-lg font-bold text-slate-800 flex items-center gap-2">
          <Sparkles className="w-5 h-5 text-emerald-600" />
          Générateur de Contenu (Gemini + RAG)
        </h2>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="space-y-2">
            <label className="text-sm font-semibold text-slate-700">Classe & Série</label>
            <div className="flex gap-2">
              <select 
                className="w-1/2 rounded-xl border-slate-200 bg-slate-50 text-sm focus:ring-emerald-500"
                value={selectedClasse} onChange={(e) => setSelectedClasse(e.target.value)}
              >
                {classes.map(c => <option key={c} value={c}>{c}</option>)}
              </select>
              <select 
                className="w-1/2 rounded-xl border-slate-200 bg-slate-50 text-sm focus:ring-emerald-500"
                value={selectedSerie} onChange={(e) => setSelectedSerie(e.target.value)}
              >
                {series.map(s => <option key={s} value={s}>{s}</option>)}
              </select>
            </div>
          </div>
          
          <div className="space-y-2">
            <label className="text-sm font-semibold text-slate-700">Chapitre</label>
            <select 
              className="w-full rounded-xl border-slate-200 bg-slate-50 text-sm focus:ring-emerald-500"
              value={selectedChapitre} onChange={(e) => setSelectedChapitre(e.target.value)}
            >
              {chapitres.map(c => <option key={c} value={c}>{c}</option>)}
            </select>
          </div>
          
          <div className="space-y-2">
            <label className="text-sm font-semibold text-slate-700">Type de contenu</label>
            <div className="flex bg-slate-100 p-1 rounded-xl">
              <button 
                onClick={() => setContentType('cours')}
                className={`flex-1 flex justify-center items-center gap-2 py-2 text-xs font-bold rounded-lg transition-colors ${contentType === 'cours' ? 'bg-white text-emerald-700 shadow-sm' : 'text-slate-500 hover:text-slate-700'}`}
              >
                <BookOpen className="w-4 h-4" /> Cours
              </button>
              <button 
                onClick={() => setContentType('exercices')}
                className={`flex-1 flex justify-center items-center gap-2 py-2 text-xs font-bold rounded-lg transition-colors ${contentType === 'exercices' ? 'bg-white text-emerald-700 shadow-sm' : 'text-slate-500 hover:text-slate-700'}`}
              >
                <CheckCircle2 className="w-4 h-4" /> Exos
              </button>
              <button 
                onClick={() => setContentType('quiz')}
                className={`flex-1 flex justify-center items-center gap-2 py-2 text-xs font-bold rounded-lg transition-colors ${contentType === 'quiz' ? 'bg-white text-emerald-700 shadow-sm' : 'text-slate-500 hover:text-slate-700'}`}
              >
                <HelpCircle className="w-4 h-4" /> Quiz
              </button>
            </div>
          </div>
        </div>

        <button
          onClick={handleGenerate}
          disabled={isGenerating || !selectedChapitre}
          className="w-full py-3 bg-emerald-600 hover:bg-emerald-700 text-white font-bold rounded-xl transition-all shadow-sm hover:shadow flex justify-center items-center gap-2 disabled:opacity-70"
        >
          {isGenerating ? <Loader2 className="w-5 h-5 animate-spin" /> : <Sparkles className="w-5 h-5" />}
          {isGenerating ? 'Génération en cours (Gemini)...' : 'Générer le contenu'}
        </button>
      </section>

      {/* Prévisualisation & Validation */}
      {generatedResult && (
        <section className="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden flex flex-col">
          <div className="bg-slate-50 border-b border-slate-200 p-4 flex justify-between items-center">
            <div>
              <h3 className="font-bold text-slate-800">Prévisualisation</h3>
              <p className="text-xs text-slate-500">
                {generatedResult.rag_used 
                  ? <span className="text-emerald-700 font-semibold">✅ Généré à partir de la base documentaire officielle (RAG + Gemini)</span>
                  : <span className="text-amber-600 font-semibold">⚠️ Généré avec les connaissances de base (Aucun doc RAG trouvé)</span>}
              </p>
            </div>
            <div className="flex gap-2">
              <button 
                onClick={() => setIsEditing(!isEditing)}
                className="px-3 py-1.5 text-sm font-semibold bg-white border border-slate-200 rounded-lg hover:bg-slate-50 flex items-center gap-2"
              >
                {isEditing ? <X className="w-4 h-4" /> : <Edit2 className="w-4 h-4" />}
                {isEditing ? 'Annuler' : 'Modifier'}
              </button>
              <button 
                onClick={handlePublish}
                className="px-4 py-1.5 text-sm font-semibold bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 flex items-center gap-2 shadow-sm"
              >
                <Check className="w-4 h-4" />
                Valider & Publier
              </button>
            </div>
          </div>
          
          <div className="p-6 bg-white overflow-auto max-h-[600px]">
            {isEditing ? (
              <textarea
                value={editedContent}
                onChange={(e) => setEditedContent(e.target.value)}
                className="w-full h-96 p-4 font-mono text-sm bg-slate-50 border border-slate-200 rounded-lg focus:ring-emerald-500 focus:border-emerald-500"
              />
            ) : contentType === 'cours' ? (
              <div className="nuru-markdown">
                <MarkdownViewer content={editedContent} />
              </div>
            ) : (
              <pre className="p-4 bg-slate-50 rounded-lg text-sm font-mono overflow-auto text-slate-700 border border-slate-100">
                {editedContent}
              </pre>
            )}
          </div>
          
          {generatedResult.sources?.length > 0 && (
            <div className="bg-slate-50 p-4 border-t border-slate-200">
              <h4 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">Sources RAG utilisées</h4>
              <ul className="text-xs text-slate-600 list-disc pl-4 space-y-1">
                {generatedResult.sources.map((s: string, i: number) => (
                  <li key={i}>{s}</li>
                ))}
              </ul>
            </div>
          )}
        </section>
      )}
    </div>
  );
}
