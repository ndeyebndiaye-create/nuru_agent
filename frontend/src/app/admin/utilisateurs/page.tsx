'use client';

import React, { useState, useEffect } from 'react';
import { fetchAdminUsers } from '@/lib/api';
import { Users, Search, ShieldCheck, UserCheck, GraduationCap, BookOpen, Filter, RefreshCw } from 'lucide-react';
import { UserRole } from '@/types';

export default function UtilisateursPage() {
  const [users, setUsers] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [roleFilter, setRoleFilter] = useState<string>('Tous');
  const [searchQuery, setSearchQuery] = useState<string>('');

  const loadUsers = async () => {
    setIsLoading(true);
    try {
      const res = await fetchAdminUsers();
      setUsers(res.users || []);
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadUsers();
  }, []);

  const filteredUsers = users.filter((u) => {
    const matchesRole = roleFilter === 'Tous' || u.role === roleFilter;
    const matchesSearch = (u.name || '').toLowerCase().includes(searchQuery.toLowerCase()) ||
                          (u.email || '').toLowerCase().includes(searchQuery.toLowerCase());
    return matchesRole && matchesSearch;
  });

  return (
    <div className="max-w-7xl mx-auto space-y-8 animate-in fade-in duration-300">
      {/* Header */}
      <div className="rounded-3xl bg-slate-900 p-6 sm:p-8 text-white shadow-xl space-y-3 border border-slate-800 relative overflow-hidden">
        <div className="absolute right-0 top-0 translate-x-12 -translate-y-12 w-64 h-64 bg-rose-500/10 rounded-full blur-3xl pointer-events-none"></div>
        <div className="flex items-center justify-between">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-rose-500/20 text-rose-300 text-xs font-semibold border border-rose-400/30">
            <Users className="w-3.5 h-3.5" />
            <span>Gestion des Comptes Réels de la Base</span>
          </div>
          <button
            onClick={loadUsers}
            className="px-3 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs text-slate-300 font-bold flex items-center gap-1.5 border border-slate-700 cursor-pointer"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin' : ''}`} />
            <span>Actualiser</span>
          </button>
        </div>
        <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight">
          Utilisateurs Enregistrés
        </h1>
        <p className="text-slate-300 text-xs sm:text-sm max-w-3xl">
          Liste complète des comptes enregistrés en base de données (`COUNT()` réel), avec répartition par rôle (Élèves, Enseignants, Parents, Admin).
        </p>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-3xl p-6 border border-slate-200 shadow-2xs space-y-4">
        <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-4">
          <div className="flex items-center gap-1.5 p-1.5 bg-slate-100 rounded-2xl shrink-0 overflow-x-auto">
            {(['Tous', 'student', 'teacher', 'parent', 'admin'] as const).map((r) => (
              <button
                key={r}
                onClick={() => setRoleFilter(r)}
                className={`px-4 py-2 rounded-xl text-xs font-extrabold transition-all whitespace-nowrap ${
                  roleFilter === r ? 'bg-white text-slate-900 shadow-xs' : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                {r === 'student' ? 'Élèves' : r === 'teacher' ? 'Enseignants' : r === 'parent' ? 'Parents' : r === 'admin' ? 'Admins' : 'Tous'}
              </button>
            ))}
          </div>

          <div className="relative flex-1 max-w-md">
            <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Rechercher par nom ou email..."
              className="w-full bg-slate-50 border border-slate-200 rounded-2xl pl-10 pr-4 py-2.5 text-xs text-slate-800 focus:bg-white outline-none"
            />
          </div>
        </div>

        {/* Table */}
        <div className="overflow-x-auto rounded-2xl border border-slate-200">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 border-b border-slate-200 text-slate-500 font-bold uppercase tracking-wider">
              <tr>
                <th className="p-4">Utilisateur</th>
                <th className="p-4">Email</th>
                <th className="p-4">Statut</th>
                <th className="p-4">Rôle</th>
                <th className="p-4">Classe / Série</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 font-medium text-slate-700">
              {filteredUsers.length > 0 ? (
                filteredUsers.map((u) => (
                  <tr key={u.id} className="hover:bg-slate-50 transition-colors">
                    <td className="p-4 font-bold text-slate-900">{u.name}</td>
                    <td className="p-4 text-slate-600">{u.email}</td>
                    <td className="p-4">
                      <span className="px-2.5 py-1 rounded-full bg-emerald-100 text-emerald-800 text-[10px] font-extrabold">
                        Actif (DB)
                      </span>
                    </td>
                    <td className="p-4">
                      <span className={`capitalize px-3 py-1 rounded-lg font-bold border ${
                        u.role === 'admin'
                          ? 'bg-slate-900 text-white border-slate-800'
                          : u.role === 'teacher'
                          ? 'bg-amber-100 text-amber-900 border-amber-200'
                          : u.role === 'parent'
                          ? 'bg-purple-100 text-purple-900 border-purple-200'
                          : 'bg-emerald-100 text-emerald-900 border-emerald-200'
                      }`}>
                        {u.role}
                      </span>
                    </td>
                    <td className="p-4 text-slate-500">{u.classe} {u.serie}</td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={5} className="p-6 text-center text-slate-400">
                    {isLoading ? 'Chargement des comptes...' : 'Aucun utilisateur trouvé.'}
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
