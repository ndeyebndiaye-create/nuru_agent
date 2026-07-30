'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { UserRole } from '@/types';
import { useAuth } from '@/context/AuthContext';
import {
  LayoutDashboard,
  BookOpen,
  CheckCircle2,
  HelpCircle,
  Search,
  TrendingUp,
  Trophy,
  User,
  Sparkles,
  Users,
  ShieldCheck,
  Brain,
  LogOut
} from 'lucide-react';

interface SidebarProps {
  currentRole: UserRole;
}

export const Sidebar: React.FC<SidebarProps> = ({ currentRole }) => {
  const pathname = usePathname();
  const router = useRouter();
  const { user, logout, isAuthenticated, openLoginModal } = useAuth();

  const activeRole = user?.role || currentRole;

  // Streamlined links for Student
  const studentLinks = [
    { href: '/', label: 'Accueil & Tableau de bord', icon: LayoutDashboard },
    { href: '/matieres', label: 'Bibliothèque des cours', icon: BookOpen },
    { href: '/exercices/exo-log-1', label: 'Exercices', icon: CheckCircle2 },
    { href: '/quiz/quiz-log-1', label: 'Quiz', icon: HelpCircle },
    { href: '/recherche', label: 'Recherche RAG', icon: Search },
    { href: '/progression', label: 'Progression', icon: TrendingUp },
    { href: '/defis', label: 'Défis & Récompenses', icon: Trophy }
  ];

  const teacherLinks = [
    { href: '/enseignant', label: 'Générer un Cours', icon: Sparkles },
    { href: '/enseignant#exercices', label: 'Générer des Exercices', icon: CheckCircle2 },
    { href: '/enseignant#quiz', label: 'Générer des Quiz', icon: HelpCircle }
  ];

  const parentLinks = [
    { href: '/parent', label: 'Suivi de Progression', icon: TrendingUp },
    { href: '/parent#devoirs', label: 'Résultats & Devoirs', icon: CheckCircle2 }
  ];

  const adminLinks = [
    { href: '/admin', label: 'Accueil', icon: LayoutDashboard },
    { href: '/admin/cibles-cognitives', label: 'Cibles Cognitives', icon: Brain },
    { href: '/admin/publications', label: 'Publications', icon: BookOpen },
    { href: '/admin/mis-en-avant', label: 'Mis en Avant', icon: Trophy },
    { href: '/admin/familles-pedagogiques', label: 'Familles Pédagogiques', icon: Search },
    { href: '/admin/generation-ia', label: 'Génération IA', icon: Sparkles },
    { href: '/admin/centre-ia', label: 'Centre IA', icon: ShieldCheck },
    { href: '/admin/utilisateurs', label: 'Utilisateurs', icon: Users },
    { href: '/admin/journal-audit', label: "Journal d'audit", icon: CheckCircle2 }
  ];

  const isAdminRoute = pathname.startsWith('/admin') || activeRole === 'admin';

  const getActiveLinks = () => {
    if (isAdminRoute) return adminLinks;
    switch (activeRole) {
      case 'teacher':
        return teacherLinks;
      case 'parent':
        return parentLinks;
      default:
        return studentLinks;
    }
  };

  const navLinks = getActiveLinks();

  const handleLogout = () => {
    logout();
    router.push('/');
  };

  return (
    <aside className="w-64 bg-white text-slate-800 min-h-[calc(100vh-4rem)] flex flex-col justify-between p-4 shrink-0 border-r border-slate-200">
      <div className="space-y-6">
        <div className="px-3 pt-2 flex items-center justify-between">
          <span className="text-[11px] font-extrabold uppercase tracking-widest text-slate-400">
            {isAdminRoute && 'Menu Administration'}
            {!isAdminRoute && activeRole === 'student' && 'Menu Élève'}
            {!isAdminRoute && activeRole === 'teacher' && 'Menu Enseignant'}
            {!isAdminRoute && activeRole === 'parent' && 'Menu Parent'}
          </span>
        </div>

        {/* Minimal Navigation Menu */}
        <nav className="space-y-1">
          {navLinks.map((item) => {
            const Icon = item.icon;
            const isActive = item.href === '/admin'
              ? pathname === '/admin'
              : pathname === item.href || pathname.startsWith(item.href + '/');

            return (
              <Link
                key={item.href}
                href={item.href}
                className={`flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-xs font-semibold transition-all ${
                  isActive
                    ? 'bg-emerald-600 text-white shadow-sm'
                    : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'
                }`}
              >
                <Icon className={`w-4 h-4 ${isActive ? 'text-white' : 'text-slate-400'}`} />
                <span>{item.label}</span>
              </Link>
            );
          })}
        </nav>
      </div>

      <div className="space-y-3 pt-4 border-t border-slate-100">
        {/* Minimal Senegalese RAG Status Banner */}
        <div className="p-3 rounded-2xl bg-emerald-50 border border-emerald-200/80 space-y-1">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-emerald-600 animate-pulse"></span>
            <span className="text-[11px] font-bold text-emerald-900 uppercase">
              RAG Maths Sénégal
            </span>
          </div>
          <p className="text-[10px] text-emerald-800 leading-tight">
            Génération conforme au programme officiel.
          </p>
        </div>

        {/* Logout / Login Button */}
        {isAuthenticated ? (
          <button
            onClick={handleLogout}
            className="w-full flex items-center justify-center gap-2 px-3 py-2.5 rounded-xl text-xs font-bold text-rose-600 hover:bg-rose-50 transition-colors border border-rose-100 cursor-pointer"
          >
            <LogOut className="w-4 h-4" />
            <span>Se déconnecter</span>
          </button>
        ) : (
          <button
            onClick={openLoginModal}
            className="w-full flex items-center justify-center gap-2 px-3 py-2.5 rounded-xl text-xs font-bold bg-emerald-600 hover:bg-emerald-700 text-white transition-colors cursor-pointer"
          >
            <User className="w-4 h-4" />
            <span>Se connecter</span>
          </button>
        )}
      </div>
    </aside>
  );
};
