'use client';

import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkMath from 'remark-math';
import remarkGfm from 'remark-gfm';
import rehypeKatex from 'rehype-katex';
import 'katex/dist/katex.min.css';

interface MarkdownViewerProps {
  content: string;
  className?: string;
}

// Génère un slug pour les ancres de navigation
function slugify(text: string): string {
  return text
    .toLowerCase()
    .replace(/[^a-z0-9\s-]/g, '')
    .replace(/\s+/g, '-')
    .slice(0, 60);
}

// Détecte si un blockquote contient un Théorème, Définition, Propriété, etc.
function getBlockquoteVariant(children: React.ReactNode): 'definition' | 'theorem' | 'property' | 'method' | 'warning' | 'default' {
  const text = extractText(children).toLowerCase();
  if (text.startsWith('définition') || text.startsWith('definition')) return 'definition';
  if (text.startsWith('théorème') || text.startsWith('theoreme') || text.startsWith('theorem')) return 'theorem';
  if (text.startsWith('propriété') || text.startsWith('propriete') || text.startsWith('corollaire')) return 'property';
  if (text.startsWith('méthode') || text.startsWith('methode') || text.startsWith('algorithme')) return 'method';
  if (text.startsWith('attention') || text.startsWith('⚠') || text.startsWith('piège') || text.startsWith('erreur')) return 'warning';
  return 'default';
}

function extractText(node: React.ReactNode): string {
  if (typeof node === 'string') return node;
  if (Array.isArray(node)) return node.map(extractText).join('');
  if (React.isValidElement(node) && node.props) {
    const props = node.props as { children?: React.ReactNode };
    return extractText(props.children);
  }
  return '';
}

const variantStyles: Record<string, { border: string; bg: string; icon: string; label: string }> = {
  definition: {
    border: 'border-l-4 border-emerald-500',
    bg: 'bg-emerald-50',
    icon: '📖',
    label: 'text-emerald-800',
  },
  theorem: {
    border: 'border-l-4 border-blue-500',
    bg: 'bg-blue-50',
    icon: '🔬',
    label: 'text-blue-800',
  },
  property: {
    border: 'border-l-4 border-purple-500',
    bg: 'bg-purple-50',
    icon: '📐',
    label: 'text-purple-800',
  },
  method: {
    border: 'border-l-4 border-orange-500',
    bg: 'bg-orange-50',
    icon: '🛠️',
    label: 'text-orange-800',
  },
  warning: {
    border: 'border-l-4 border-red-400',
    bg: 'bg-red-50',
    icon: '⚠️',
    label: 'text-red-800',
  },
  default: {
    border: 'border-l-4 border-slate-300',
    bg: 'bg-slate-50',
    icon: '',
    label: 'text-slate-700',
  },
};

export const MarkdownViewer: React.FC<MarkdownViewerProps> = ({ content, className = '' }) => {
  return (
    <div className={`nuru-markdown ${className}`}>
      <ReactMarkdown
        remarkPlugins={[remarkMath, remarkGfm]}
        rehypePlugins={[[rehypeKatex, { strict: false, throwOnError: false }]]}
        components={{
          // ── Titres avec ancres de navigation
          h1: ({ children }) => {
            const id = slugify(extractText(children));
            return (
              <h1 id={id} className="text-3xl font-extrabold text-slate-900 mt-8 mb-4 pb-3 border-b-2 border-emerald-200 tracking-tight">
                {children}
              </h1>
            );
          },
          h2: ({ children }) => {
            const id = slugify(extractText(children));
            return (
              <h2 id={id} className="text-2xl font-bold text-slate-800 mt-8 mb-3 pb-2 border-b border-slate-200 flex items-center gap-2">
                {children}
              </h2>
            );
          },
          h3: ({ children }) => {
            const id = slugify(extractText(children));
            return (
              <h3 id={id} className="text-xl font-semibold text-slate-700 mt-6 mb-2">
                {children}
              </h3>
            );
          },
          h4: ({ children }) => (
            <h4 className="text-base font-semibold text-slate-600 mt-4 mb-1.5 uppercase tracking-wide text-sm">
              {children}
            </h4>
          ),

          // ── Paragraphe
          p: ({ children }) => (
            <p className="text-slate-700 leading-7 mb-4 text-[0.97rem]">{children}</p>
          ),

          // ── Blockquote stylisé selon le contenu (définition, théorème…)
          blockquote: ({ children }) => {
            const variant = getBlockquoteVariant(children);
            const style = variantStyles[variant];
            return (
              <blockquote
                className={`${style.border} ${style.bg} rounded-r-xl px-5 py-4 my-5 shadow-sm`}
              >
                <div className={`font-medium ${style.label} text-[0.95rem] leading-7`}>
                  {children}
                </div>
              </blockquote>
            );
          },

          // ── Listes
          ul: ({ children }) => (
            <ul className="list-disc list-outside pl-6 space-y-1.5 mb-4 text-slate-700 text-[0.97rem]">
              {children}
            </ul>
          ),
          ol: ({ children }) => (
            <ol className="list-decimal list-outside pl-6 space-y-1.5 mb-4 text-slate-700 text-[0.97rem]">
              {children}
            </ol>
          ),
          li: ({ children }) => (
            <li className="leading-7">{children}</li>
          ),

          // ── Séparateur horizontal
          hr: () => (
            <hr className="my-8 border-t-2 border-slate-100" />
          ),

          // ── Code inline
          code: ({ children, className: cname }) => {
            const isBlock = cname?.includes('language-');
            if (isBlock) {
              return (
                <pre className="bg-slate-900 text-emerald-300 rounded-xl p-4 my-5 overflow-x-auto text-sm font-mono shadow-inner">
                  <code>{children}</code>
                </pre>
              );
            }
            return (
              <code className="bg-slate-100 text-emerald-700 px-1.5 py-0.5 rounded text-[0.88rem] font-mono border border-slate-200">
                {children}
              </code>
            );
          },

          // ── Tableaux (GFM)
          table: ({ children }) => (
            <div className="overflow-x-auto my-6 rounded-xl border border-slate-200 shadow-sm">
              <table className="w-full text-sm text-left text-slate-700">
                {children}
              </table>
            </div>
          ),
          thead: ({ children }) => (
            <thead className="bg-emerald-50 text-emerald-800 text-xs uppercase tracking-wider">
              {children}
            </thead>
          ),
          tbody: ({ children }) => (
            <tbody className="divide-y divide-slate-100">{children}</tbody>
          ),
          tr: ({ children }) => (
            <tr className="hover:bg-slate-50 transition-colors">{children}</tr>
          ),
          th: ({ children }) => (
            <th className="px-4 py-3 font-bold">{children}</th>
          ),
          td: ({ children }) => (
            <td className="px-4 py-3">{children}</td>
          ),

          // ── Texte fort / italique
          strong: ({ children }) => (
            <strong className="font-bold text-slate-900">{children}</strong>
          ),
          em: ({ children }) => (
            <em className="italic text-slate-600">{children}</em>
          ),
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
};
