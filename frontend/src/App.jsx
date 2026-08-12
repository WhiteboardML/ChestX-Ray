import React, { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import DashboardView from './components/DashboardView';
import ResultView from './components/ResultView';
import ArchiveView from './components/ArchiveView';
import GuideView from './components/GuideView';
import PatientsView from './components/PatientsView';

export default function App() {
  const [activeTab, setActiveTab] = useState('asosiy'); // 'asosiy' | 'bemorlar' | 'arxiv' | 'yo\'riqnoma'
  const [currentPatient, setCurrentPatient] = useState(null);
  const [patients, setPatients] = useState([]);

  // Fetch patience history logs on startup
  const fetchHistory = async () => {
    try {
      const res = await fetch('/api/history');
      if (res.ok) {
        const data = await res.json();
        setPatients(data);
      }
    } catch (e) {
      console.error("Bemorlar tarixini yuklashda xatolik yuzaga keldi:", e);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, []);

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

  return (
    <div className="bg-surface font-sans text-on-surface flex min-h-screen">
      {/* Global Navigation Sidebar */}
      <Sidebar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        onNewAnalysis={handleNewAnalysis}
      />

      {/* Main App Frame */}
      <div className="flex-1 pl-[280px] min-h-screen flex flex-col">
        {/* Sticky Header */}
        <Header 
          patientCount={patients.length} 
          onNewAnalysis={handleNewAnalysis} 
        />

        {/* Body Router Content */}
        <main className="flex-1 mt-20 p-6 flex flex-col">
          {activeTab === 'asosiy' ? (
            currentPatient ? (
              <ResultView
                patient={currentPatient}
                onApproveSuccess={handleApproveSuccess}
              />
            ) : (
              <DashboardView 
                onUploadSuccess={handleUploadSuccess} 
              />
            )
          ) : activeTab === 'bemorlar' ? (
            <PatientsView
              patients={patients}
              onSelectPatient={handleSelectPatient}
              onRegisterNewPatient={handleRegisterNewPatient}
            />
          ) : activeTab === 'yo\'riqnoma' ? (
            <GuideView />
          ) : (
            <ArchiveView
              onSelectPatient={handleSelectPatient}
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
