import React from 'react';
import { translations } from '../i18n';

export default function Header({ patientCount, onNewAnalysis, lang = 'uz', setLang }) {
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
        {/* Language Selector Switcher Pill */}
        <div className="flex items-center bg-surface-container-low p-1 rounded-full border border-outline-variant/40 shadow-xs">
          <button
            onClick={() => setLang && setLang('uz')}
            className={`px-3 py-1 rounded-full text-xs font-bold transition-all cursor-pointer ${
              lang === 'uz'
                ? 'bg-primary text-white shadow-sm'
                : 'text-on-surface-variant hover:text-on-surface'
            }`}
          >
            UZ 🇺🇿
          </button>
          <button
            onClick={() => setLang && setLang('ru')}
            className={`px-3 py-1 rounded-full text-xs font-bold transition-all cursor-pointer ${
              lang === 'ru'
                ? 'bg-primary text-white shadow-sm'
                : 'text-on-surface-variant hover:text-on-surface'
            }`}
          >
            RU 🇷🇺
          </button>
          <button
            onClick={() => setLang && setLang('en')}
            className={`px-3 py-1 rounded-full text-xs font-bold transition-all cursor-pointer ${
              lang === 'en'
                ? 'bg-primary text-white shadow-sm'
                : 'text-on-surface-variant hover:text-on-surface'
            }`}
          >
            EN 🇬🇧
          </button>
        </div>

        <button
          onClick={onNewAnalysis}
          className="px-5 py-2.5 bg-primary text-white rounded-full text-xs font-semibold flex items-center gap-2 hover:bg-primary-container transition-all shadow-md cursor-pointer"
        >
          <span className="material-symbols-outlined text-[18px]">upload_file</span> {t.nav_new_analysis}
        </button>
      </div>
    </header>
  );
}
