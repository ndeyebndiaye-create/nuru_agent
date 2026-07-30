'use client';

import React, { useState } from 'react';
import { UserRole, GradeLevel, Subject } from '@/types';
import { AuthProvider } from '@/context/AuthContext';
import { AuthModal } from '@/components/auth/AuthModal';
import { Navbar } from '@/components/layout/Navbar';
import { Sidebar } from '@/components/layout/Sidebar';
import { NuruAssistantDrawer } from '@/components/ai/NuruAssistantDrawer';
import { SubjectPlaceholderModal } from '@/components/ui/SubjectPlaceholderModal';
import './globals.css';

export default function RootLayout({ children }: { children: React.ReactNode }) {
  const [currentRole, setCurrentRole] = useState<UserRole>('student');
  const [selectedGrade, setSelectedGrade] = useState<GradeLevel>('Terminale S1');
  const [activePlaceholderSubject, setActivePlaceholderSubject] = useState<Subject | null>(null);

  return (
    <html lang="fr" className="h-full">
      <head>
        <title>NURU - Plateforme Éducative IA Mathématiques</title>
        <meta name="description" content="NURU est une plateforme éducative d'apprentissage des mathématiques alimentée par RAG et l'IA, inspirée de Kartable." />
      </head>
      <body className="h-full flex flex-col bg-slate-50 text-slate-900">
        <AuthProvider>
          <Navbar
            currentRole={currentRole}
            onRoleChange={setCurrentRole}
            selectedGrade={selectedGrade}
            onGradeChange={setSelectedGrade}
          />

          <div className="flex-1 flex overflow-hidden">
            <Sidebar currentRole={currentRole} />

            <main className="flex-1 overflow-y-auto p-4 sm:p-6 lg:p-8">
              {children}
            </main>
          </div>

          {/* Authentication & Login Modal */}
          <AuthModal />

          {/* Global AI Assistant Floating Drawer */}
          <NuruAssistantDrawer />

          {/* Subject Placeholder Modal */}
          <SubjectPlaceholderModal
            subject={activePlaceholderSubject}
            onClose={() => setActivePlaceholderSubject(null)}
          />
        </AuthProvider>
      </body>
    </html>
  );
}
