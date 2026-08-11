import React, { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import DashboardView from './components/DashboardView';
import ResultView from './components/ResultView';
import ArchiveView from './components/ArchiveView';

export default function App() {
  const [activeTab, setActiveTab] = useState('asosiy'); // 'asosiy' | 'arxiv'
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
          ) : (
            <ArchiveView
              patients={patients}
              onSelectPatient={handleSelectPatient}
            />
          )}
        </main>
      </div>
    </div>
  );
}
