'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { UserRole, GradeLevel } from '@/types';
import { useAuth } from '@/context/AuthContext';
import {
  Search,
  User,
  GraduationCap,
  BookOpen,
  ChevronDown,
  ShieldCheck,
  Users,
  Brain,
  Star,
  LogOut,
  LogIn,
  Check
} from 'lucide-react';

interface NavbarProps {
  currentRole: UserRole;
  onRoleChange: (role: UserRole) => void;
  selectedGrade: GradeLevel;
  onGradeChange: (grade: GradeLevel) => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  currentRole,
  onRoleChange,
  selectedGrade,
  onGradeChange
}) => {
  const router = useRouter();
  const { user, isAuthenticated, openLoginModal, logout } = useAuth();

  const [searchQuery, setSearchQuery] = useState('');
  const [showRoleDropdown, setShowRoleDropdown] = useState(false);
  const [showGradeDropdown, setShowGradeDropdown] = useState(false);
  const [showProfileDropdown, setShowProfileDropdown] = useState(false);

  const activeRole = user?.role || currentRole;
  const activeGrade = user?.grade || selectedGrade;

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      router.push(`/recherche?q=${encodeURIComponent(searchQuery.trim())}`);
    }
  };

  const rolesConfig: { id: UserRole; label: string; icon: any; color: string }[] = [
    { id: 'student', label: 'Espace Élève', icon: GraduationCap, color: 'text-emerald-600' },
    { id: 'teacher', label: 'Espace Enseignant', icon: BookOpen, color: 'text-amber-600' },
    { id: 'parent', label: 'Espace Parent', icon: Users, color: 'text-slate-600' },
    { id: 'admin', label: 'Administrateur', icon: ShieldCheck, color: 'text-slate-800' }
  ];

  const gradeLevels: GradeLevel[] = [
    '6ème',
    '5ème',
    '4ème',
    '3ème (BFEM)',
    'Seconde S',
    'Première S1/S2',
    'Terminale S1',
    'Terminale S2'
  ];

  const activeRoleObj = rolesConfig.find((r) => r.id === activeRole) || rolesConfig[0];

  const getInitials = (name?: string) => {
    if (!name) return 'SN';
    const parts = name.split(' ');
    if (parts.length >= 2) return `${parts[0][0]}${parts[1][0]}`.toUpperCase();
    return name.substring(0, 2).toUpperCase();
  };

  return (
    <header className="sticky top-0 z-40 bg-white border-b border-slate-200 shadow-2xs">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between gap-4">
        {/* Left: Brand Logo */}
        <div className="flex items-center gap-6 shrink-0">
          <Link href="/" className="flex items-center gap-3 group">
            <div className="w-10 h-10 rounded-xl bg-emerald-600 text-white flex items-center justify-center shadow-sm relative overflow-hidden group-hover:bg-emerald-700 transition-colors">
              <Brain className="w-5 h-5 text-white" />
              <Star className="w-2.5 h-2.5 text-amber-300 fill-amber-300 absolute top-1 right-1" />
            </div>
            <div>
              <div className="flex items-center gap-1.5">
                <span className="font-extrabold text-xl text-slate-900 tracking-tight">NURU</span>
                <span className="text-[10px] px-2 py-0.5 rounded-md font-extrabold bg-emerald-100 text-emerald-800 uppercase tracking-wider">
                  MATHS SÉNÉGAL
                </span>
              </div>
              <p className="text-[11px] text-slate-500 font-medium leading-none">Programme Officiel JS/BAC</p>
            </div>
          </Link>

          {/* Senegalese Grade Level Selector */}
          <div className="relative hidden md:block">
            <button
              onClick={() => setShowGradeDropdown(!showGradeDropdown)}
              className="flex items-center gap-1.5 text-xs font-semibold bg-slate-100 hover:bg-slate-200/80 text-slate-700 px-3 py-1.5 rounded-xl transition-colors border border-slate-200"
            >
              <span>{activeGrade}</span>
              <ChevronDown className="w-3.5 h-3.5 text-slate-500" />
            </button>

            {showGradeDropdown && (
              <div className="absolute top-full left-0 mt-1.5 w-48 bg-white rounded-2xl shadow-xl border border-slate-200 py-1.5 z-50 animate-in fade-in zoom-in-95">
                <div className="px-3 py-1.5 text-[11px] font-bold text-slate-400 uppercase tracking-wider">
                  Niveau Scolaire (Sénégal)
                </div>
                {gradeLevels.map((grade) => (
                  <button
                    key={grade}
                    onClick={() => {
                      onGradeChange(grade);
                      setShowGradeDropdown(false);
                    }}
                    className={`w-full text-left px-3.5 py-2 text-xs font-medium transition-colors flex items-center justify-between ${
                      activeGrade === grade
                        ? 'bg-emerald-50 text-emerald-800 font-bold'
                        : 'text-slate-700 hover:bg-slate-50'
                    }`}
                  >
                    {grade}
                    {grade.includes('S1') && (
                      <span className="text-[10px] bg-emerald-100 text-emerald-800 px-1.5 py-0.2 rounded font-bold">
                        BAC S1
                      </span>
                    )}
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Center: Search Bar */}
        <div className="flex-1 max-w-md mx-2 hidden sm:block">
          <form onSubmit={handleSearchSubmit} className="relative">
            <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Rechercher un chapitre ou une notion de maths..."
              className="w-full bg-slate-100 hover:bg-slate-200/60 focus:bg-white text-xs text-slate-800 pl-10 pr-4 py-2 rounded-xl border border-slate-200 focus:border-emerald-500 focus:ring-2 focus:ring-emerald-100 outline-none transition-all"
            />
          </form>
        </div>

        {/* Right: Role & Authentication Controls */}
        <div className="flex items-center gap-3 shrink-0">
          {isAuthenticated ? (
            <>
              {/* Role Switcher Pill */}
              <div className="relative">
                <button
                  onClick={() => setShowRoleDropdown(!showRoleDropdown)}
                  className="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-slate-900 text-white hover:bg-slate-800 transition-colors shadow-xs"
                >
                  <activeRoleObj.icon className={`w-4 h-4 ${activeRoleObj.color}`} />
                  <span className="text-xs font-semibold">{activeRoleObj.label}</span>
                  <ChevronDown className="w-3.5 h-3.5 text-slate-400" />
                </button>

                {showRoleDropdown && (
                  <div className="absolute top-full right-0 mt-1.5 w-56 bg-white rounded-2xl shadow-xl border border-slate-200 p-1.5 z-50 animate-in fade-in">
                    <div className="px-3 py-2 text-[11px] font-bold text-slate-400 uppercase border-b border-slate-100 mb-1">
                      Changer d'Espace & Rôle
                    </div>
                    {rolesConfig.map((role) => {
                      const Icon = role.icon;
                      const isCurrent = activeRole === role.id;
                      return (
                        <button
                          key={role.id}
                          onClick={() => {
                            onRoleChange(role.id);
                            setShowRoleDropdown(false);
                            if (role.id === 'teacher') router.push('/enseignant');
                            else if (role.id === 'parent') router.push('/parent');
                            else if (role.id === 'admin') router.push('/admin');
                            else router.push('/');
                          }}
                          className={`w-full text-left px-3 py-2.5 rounded-xl text-xs font-medium flex items-center justify-between ${
                            isCurrent
                              ? 'bg-emerald-50 text-emerald-800 font-bold border border-emerald-200'
                              : 'text-slate-700 hover:bg-slate-50'
                          }`}
                        >
                          <div className="flex items-center gap-2.5">
                            <Icon className={`w-4 h-4 ${role.color}`} />
                            <span>{role.label}</span>
                          </div>
                          {isCurrent && <Check className="w-3.5 h-3.5 text-emerald-600" />}
                        </button>
                      );
                    })}
                  </div>
                )}
              </div>

              {/* User Profile Badge & Dropdown */}
              <div className="relative">
                <button
                  onClick={() => setShowProfileDropdown(!showProfileDropdown)}
                  className="flex items-center gap-2 p-1 pr-2.5 rounded-full hover:bg-slate-100 transition-colors border border-slate-200"
                >
                  <div className="w-8 h-8 rounded-full bg-emerald-600 text-white font-bold text-xs flex items-center justify-center shadow-xs">
                    {getInitials(user?.name)}
                  </div>
                  <span className="text-xs font-extrabold text-slate-800 hidden md:inline">
                    {user?.name || 'Moussa Diop'}
                  </span>
                  <ChevronDown className="w-3.5 h-3.5 text-slate-400" />
                </button>

                {showProfileDropdown && (
                  <div className="absolute top-full right-0 mt-1.5 w-56 bg-white rounded-2xl shadow-xl border border-slate-200 p-2 z-50 animate-in fade-in">
                    <div className="p-3 bg-slate-50 rounded-xl space-y-0.5 mb-2 border border-slate-100">
                      <p className="text-xs font-extrabold text-slate-900">{user?.name}</p>
                      <p className="text-[11px] text-slate-500 font-medium truncate">{user?.email}</p>
                      <span className="inline-block mt-1 text-[10px] font-bold px-2 py-0.5 rounded bg-emerald-100 text-emerald-800 capitalize">
                        {user?.role === 'student' ? 'Élève (Sénégal)' : user?.role}
                      </span>
                    </div>

                    <button
                      onClick={() => {
                        setShowProfileDropdown(false);
                        logout();
                      }}
                      className="w-full flex items-center gap-2 px-3 py-2 rounded-xl text-xs font-bold text-rose-600 hover:bg-rose-50 transition-colors"
                    >
                      <LogOut className="w-4 h-4" />
                      <span>Se déconnecter</span>
                    </button>
                  </div>
                )}
              </div>
            </>
          ) : (
            <button
              onClick={openLoginModal}
              className="flex items-center gap-2 px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-extrabold text-xs transition-all shadow-sm cursor-pointer"
            >
              <LogIn className="w-4 h-4" />
              <span>Se connecter</span>
            </button>
          )}
        </div>
      </div>
    </header>
  );
};
