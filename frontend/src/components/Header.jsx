import React from 'react';
import { translations } from '../i18n';

export default function Header({ patientCount, onNewAnalysis, lang = 'uz', setLang, currentUser, onLogout }) {
  const t = translations[lang] || translations.uz;

  return (
    <header className="fixed top-0 left-[280px] right-0 h-20 bg-surface/80 backdrop-blur-xl z-40 px-6 flex items-center justify-between border-b border-surface-container-high">
      <div className="flex items-center gap-3">
        <span className="material-symbols-outlined text-primary text-[26px] font-light">local_hospital</span>
        <div className="flex flex-col">
          <span className="font-geist text-base font-bold text-on-surface">{t.dash_title}</span>
          <span className="text-[11px] text-on-surface-variant font-medium">{t.system_status}</span>
        </div>
      </div>

      <div className="flex items-center gap-4">
        {/* Language Selector */}
        <div className="flex items-center bg-surface-container-low p-1 rounded-full border border-outline-variant/40 shadow-xs">
          {['uz', 'ru', 'en'].map((l) => (
            <button
              key={l}
              onClick={() => setLang && setLang(l)}
              className={`px-3 py-1 rounded-full text-xs font-bold transition-all cursor-pointer ${
                lang === l
                  ? 'bg-primary text-white shadow-sm'
                  : 'text-on-surface-variant hover:text-on-surface'
              }`}
            >
              {l === 'uz' ? 'UZ 🇺🇿' : l === 'ru' ? 'RU 🇷🇺' : 'EN 🇬🇧'}
            </button>
          ))}
        </div>

        <button
          onClick={onNewAnalysis}
          className="px-5 py-2.5 bg-primary text-white rounded-full text-xs font-semibold flex items-center gap-2 hover:bg-primary-container transition-all shadow-md cursor-pointer"
        >
          <span className="material-symbols-outlined text-[18px]">upload_file</span>
          {t.nav_new_analysis}
        </button>

        {/* User info + logout */}
        {currentUser && (
          <div className="flex items-center gap-2 pl-2 border-l border-outline-variant/30">
            <div className="w-8 h-8 rounded-full bg-primary/15 flex items-center justify-center text-primary font-bold text-sm">
              {(currentUser.username || 'D').charAt(0).toUpperCase()}
            </div>
            <div className="flex flex-col">
              <span className="text-xs font-bold text-on-surface leading-tight">{currentUser.username}</span>
              <span className="text-[10px] text-on-surface-variant leading-tight">{currentUser.role}</span>
            </div>
            <button
              onClick={onLogout}
              title="Chiqish"
              className="w-8 h-8 rounded-full hover:bg-surface-container-high flex items-center justify-center text-on-surface-variant hover:text-error transition cursor-pointer"
            >
              <span className="material-symbols-outlined text-[18px]">logout</span>
            </button>
          </div>
        )}
      </div>
    </header>
  );
}
