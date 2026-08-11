import React from 'react';

export default function Header({ patientCount, onNewAnalysis }) {
  return (
    <header className="fixed top-0 left-[280px] right-0 h-20 bg-surface/80 backdrop-blur-xl z-40 px-6 flex items-center justify-between border-b border-surface-container-high">
      <div className="flex items-center gap-8">
        <div className="flex flex-col">
          <span className="text-[11px] text-on-surface-variant font-semibold uppercase tracking-wider">Tizim holati</span>
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-success animate-pulse"></span>
            <span className="text-sm font-semibold text-on-surface">AI Tahlil Faol</span>
          </div>
        </div>
        <div className="h-8 w-[1px] bg-outline-variant/50"></div>
        <div className="flex gap-6">
          <div className="flex flex-col">
            <span className="text-[11px] text-on-surface-variant uppercase font-semibold">Tahlillar yuklangan</span>
            <span className="text-lg font-bold text-primary leading-none">
              {patientCount !== null ? `${patientCount} tahlil` : '...'}
            </span>
          </div>
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
