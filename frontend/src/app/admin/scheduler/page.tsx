'use client';

import React, { useState } from 'react';
import { Clock, Play, CheckCircle2, RefreshCw, MessageSquare, Mail, AlertTriangle } from 'lucide-react';

export default function SchedulerPage() {
  const [tasks, setTasks] = useState([
    {
      id: 'task-1',
      name: 'Alertes SMS Parents & Élèves',
      description: 'Envoi d’alertes SMS en cas de retard ou de performance exceptionnelle.',
      schedule: 'Tous les jours à 18h00',
      status: 'Actif',
      lastRun: 'Aujourd’hui, 18:00',
      nextRun: 'Demain, 18:00',
      type: 'SMS'
    },
    {
      id: 'task-2',
      name: 'Digest Hebdomadaire Pédagogique',
      description: 'Génération et envoi du résumé hebdomadaire par email/WhatsApp.',
      schedule: 'Chaque Dimanche à 20h00',
      status: 'Actif',
      lastRun: '26/07/2026 20:00',
      nextRun: '02/08/2026 20:00',
      type: 'Email'
    }
  ]);

  const [notificationMsg, setNotificationMsg] = useState<string | null>(null);

  const handleRunNow = (taskName: string) => {
    setNotificationMsg(`Exécution manuelle lancée pour : ${taskName}`);
    setTimeout(() => {
      setNotificationMsg(null);
    }, 4000);
  };

  return (
    <div className="max-w-7xl mx-auto space-y-8 animate-in fade-in duration-300">
      {/* Header */}
      <div className="rounded-3xl bg-slate-900 p-6 sm:p-8 text-white shadow-xl space-y-3 border border-slate-800 relative overflow-hidden">
        <div className="absolute right-0 top-0 translate-x-12 -translate-y-12 w-64 h-64 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none"></div>
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-cyan-500/20 text-cyan-300 text-xs font-semibold border border-cyan-400/30">
          <Clock className="w-3.5 h-3.5" />
          <span>Gestion des Tâches Planifiées (CRON)</span>
        </div>
        <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight">
          Scheduler
        </h1>
        <p className="text-slate-300 text-xs sm:text-sm max-w-3xl">
          Tâches récurrentes (alertes SMS et digest hebdomadaire) pour la communication automatisée avec les élèves et parents.
        </p>
      </div>

      {notificationMsg && (
        <div className="p-4 rounded-2xl bg-cyan-600 text-white shadow-lg flex items-center justify-between animate-in slide-in-from-top duration-300">
          <div className="flex items-center gap-3">
            <CheckCircle2 className="w-5 h-5 text-cyan-200" />
            <span className="text-xs font-extrabold">{notificationMsg}</span>
          </div>
          <button onClick={() => setNotificationMsg(null)} className="text-xs font-bold px-3 py-1 bg-cyan-700 rounded-lg">
            OK
          </button>
        </div>
      )}

      {/* Task cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {tasks.map((task) => (
          <div key={task.id} className="bg-white rounded-3xl p-6 border border-slate-200 shadow-2xs space-y-4 hover:shadow-md transition-shadow">
            <div className="flex items-start justify-between">
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  {task.type === 'SMS' ? (
                    <span className="p-1.5 rounded-lg bg-cyan-50 text-cyan-600 border border-cyan-200">
                      <MessageSquare className="w-4 h-4" />
                    </span>
                  ) : (
                    <span className="p-1.5 rounded-lg bg-indigo-50 text-indigo-600 border border-indigo-200">
                      <Mail className="w-4 h-4" />
                    </span>
                  )}
                  <span className="text-xs font-extrabold text-slate-900">{task.name}</span>
                </div>
                <p className="text-xs text-slate-500">{task.description}</p>
              </div>

              <span className="px-3 py-1 rounded-full bg-emerald-100 text-emerald-800 text-[10px] font-extrabold">
                {task.status}
              </span>
            </div>

            <div className="pt-3 border-t border-slate-100 space-y-2 text-xs">
              <div className="flex items-center justify-between text-slate-600">
                <span className="font-semibold">Fréquence :</span>
                <span className="font-bold text-slate-900">{task.schedule}</span>
              </div>
              <div className="flex items-center justify-between text-slate-600">
                <span className="font-semibold">Dernière exécution :</span>
                <span className="text-slate-500">{task.lastRun}</span>
              </div>
              <div className="flex items-center justify-between text-slate-600">
                <span className="font-semibold">Prochaine exécution :</span>
                <span className="text-slate-500">{task.nextRun}</span>
              </div>
            </div>

            <div className="pt-3 border-t border-slate-100 flex justify-end">
              <button
                onClick={() => handleRunNow(task.name)}
                className="px-4 py-2 rounded-xl bg-slate-900 hover:bg-slate-800 text-white font-extrabold text-xs flex items-center gap-2 transition-colors cursor-pointer"
              >
                <Play className="w-3.5 h-3.5 fill-white" />
                <span>Exécuter maintenant</span>
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
