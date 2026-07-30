'use client';

import React, { useState } from 'react';
import { History, ShieldAlert, Filter, Search, Lock, ShieldCheck } from 'lucide-react';

interface AuditLogEntry {
  id: string;
  timestamp: string;
  actor: string;
  action: string;
  target: string;
  severity: 'INFO' | 'WARNING' | 'CRITICAL';
  hash: string;
}

export default function JournalAuditPage() {
  const [logs] = useState<AuditLogEntry[]>([
    {
      id: 'log-101',
      timestamp: '2026-07-27 18:30:12',
      actor: 'admin@nuru.sn',
      action: 'Modification cibles cognitives',
      target: 'Distribution Taxonomique (50/35/15)',
      severity: 'WARNING',
      hash: '0x8f2a...9d1e'
    },
    {
      id: 'log-102',
      timestamp: '2026-07-26 14:15:00',
      actor: 'admin@nuru.sn',
      action: 'Changement de rôle utilisateur',
      target: 'Prof. Amadou Diop -> Enseignant',
      severity: 'INFO',
      hash: '0x3c4e...1a7b'
    },
    {
      id: 'log-103',
      timestamp: '2026-07-25 09:00:44',
      actor: 'system_rag',
      action: 'Validation automatique lot RAG',
      target: '12 Quiz BAC S1',
      severity: 'INFO',
      hash: '0x7e1b...4f8c'
    },
    {
      id: 'log-104',
      timestamp: '2026-07-22 11:20:05',
      actor: 'admin@nuru.sn',
      action: 'Réallocation du budget IA',
      target: 'Plafond Mensuel USD 150.00$',
      severity: 'CRITICAL',
      hash: '0x9a2d...3b5e'
    }
  ]);

  const [severityFilter, setSeverityFilter] = useState('Tous');

  const filteredLogs = logs.filter((l) => severityFilter === 'Tous' || l.severity === severityFilter);

  return (
    <div className="max-w-7xl mx-auto space-y-8 animate-in fade-in duration-300">
      {/* Header */}
      <div className="rounded-3xl bg-slate-900 p-6 sm:p-8 text-white shadow-xl space-y-3 border border-slate-800 relative overflow-hidden">
        <div className="absolute right-0 top-0 translate-x-12 -translate-y-12 w-64 h-64 bg-slate-500/10 rounded-full blur-3xl pointer-events-none"></div>
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-slate-500/20 text-slate-300 text-xs font-semibold border border-slate-400/30">
          <Lock className="w-3.5 h-3.5" />
          <span>Registre d'Intégrité Append-Only</span>
        </div>
        <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight">
          Journal d'audit
        </h1>
        <p className="text-slate-300 text-xs sm:text-sm max-w-3xl">
          Journal append-only des actions admin sensibles, traçabilité infalsifiable des modifications de configuration et d'accès.
        </p>
      </div>

      {/* Filter and Table */}
      <div className="bg-white rounded-3xl p-6 border border-slate-200 shadow-2xs space-y-4">
        <div className="flex items-center gap-2 p-1.5 bg-slate-100 rounded-2xl w-fit">
          {(['Tous', 'INFO', 'WARNING', 'CRITICAL'] as const).map((s) => (
            <button
              key={s}
              onClick={() => setSeverityFilter(s)}
              className={`px-4 py-2 rounded-xl text-xs font-extrabold transition-all ${
                severityFilter === s ? 'bg-white text-slate-900 shadow-xs' : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              {s}
            </button>
          ))}
        </div>

        <div className="overflow-x-auto rounded-2xl border border-slate-200">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 border-b border-slate-200 text-slate-500 font-bold uppercase tracking-wider">
              <tr>
                <th className="p-4">Horodatage</th>
                <th className="p-4">Acteur</th>
                <th className="p-4">Action</th>
                <th className="p-4">Cible / Détails</th>
                <th className="p-4">Sévérité</th>
                <th className="p-4 text-right">Hash Cryptographique</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 font-medium text-slate-700">
              {filteredLogs.map((log) => (
                <tr key={log.id} className="hover:bg-slate-50 transition-colors">
                  <td className="p-4 font-mono text-slate-500">{log.timestamp}</td>
                  <td className="p-4 font-bold text-slate-900">{log.actor}</td>
                  <td className="p-4 font-bold text-slate-800">{log.action}</td>
                  <td className="p-4 text-slate-600">{log.target}</td>
                  <td className="p-4">
                    <span
                      className={`px-2.5 py-1 rounded-full text-[10px] font-extrabold border ${
                        log.severity === 'CRITICAL'
                          ? 'bg-rose-100 text-rose-800 border-rose-300'
                          : log.severity === 'WARNING'
                          ? 'bg-amber-100 text-amber-800 border-amber-300'
                          : 'bg-blue-100 text-blue-800 border-blue-300'
                      }`}
                    >
                      {log.severity}
                    </span>
                  </td>
                  <td className="p-4 text-right font-mono text-slate-400">{log.hash}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
