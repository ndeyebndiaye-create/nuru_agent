'use client';

import React, { useEffect, useState } from 'react';
import { useAuth } from '@/context/AuthContext';
import { fetchParentStudents } from '@/lib/api';
import { Loader2, TrendingUp, BookOpen, AlertCircle, Calendar } from 'lucide-react';

export default function ParentDashboard() {
  const { user } = useAuth();
  const [students, setStudents] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (user?.id) {
      fetchParentStudents(user.id).then(data => {
        setStudents(data.students || []);
        setLoading(false);
      });
    }
  }, [user]);

  if (user?.role !== 'parent' && user?.role !== 'admin') {
    return <div className="p-8">Accès réservé aux parents.</div>;
  }

  if (loading) return <div className="p-8 flex justify-center"><Loader2 className="w-8 h-8 animate-spin text-emerald-600" /></div>;

  return (
    <div className="p-8 max-w-6xl mx-auto space-y-8 animate-in fade-in">
      <header className="flex justify-between items-end border-b border-slate-200 pb-4">
        <div>
          <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">Espace Parent</h1>
          <p className="text-slate-500 mt-1">Suivez la progression de vos enfants en temps réel.</p>
        </div>
      </header>

      {students.length === 0 ? (
        <div className="bg-white rounded-2xl p-12 text-center border border-slate-200 shadow-sm">
          <TrendingUp className="w-12 h-12 text-slate-300 mx-auto mb-4" />
          <h3 className="text-lg font-bold text-slate-800">Aucun enfant lié</h3>
          <p className="text-slate-500 mt-2">Vous n'avez pas encore lié le compte de votre enfant à votre espace parent.</p>
        </div>
      ) : (
        <div className="space-y-8">
          {students.map((student, idx) => (
            <div key={idx} className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm space-y-6">
              <div className="flex justify-between items-center border-b border-slate-100 pb-4">
                <h2 className="text-xl font-bold text-slate-800">{student.name}</h2>
                <span className="px-3 py-1 bg-emerald-100 text-emerald-800 rounded-lg text-sm font-bold">
                  {student.grade}
                </span>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h3 className="text-sm font-bold text-slate-500 uppercase tracking-wider mb-4 flex items-center gap-2">
                    <TrendingUp className="w-4 h-4" /> Maîtrise des chapitres
                  </h3>
                  {student.mastery_map?.length > 0 ? (
                    <div className="space-y-4">
                      {student.mastery_map.map((item: any, i: number) => (
                        <div key={i} className="space-y-1">
                          <div className="flex justify-between text-sm">
                            <span className="font-medium text-slate-700">{item.concept}</span>
                            <span className="font-bold text-emerald-600">{Math.round(item.mastery_score * 100)}%</span>
                          </div>
                          <div className="w-full bg-slate-100 rounded-full h-2">
                            <div className="bg-emerald-500 h-2 rounded-full" style={{ width: `${Math.round(item.mastery_score * 100)}%` }} />
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-sm text-slate-500 italic">Aucune donnée disponible.</p>
                  )}
                </div>

                <div>
                  <h3 className="text-sm font-bold text-slate-500 uppercase tracking-wider mb-4 flex items-center gap-2">
                    <AlertCircle className="w-4 h-4" /> Recommandations
                  </h3>
                  {student.recommendations?.length > 0 ? (
                    <div className="space-y-3">
                      {student.recommendations.map((rec: any, i: number) => (
                        <div key={i} className="p-3 bg-amber-50 border border-amber-100 rounded-xl">
                          <p className="text-sm font-bold text-amber-900">{rec.concept}</p>
                          <p className="text-xs text-amber-700 mt-1">{rec.message}</p>
                          <p className="text-xs text-amber-500 mt-2 flex items-center gap-1">
                            <Calendar className="w-3 h-3" /> {new Date(rec.date).toLocaleDateString()}
                          </p>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-sm text-slate-500 italic">Aucune recommandation.</p>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
