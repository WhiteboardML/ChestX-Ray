import React from 'react';

export default function GuideView() {
  const steps = [
    {
      num: '01',
      icon: 'cloud_upload',
      title: 'Rentgenogrammani Yuklash',
      description: "Bemor ko'krak qafasi tasvirini (PNG, JPG yoki DICOM formatida) ishchi panelga joylashtiring. Tizim avtomatik ravishda ma'lumotlarni o'qiydi.",
      detail: "Ish rejimini boshlash uchun kompyuterdan fayl tanlash tugmasini bosing yoki faylni sudrab 'Drag and Drop' zonaga tashlang."
    },
    {
      num: '02',
      icon: 'layers',
      title: "AI Tahlili va Grad-CAM Xaritasi",
      description: "Sun'iy intellektingiz tasvirdan o'pka segmentatsiyasi va patologiyani (Pnevmoniya, Tuberkuloz yoki Norma) % ehtimoli bilan aniqlaydi.",
      detail: "Grad-CAM faollashuv xaritasi patologiya zonalarini issiqlik ranglarida ko'rsatadi. Qatlam shaffofligini o'zingizga moslab boshqara olasiz."
    },
    {
      num: '03',
      icon: 'smart_toy',
      title: "Klinik Chatbot va Chuqur Maslahatlar",
      description: "Tahlil tugagandan so'ng, bemordagi isitma, yo'tal, balg'am, nafas qisishi yoki boshqa muammolarni botga yozib chuqur differential tahlil oling.",
      detail: "Chatbot SSV bayonnomalari va dori ko'rsatkichlariga ko'ra o'pka tashxisi bilan uyg'unlashgan aniq davolash maslahatlarini taqdim qiladi."
    },
    {
      num: '04',
      icon: 'assignment_turned_in',
      title: "Tasdiqlash va PDF Chop Etish",
      description: "Natijalar shifokor nazoratidan o'tgach, 'Tasdiqlash va Elektron Imzolash' orqali hujjat rasmiylashtiriladi.",
      detail: "Tasdiqlangan hisobot ostida davolash choralari va elektron imzo shakllanadi. Tayyor PDF varag'ini bevosita yuklash va chop etish mumkin."
    }
  ];

  return (
    <div className="flex-1 flex flex-col gap-6">
      {/* Page Header */}
      <div className="flex items-center justify-between bg-surface-container-low px-8 py-4 rounded-3xl relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-r from-primary/5 to-transparent pointer-events-none"></div>
        <div className="flex items-center gap-4 relative z-10">
          <span className="material-symbols-outlined text-primary text-[32px] font-light">menu_book</span>
          <div className="flex flex-col">
            <span className="font-geist text-xl font-bold text-on-surface">Platformadan foydalanish yo'riqnomasi</span>
            <span className="text-xs text-on-surface-variant font-medium">MedX AI diagnostika tizimi bilan ishlash bo'yicha to'liq qo'llanma</span>
          </div>
        </div>
      </div>

      {/* Guide Steps Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 flex-1">
        {steps.map((step, idx) => (
          <div key={idx} className="bg-surface-container-lowest rounded-[2rem] p-6 border border-outline-variant/20 shadow-sm flex flex-col gap-4 hover:border-primary/20 hover:shadow-md transition-all group relative overflow-hidden">
            <div className="absolute -top-4 -right-4 text-primary/5 text-9xl font-extrabold select-none font-geist group-hover:text-primary/10 transition-colors">
              {step.num}
            </div>
            
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-2xl bg-primary/10 text-primary flex items-center justify-center group-hover:scale-110 transition-transform">
                <span className="material-symbols-outlined text-[24px]">{step.icon}</span>
              </div>
              <h3 className="font-geist text-base font-bold text-on-surface">{step.title}</h3>
            </div>
            
            <p className="text-sm text-on-surface-variant leading-relaxed">
              {step.description}
            </p>
            
            <div className="mt-auto pt-4 border-t border-outline-variant/10 text-xs text-on-surface/70 leading-relaxed font-medium bg-surface-container-low/40 p-3.5 rounded-xl">
              {step.detail}
            </div>
          </div>
        ))}
      </div>

      {/* Health Standard Info Card */}
      <div className="bg-surface-container-high rounded-3xl p-6 border border-outline-variant/40 flex flex-col sm:flex-row gap-4 items-center justify-between">
        <div className="flex items-center gap-3">
          <span className="material-symbols-outlined text-primary text-[28px]">shield</span>
          <div className="flex flex-col">
            <span className="text-xs font-bold text-on-surface">HIPAA va ISO 27001 Axborot Xavfsizligi standarti</span>
            <span className="text-[11px] text-on-surface-variant">Barcha bemor rasmlari va shaxsiy ma'lumotlar uzatish va saqlash vaqtida to'liq shifrlangan.</span>
          </div>
        </div>
        <div className="px-4 py-2 bg-success/10 text-success rounded-full border border-success/20 text-xs font-bold flex items-center gap-1.5 whitespace-nowrap">
          <span className="w-1.5 h-1.5 rounded-full bg-success"></span>
          Xavfsiz ulanish
        </div>
      </div>
    </div>
  );
}
