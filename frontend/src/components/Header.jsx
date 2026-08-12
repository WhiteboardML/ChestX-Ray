import React from 'react';

export default function Header({ patientCount, onNewAnalysis }) {
  return (
    <header className="fixed top-0 left-[280px] right-0 h-20 bg-surface/80 backdrop-blur-xl z-40 px-6 flex items-center justify-between border-b border-surface-container-high">
      <div className="flex items-center gap-3">
        <span className="material-symbols-outlined text-primary text-[26px] font-light">local_hospital</span>
        <div className="flex flex-col">
          <span className="font-geist text-base font-bold text-on-surface">Asosiy ish paneli</span>
          <span className="text-[11px] text-on-surface-variant font-medium">Yangi rentgenogramma va patologiyani aniqlash tizimi</span>
        </div>
      </div>

      <button
        onClick={onNewAnalysis}
        className="px-5 py-2.5 bg-primary text-white rounded-full text-xs font-semibold flex items-center gap-2 hover:bg-primary-container transition-all shadow-md cursor-pointer"
      >
        <span className="material-symbols-outlined text-[18px]">upload_file</span> Yangi tahlil
      </button>
    </header>
  );
}
