'use client';

import React, { useState, useEffect, useMemo } from 'react';
import Link from 'next/link';
import { useAuth } from '@/context/AuthContext';
import { generateContent } from '@/lib/api';
import { MarkdownViewer } from '@/components/math/MarkdownViewer';
import { useParams } from 'next/navigation';
import {
  ArrowLeft,
  BookOpen,
  Sparkles,
  Loader2,
  List,
  ChevronRight,
  Database,
  AlertCircle,
} from 'lucide-react';

// ── Extrait les titres H2/H3 du markdown pour la table des matières
function extractTOC(markdown: string): { level: number; text: string; id: string }[] {
  const lines = markdown.split('\n');
  const toc: { level: number; text: string; id: string }[] = [];
  for (const line of lines) {
    const h2 = line.match(/^## (.+)/);
    const h3 = line.match(/^### (.+)/);
    if (h2) {
      const text = h2[1].replace(/[📌🎯📖📚🔬🛠️✏️⚠️📝]/gu, '').trim();
      const id = text.toLowerCase().replace(/[^a-z0-9\s-]/g, '').replace(/\s+/g, '-').slice(0, 60);
      toc.push({ level: 2, text, id });
    } else if (h3) {
      const text = h3[1].replace(/[📌🎯📖📚🔬🛠️✏️⚠️📝]/gu, '').trim();
      const id = text.toLowerCase().replace(/[^a-z0-9\s-]/g, '').replace(/\s+/g, '-').slice(0, 60);
      toc.push({ level: 3, text, id });
    }
  }
  return toc;
}

export default function CourseDetailPage() {
  const { user } = useAuth();
  const params = useParams();
  const concept =
    typeof params.id === 'string'
      ? decodeURIComponent(params.id).replace(/-/g, ' ')
      : 'Chapitre Général';

  const [course, setCourse] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeSection, setActiveSection] = useState('');

  useEffect(() => {
    setLoading(true);
    setError(null);
    generateContent({
      classe: user?.classe || 'Terminale',
      serie: user?.serie || 'S1',
      chapitre: concept,
      content_type: 'cours',
    })
      .then((res) => {
        setCourse(res);
        setLoading(false);
      })
      .catch((err) => {
        console.error(err);
        setError("Erreur lors de la génération du cours. Vérifiez que l'API est accessible.");
        setLoading(false);
      });
  }, [concept, user]);

  const toc = useMemo(() => (course?.markdown ? extractTOC(course.markdown) : []), [course]);

  if (loading) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center gap-4 bg-slate-50">
        <div className="w-16 h-16 rounded-2xl bg-emerald-100 flex items-center justify-center">
          <Loader2 className="w-8 h-8 animate-spin text-emerald-600" />
        </div>
        <div className="text-center">
          <p className="font-bold text-slate-800 text-lg">Génération du cours en cours…</p>
          <p className="text-slate-500 text-sm mt-1">NURU consulte le programme sénégalais (RAG + Gemini)</p>
        </div>
      </div>
    );
  }

  if (error || !course) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center gap-4 p-8">
        <div className="w-16 h-16 rounded-2xl bg-red-100 flex items-center justify-center">
          <AlertCircle className="w-8 h-8 text-red-500" />
        </div>
        <p className="text-slate-700 font-semibold text-center">{error || 'Erreur inconnue'}</p>
        <Link href="/matieres" className="text-emerald-600 hover:underline text-sm font-semibold">
          ← Retour à la bibliothèque
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-[1400px] mx-auto animate-in fade-in duration-300 px-4 py-6 sm:px-8">
      {/* Barre de navigation supérieure */}
      <div className="flex items-center justify-between mb-6 flex-wrap gap-3">
        <Link
          href="/matieres"
          className="text-sm font-bold text-slate-600 hover:text-emerald-700 flex items-center gap-1.5 transition-colors"
        >
          <ArrowLeft className="w-4 h-4 text-emerald-600" />
          Retour à la Bibliothèque
        </Link>
        <div className="flex gap-2 flex-wrap">
          <span
            className={`text-xs font-bold px-3 py-1 rounded-full border ${
              course.rag_used
                ? 'bg-emerald-50 text-emerald-700 border-emerald-200'
                : 'bg-amber-50 text-amber-700 border-amber-200'
            }`}
          >
            <Database className="w-3 h-3 inline mr-1" />
            {course.rag_used ? 'RAG Actif' : 'Connaissances générales'}
          </span>
          <span className="text-[11px] font-extrabold uppercase px-2.5 py-1 rounded bg-emerald-100 text-emerald-800">
            {course.classe} {course.serie}
          </span>
        </div>
      </div>

      {/* Disposition principale : sidebar TOC + contenu */}
      <div className="bg-white rounded-3xl border border-slate-200 shadow-sm overflow-hidden flex flex-col md:flex-row min-h-[85vh]">

        {/* ── Sidebar Table des Matières */}
        <aside className="w-full md:w-72 border-r border-slate-100 bg-slate-50 flex flex-col overflow-y-auto shrink-0">
          {/* En-tête sidebar */}
          <div className="p-4 border-b border-slate-100 flex items-center gap-3 sticky top-0 bg-slate-50 z-10">
            <div className="w-9 h-9 rounded-xl bg-emerald-100 text-emerald-700 flex items-center justify-center shrink-0">
              <BookOpen className="w-4 h-4" />
            </div>
            <div className="min-w-0">
              <span className="text-[10px] font-extrabold text-slate-400 uppercase tracking-wider block">
                Table des matières
              </span>
              <h3 className="text-sm font-bold text-slate-900 truncate">{concept}</h3>
            </div>
          </div>

          {/* Liens de navigation TOC */}
          <nav className="p-3 space-y-0.5 flex-1">
            {toc.length === 0 ? (
              <p className="text-xs text-slate-400 px-3 py-2 italic">Navigation disponible après génération</p>
            ) : (
              toc.map((item, idx) => (
                <a
                  key={idx}
                  href={`#${item.id}`}
                  onClick={() => setActiveSection(item.id)}
                  className={`flex items-center gap-2 px-3 py-2 rounded-lg text-xs font-medium transition-all hover:bg-emerald-50 hover:text-emerald-800 group ${
                    item.level === 3 ? 'pl-6 text-slate-500 hover:text-emerald-700' : 'text-slate-700'
                  } ${activeSection === item.id ? 'bg-emerald-100 text-emerald-800 font-semibold' : ''}`}
                >
                  {item.level === 2 && (
                    <ChevronRight className="w-3 h-3 text-emerald-500 group-hover:translate-x-0.5 transition-transform shrink-0" />
                  )}
                  {item.level === 3 && (
                    <span className="w-1.5 h-1.5 rounded-full bg-slate-300 group-hover:bg-emerald-400 shrink-0" />
                  )}
                  <span className="truncate">{item.text}</span>
                </a>
              ))
            )}
          </nav>

          {/* Sources RAG */}
          {course.sources && course.sources.length > 0 && (
            <div className="p-4 border-t border-slate-100 mt-auto">
              <span className="text-[10px] font-extrabold text-slate-400 uppercase tracking-wider block mb-2">
                Sources (Programme Officiel)
              </span>
              <ul className="space-y-1">
                {course.sources.map((s: string, idx: number) => (
                  <li
                    key={idx}
                    title={s}
                    className="text-[11px] text-slate-500 truncate flex items-center gap-1"
                  >
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 shrink-0" />
                    {s}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </aside>

        {/* ── Contenu Principal du Cours */}
        <main className="flex-1 overflow-y-auto">
          {/* En-tête du cours */}
          <header className="sticky top-0 z-10 bg-white/90 backdrop-blur-sm border-b border-slate-100 px-8 py-4 flex items-center justify-between">
            <div className="flex items-center gap-2 min-w-0">
              <Sparkles className="w-5 h-5 text-emerald-500 shrink-0" />
              <h1 className="text-lg font-extrabold text-slate-900 truncate">{concept}</h1>
            </div>
            <span className="text-xs text-slate-400 shrink-0 ml-4">Mathématiques · {course.classe} {course.serie}</span>
          </header>

          {/* Corps du cours */}
          <article className="px-6 sm:px-10 py-8 max-w-4xl">
            <MarkdownViewer content={course.markdown || 'Aucun contenu généré.'} />
          </article>

          {/* Pied de page du cours */}
          <footer className="px-8 py-6 border-t border-slate-100 bg-slate-50 flex items-center justify-between flex-wrap gap-3">
            <div className="flex items-center gap-2 text-xs text-slate-500">
              <Sparkles className="w-3.5 h-3.5 text-emerald-500" />
              Généré par NURU IA · Programme sénégalais officiel
            </div>
            <Link
              href="/exercices"
              className="text-xs font-bold text-emerald-700 hover:underline flex items-center gap-1"
            >
              Pratiquer avec des exercices <ChevronRight className="w-3 h-3" />
            </Link>
          </footer>
        </main>
      </div>
    </div>
  );
}
