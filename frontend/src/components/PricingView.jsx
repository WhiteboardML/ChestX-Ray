import React, { useState } from 'react';
import { translations } from '../i18n';

export default function PricingView({ currentUser, setCurrentUser, lang = 'uz' }) {
  const t = translations[lang] || translations.uz;
  const [selectedPlan, setSelectedPlan] = useState('saas'); // 'token' | 'saas' | 'university'
  const [showCheckoutModal, setShowCheckoutModal] = useState(false);
  const [activeSub, setActiveSub] = useState({
    planName: currentUser?.plan_name || "SaaS Obunasi",
    status: currentUser?.is_subscribed ? "Faol (Active)" : "To'lanmagan",
    scansLeft: currentUser?.is_subscribed ? "Cheksiz (Unlimited)" : "0 Token",
    expiresAt: "2026-09-12"
  });
  const [paymentMethod, setPaymentMethod] = useState('click');
  const [cardNumber, setCardNumber] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [paymentSuccess, setPaymentSuccess] = useState(false);

  const RECEIVING_CARD = "4916 9903 3783 3237";

  const handleSelectPlan = (planId) => {
    setSelectedPlan(planId);
    setShowCheckoutModal(true);
    setPaymentSuccess(false);
  };

  const handlePayment = async (e) => {
    e.preventDefault();
    setIsProcessing(true);

    try {
      const res = await fetch('/api/auth/subscribe', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: currentUser?.email || "dr.karimov@clinic.uz",
          plan_type: selectedPlan,
          card_number: RECEIVING_CARD
        })
      });

      setIsProcessing(false);

      if (res.ok) {
        const updatedUser = await res.json();
        if (setCurrentUser) setCurrentUser(updatedUser);
        setPaymentSuccess(true);
        setActiveSub({
          planName: updatedUser.plan_name,
          status: "Faol (Active) ✅",
          scansLeft: updatedUser.plan_name.includes("SaaS") ? "Cheksiz (Unlimited)" : `${updatedUser.scan_tokens} Token`,
          expiresAt: "2026-09-12"
        });
      } else {
        alert("To'lovni amalga oshirishda xatolik yuz berdi.");
      }
    } catch (err) {
      setIsProcessing(false);
      alert("Server bilan aloqada xatolik.");
    }
  };

  return (
    <div className="flex-1 flex flex-col gap-8 pb-12 max-w-7xl mx-auto w-full">
      {/* Top Title Section */}
      <div className="flex flex-col items-center text-center gap-3 pt-4">
        <span className="bg-primary/10 text-primary px-4 py-1.5 rounded-full text-xs font-bold uppercase tracking-widest border border-primary/20">
          TARIFLAR
        </span>
        <h1 className="text-3xl lg:text-4xl font-bold font-geist text-on-surface tracking-tight">
          To'lov rejalari va tariflar
        </h1>
        <p className="text-sm text-on-surface-variant max-w-2xl leading-relaxed">
          Klinikangiz yoki tadqiqot markazingiz uchun eng mos variantni tanlang. AI tahlillari bilan diagnostika aniqligini oshiring.
        </p>
      </div>

      {/* 3 Pricing Cards Container */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 lg:gap-8 items-stretch pt-4">
        
        {/* CARD 1: Token-based to'lov */}
        <div className="bg-surface-container-lowest rounded-3xl p-8 shadow-lg border border-outline-variant/30 flex flex-col justify-between hover:shadow-xl transition-all">
          <div>
            <div className="w-12 h-12 rounded-2xl bg-teal-50 flex items-center justify-center text-teal-600 mb-6 border border-teal-100">
              <span className="material-symbols-outlined text-[24px]">description</span>
            </div>

            <h3 className="text-xl font-bold font-geist text-on-surface mb-1">
              Token-based to'lov
            </h3>
            <p className="text-xs text-on-surface-variant mb-6">
              Kichik klinikalar, diagnostika markazlari
            </p>

            <div className="mb-6">
              <div className="flex items-baseline gap-1">
                <span className="text-3xl font-bold text-on-surface font-geist">2.000 UZS</span>
              </div>
              <span className="text-xs text-primary font-semibold block mt-1">
                1 oy bepul sinov davri
              </span>
            </div>

            {/* Features */}
            <ul className="space-y-3 text-xs text-on-surface mb-8 border-t border-outline-variant/20 pt-6">
              <li className="flex items-center gap-2.5">
                <span className="material-symbols-outlined text-teal-600 text-[18px]">check_circle</span>
                <span>AI – rentgen tahlili</span>
              </li>
              <li className="flex items-center gap-2.5">
                <span className="material-symbols-outlined text-teal-600 text-[18px]">check_circle</span>
                <span>Arxiv va bulutda saqlash</span>
              </li>
              <li className="flex items-center gap-2.5">
                <span className="material-symbols-outlined text-teal-600 text-[18px]">check_circle</span>
                <span>Bemor xulosasi</span>
              </li>
              <li className="flex items-center gap-2.5">
                <span className="material-symbols-outlined text-teal-600 text-[18px]">check_circle</span>
                <span>Muolajalar tavsiyasi</span>
              </li>
            </ul>
          </div>

          <button
            onClick={() => handleSelectPlan('token')}
            className="w-full py-3.5 px-6 rounded-2xl bg-surface-container-high hover:bg-surface-container-highest text-on-surface text-xs font-bold transition-all shadow-sm cursor-pointer"
          >
            Boshlash
          </button>
        </div>

        {/* CARD 2: SaaS obunasi (HIGHLIGHTED DARK BLUE) */}
        <div className="bg-[#1e3a8a] text-white rounded-3xl p-8 shadow-2xl flex flex-col justify-between relative transform hover:-translate-y-1 transition-all border border-blue-700/50">
          {/* Eng Ommabop Badge */}
          <div className="absolute top-6 right-6">
            <span className="bg-[#0d9488] text-white px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider shadow-sm">
              ENG OMMABOP
            </span>
          </div>

          <div>
            <div className="w-12 h-12 rounded-2xl bg-blue-600/40 flex items-center justify-center text-white mb-6 border border-blue-400/30">
              <span className="material-symbols-outlined text-[24px]">account_balance_wallet</span>
            </div>

            <h3 className="text-xl font-bold font-geist text-white mb-1">
              SaaS obunasi
            </h3>
            <p className="text-xs text-blue-200 mb-6">
              Klinikalar va shifoxona bo'limlari
            </p>

            <div className="mb-6">
              <div className="flex items-baseline gap-1">
                <span className="text-3xl font-bold text-white font-geist">1.000.000 UZS</span>
                <span className="text-xs text-blue-200">/oyiga</span>
              </div>
              <span className="text-xs text-blue-200 font-semibold block mt-1">
                Cheksiz (Unlimited) tahlillar
              </span>
            </div>

            {/* Features */}
            <ul className="space-y-3 text-xs text-blue-50 mb-8 border-t border-blue-700/60 pt-6">
              <li className="flex items-center gap-2.5">
                <span className="material-symbols-outlined text-teal-300 text-[18px]">check_circle</span>
                <span>Token-based to'lovning barchasi</span>
              </li>
              <li className="flex items-center gap-2.5">
                <span className="material-symbols-outlined text-teal-300 text-[18px]">check_circle</span>
                <span>Cheklovsiz oylik AI rentgen tahlillari</span>
              </li>
              <li className="flex items-center gap-2.5">
                <span className="material-symbols-outlined text-teal-300 text-[18px]">check_circle</span>
                <span>Kunlik, oylik, yillik analitika</span>
              </li>
              <li className="flex items-center gap-2.5">
                <span className="material-symbols-outlined text-teal-300 text-[18px]">check_circle</span>
                <span>Bemor kuzatish tizimi</span>
              </li>
              <li className="flex items-center gap-2.5">
                <span className="material-symbols-outlined text-teal-300 text-[18px]">check_circle</span>
                <span>Bemor uchun tushunarli analiz</span>
              </li>
              <li className="flex items-center gap-2.5">
                <span className="material-symbols-outlined text-teal-300 text-[18px]">check_circle</span>
                <span>Uzoq hududdagi bemorlar uchun diagnostik Telegram bot</span>
              </li>
            </ul>
          </div>

          <button
            onClick={() => handleSelectPlan('saas')}
            className="w-full py-3.5 px-6 rounded-2xl bg-white hover:bg-blue-50 text-[#1e3a8a] text-xs font-bold transition-all shadow-md cursor-pointer"
          >
            Hozir ulanish
          </button>
        </div>

        {/* CARD 3: Universitetlar va tadqiqot markazlari */}
        <div className="bg-surface-container-lowest rounded-3xl p-8 shadow-lg border border-outline-variant/30 flex flex-col justify-between hover:shadow-xl transition-all">
          <div>
            <div className="w-12 h-12 rounded-2xl bg-indigo-50 flex items-center justify-center text-indigo-600 mb-6 border border-indigo-100">
              <span className="material-symbols-outlined text-[24px]">hub</span>
            </div>

            <h3 className="text-xl font-bold font-geist text-on-surface mb-1">
              Universitetlar va tadqiqot markazlari
            </h3>
            <p className="text-xs text-on-surface-variant mb-6">
              Tarmoqlar · Universitetlar · Telemeditsina
            </p>

            <div className="mb-6">
              <div className="flex items-baseline gap-1">
                <span className="text-3xl font-bold text-on-surface font-geist">1.000 UZS</span>
              </div>
              <span className="text-xs text-primary font-semibold block mt-1">
                50% chegirmali litsenziya
              </span>
            </div>

            {/* Features */}
            <ul className="space-y-3 text-xs text-on-surface mb-8 border-t border-outline-variant/20 pt-6">
              <li className="flex items-center gap-2.5">
                <span className="material-symbols-outlined text-teal-600 text-[18px]">check_circle</span>
                <span>Alohida interface</span>
              </li>
              <li className="flex items-center gap-2.5">
                <span className="material-symbols-outlined text-teal-600 text-[18px]">check_circle</span>
                <span>Student-friendly muhit</span>
              </li>
              <li className="flex items-center gap-2.5">
                <span className="material-symbols-outlined text-teal-600 text-[18px]">check_circle</span>
                <span>Datasetlarni ishlatish huquqi</span>
              </li>
              <li className="flex items-center gap-2.5">
                <span className="material-symbols-outlined text-teal-600 text-[18px]">check_circle</span>
                <span>Klinikalar bilan kelishuvlar</span>
              </li>
              <li className="flex items-center gap-2.5">
                <span className="material-symbols-outlined text-teal-600 text-[18px]">check_circle</span>
                <span>50% arzon tokenlar</span>
              </li>
            </ul>
          </div>

          <button
            onClick={() => handleSelectPlan('university')}
            className="w-full py-3.5 px-6 rounded-2xl bg-white border border-outline-variant hover:bg-surface-container-high text-on-surface text-xs font-bold transition-all shadow-xs cursor-pointer"
          >
            Biz bilan bog'laning
          </button>
        </div>

      </div>

      {/* Bottom Dashboard: TO'LOV TIZIMI STATISTIKASI */}
      <div className="bg-surface-container-lowest rounded-3xl p-8 border border-outline-variant/30 shadow-md mt-6 flex flex-col gap-6">
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 border-b border-surface-container-high pb-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center text-primary">
              <span className="material-symbols-outlined">analytics</span>
            </div>
            <div>
              <span className="text-[10px] font-bold text-primary uppercase tracking-widest block">
                TO'LOV TIZIMI STATISTIKASI
              </span>
              <h2 className="text-lg font-bold text-on-surface font-geist">
                Joriy Obuna va Shifokor Hisob Balansi
              </h2>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <span className="text-xs font-bold px-3 py-1.5 rounded-full bg-success/10 text-success border border-success/20 flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-success animate-pulse"></span>
              {activeSub.status}
            </span>
          </div>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="p-4 bg-surface-container-low rounded-2xl border border-outline-variant/20 flex flex-col gap-1">
            <span className="text-[11px] text-on-surface-variant font-medium">Joriy Tarif Rejasi</span>
            <span className="text-base font-bold text-on-surface font-geist">{activeSub.planName}</span>
          </div>

          <div className="p-4 bg-surface-container-low rounded-2xl border border-outline-variant/20 flex flex-col gap-1">
            <span className="text-[11px] text-on-surface-variant font-medium">Qolgan Tahlil Balansi</span>
            <span className="text-base font-bold text-primary font-geist">{activeSub.scansLeft}</span>
          </div>

          <div className="p-4 bg-surface-container-low rounded-2xl border border-outline-variant/20 flex flex-col gap-1">
            <span className="text-[11px] text-on-surface-variant font-medium">Bajarilgan AI Tahlillar</span>
            <span className="text-base font-bold text-on-surface font-geist">1,420 Rentgenogramma</span>
          </div>

          <div className="p-4 bg-surface-container-low rounded-2xl border border-outline-variant/20 flex flex-col gap-1">
            <span className="text-[11px] text-on-surface-variant font-medium">Keyingi To'lov Sanasi</span>
            <span className="text-base font-bold text-on-surface font-geist">{activeSub.expiresAt}</span>
          </div>
        </div>
      </div>

      {/* CHECKOUT MODAL */}
      {showCheckoutModal && (
        <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-surface-container-lowest rounded-3xl p-6 shadow-2xl max-w-lg w-full border border-outline-variant/30 flex flex-col gap-5">
            
            <div className="flex items-center justify-between border-b border-surface-container-high pb-3">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center text-primary">
                  <span className="material-symbols-outlined">payments</span>
                </div>
                <div>
                  <h3 className="font-geist text-lg font-bold text-on-surface">To'lovni Amalga Oshirish</h3>
                  <p className="text-xs text-on-surface-variant">Klinika obunasini rasmiylashtirish</p>
                </div>
              </div>
              <button 
                onClick={() => setShowCheckoutModal(false)}
                className="w-8 h-8 rounded-full hover:bg-surface-container-high flex items-center justify-center text-on-surface-variant"
              >
                <span className="material-symbols-outlined text-[20px]">close</span>
              </button>
            </div>

            {paymentSuccess ? (
              <div className="py-8 flex flex-col items-center text-center gap-4">
                <div className="w-16 h-16 rounded-full bg-success/15 flex items-center justify-center text-success">
                  <span className="material-symbols-outlined text-[36px]">check_circle</span>
                </div>
                <h4 className="text-xl font-bold text-on-surface font-geist">To'lov Muvaffaqiyatli Bajarildi!</h4>
                <p className="text-xs text-on-surface-variant max-w-xs">
                  Sizning klinika obunangiz faollashtirildi. Cheksiz AI rentgen tahlillaridan foydalanishingiz mumkin.
                </p>
                <button
                  onClick={() => setShowCheckoutModal(false)}
                  className="mt-2 px-8 py-3 bg-primary text-white rounded-full text-xs font-bold shadow-md cursor-pointer"
                >
                  Tizimga qaytish
                </button>
              </div>
            ) : (
              <form onSubmit={handlePayment} className="flex flex-col gap-4">
                {/* Selected Plan Summary */}
                <div className="p-4 bg-surface-container-low rounded-2xl border border-outline-variant/30 flex items-center justify-between">
                  <div className="flex flex-col">
                    <span className="text-[11px] text-on-surface-variant font-semibold">Tanlangan tarif:</span>
                    <span className="text-sm font-bold text-on-surface uppercase">
                      {selectedPlan === 'saas' ? 'SaaS Obunasi' : selectedPlan === 'token' ? 'Token-based to\'lov' : 'Universitet Litsenziyasi'}
                    </span>
                  </div>
                  <span className="text-base font-bold text-primary font-geist">
                    {selectedPlan === 'saas' ? '1.000.000 UZS/oy' : selectedPlan === 'token' ? '2.000 UZS/scan' : '1.000 UZS/scan'}
                  </span>
                </div>

                {/* Receiver Card Info Banner */}
                <div className="p-3 bg-primary/10 border border-primary/20 rounded-2xl flex items-center justify-between">
                  <div className="flex items-center gap-2.5">
                    <span className="material-symbols-outlined text-primary text-[20px]">credit_card</span>
                    <div className="flex flex-col">
                      <span className="text-[10px] uppercase font-bold text-primary tracking-wider">Mablag' o'tkaziladigan rasmiy karta:</span>
                      <span className="text-sm font-extrabold text-on-surface tracking-wider font-geist">{RECEIVING_CARD}</span>
                    </div>
                  </div>
                  <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-primary text-white">Rasmiy</span>
                </div>

                {/* Payment Provider Selection */}
                <div className="flex flex-col gap-1.5">
                  <label className="text-xs font-bold text-on-surface-variant">To'lov Usulini Tanlang:</label>
                  <div className="grid grid-cols-3 gap-3">
                    <button
                      type="button"
                      onClick={() => setPaymentMethod('click')}
                      className={`p-3 rounded-2xl border text-xs font-bold flex flex-col items-center gap-1 transition-all ${
                        paymentMethod === 'click' ? 'bg-primary/10 border-primary text-primary' : 'bg-surface border-outline-variant/30'
                      }`}
                    >
                      <span className="material-symbols-outlined">touch_app</span>
                      <span>CLICK</span>
                    </button>

                    <button
                      type="button"
                      onClick={() => setPaymentMethod('payme')}
                      className={`p-3 rounded-2xl border text-xs font-bold flex flex-col items-center gap-1 transition-all ${
                        paymentMethod === 'payme' ? 'bg-primary/10 border-primary text-primary' : 'bg-surface border-outline-variant/30'
                      }`}
                    >
                      <span className="material-symbols-outlined">account_balance</span>
                      <span>Payme</span>
                    </button>

                    <button
                      type="button"
                      onClick={() => setPaymentMethod('card')}
                      className={`p-3 rounded-2xl border text-xs font-bold flex flex-col items-center gap-1 transition-all ${
                        paymentMethod === 'card' ? 'bg-primary/10 border-primary text-primary' : 'bg-surface border-outline-variant/30'
                      }`}
                    >
                      <span className="material-symbols-outlined">credit_card</span>
                      <span>Uzcard/Humos</span>
                    </button>
                  </div>
                </div>

                {/* Card Number Input */}
                <div className="flex flex-col gap-1">
                  <label className="text-xs font-bold text-on-surface-variant">Karta Raqami (8600 / 9860):</label>
                  <input
                    required
                    type="text"
                    value={cardNumber}
                    onChange={(e) => setCardNumber(e.target.value)}
                    placeholder="8600 0000 0000 0000"
                    className="w-full bg-surface border border-outline-variant/40 rounded-2xl p-3 text-xs focus:ring-2 focus:ring-primary/20 outline-none"
                  />
                </div>

                {/* Buttons */}
                <div className="flex items-center justify-end gap-3 pt-3 border-t border-surface-container-high">
                  <button
                    type="button"
                    onClick={() => setShowCheckoutModal(false)}
                    className="px-5 py-2.5 rounded-full text-xs font-semibold text-on-surface-variant hover:bg-surface-container-high"
                  >
                    Bekor qilish
                  </button>
                  <button
                    type="submit"
                    disabled={isProcessing}
                    className="px-6 py-2.5 rounded-full bg-primary text-white text-xs font-bold shadow-md hover:bg-primary-container disabled:opacity-50 flex items-center gap-2 cursor-pointer"
                  >
                    {isProcessing && <span className="w-3.5 h-3.5 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>}
                    <span>To'lovni Tasdiqlash</span>
                  </button>
                </div>
              </form>
            )}

          </div>
        </div>
      )}

    </div>
  );
}
