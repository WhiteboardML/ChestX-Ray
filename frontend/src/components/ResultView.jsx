import React, { useState, useEffect, useRef } from 'react';

const diseaseUzMap = {
  "Atelectasis": "Atelektaz",
  "Consolidation": "Konsolidatsiya",
  "Infiltration": "Infiltratsiya",
  "Pneumothorax": "Pnevmotoraks",
  "Edema": "O'pka shishi",
  "Emphysema": "Emfizema",
  "Fibrosis": "Fibroz",
  "Effusion": "Plevral efuziya",
  "Pneumonia": "Pnevmoniya",
  "Pleural_Thickening": "Plevra qalinlashishi",
  "Cardiomegaly": "Kardiomegaliya",
  "Nodule": "O'pka tugunlari",
  "Mass": "Hajmli hosila",
  "Hernia": "Churra",
  "Lung Lesion": "O'pka zararlanishi",
  "Fracture": "Qovurg'a sinishi",
  "Lung Opacity": "O'pka xiralashishi",
  "Enlarged Cardiomediastinum": "Kengaygan kardiomediastinum"
};

const getUzName = (name) => diseaseUzMap[name] || name;

export default function ResultView({ patient, onApproveSuccess }) {
  const scans = patient?.scans || [];
  
  // Selected scan index for single-view mode
  const [selectedScanIndex, setSelectedScanIndex] = useState(scans.length > 0 ? scans.length - 1 : 0);
  const activeScan = scans[selectedScanIndex] || patient;

  // Comparison view mode state
  const [viewMode, setViewMode] = useState('single'); // 'single' | 'compare'
  const [compareScanIndex, setCompareScanIndex] = useState(scans.length > 1 ? 0 : 0); // Past scan index for comparison

  const [opacity, setOpacity] = useState(80);
  const [heatmapVisible, setHeatmapVisible] = useState(true);

  // Comparison HUD controls
  const [leftOpacity, setLeftOpacity] = useState(80);
  const [leftHeatmapVisible, setLeftHeatmapVisible] = useState(true);
  const [rightOpacity, setRightOpacity] = useState(80);
  const [rightHeatmapVisible, setRightHeatmapVisible] = useState(true);

  const [activeSegmentTab, setActiveSegmentTab] = useState('simple'); // 'simple' | 'raw_scores' | 'technical'
  const [selectedDisease, setSelectedDisease] = useState(activeScan?.diagnosis || '');
  const [activeHeatmapUrl, setActiveHeatmapUrl] = useState(activeScan?.heatmap_image || '');
  const [loadingHeatmap, setLoadingHeatmap] = useState(false);

  const [chatMessages, setChatMessages] = useState([]);
  const [chatInput, setChatInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  
  const chatMessagesEndRef = useRef(null);

  useEffect(() => {
    if (scans.length > 0) {
      setSelectedScanIndex(scans.length - 1);
    }
  }, [patient]);

  useEffect(() => {
    if (activeScan) {
      setSelectedDisease(activeScan.diagnosis);
      setActiveHeatmapUrl(activeScan.heatmap_image);
      setChatMessages([
        {
          id: 1,
          sender: 'ai',
          name: 'SSV AI Yordamchi',
          text: `Tahlil yakunlandi! Bemor ${patient.name} uchun ${activeScan.diagnosis} (${activeScan.probability}%) aniqlanmoqda. SSV davolash bayonnomalari va dori dozalari haqida maslahatlar bera olaman.`
        }
      ]);
    }
  }, [selectedScanIndex, patient]);

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
          diagnosis: activeScan.diagnosis,
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

  const isApproved = activeScan.status === 'Tasdiqlangan';
  const riskClass = activeScan.diagnosis === 'Norma'
    ? 'bg-success/10 border-success/30 text-success'
    : 'bg-error/10 border-error/30 text-error';

  const rawScores = activeScan.raw_scores || [];
  const selectedDiseaseUz = getUzName(selectedDisease);

  // Comparison objects
  const pastScan = scans[compareScanIndex] || scans[0];
  const currentScan = activeScan;

  return (
    <div className="flex-1 flex flex-col gap-6">
      
      {/* 1. Dynamic Status & Demographic Banner */}
      <div className="bg-surface-container-lowest rounded-3xl p-6 shadow-sm border border-outline-variant/20 flex flex-col md:flex-row justify-between items-start md:items-center gap-4 relative overflow-hidden">
        {isApproved && (
          <div className="absolute top-0 left-0 right-0 py-1.5 px-6 bg-success/15 border-b border-success/30 flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-success"></span>
            <span className="text-[10px] font-bold text-success uppercase tracking-wider">
              Tasdiqlangan. Shifokor: {activeScan.approved_by || 'Dr. Karimov'} ({activeScan.approved_time || 'Bugun'})
            </span>
          </div>
        )}
        
        <div className={`flex items-center gap-4 ${isApproved ? 'pt-4 md:pt-0' : ''}`}>
          <div className="h-12 w-12 rounded-full bg-primary/10 flex items-center justify-center">
            <span className="material-symbols-outlined text-primary text-[28px] font-light">personal_injury</span>
          </div>
          <div className="flex flex-col">
            <div className="flex items-center gap-2">
              <h2 className="font-geist text-xl font-bold text-on-surface">{patient.name}</h2>
              <span className="text-xs font-bold px-2.5 py-0.5 bg-surface-container rounded-full text-primary font-mono">
                {scans.length} ta rentgen tahlili
              </span>
            </div>
            <p className="text-[11px] text-on-surface-variant font-bold uppercase tracking-wider mt-1">
              ID: {patient.id} • {patient.age} Yosh • {patient.gender}
            </p>
          </div>
        </div>
        
        <div className="flex items-center gap-3">
          {/* View Mode Selector Tabs */}
          <div className="flex bg-surface-container-low p-1 rounded-2xl border border-outline-variant/40">
            <button
              onClick={() => setViewMode('single')}
              className={`px-4 py-2 rounded-xl text-xs font-bold transition-all cursor-pointer flex items-center gap-1.5 ${
                viewMode === 'single'
                  ? 'bg-white text-primary shadow-sm font-bold'
                  : 'text-on-surface-variant hover:text-on-surface'
              }`}
            >
              <span className="material-symbols-outlined text-[16px]">visibility</span> Tahlil Ko'rinishi
            </button>
            {scans.length >= 2 && (
              <button
                onClick={() => setViewMode('compare')}
                className={`px-4 py-2 rounded-xl text-xs font-bold transition-all cursor-pointer flex items-center gap-1.5 ${
                  viewMode === 'compare'
                    ? 'bg-white text-primary shadow-sm font-bold'
                    : 'text-on-surface-variant hover:text-on-surface'
                }`}
              >
                <span className="material-symbols-outlined text-[16px]">compare</span> Taqoslash ({scans.length})
              </button>
            )}
          </div>

          <div className={`px-4 py-2 rounded-full border ${riskClass}`}>
            <span className="text-xs font-bold flex items-center gap-2">
              <span className={`w-2 h-2 rounded-full ${activeScan.diagnosis === 'Norma' ? 'bg-success' : 'bg-error animate-pulse'}`}></span>
              <span>{activeScan.diagnosis}: {activeScan.probability}%</span>
            </span>
          </div>
        </div>
      </div>

      {/* Scan Timeline History Selector Bar */}
      {scans.length > 1 && (
        <div className="bg-surface-container-low/60 rounded-2xl p-3 border border-outline-variant/30 flex items-center gap-3 overflow-x-auto">
          <span className="text-xs font-bold text-on-surface-variant uppercase tracking-wider flex items-center gap-1 shrink-0">
            <span className="material-symbols-outlined text-[16px] text-primary">history</span> Rentgenlar Tarixi:
          </span>
          <div className="flex items-center gap-2">
            {scans.map((scan, idx) => {
              const isSelected = selectedScanIndex === idx;
              return (
                <button
                  key={idx}
                  onClick={() => {
                    setSelectedScanIndex(idx);
                    if (viewMode === 'compare' && idx === compareScanIndex) {
                      setCompareScanIndex((idx + 1) % scans.length);
                    }
                  }}
                  className={`px-3.5 py-1.5 rounded-xl text-xs font-bold transition-all cursor-pointer flex items-center gap-2 border ${
                    isSelected
                      ? 'bg-primary text-white border-primary shadow-sm'
                      : 'bg-surface hover:bg-surface-container border-outline-variant/30 text-on-surface'
                  }`}
                >
                  <span className="material-symbols-outlined text-[14px]">
                    {idx === scans.length - 1 ? 'new_releases' : 'event'}
                  </span>
                  <span>{scan.timestamp}</span>
                  <span className={`text-[10px] px-1.5 py-0.5 rounded-md ${isSelected ? 'bg-white/20' : 'bg-surface-container-high'}`}>
                    {scan.diagnosis} ({scan.probability}%)
                  </span>
                </button>
              );
            })}
          </div>
        </div>
      )}

      {/* 2. MAIN CONTENT AREA */}
      {viewMode === 'compare' && scans.length >= 2 ? (
        /* SIDE-BY-SIDE COMPARISON PANEL */
        <div className="flex flex-col gap-6">
          {/* Comparison Controls Banner */}
          <div className="bg-surface-container-lowest rounded-3xl p-5 border border-outline-variant/30 shadow-sm flex flex-col md:flex-row justify-between items-center gap-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-secondary/15 flex items-center justify-center text-secondary">
                <span className="material-symbols-outlined">compare_arrows</span>
              </div>
              <div>
                <h3 className="font-geist text-base font-bold text-on-surface">Rentgenogrammalar Taqoslashi va Klinik Dinamika</h3>
                <p className="text-xs text-on-surface-variant">Eski va yangi tasvirlarni yonma-yon solishtiring</p>
              </div>
            </div>

            {/* Select past scan dropdown */}
            <div className="flex items-center gap-2">
              <span className="text-xs font-bold text-on-surface-variant">Taqoslanayotgan eski tahlil:</span>
              <select
                value={compareScanIndex}
                onChange={(e) => setCompareScanIndex(parseInt(e.target.value))}
                className="bg-surface-container-low border border-outline-variant/40 rounded-xl px-3 py-1.5 text-xs font-bold text-on-surface cursor-pointer focus:outline-none"
              >
                {scans.map((s, idx) => (
                  <option key={idx} value={idx} disabled={idx === selectedScanIndex}>
                    {s.timestamp} — {s.diagnosis} ({s.probability}%) {idx === selectedScanIndex ? '(Hozirgi)' : ''}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Dual Canvas Viewer */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            
            {/* LEFT CANVAS: PAST SCAN */}
            <div className="flex flex-col gap-3">
              <div className="flex items-center justify-between px-2">
                <span className="text-xs font-bold text-on-surface-variant flex items-center gap-1.5">
                  <span className="w-2.5 h-2.5 rounded-full bg-secondary"></span>
                  Eski Tahlil: {pastScan.timestamp}
                </span>
                <span className="text-xs font-bold px-3 py-1 rounded-full bg-secondary/10 text-secondary border border-secondary/20">
                  {pastScan.diagnosis} ({pastScan.probability}%)
                </span>
              </div>

              <div className="bg-black rounded-3xl overflow-hidden relative shadow-lg border border-surface-container-high h-[420px] flex items-center justify-center group">
                <img
                  alt="Past Chest X-ray"
                  className="w-full h-full object-contain"
                  src={pastScan.original_image}
                  onError={handleImgError}
                />
                <img
                  alt="Past Heatmap"
                  className="w-full h-full object-contain absolute z-20 pointer-events-none transition-opacity duration-300"
                  src={pastScan.heatmap_image}
                  style={{ opacity: leftHeatmapVisible ? leftOpacity / 100 : 0 }}
                  onError={handleImgError}
                />

                <div className="absolute bottom-4 left-4 right-4 z-30 flex items-center justify-between bg-surface/90 backdrop-blur-md rounded-2xl p-3 shadow-md border border-outline-variant/30 text-xs">
                  <button
                    onClick={() => setLeftHeatmapVisible(!leftHeatmapVisible)}
                    className="px-3 py-1.5 bg-secondary text-white rounded-xl font-bold flex items-center gap-1 text-[11px]"
                  >
                    <span className="material-symbols-outlined text-[16px]">{leftHeatmapVisible ? 'visibility' : 'visibility_off'}</span>
                    <span>Grad-CAM</span>
                  </button>
                  <div className="flex items-center gap-2 flex-1 max-w-[140px] ml-auto">
                    <input
                      className="w-full h-1 bg-outline-variant rounded-lg appearance-none cursor-pointer accent-secondary"
                      max="100"
                      min="0"
                      type="range"
                      value={leftOpacity}
                      onChange={(e) => setLeftOpacity(parseInt(e.target.value))}
                    />
                    <span className="font-bold text-[11px] text-secondary">{leftOpacity}%</span>
                  </div>
                </div>
              </div>
            </div>

            {/* RIGHT CANVAS: CURRENT / NEW SCAN */}
            <div className="flex flex-col gap-3">
              <div className="flex items-center justify-between px-2">
                <span className="text-xs font-bold text-on-surface-variant flex items-center gap-1.5">
                  <span className="w-2.5 h-2.5 rounded-full bg-primary"></span>
                  Yangi Tahlil: {currentScan.timestamp}
                </span>
                <span className={`text-xs font-bold px-3 py-1 rounded-full border ${currentScan.diagnosis === 'Norma' ? 'bg-success/10 text-success border-success/20' : 'bg-error/10 text-error border-error/20'}`}>
                  {currentScan.diagnosis} ({currentScan.probability}%)
                </span>
              </div>

              <div className="bg-black rounded-3xl overflow-hidden relative shadow-lg border border-surface-container-high h-[420px] flex items-center justify-center group">
                <img
                  alt="Current Chest X-ray"
                  className="w-full h-full object-contain"
                  src={currentScan.original_image}
                  onError={handleImgError}
                />
                <img
                  alt="Current Heatmap"
                  className="w-full h-full object-contain absolute z-20 pointer-events-none transition-opacity duration-300"
                  src={currentScan.heatmap_image}
                  style={{ opacity: rightHeatmapVisible ? rightOpacity / 100 : 0 }}
                  onError={handleImgError}
                />

                <div className="absolute bottom-4 left-4 right-4 z-30 flex items-center justify-between bg-surface/90 backdrop-blur-md rounded-2xl p-3 shadow-md border border-outline-variant/30 text-xs">
                  <button
                    onClick={() => setRightHeatmapVisible(!rightHeatmapVisible)}
                    className="px-3 py-1.5 bg-primary text-white rounded-xl font-bold flex items-center gap-1 text-[11px]"
                  >
                    <span className="material-symbols-outlined text-[16px]">{rightHeatmapVisible ? 'visibility' : 'visibility_off'}</span>
                    <span>Grad-CAM</span>
                  </button>
                  <div className="flex items-center gap-2 flex-1 max-w-[140px] ml-auto">
                    <input
                      className="w-full h-1 bg-outline-variant rounded-lg appearance-none cursor-pointer accent-primary"
                      max="100"
                      min="0"
                      type="range"
                      value={rightOpacity}
                      onChange={(e) => setRightOpacity(parseInt(e.target.value))}
                    />
                    <span className="font-bold text-[11px] text-primary">{rightOpacity}%</span>
                  </div>
                </div>
              </div>
            </div>

          </div>

          {/* Clinical Evolution Comparison Table */}
          <div className="bg-surface-container-lowest rounded-3xl p-6 border border-outline-variant/20 shadow-sm flex flex-col gap-4">
            <h4 className="font-geist text-sm font-bold text-on-surface flex items-center gap-2">
              <span className="material-symbols-outlined text-primary text-[20px]">trending_up</span>
              Patologiyalar bo'yicha dinamik o'zgarishlar ko'rsatkichlari (18 ta raw score)
            </h4>

            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
              {(currentScan.raw_scores || []).map((curItem, idx) => {
                const pastItem = (pastScan.raw_scores || []).find(p => p.disease === curItem.disease) || { score: 0 };
                const diff = (curItem.score - pastItem.score) * 100;
                const isImproved = diff < -2; // Decrease in pathology score is positive!
                const isWorsened = diff > 2;
                const nameUz = curItem.disease_uz || getUzName(curItem.disease);

                return (
                  <div key={idx} className="p-3.5 bg-surface rounded-2xl border border-outline-variant/30 flex flex-col gap-1.5">
                    <div className="flex justify-between items-center">
                      <span className="text-xs font-bold text-on-surface">{nameUz}</span>
                      <span className={`text-[11px] font-bold px-2 py-0.5 rounded-full ${
                        isImproved ? 'bg-success/15 text-success' : isWorsened ? 'bg-error/15 text-error' : 'bg-surface-container text-on-surface-variant'
                      }`}>
                        {diff > 0 ? `+${diff.toFixed(1)}%` : `${diff.toFixed(1)}%`}
                      </span>
                    </div>

                    <div className="flex items-center justify-between text-[11px] text-on-surface-variant">
                      <span>Eski: {(pastItem.score * 100).toFixed(1)}%</span>
                      <span className="material-symbols-outlined text-[14px]">arrow_forward</span>
                      <span className="font-bold text-on-surface">Yangi: {(curItem.score * 100).toFixed(1)}%</span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      ) : (
        /* SINGLE SCAN DETAILED VIEW */
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 flex-1">
          
          {/* Left Columns: Visualizer and Findings */}
          <div className="lg:col-span-8 flex flex-col gap-6">
            
            {/* Overlapping Canvas Viewer */}
            <div className="bg-black rounded-3xl overflow-hidden relative shadow-xl border border-surface-container-high h-[500px] flex items-center justify-center group">
              {/* Base Image */}
              <img
                alt="Chest X-ray"
                className="w-full h-full object-contain"
                src={activeScan.original_image}
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
                    <span className="text-xs font-bold text-on-surface">Grad-CAM {selectedDiseaseUz} hisoblanmoqda...</span>
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
                    {heatmapVisible ? `Grad-CAM (${selectedDiseaseUz}) Yashirish` : `Grad-CAM (${selectedDiseaseUz}) Ko'rsatish`}
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
                  <span className="text-[9px] uppercase font-bold text-on-surface-variant tracking-wider">AI Faollashuv ({selectedDiseaseUz})</span>
                  <div className="w-28 h-2.5 bg-gradient-to-r from-blue-600 via-green-400 to-red-600 rounded-full"></div>
                  <div className="flex justify-between text-[9px] font-bold text-on-surface">
                    <span>Past</span>
                    <span>Yuqori</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Diagnostic Details Area */}
            <div className="bg-surface-container-lowest rounded-3xl p-6 shadow-sm border border-outline-variant/20 relative overflow-hidden">
              <div className="flex items-center justify-between border-b border-surface-container-high pb-4 mb-4">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-secondary/15 flex items-center justify-center text-secondary">
                    <span className="material-symbols-outlined">stethoscope</span>
                  </div>
                  <h3 className="text-base font-bold text-on-surface">Tashxis Xulosalari</h3>
                </div>
                
                {/* Segmented Tab */}
                <div className="flex bg-surface-container-low p-1 rounded-xl border border-outline-variant/50">
                  <button
                    onClick={() => setActiveSegmentTab('simple')}
                    className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all cursor-pointer ${
                      activeSegmentTab === 'simple'
                        ? 'bg-white shadow-sm text-primary font-bold'
                        : 'text-on-surface-variant hover:text-on-surface'
                    }`}
                  >
                    Sodda xulosa
                  </button>
                  {rawScores.length > 0 && (
                    <button
                      onClick={() => setActiveSegmentTab('raw_scores')}
                      className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all cursor-pointer ${
                        activeSegmentTab === 'raw_scores'
                          ? 'bg-white shadow-sm text-primary font-bold'
                          : 'text-on-surface-variant hover:text-on-surface'
                      }`}
                    >
                      Raw Model Score'lar ({rawScores.length})
                    </button>
                  )}
                  <button
                    onClick={() => setActiveSegmentTab('technical')}
                    className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all cursor-pointer ${
                      activeSegmentTab === 'technical'
                        ? 'bg-white shadow-sm text-primary font-bold'
                        : 'text-on-surface-variant hover:text-on-surface'
                    }`}
                  >
                    Rentgenologik hisobot (Texnik)
                  </button>
                </div>
              </div>

              {/* TAB CONTENT: Raw Scores Interactive Selector */}
              {activeSegmentTab === 'raw_scores' && (
                <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
                  {rawScores.map((item, idx) => {
                    const isSelected = selectedDisease === item.disease || selectedDisease === item.disease_uz;
                    const pct = Math.min(Math.max(Math.round(item.score * 100), 0), 100);
                    const nameUz = item.disease_uz || getUzName(item.disease);
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
                          <div className="flex flex-col truncate pr-2">
                            <span className="text-xs font-bold truncate">{nameUz}</span>
                            <span className="text-[10px] text-on-surface-variant/70 font-medium truncate">{item.disease}</span>
                          </div>
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
                          {activeScan.findings.summary}
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
                          {activeScan.findings.simple_lang}
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
                          {(activeScan.findings.precautions || []).map((prec, idx) => (
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
                  <p className="font-mono text-xs whitespace-pre-wrap">{activeScan.findings.technical}</p>
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
      )}
    </div>
  );
}
