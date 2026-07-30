'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/context/AuthContext';
import { UserRole } from '@/types';
import {
  Brain,
  Star,
  GraduationCap,
  BookOpen,
  Users,
  ShieldCheck,
  X,
  Lock,
  Mail,
  User,
  ArrowRight,
  AlertCircle,
  Link2,
  CheckCircle2
} from 'lucide-react';

export const AuthModal: React.FC = () => {
  const router = useRouter();
  const { isLoginModalOpen, closeLoginModal, login, register, isAuthenticated } = useAuth();

  const [mode, setMode] = useState<'login' | 'register'>('login');

  // Form states
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [selectedRole, setSelectedRole] = useState<UserRole>('student');
  const [linkedStudent, setLinkedStudent] = useState('');

  const [errorMsg, setErrorMsg] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  if (!isLoginModalOpen) return null;

  const handleLoginSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email.trim() || !password.trim()) {
      setErrorMsg('Veuillez renseigner votre adresse email et votre mot de passe.');
      return;
    }
    setErrorMsg('');
    setIsSubmitting(true);
    try {
      const loggedUser = await login(email.trim(), password);
      // Auto redirection depending on role
      if (loggedUser.role === 'admin') router.push('/admin');
      else if (loggedUser.role === 'teacher') router.push('/enseignant');
      else if (loggedUser.role === 'parent') router.push('/parent');
      else router.push('/');
    } catch (err: any) {
      setErrorMsg(err.message || 'Échec de connexion. Vérifiez vos identifiants.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleRegisterSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim() || !email.trim() || !password.trim()) {
      setErrorMsg('Veuillez remplir tous les champs obligatoires.');
      return;
    }
    if (selectedRole === ('admin' as any)) {
      setErrorMsg("La création de compte Administrateur est strictement interdite.");
      return;
    }
    setErrorMsg('');
    setIsSubmitting(true);
    try {
      const newUser = await register({
        name: name.trim(),
        email: email.trim(),
        password,
        role: selectedRole,
        linked_student_identifier: linkedStudent.trim() || undefined
      });

      if (newUser.role === 'teacher') router.push('/enseignant');
      else if (newUser.role === 'parent') router.push('/parent');
      else router.push('/');
    } catch (err: any) {
      setErrorMsg(err.message || 'Erreur lors de l’inscription.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const rolesPublic = [
    {
      id: 'student' as UserRole,
      label: 'Élève',
      desc: 'Accès aux cours, quiz & révisions IA',
      icon: GraduationCap,
      color: 'bg-emerald-50 text-emerald-700 border-emerald-300'
    },
    {
      id: 'teacher' as UserRole,
      label: 'Enseignant',
      desc: 'Suivi connecté des élèves & génération RAG',
      icon: BookOpen,
      color: 'bg-amber-50 text-amber-700 border-amber-300'
    },
    {
      id: 'parent' as UserRole,
      label: 'Parent',
      desc: 'Suivi dynamique en temps réel des enfants',
      icon: Users,
      color: 'bg-slate-100 text-slate-800 border-slate-300'
    }
  ];

  return (
    <div className="fixed inset-0 z-50 bg-slate-900/70 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-white rounded-3xl max-w-lg w-full p-6 sm:p-8 space-y-6 shadow-2xl border border-slate-200 animate-in zoom-in-95 duration-200 relative overflow-hidden">
        {/* Header */}
        <div className="flex items-start justify-between pb-4 border-b border-slate-100">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-2xl bg-emerald-600 text-white flex items-center justify-center shadow-md relative">
              <Brain className="w-6 h-6" />
              <Star className="w-3 h-3 text-amber-300 fill-amber-300 absolute top-1 right-1" />
            </div>
            <div>
              <h2 className="text-xl font-extrabold text-slate-900 tracking-tight">Plateforme NURU</h2>
              <p className="text-xs text-slate-500 font-medium">Authentification & Accès aux Espaces Métier</p>
            </div>
          </div>

          {isAuthenticated && (
            <button
              onClick={closeLoginModal}
              className="p-2 rounded-full hover:bg-slate-100 text-slate-400 hover:text-slate-600 transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          )}
        </div>

        {/* Tab Switcher: Login vs Register */}
        <div className="grid grid-cols-2 p-1 bg-slate-100 rounded-2xl border border-slate-200">
          <button
            type="button"
            onClick={() => {
              setMode('login');
              setErrorMsg('');
            }}
            className={`py-2.5 text-xs font-extrabold rounded-xl transition-all ${
              mode === 'login' ? 'bg-white text-slate-900 shadow-xs' : 'text-slate-500 hover:text-slate-800'
            }`}
          >
            Se connecter
          </button>
          <button
            type="button"
            onClick={() => {
              setMode('register');
              setErrorMsg('');
            }}
            className={`py-2.5 text-xs font-extrabold rounded-xl transition-all ${
              mode === 'register' ? 'bg-emerald-600 text-white shadow-xs' : 'text-slate-500 hover:text-slate-800'
            }`}
          >
            Créer un compte
          </button>
        </div>

        {errorMsg && (
          <div className="p-3.5 rounded-2xl bg-rose-50 border border-rose-200 text-rose-800 text-xs font-semibold flex items-center gap-2 animate-in fade-in">
            <AlertCircle className="w-4 h-4 shrink-0 text-rose-600" />
            <span>{errorMsg}</span>
          </div>
        )}

        {/* Mode LOGIN */}
        {mode === 'login' ? (
          <form onSubmit={handleLoginSubmit} className="space-y-4">
            <div className="space-y-3">
              <div>
                <label className="text-xs font-extrabold text-slate-700 block mb-1">Adresse Email</label>
                <div className="relative">
                  <Mail className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
                  <input
                    type="email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="votre.email@nuru.sn"
                    className="w-full bg-slate-50 border border-slate-200 rounded-xl pl-10 pr-4 py-2.5 text-xs text-slate-800 focus:bg-white focus:border-emerald-500 focus:ring-2 focus:ring-emerald-100 outline-none transition-all"
                  />
                </div>
              </div>

              <div>
                <label className="text-xs font-extrabold text-slate-700 block mb-1">Mot de passe</label>
                <div className="relative">
                  <Lock className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
                  <input
                    type="password"
                    required
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="••••••••"
                    className="w-full bg-slate-50 border border-slate-200 rounded-xl pl-10 pr-4 py-2.5 text-xs text-slate-800 focus:bg-white focus:border-emerald-500 focus:ring-2 focus:ring-emerald-100 outline-none transition-all"
                  />
                </div>
              </div>
            </div>

            <button
              type="submit"
              disabled={isSubmitting}
              className="w-full py-3 rounded-2xl bg-slate-900 hover:bg-slate-800 text-white font-extrabold text-xs flex items-center justify-center gap-2 shadow-md transition-colors cursor-pointer"
            >
              <Lock className="w-4 h-4" />
              <span>{isSubmitting ? 'Connexion en cours...' : 'Se connecter'}</span>
            </button>
          </form>
        ) : (
          /* Mode REGISTER */
          <form onSubmit={handleRegisterSubmit} className="space-y-4">
            {/* Choix du rôle public (Élève, Enseignant, Parent) */}
            <div className="space-y-2">
              <label className="text-xs font-extrabold text-slate-700 block">Choisissez votre Rôle Utilisateur</label>
              <div className="grid grid-cols-3 gap-2">
                {rolesPublic.map((r) => {
                  const Icon = r.icon;
                  const isSelected = selectedRole === r.id;
                  return (
                    <button
                      key={r.id}
                      type="button"
                      onClick={() => setSelectedRole(r.id)}
                      className={`p-3 rounded-2xl border text-center transition-all cursor-pointer flex flex-col items-center gap-1.5 ${
                        isSelected
                          ? 'border-emerald-600 bg-emerald-50 text-emerald-950 font-bold ring-2 ring-emerald-200'
                          : 'border-slate-200 bg-slate-50 text-slate-600 hover:bg-slate-100'
                      }`}
                    >
                      <Icon className={`w-5 h-5 ${isSelected ? 'text-emerald-600' : 'text-slate-400'}`} />
                      <span className="text-xs font-bold leading-tight">{r.label}</span>
                    </button>
                  );
                })}
              </div>
            </div>

            <div className="space-y-3">
              <div>
                <label className="text-xs font-extrabold text-slate-700 block mb-1">Nom Complet</label>
                <div className="relative">
                  <User className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
                  <input
                    type="text"
                    required
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder="Prénom et Nom"
                    className="w-full bg-slate-50 border border-slate-200 rounded-xl pl-10 pr-4 py-2 text-xs text-slate-800 focus:bg-white focus:border-emerald-500 outline-none"
                  />
                </div>
              </div>

              <div>
                <label className="text-xs font-extrabold text-slate-700 block mb-1">Adresse Email</label>
                <div className="relative">
                  <Mail className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
                  <input
                    type="email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="nom@nuru.sn"
                    className="w-full bg-slate-50 border border-slate-200 rounded-xl pl-10 pr-4 py-2 text-xs text-slate-800 focus:bg-white focus:border-emerald-500 outline-none"
                  />
                </div>
              </div>

              <div>
                <label className="text-xs font-extrabold text-slate-700 block mb-1">Mot de passe</label>
                <div className="relative">
                  <Lock className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
                  <input
                    type="password"
                    required
                    minLength={6}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="•••••••• (6+ caractères)"
                    className="w-full bg-slate-50 border border-slate-200 rounded-xl pl-10 pr-4 py-2 text-xs text-slate-800 focus:bg-white focus:border-emerald-500 outline-none"
                  />
                </div>
              </div>

              {/* Champ optionnel de liaison d'élève pour Parent et Enseignant */}
              {(selectedRole === 'parent' || selectedRole === 'teacher') && (
                <div className="p-3.5 rounded-2xl bg-emerald-50/70 border border-emerald-200 space-y-1.5">
                  <label className="text-xs font-extrabold text-emerald-950 flex items-center gap-1.5">
                    <Link2 className="w-4 h-4 text-emerald-600" />
                    <span>{selectedRole === 'parent' ? "Email ou ID de l'Élève à associer" : "Email ou ID de l'Élève (optionnel)"}</span>
                  </label>
                  <input
                    type="text"
                    value={linkedStudent}
                    onChange={(e) => setLinkedStudent(e.target.value)}
                    placeholder="ex: eleve.moussa@nuru.sn ou ID élève"
                    className="w-full bg-white border border-emerald-300 rounded-xl px-3 py-2 text-xs text-slate-800 focus:outline-none"
                  />
                  <p className="text-[10px] text-emerald-750">
                    Vous pourrez également lier des élèves à tout moment depuis votre tableau de bord.
                  </p>
                </div>
              )}
            </div>

            <button
              type="submit"
              disabled={isSubmitting}
              className="w-full py-3 rounded-2xl bg-emerald-600 hover:bg-emerald-700 text-white font-extrabold text-xs flex items-center justify-center gap-2 shadow-md transition-colors cursor-pointer"
            >
              <CheckCircle2 className="w-4 h-4" />
              <span>{isSubmitting ? 'Création en cours...' : 'Créer mon Compte'}</span>
            </button>
          </form>
        )}
      </div>
    </div>
  );
};
