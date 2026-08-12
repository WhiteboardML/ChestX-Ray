import React, { useState } from 'react';
import { translations } from '../i18n';

export default function PricingView({ currentUser, lang = 'uz' }) {
  const t = translations[lang] || translations.uz;
  const [showContact, setShowContact] = useState(false);

  const plans = [
    {
      id: 'token',
      icon: 'description',
      iconBg: 'bg-teal-50 text-teal-600 border-teal-100',
      title: "Token-based to'lov",
      subtitle: "Kichik klinikalar, diagnostika markazlari",
      price: "2.000 UZS",
      priceNote: "1 oy bepul sinov davri",
      features: [
        "AI – rentgen tahlili",
        "Arxiv va bulutda saqlash",
        "Bemor xulosasi",
        "Muolajalar tavsiyasi",
      ],
      highlight: false,
      btnLabel: "Bog'lanish",
    },
    {
      id: 'saas',
      icon: 'account_balance_wallet',
      iconBg: 'bg-blue-600/40 text-white border-blue-400/30',
      title: "SaaS obunasi",
      subtitle: "Klinikalar va shifoxona bo'limlari",
      price: "1.000.000 UZS",
      priceNote: "Cheksiz (Unlimited) tahlillar",
      priceSuffix: "/oyiga",
      features: [
        "Token-based to'lovning barchasi",
        "Cheklovsiz oylik AI rentgen tahlillari",
        "Kunlik, oylik, yillik analitika",
        "Bemor kuzatish tizimi",
        "Bemor uchun tushunarli analiz",
        "Uzoq hududdagi bemorlar uchun Telegram bot",
      ],
      highlight: true,
      badge: "ENG OMMABOP",
      btnLabel: "Hozir ulanish",
    },
    {
      id: 'university',
      icon: 'hub',
      iconBg: 'bg-indigo-50 text-indigo-600 border-indigo-100',
      title: "Universitetlar va tadqiqot markazlari",
      subtitle: "Tarmoqlar · Universitetlar · Telemeditsina",
      price: "1.000 UZS",
      priceNote: "50% chegirmali litsenziya",
      features: [
        "Alohida interface",
        "Student-friendly muhit",
        "Datasetlarni ishlatish huquqi",
        "Klinikalar bilan kelishuvlar",
        "50% arzon tokenlar",
      ],
      highlight: false,
      btnLabel: "Biz bilan bog'laning",
    },
  ];

  return (
    <div className="flex-1 flex flex-col gap-8 pb-12 max-w-7xl mx-auto w-full">
      {/* Top Title */}
      <div className="flex flex-col items-center text-center gap-3 pt-4">
        <span className="bg-primary/10 text-primary px-4 py-1.5 rounded-full text-xs font-bold uppercase tracking-widest border border-primary/20">
          TARIFLAR
        </span>
        <h1 className="text-3xl lg:text-4xl font-bold font-geist text-on-surface tracking-tight">
          To'lov rejalari va tariflar
        </h1>
        <p className="text-sm text-on-surface-variant max-w-2xl leading-relaxed">
          Klinikangiz yoki tadqiqot markazingiz uchun eng mos variantni tanlang.
          AI tahlillari bilan diagnostika aniqligini oshiring.
        </p>

        {/* Coming Soon banner */}
        <div className="mt-2 flex items-center gap-2 bg-amber-500/10 border border-amber-400/30 text-amber-700 px-5 py-2.5 rounded-full text-xs font-semibold">
          <span className="material-symbols-outlined text-[16px]">schedule</span>
          To'lov tizimi tez orada ishga tushiriladi — bog'lanish uchun quyidagi tugmalarni bosing.
        </div>
      </div>

      {/* Pricing Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 lg:gap-8 items-stretch pt-4">
        {plans.map((plan) => (
          <div
            key={plan.id}
            className={`rounded-3xl p-8 shadow-lg flex flex-col justify-between transition-all relative ${
              plan.highlight
                ? 'bg-[#1e3a8a] text-white border border-blue-700/50 shadow-2xl transform hover:-translate-y-1'
                : 'bg-surface-container-lowest border border-outline-variant/30 hover:shadow-xl'
            }`}
          >
            {plan.badge && (
              <div className="absolute top-6 right-6">
                <span className="bg-[#0d9488] text-white px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider shadow-sm">
                  {plan.badge}
                </span>
              </div>
            )}

            <div>
              <div className={`w-12 h-12 rounded-2xl flex items-center justify-center mb-6 border ${plan.iconBg}`}>
                <span className="material-symbols-outlined text-[24px]">{plan.icon}</span>
              </div>

              <h3 className={`text-xl font-bold font-geist mb-1 ${plan.highlight ? 'text-white' : 'text-on-surface'}`}>
                {plan.title}
              </h3>
              <p className={`text-xs mb-6 ${plan.highlight ? 'text-blue-200' : 'text-on-surface-variant'}`}>
                {plan.subtitle}
              </p>

              <div className="mb-6">
                <div className="flex items-baseline gap-1">
                  <span className={`text-3xl font-bold font-geist ${plan.highlight ? 'text-white' : 'text-on-surface'}`}>
                    {plan.price}
                  </span>
                  {plan.priceSuffix && (
                    <span className="text-xs text-blue-200">{plan.priceSuffix}</span>
                  )}
                </div>
                <span className={`text-xs font-semibold block mt-1 ${plan.highlight ? 'text-blue-200' : 'text-primary'}`}>
                  {plan.priceNote}
                </span>
              </div>

              <ul className={`space-y-3 text-xs mb-8 border-t pt-6 ${
                plan.highlight ? 'text-blue-50 border-blue-700/60' : 'text-on-surface border-outline-variant/20'
              }`}>
                {plan.features.map((f) => (
                  <li key={f} className="flex items-center gap-2.5">
                    <span className={`material-symbols-outlined text-[18px] ${plan.highlight ? 'text-teal-300' : 'text-teal-600'}`}>check_circle</span>
                    <span>{f}</span>
                  </li>
                ))}
              </ul>
            </div>

            <button
              onClick={() => setShowContact(true)}
              className={`w-full py-3.5 px-6 rounded-2xl text-xs font-bold transition-all cursor-pointer ${
                plan.highlight
                  ? 'bg-white hover:bg-blue-50 text-[#1e3a8a] shadow-md'
                  : 'bg-surface-container-high hover:bg-surface-container-highest text-on-surface shadow-sm'
              }`}
            >
              {plan.btnLabel}
            </button>
          </div>
        ))}
      </div>

      {/* Current Subscription Status */}
      <div className="bg-surface-container-lowest rounded-3xl p-8 border border-outline-variant/30 shadow-md flex flex-col gap-6">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center text-primary">
            <span className="material-symbols-outlined">analytics</span>
          </div>
          <div>
            <span className="text-[10px] font-bold text-primary uppercase tracking-widest block">JORIY HOLAT</span>
            <h2 className="text-lg font-bold text-on-surface font-geist">Shifokor Hisob Holati</h2>
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div className="p-4 bg-surface-container-low rounded-2xl border border-outline-variant/20 flex flex-col gap-1">
            <span className="text-[11px] text-on-surface-variant font-medium">Foydalanuvchi</span>
            <span className="text-base font-bold text-on-surface font-geist">{currentUser?.username || '—'}</span>
          </div>
          <div className="p-4 bg-surface-container-low rounded-2xl border border-outline-variant/20 flex flex-col gap-1">
            <span className="text-[11px] text-on-surface-variant font-medium">Lavozim</span>
            <span className="text-base font-bold text-on-surface font-geist">{currentUser?.role || 'Doctor'}</span>
          </div>
          <div className="p-4 bg-surface-container-low rounded-2xl border border-outline-variant/20 flex flex-col gap-1">
            <span className="text-[11px] text-on-surface-variant font-medium">Holat</span>
            <span className="text-base font-bold text-success font-geist flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-success animate-pulse" />
              Faol (Cheksiz)
            </span>
          </div>
        </div>
      </div>

      {/* Contact Modal */}
      {showContact && (
        <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-surface-container-lowest rounded-3xl p-8 shadow-2xl max-w-md w-full border border-outline-variant/30 flex flex-col items-center text-center gap-5">
            <div className="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center text-primary">
              <span className="material-symbols-outlined text-[36px]">schedule_send</span>
            </div>
            <h3 className="text-xl font-bold font-geist text-on-surface">Tez orada!</h3>
            <p className="text-sm text-on-surface-variant leading-relaxed">
              To'lov tizimi hozirda ishlab chiqilmoqda. Obuna uchun bizga murojaat qiling:
            </p>
            <div className="flex flex-col gap-2 w-full">
              <a
                href="mailto:avicennaai@clinic.uz"
                className="flex items-center justify-center gap-2 px-5 py-3 bg-primary text-white rounded-2xl text-sm font-bold hover:bg-primary-container transition"
              >
                <span className="material-symbols-outlined text-[18px]">email</span>
                avicennaai@clinic.uz
              </a>
              <a
                href="https://t.me/avicennaai"
                target="_blank"
                rel="noreferrer"
                className="flex items-center justify-center gap-2 px-5 py-3 bg-surface-container-high text-on-surface rounded-2xl text-sm font-bold hover:bg-surface-container-highest transition"
              >
                <span className="material-symbols-outlined text-[18px]">send</span>
                Telegram: @avicennaai
              </a>
            </div>
            <button
              onClick={() => setShowContact(false)}
              className="text-xs text-on-surface-variant hover:text-on-surface transition cursor-pointer"
            >
              Yopish
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
