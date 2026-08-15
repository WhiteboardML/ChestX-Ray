import React from 'react';
import { translations } from '../i18n';

export default function Sidebar({ activeTab, setActiveTab, onNewAnalysis, lang = 'uz' }) {
  const t = translations[lang] || translations.uz;

  return (
    <aside className="fixed left-0 top-0 h-full w-[280px] bg-surface-container shadow-[2px_0_12px_rgba(0,0,0,0.02)] z-50 flex flex-col pt-6 pb-8 transition-all">
      {/* Logo and Certification */}
      <div className="px-6 mb-10 flex flex-col gap-1">
        <div className="flex items-center gap-3">
          <img
            alt="AvicennaX AI Logo"
            className="h-10 w-auto object-contain"
            src="/logo-icon.png"
          />
          <span className="font-geist text-2xl font-bold text-primary tracking-tight">AvicennaX AI</span>
        </div>
      </div>

      {/* Links */}
      <nav className="flex-1 px-4 space-y-1">
        <button
          onClick={() => setActiveTab('asosiy')}
          className={`w-full flex items-center px-4 py-3 rounded-xl transition-all group font-semibold text-left ${
            activeTab === 'asosiy'
              ? 'bg-primary-container text-on-primary-container shadow-sm'
              : 'text-on-surface-variant hover:bg-surface-container-high hover:text-on-surface'
          }`}
        >
          <span className="material-symbols-outlined mr-4 group-hover:scale-110 transition-transform">dashboard</span>
          <span className="font-geist text-sm uppercase font-semibold">{t.nav_dashboard}</span>
        </button>

        <button
          onClick={() => setActiveTab('bemorlar')}
          className={`w-full flex items-center px-4 py-3 rounded-xl transition-all group font-semibold text-left ${
            activeTab === 'bemorlar'
              ? 'bg-primary-container text-on-primary-container shadow-sm'
              : 'text-on-surface-variant hover:bg-surface-container-high hover:text-on-surface'
          }`}
        >
          <span className="material-symbols-outlined mr-4 group-hover:scale-110 transition-transform">groups</span>
          <span className="font-geist text-sm uppercase font-semibold">{t.nav_patients}</span>
        </button>

        <button
          onClick={() => setActiveTab('arxiv')}
          className={`w-full flex items-center px-4 py-3 rounded-xl transition-all group font-semibold text-left ${
            activeTab === 'arxiv'
              ? 'bg-primary-container text-on-primary-container shadow-sm'
              : 'text-on-surface-variant hover:bg-surface-container-high hover:text-on-surface'
          }`}
        >
          <span className="material-symbols-outlined mr-4 group-hover:scale-110 transition-transform">folder_zip</span>
          <span className="font-geist text-sm uppercase font-semibold">{t.nav_archive}</span>
        </button>

        <button
          onClick={() => setActiveTab('statistika')}
          className={`w-full flex items-center px-4 py-3 rounded-xl transition-all group font-semibold text-left ${
            activeTab === 'statistika'
              ? 'bg-primary-container text-on-primary-container shadow-sm'
              : 'text-on-surface-variant hover:bg-surface-container-high hover:text-on-surface'
          }`}
        >
          <span className="material-symbols-outlined mr-4 group-hover:scale-110 transition-transform">monitoring</span>
          <span className="font-geist text-sm uppercase font-semibold">{t.nav_stats}</span>
        </button>

        <button
          onClick={() => setActiveTab('tariflar')}
          className={`w-full flex items-center px-4 py-3 rounded-xl transition-all group font-semibold text-left ${
            activeTab === 'tariflar'
              ? 'bg-primary-container text-on-primary-container shadow-sm'
              : 'text-on-surface-variant hover:bg-surface-container-high hover:text-on-surface'
          }`}
        >
          <span className="material-symbols-outlined mr-4 group-hover:scale-110 transition-transform">payments</span>
          <span className="font-geist text-sm uppercase font-semibold">{t.nav_pricing}</span>
        </button>

        <button
          onClick={() => setActiveTab('yo\'riqnoma')}
          className={`w-full flex items-center px-4 py-3 rounded-xl transition-all group font-semibold text-left ${
            activeTab === 'yo\'riqnoma'
              ? 'bg-primary-container text-on-primary-container shadow-sm'
              : 'text-on-surface-variant hover:bg-surface-container-high hover:text-on-surface'
          }`}
        >
          <span className="material-symbols-outlined mr-4 group-hover:scale-110 transition-transform">menu_book</span>
          <span className="font-geist text-sm uppercase font-semibold">{t.nav_analytics}</span>
        </button>
      </nav>

    
    </aside>
  );
}
