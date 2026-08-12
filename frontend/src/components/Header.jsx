import React from 'react';

export default function Header({ patientCount, onNewAnalysis }) {
  return (
    <header className="fixed top-0 left-[280px] right-0 h-20 bg-surface/80 backdrop-blur-xl z-40 px-6 flex items-center justify-end border-b border-surface-container-high">
      <button
        onClick={onNewAnalysis}
        className="px-5 py-2.5 bg-primary text-white rounded-full text-xs font-semibold flex items-center gap-2 hover:bg-primary-container transition-all shadow-md cursor-pointer"
      >
        <span className="material-symbols-outlined text-[18px]">upload_file</span> Yangi tahlil
      </button>
    </header>
  );
}
