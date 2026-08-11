import React, { useState, useEffect, useRef } from 'react';

export default function ResultView({ patient, onApproveSuccess }) {
  const [opacity, setOpacity] = useState(80);
  const [heatmapVisible, setHeatmapVisible] = useState(true);
  const [activeSegmentTab, setActiveSegmentTab] = useState('simple'); // 'simple' | 'technical' | 'raw_scores'
  const [selectedDisease, setSelectedDisease] = useState(patient?.diagnosis || '');
  const [activeHeatmapUrl, setActiveHeatmapUrl] = useState(patient?.heatmap_image || '');
  const [loadingHeatmap, setLoadingHeatmap] = useState(false);
  const [chatMessages, setChatMessages] = useState([]);
  const [chatInput, setChatInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  
  const chatMessagesEndRef = useRef(null);

  useEffect(() => {
    if (patient) {
      setSelectedDisease(patient.diagnosis);
      setActiveHeatmapUrl(patient.heatmap_image);
      setChatMessages([
        {
          id: 1,
          sender: 'ai',
          name: 'SSV AI Yordamchi',
          text: `Tahlil yakunlandi! TorchXRayVision DenseNet-121 modeli orqali ${patient.diagnosis} (${patient.probability}%) aniqlanmoqda. Pastdagi ro'yxatdan boshqa patologiyalarni tanlab, Grad-CAM xaritasini o'zgartirishingiz mumkin.`
        }
      ]);
    }
  }, [patient]);

  if (!patient) return null;

  const handleSelectDisease = async (diseaseName) => {
    setSelectedDisease(diseaseName);
    setLoadingHeatmap(true);
    try {
      const res = await fetch(`/api/gradcam/${patient.id}/${encodeURIComponent(diseaseName)}`);
      if (res.ok) {
        const blob = await res.blob();
        const objectUrl = URL.createObjectURL(blob);
        setActiveHeatmapUrl(objectUrl);
        setHeatmapVisible(true);
      }
    } catch (e) {
      console.error("Grad-CAM xaritasini olishda xatolik:", e);
    } finally {
      setLoadingHeatmap(false);
    }
  };

  const handleApprove = async () => {
    try {
      const res = await fetch(`/api/approve/${patient.id}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ doctor_name: "Dr. A. Karimov" })
      });
      if (res.ok) {
        const updatedPatient = await res.json();
        onApproveSuccess(updatedPatient);
        alert("Hisobot muvaffaqiyatli elektron imzolandi va tizimda tasdiqlandi!");
      } else {
        alert("Tasdiqlashda xatolik yuzaga keldi.");
      }
    } catch(e) {
      alert("Hisobotni tasdiqlashda server xatosi.");
    }
  };

  const handleDownloadPdf = () => {
    window.location.href = `/api/pdf/${patient.id}`;
  };

  const handlePrint = () => {
    window.print();
  };

  const sendChatMessage = async (msgText) => {
    if (!msgText.trim()) return;

    const userMsg = {
      id: Date.now(),
      sender: 'doctor',
      name: 'Shifokor',
      text: msgText
    };

    setChatMessages((prev) => [...prev, userMsg]);
    setChatInput('');
    setIsTyping(true);
    setTimeout(scrollToBottom, 50);

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          message: msgText,
          diagnosis: patient.diagnosis,
          patient_id: patient.id
        })
      });

      setIsTyping(false);

      if (res.ok) {
        const data = await res.json();
        const aiMsg = {
          id: Date.now() + 1,
          sender: 'ai',
          name: 'SSV AI Yordamchi',
          text: data.message
        };
        setChatMessages((prev) => [...prev, aiMsg]);
        setTimeout(scrollToBottom, 50);
      }
    } catch(e) {
      setIsTyping(false);
      alert('Chatbot javob berishda xatolik yuz berdi.');
    }
  };

  const handleChatSubmit = (e) => {
    e.preventDefault();
    sendChatMessage(chatInput);
  };

  const scrollToBottom = () => {
    chatMessagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleImgError = (e) => {
    e.target.src = "https://lh3.googleusercontent.com/aida-public/AB6AXuDMcQ36_FVVhgPn67Es1UG6qy-D_zHw2_IlVjrF0vAtjCdjnJV4G9rJHka8kiIHMcJYHdWPVb2CY78O_KC32vF04-wGVZyC3Kj41CYsPetxqRBO52OzLWVPXFA5p-wEvYOn-cbV1bVb2Y4BtCf-1XpOULFJe_vI4hCwGO5jgkVOU7Q5nPTWgXw_OobYMyPh-MGtEw7ZO6Kid31-tQSoMtDHs1ve7Etjp1reCkxBkLRbFR_j-jTo9cryHg";
  };

  const isApproved = patient.status === 'Tasdiqlangan';
  const riskClass = patient.diagnosis === 'Norma'
    ? 'bg-success/10 border-success/30 text-success'
    : 'bg-error/10 border-error/30 text-error';

  const rawScores = patient.raw_scores || [];

  return (
    <div className="flex-1 flex flex-col gap-6">
      
      {/* 1. Dynamic Status & Demographic Banner */}
      <div className="bg-surface-container-lowest rounded-3xl p-6 shadow-sm border border-outline-variant/20 flex flex-col md:flex-row justify-between items-start md:items-center gap-4 relative overflow-hidden">
        {isApproved && (
          <div className="absolute top-0 left-0 right-0 py-1.5 px-6 bg-success/15 border-b border-success/30 flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-success"></span>
            <span className="text-[10px] font-bold text-success uppercase tracking-wider">
              Tasdiqlangan. Shifokor: {patient.approved_by || 'Dr. Karimov'} ({patient.approved_time || 'Bugun'})
            </span>
          </div>
        )}
        
        <div className={`flex items-center gap-4 ${isApproved ? 'pt-4 md:pt-0' : ''}`}>
          <div className="h-12 w-12 rounded-full bg-primary/10 flex items-center justify-center">
            <span className="material-symbols-outlined text-primary text-[28px] font-light">personal_injury</span>
          </div>
          <div className="flex flex-col">
            <h2 className="font-geist text-xl font-bold text-on-surface">Bemor: <span className="font-bold">{patient.name}</span></h2>
            <p className="text-[11px] text-on-surface-variant font-bold uppercase tracking-wider mt-1">
              ID: {patient.id} • {patient.age} Yosh • {patient.gender}
            </p>
          </div>
        </div>
        
        <div className="flex items-center gap-3">
          <div className={`px-4 py-2 rounded-full border ${riskClass}`}>
            <span className="text-xs font-bold flex items-center gap-2">
              <span className={`w-2 h-2 rounded-full ${patient.diagnosis === 'Norma' ? 'bg-success' : 'bg-error animate-pulse'}`}></span>
              <span>{patient.diagnosis}: {patient.probability}%</span>
            </span>
          </div>
          <div className="px-4 py-2 bg-surface-container-high rounded-full border border-outline-variant/30">
            <span className="text-xs font-semibold text-on-surface flex items-center gap-2">
              <span className="material-symbols-outlined text-[16px]">psychology</span> DenseNet-121 AI
            </span>
          </div>
        </div>
      </div>

      {/* 2. Visualizer and Side Chat Container */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 flex-1">
        
        {/* Left Columns: Visualizer and Findings */}
        <div className="lg:col-span-8 flex flex-col gap-6">
          
          {/* Overlapping Canvas Viewer */}
          <div className="bg-black rounded-3xl overflow-hidden relative shadow-xl border border-surface-container-high h-[500px] flex items-center justify-center group">
            {/* Base Image */}
            <img
              alt="Chest X-ray"
              className="w-full h-full object-contain"
              src={patient.original_image}
              onError={handleImgError}
            />
            {/* Heatmap Overlay */}
            <img
              alt="Heatmap Overlay"
              className="w-full h-full object-contain absolute z-20 pointer-events-none transition-opacity duration-300"
              src={activeHeatmapUrl}
              style={{ opacity: heatmapVisible ? opacity / 100 : 0 }}
              onError={handleImgError}
            />

            {loadingHeatmap && (
              <div className="absolute inset-0 bg-black/60 z-30 flex items-center justify-center backdrop-blur-xs">
                <div className="flex items-center gap-2 bg-surface px-4 py-2 rounded-full shadow-lg">
                  <span className="w-4 h-4 rounded-full border-2 border-primary border-t-transparent animate-spin"></span>
                  <span className="text-xs font-bold text-on-surface">Grad-CAM {selectedDisease} hisoblanmoqda...</span>
                </div>
              </div>
            )}

            {/* Float HUD Controls */}
            <div className="absolute bottom-6 left-6 right-6 z-30 flex flex-col sm:flex-row gap-4 items-center justify-between bg-surface/90 backdrop-blur-md rounded-2xl p-4 shadow-lg border border-outline-variant/30">
              <button
                onClick={() => setHeatmapVisible(!heatmapVisible)}
                className={`px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-2 shadow-sm cursor-pointer ${
                  heatmapVisible
                    ? 'bg-secondary text-white hover:bg-secondary/90'
                    : 'bg-surface border border-outline-variant text-on-surface hover:bg-surface-container'
                }`}
              >
                <span className="material-symbols-outlined text-[18px]">
                  {heatmapVisible ? 'visibility' : 'visibility_off'}
                </span>
                <span>
                  {heatmapVisible ? `Grad-CAM (${selectedDisease}) Yashirish` : `Grad-CAM (${selectedDisease}) Ko'rsatish`}
                </span>
              </button>
              
              <div className="flex items-center gap-4 flex-1 max-w-xs ml-auto w-full">
                <span className="text-[11px] font-bold text-on-surface uppercase tracking-wide whitespace-nowrap">Qatlam Shaffofligi</span>
                <input
                  className="w-full h-1.5 bg-outline-variant rounded-lg appearance-none cursor-pointer accent-secondary"
                  max="100"
                  min="0"
                  type="range"
                  value={opacity}
                  onChange={(e) => setOpacity(parseInt(e.target.value))}
                />
                <span className="text-xs font-bold text-secondary w-8 text-right">{opacity}%</span>
              </div>
            </div>

            {/* Gradient Legends */}
            <div className="absolute top-6 right-6 z-30 bg-surface/90 backdrop-blur-md rounded-xl p-3 shadow-lg border border-outline-variant/30">
              <div className="flex flex-col gap-1.5">
                <span className="text-[9px] uppercase font-bold text-on-surface-variant tracking-wider">AI Faollashuv ({selectedDisease})</span>
                <div className="w-28 h-2.5 bg-gradient-to-r from-blue-600 via-green-400 to-red-600 rounded-full"></div>
                <div className="flex justify-between text-[9px] font-bold text-on-surface">
                  <span>Past</span>
                  <span>Yuqori</span>
                </div>
              </div>
            </div>
          </div>

          {/* TorchXRayVision 18 Pathology Breakdown Grid */}
          <div className="bg-surface-container-lowest rounded-3xl p-6 shadow-sm border border-outline-variant/20 relative">
            <div className="flex items-center justify-between border-b border-surface-container-high pb-4 mb-4">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-primary/15 flex items-center justify-center text-primary">
                  <span className="material-symbols-outlined">analytics</span>
                </div>
                <div>
                  <h3 className="text-base font-bold text-on-surface">TorchXRayVision 18 ta Patologiya Tahlili</h3>
                  <p className="text-[11px] text-on-surface-variant font-medium">Boshqa patologiyani bosing va uning Grad-CAM xaritasini ko'ring</p>
                </div>
              </div>

              {/* Segmented Tab */}
              <div className="flex bg-surface-container-low p-1 rounded-xl border border-outline-variant/50">
                <button
                  onClick={() => setActiveSegmentTab('simple')}
                  className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all cursor-pointer ${
                    activeSegmentTab === 'simple'
                      ? 'bg-white shadow-sm text-primary'
                      : 'text-on-surface-variant hover:text-on-surface'
                  }`}
                >
                  Sodda Xulosa
                </button>
                <button
                  onClick={() => setActiveSegmentTab('raw_scores')}
                  className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all cursor-pointer ${
                    activeSegmentTab === 'raw_scores'
                      ? 'bg-white shadow-sm text-primary'
                      : 'text-on-surface-variant hover:text-on-surface'
                  }`}
                >
                  Raw Model Score'lar ({rawScores.length})
                </button>
                <button
                  onClick={() => setActiveSegmentTab('technical')}
                  className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all cursor-pointer ${
                    activeSegmentTab === 'technical'
                      ? 'bg-white shadow-sm text-primary'
                      : 'text-on-surface-variant hover:text-on-surface'
                  }`}
                >
                  Texnik Hisobot
                </button>
              </div>
            </div>

            {/* TAB CONTENT: Raw Scores Interactive Selector */}
            {activeSegmentTab === 'raw_scores' && (
              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
                {rawScores.map((item, idx) => {
                  const isSelected = selectedDisease === item.disease;
                  const pct = Math.min(Math.max(roundScore(item.score), 0), 100);
                  return (
                    <button
                      key={idx}
                      onClick={() => handleSelectDisease(item.disease)}
                      className={`p-3 rounded-2xl border text-left transition-all cursor-pointer flex flex-col gap-2 ${
                        isSelected
                          ? 'bg-primary/10 border-primary text-primary shadow-sm ring-2 ring-primary/20'
                          : 'bg-surface hover:bg-surface-container border-outline-variant/30 text-on-surface'
                      }`}
                    >
                      <div className="flex justify-between items-center w-full">
                        <span className="text-xs font-bold truncate">{item.disease}</span>
                        <span className="text-xs font-mono font-semibold">{item.score.toFixed(3)}</span>
                      </div>
                      <div className="w-full bg-outline-variant/30 h-1.5 rounded-full overflow-hidden">
                        <div
                          className={`h-full rounded-full ${isSelected ? 'bg-primary' : 'bg-secondary/70'}`}
                          style={{ width: `${Math.max(pct, 4)}%` }}
                        ></div>
                      </div>
                    </button>
                  );
                })}
              </div>
            )}

            {/* TAB CONTENT: Simple descriptions */}
            {activeSegmentTab === 'simple' && (
              <div className="space-y-4">
                <div className="p-4 bg-success/5 rounded-2xl border border-success/15">
                  <div className="flex gap-3">
                    <span className="material-symbols-outlined text-success mt-0.5">check_circle</span>
                    <div>
                      <h4 className="text-xs font-bold text-on-surface mb-1 font-geist">Xulosa</h4>
                      <p className="text-sm text-on-surface-variant leading-relaxed">
                        {patient.findings.summary}
                      </p>
                    </div>
                  </div>
                </div>

                <div className="p-4 bg-secondary/5 rounded-2xl border border-secondary/15">
                  <div className="flex gap-3">
                    <span className="material-symbols-outlined text-secondary mt-0.5">lightbulb</span>
                    <div>
                      <h4 className="text-xs font-bold text-on-surface mb-1 font-geist">Sodda tushuntirish</h4>
                      <p className="text-sm text-on-surface-variant leading-relaxed">
                        {patient.findings.simple_lang}
                      </p>
                    </div>
                  </div>
                </div>

                <div className="p-4 bg-primary/5 rounded-2xl border border-primary/15">
                  <div className="flex gap-3">
                    <span className="material-symbols-outlined text-primary mt-0.5">medical_services</span>
                    <div>
                      <h4 className="text-xs font-bold text-on-surface mb-1 font-geist">Tavsiyalar</h4>
                      <ul className="text-sm text-on-surface-variant space-y-1.5 mt-2">
                        {patient.findings.precautions.map((prec, idx) => (
                          <li key={idx} className="flex items-center gap-2">
                            <span className="w-1.5 h-1.5 rounded-full bg-primary/50"></span>
                            <span>{prec}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* TAB CONTENT: Technical reports */}
            {activeSegmentTab === 'technical' && (
              <div className="p-4 bg-surface rounded-2xl border border-outline-variant/30 leading-relaxed text-sm text-on-surface-variant">
                <p className="font-mono text-xs whitespace-pre-wrap">{patient.findings.technical}</p>
              </div>
            )}
          </div>
        </div>

        {/* Right Column: Chatbot box & Action approval drawers */}
        <div className="lg:col-span-4 flex flex-col gap-6">
          
          {/* Chatbox inside ResultView */}
          <div className="bg-surface-container-lowest rounded-[2rem] shadow-lg flex flex-col border border-primary/10 h-[480px] overflow-hidden">
            <div className="p-4 bg-primary text-white flex items-center gap-3">
              <div className="w-8 h-8 rounded-full bg-white/25 flex items-center justify-center">
                <span className="material-symbols-outlined text-[18px]">smart_toy</span>
              </div>
              <div className="flex flex-col">
                <span className="text-xs font-bold leading-tight">SSV AI Yordamchi</span>
                <span className="text-[9px] opacity-80 uppercase font-semibold">Tahlil asosida maslahat</span>
              </div>
            </div>

            {/* Messaging Thread */}
            <div className="flex-1 p-4 overflow-y-auto space-y-4 bg-surface-container-low/30 scrollbar-thin">
              {chatMessages.map((msg, idx) => (
                <div
                  key={idx}
                  className={`flex flex-col gap-1 max-w-[85%] ${
                    msg.sender === 'doctor' ? 'self-end items-end ml-auto' : 'items-start'
                  }`}
                >
                  <span className="text-[9px] text-on-surface-variant ml-2 font-semibold font-geist">
                    {msg.name || (msg.sender === 'doctor' ? 'Shifokor' : 'AI Yordamchi')}
                  </span>
                  <div
                    className={`p-3 rounded-2xl shadow-sm text-xs leading-relaxed ${
                      msg.sender === 'doctor'
                        ? 'bg-primary text-white rounded-tr-sm'
                        : 'bg-white text-on-surface rounded-tl-sm border border-outline-variant/30'
                    }`}
                  >
                    {msg.text}
                  </div>
                </div>
              ))}

              {isTyping && (
                <div className="flex flex-col gap-1 items-start max-w-[85%]">
                  <span className="text-[9px] text-on-surface-variant ml-2 font-semibold">SSV AI Yordamchi</span>
                  <div className="bg-white p-3 rounded-2xl rounded-tl-sm border border-outline-variant/30 shadow-sm flex items-center gap-1.5">
                    <span className="w-1.5 h-1.5 rounded-full bg-primary animate-bounce"></span>
                    <span className="w-1.5 h-1.5 rounded-full bg-primary animate-bounce" style={{ animationDelay: '0.2s' }}></span>
                    <span className="w-1.5 h-1.5 rounded-full bg-primary animate-bounce" style={{ animationDelay: '0.4s' }}></span>
                  </div>
                </div>
              )}

              <div ref={chatMessagesEndRef} />
            </div>

            {/* Chat Input */}
            <div className="p-3 bg-surface-container-low border-t border-outline-variant/30">
              <form onSubmit={handleChatSubmit} className="relative flex items-center gap-2">
                <div className="relative flex-1">
                  <input
                    value={chatInput}
                    onChange={(e) => setChatInput(e.target.value)}
                    className="w-full bg-white border border-outline-variant/40 rounded-full py-2.5 pl-4 pr-10 text-xs focus:outline-none focus:ring-1 focus:ring-primary/40 text-on-surface placeholder:text-on-surface-variant/45"
                    placeholder="Savol yozing..."
                    type="text"
                  />
                </div>
                <button
                  type="submit"
                  disabled={!chatInput.trim()}
                  className="w-9 h-9 bg-primary text-white rounded-full flex items-center justify-center shadow-md hover:bg-primary-container transition-all cursor-pointer"
                >
                  <span className="material-symbols-outlined text-[16px]">send</span>
                </button>
              </form>
            </div>
          </div>

          {/* Action Approval Drawer */}
          <div className="bg-surface-container-high rounded-[2rem] p-6 border border-outline-variant/50 shadow-inner flex flex-col gap-4">
            <div className="flex items-center gap-3">
              <span className="relative flex h-3.5 w-3.5">
                {!isApproved && <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[#eca52b] opacity-75"></span>}
                <span className={`relative inline-flex rounded-full h-3.5 w-3.5 ${isApproved ? 'bg-success' : 'bg-[#eca52b]'}`}></span>
              </span>
              <span className="text-xs font-bold text-on-surface">
                {isApproved ? 'Hujjat shifokor tomonidan tasdiqlangan' : "Shifokor Tasdig'i kutilmoqda"}
              </span>
            </div>

            {!isApproved ? (
              <button
                onClick={handleApprove}
                className="w-full py-4 bg-success hover:bg-success/90 text-white rounded-2xl text-sm font-bold transition-colors flex items-center justify-center gap-2 shadow-md cursor-pointer"
              >
                <span className="material-symbols-outlined">edit_document</span> Tasdiqlash va Elektron Imzolash
              </button>
            ) : (
              <div className="flex flex-col gap-3 mt-2 pt-4 border-t border-outline-variant/30">
                <button
                  onClick={handleDownloadPdf}
                  className="w-full bg-secondary text-white py-3.5 px-4 rounded-xl text-xs font-bold flex items-center justify-center gap-2 hover:bg-secondary/90 transition-colors shadow-sm cursor-pointer"
                >
                  <span className="material-symbols-outlined text-[18px]">picture_as_pdf</span> Rasmiy PDF Hisobotni yuklash
                </button>
                <button
                  onClick={handlePrint}
                  className="w-full bg-surface-container-lowest text-on-surface border border-outline-variant/40 py-2.5 px-4 rounded-xl text-xs font-bold flex items-center justify-center gap-2 hover:bg-surface-container-high transition-colors cursor-pointer"
                >
                  <span className="material-symbols-outlined text-[16px]">print</span> Hujjatni chop etish
                </button>
              </div>
            )}
          </div>

        </div>
      </div>
    </div>
  );
}

function roundScore(val) {
  if (typeof val !== 'number') return 0;
  return Math.round(val * 100);
}
