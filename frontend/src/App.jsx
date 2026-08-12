import React, { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import DashboardView from './components/DashboardView';
import ResultView from './components/ResultView';
import ArchiveView from './components/ArchiveView';
import GuideView from './components/GuideView';
import PatientsView from './components/PatientsView';
import PricingView from './components/PricingView';
import LoginView from './components/LoginView';

export default function App() {
  const [activeTab, setActiveTab] = useState('asosiy');
  const [currentPatient, setCurrentPatient] = useState(null);
  const [patients, setPatients] = useState([]);
  const [lang, setLang] = useState('uz');
  const [currentUser, setCurrentUser] = useState(null);
  const [authReady, setAuthReady] = useState(false); // prevents flash

  // Restore session from sessionStorage on mount
  useEffect(() => {
    const savedEmail = sessionStorage.getItem('avicenna_user_email');
    if (savedEmail) {
      fetch(`/api/auth/me?email=${encodeURIComponent(savedEmail)}`)
        .then((res) => (res.ok ? res.json() : null))
        .then((userData) => {
          if (userData) setCurrentUser(userData);
          setAuthReady(true);
        })
        .catch(() => setAuthReady(true));
    } else {
      setAuthReady(true);
    }
  }, []);

  // Fetch patient history when user is logged in
  useEffect(() => {
    if (currentUser) fetchHistory();
  }, [currentUser]);

  const fetchHistory = async () => {
    try {
      const res = await fetch('/api/history');
      if (res.ok) {
        const data = await res.json();
        setPatients(data);
      }
    } catch (e) {
      console.error('Bemorlar tarixini yuklashda xatolik:', e);
    }
  };

  const handleLoginSuccess = (user) => {
    setCurrentUser(user);
  };

  const handleLogout = () => {
    sessionStorage.removeItem('avicenna_user_email');
    setCurrentUser(null);
    setCurrentPatient(null);
    setPatients([]);
    setActiveTab('asosiy');
  };

  const handleUploadSuccess = (patient) => {
    setCurrentPatient(patient);
    setPatients((prev) => [patient, ...prev]);
    setActiveTab('asosiy');
  };

  const handleSelectPatient = (patient) => {
    setCurrentPatient(patient);
    setActiveTab('asosiy');
  };

  const handleApproveSuccess = (updatedPatient) => {
    setCurrentPatient(updatedPatient);
    setPatients((prev) =>
      prev.map((pat) => (pat.id === updatedPatient.id ? updatedPatient : pat))
    );
  };

  const handleNewAnalysis = () => {
    setCurrentPatient(null);
    setActiveTab('asosiy');
  };

  const handleRegisterNewPatient = (newPatient) => {
    setPatients((prev) => [newPatient, ...prev]);
  };

  // Prevent flash while restoring session
  if (!authReady) {
    return (
      <div className="min-h-screen bg-[#0f172a] flex items-center justify-center">
        <span className="w-8 h-8 border-4 border-teal-400/30 border-t-teal-400 rounded-full animate-spin" />
      </div>
    );
  }

  // If not logged in — show auth screen
  if (!currentUser) {
    return <LoginView onLoginSuccess={handleLoginSuccess} />;
  }

  return (
    <div className="bg-surface font-sans text-on-surface flex min-h-screen">
      {/* Global Navigation Sidebar */}
      <Sidebar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        onNewAnalysis={handleNewAnalysis}
        lang={lang}
      />

      {/* Main App Frame */}
      <div className="flex-1 pl-[280px] min-h-screen flex flex-col">
        {/* Sticky Header */}
        <Header
          patientCount={patients.length}
          onNewAnalysis={handleNewAnalysis}
          lang={lang}
          setLang={setLang}
          currentUser={currentUser}
          onLogout={handleLogout}
        />

        {/* Body Router Content */}
        <main className="flex-1 mt-20 p-6 flex flex-col">
          {activeTab === 'asosiy' ? (
            currentPatient ? (
              <ResultView
                patient={currentPatient}
                onApproveSuccess={handleApproveSuccess}
                lang={lang}
              />
            ) : (
              <DashboardView
                onUploadSuccess={handleUploadSuccess}
                currentUser={currentUser}
                lang={lang}
              />
            )
          ) : activeTab === 'bemorlar' ? (
            <PatientsView
              patients={patients}
              onSelectPatient={handleSelectPatient}
              onRegisterNewPatient={handleRegisterNewPatient}
              lang={lang}
            />
          ) : activeTab === 'tariflar' ? (
            <PricingView
              currentUser={currentUser}
              setCurrentUser={setCurrentUser}
              lang={lang}
            />
          ) : activeTab === "yo'riqnoma" ? (
            <GuideView lang={lang} />
          ) : (
            <ArchiveView
              onSelectPatient={handleSelectPatient}
              lang={lang}
            />
          )}
        </main>

        {/* Safety Standard Footer */}
        <footer className="w-full bg-surface-container-low py-6 px-6 border-t border-outline-variant/20 mt-auto">
          <div className="flex items-center justify-center opacity-75">
            <span className="text-[11px] text-on-surface-variant font-medium text-center">
              © 2026 AvicennaX AI - Chest X-ray Diagnostic System. Barcha huquqlar himoyalangan.
            </span>
          </div>
        </footer>
      </div>
    </div>
  );
}
