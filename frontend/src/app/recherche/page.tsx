'use client';

import React, { Suspense, useState, useEffect } from 'react';
import { useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { sendChatMessage } from '@/lib/api';
import { MarkdownViewer } from '@/components/math/MarkdownViewer';
import { Search, Brain, BookOpen, ArrowRight, Sparkles, FileText, CheckCircle2 } from 'lucide-react';

function SearchContent() {
  const searchParams = useSearchParams();
  const query = searchParams.get('q') || '';
  const [resultText, setResultText] = useState<string>('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (query) {
      setLoading(true);
      sendChatMessage(query)
        .then((res) => setResultText(res.response))
        .catch(() => setResultText('⚠️ Erreur lors de la recherche RAG.'))
        .finally(() => setLoading(false));
    }
  }, [query]);

  return (
    <div className="max-w-4xl mx-auto space-y-8 animate-in fade-in duration-300">
      {/* Header */}
      <div className="space-y-2">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-100 text-blue-700 text-xs font-bold">
          <Search className="w-3.5 h-3.5" />
          <span>Recherche Vectorielle Qdrant RAG</span>
        </div>
        <h1 className="text-2xl font-extrabold text-slate-900">
          Résultats pour « <span className="text-blue-600">{query || 'Mathématiques'}</span> »
        </h1>
      </div>

      {/* Result Card */}
      <div className="bg-white rounded-3xl p-6 sm:p-8 border border-slate-200 shadow-xs space-y-6">
        {loading ? (
          <div className="p-8 text-center text-xs text-slate-500 space-y-2">
            <Brain className="w-8 h-8 text-blue-600 animate-pulse mx-auto" />
            <p>Recherche des passages pertinents dans les documents de Mathématiques indexés...</p>
          </div>
        ) : (
          <div className="space-y-4">
            <h3 className="font-bold text-sm text-slate-900 flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-blue-600" />
              Réponse & Synthèse RAG NURU
            </h3>
            <MarkdownViewer content={resultText || `Aucun résultat direct pour "${query}". Essayez avec des termes comme "logarithme", "limite", "intégrale".`} />
          </div>
        )}
      </div>
    </div>
  );
}

export default function SearchPage() {
  return (
    <Suspense fallback={<div className="p-8 text-center text-xs text-slate-500">Chargement de la recherche...</div>}>
      <SearchContent />
    </Suspense>
  );
}
