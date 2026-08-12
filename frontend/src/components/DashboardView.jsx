import React, { useState, useEffect, useRef } from 'react';

export default function DashboardView({ onUploadSuccess }) {
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState('');
  
  // Patient Modal & Search State
  const [pendingFile, setPendingFile] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [age, setAge] = useState(40);
  const [gender, setGender] = useState('Erkak');
  const [searchResults, setSearchResults] = useState([]);
  const [selectedPatientId, setSelectedPatientId] = useState(null);
  const [isSearching, setIsSearching] = useState(false);

  const [chatMessages, setChatMessages] = useState([
    {
      id: 1,
      sender: 'ai',
      name: 'SSV AI Yordamchi',
      text: "Assalomu alaykum! Men SSV yo'riqnomalari va davolash bayonnomalari bo'yicha o'qitilgan sun'iy intellekt maslahatchisiman. Rentgen suratini yuklamasdan turib ham nafas yo'li simptomlari, isitma yoki birinchi yordam haqida savol berishingiz mumkin.",
      statusText: 'Tibbiy maslahat • Onlayn'
    }
  ]);
  const [chatInput, setChatInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const fileInputRef = useRef(null);
  const chatMessagesEndRef = useRef(null);

  // Search existing patients when first_name or last_name changes
  useEffect(() => {
    const query = `${lastName} ${firstName}`.trim();
    if (!query) {
      setSearchResults([]);
      return;
    }
    const timer = setTimeout(async () => {
      setIsSearching(true);
      try {
        const res = await fetch(`/api/patients/search?q=${encodeURIComponent(query)}`);
        if (res.ok) {
          const data = await res.json();
          setSearchResults(data);
        }
      } catch (e) {
        console.error("Bemorlarni qidirishda xatolik:", e);
      } finally {
        setIsSearching(false);
      }
    }, 250);

    return () => clearTimeout(timer);
  }, [firstName, lastName]);

  // File Selection Handlers
  const handleFileSelected = (file) => {
    if (!file) return;
    setPendingFile(file);
    setShowModal(true);
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      handleFileSelected(e.target.files[0]);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFileSelected(e.dataTransfer.files[0]);
    }
  };

  const startAnalysis = async () => {
    if (!pendingFile) return;
    setShowModal(false);
    setIsUploading(true);
    setUploadStatus("DICOM ma'lumotlar o'qilmoqda...");

    const steps = [
      "DICOM ma'lumotlar o'qilmoqda...",
      "O'pka naqshi segmentatsiyasi...",
      "O'pka segmentatsiya tahlili...",
      "Grad-CAM patologiya aniqlash..."
    ];

    let currentStep = 0;
    const interval = setInterval(() => {
      if (currentStep < steps.length - 1) {
        currentStep++;
        setUploadStatus(steps[currentStep]);
      }
    }, 700);

    const formData = new FormData();
    formData.append('file', pendingFile);
    if (selectedPatientId) {
      formData.append('existing_patient_id', selectedPatientId);
    } else {
      formData.append('first_name', firstName);
      formData.append('last_name', lastName);
      formData.append('age', age);
      formData.append('gender', gender);
    }

    try {
      const response = await fetch('/api/upload', {
        method: 'POST',
        body: formData
      });
      clearInterval(interval);
      if (response.ok) {
        const patient = await response.json();
        onUploadSuccess(patient);
      } else {
        const err = await response.json();
        alert("Xatolik: " + (err.detail || 'Faylni tahlil qilishda xatolik.'));
        setIsUploading(false);
      }
    } catch (e) {
      clearInterval(interval);
      alert("Serverga ulanishda xatolik yuzaga keldi.");
      setIsUploading(false);
    }
  };

  // Chat Handlers
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
          diagnosis: 'Norma',
          patient_id: 'NO_PATIENT'
        })
      });

      setIsTyping(false);

      if (res.ok) {
        const data = await res.json();
        const aiMsg = {
          id: Date.now() + 1,
          sender: 'ai',
          name: 'AvicennaX AI Yordamchi',
          text: data.message
        };
        setChatMessages((prev) => [...prev, aiMsg]);
        setTimeout(scrollToBottom, 50);
      }
    } catch (e) {
      setIsTyping(false);
      alert('Chatbot javob berishda xatolikka yo\'l qo\'ydi.');
    }
  };

  const handleChatSubmit = (e) => {
    e.preventDefault();
    sendChatMessage(chatInput);
  };

  const scrollToBottom = () => {
    chatMessagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  return (
    <div className="flex-1 flex flex-col gap-6 relative">
      
      {/* PATIENT DEMOGRAPHIC & MATCHING MODAL */}
      {showModal && (
        <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-surface-container-lowest rounded-3xl p-6 shadow-2xl max-w-xl w-full border border-outline-variant/30 flex flex-col gap-5 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between border-b border-surface-container-high pb-3">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center text-primary">
                  <span className="material-symbols-outlined">badge</span>
                </div>
                <div>
                  <h3 className="font-geist text-lg font-bold text-on-surface">Bemor Kartochkasi Ma'lumotlari</h3>
                  <p className="text-xs text-on-surface-variant">Rentgen tahlilini bemor tarixiga biriktiring</p>
                </div>
              </div>
              <button 
                onClick={() => setShowModal(false)}
                className="w-8 h-8 rounded-full hover:bg-surface-container-high flex items-center justify-center text-on-surface-variant"
              >
                <span className="material-symbols-outlined text-[20px]">close</span>
              </button>
            </div>

            {/* Existing Patient Match Notification */}
            {searchResults.length > 0 && (
              <div className="p-4 bg-primary/5 border border-primary/20 rounded-2xl flex flex-col gap-3">
                <span className="text-xs font-bold text-primary flex items-center gap-1.5">
                  <span className="material-symbols-outlined text-[18px]">find_replace</span>
                  Tizimda mos bemorlar topildi ({searchResults.length} ta):
                </span>

                <div className="space-y-2 max-h-40 overflow-y-auto">
                  {searchResults.map((pat) => {
                    const isSelected = selectedPatientId === pat.id;
                    return (
                      <div
                        key={pat.id}
                        onClick={() => setSelectedPatientId(isSelected ? null : pat.id)}
                        className={`p-3 rounded-xl border text-left cursor-pointer transition-all flex items-center justify-between ${
                          isSelected
                            ? 'bg-primary text-white border-primary shadow-sm'
                            : 'bg-white hover:bg-surface-container border-outline-variant/30 text-on-surface'
                        }`}
                      >
                        <div className="flex flex-col">
                          <span className="text-xs font-bold">{pat.name} ({pat.age} yosh, {pat.gender})</span>
                          <span className={`text-[10px] ${isSelected ? 'text-white/80' : 'text-on-surface-variant'}`}>
                            ID: {pat.id} • {pat.scan_count} ta oldingi rentgen tahlili • Oxirgi: {pat.last_diagnosis}
                          </span>
                        </div>
                        <span className="material-symbols-outlined text-[20px]">
                          {isSelected ? 'check_circle' : 'radio_button_unchecked'}
                        </span>
                      </div>
                    );
                  })}
                </div>

                <div className="flex items-center justify-between text-[11px] pt-1 text-on-surface-variant font-medium">
                  <span>Mavjud kartochkani tanlaysizmi yoki yangi yaratasizmi?</span>
                  {selectedPatientId && (
                    <button 
                      onClick={() => setSelectedPatientId(null)}
                      className="text-primary font-bold hover:underline"
                    >
                      Yangi bemor sifatida yaratish
                    </button>
                  )}
                </div>
              </div>
            )}

            {/* Inputs Form (Disabled if existing patient is selected) */}
            <div className={`space-y-4 transition-opacity ${selectedPatientId ? 'opacity-50 pointer-events-none' : ''}`}>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-xs font-bold text-on-surface-variant mb-1 block">Familiya</label>
                  <input
                    type="text"
                    value={lastName}
                    onChange={(e) => setLastName(e.target.value)}
                    placeholder="Masalan: Azizov"
                    className="w-full bg-surface-container-low border border-outline-variant/40 rounded-xl px-3.5 py-2.5 text-xs focus:ring-2 focus:ring-primary/20 outline-none text-on-surface"
                  />
                </div>
                <div>
                  <label className="text-xs font-bold text-on-surface-variant mb-1 block">Ism</label>
                  <input
                    type="text"
                    value={firstName}
                    onChange={(e) => setFirstName(e.target.value)}
                    placeholder="Masalan: Bekzod"
                    className="w-full bg-surface-container-low border border-outline-variant/40 rounded-xl px-3.5 py-2.5 text-xs focus:ring-2 focus:ring-primary/20 outline-none text-on-surface"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-xs font-bold text-on-surface-variant mb-1 block">Yosh</label>
                  <input
                    type="number"
                    value={age}
                    onChange={(e) => setAge(parseInt(e.target.value) || 0)}
                    className="w-full bg-surface-container-low border border-outline-variant/40 rounded-xl px-3.5 py-2.5 text-xs focus:ring-2 focus:ring-primary/20 outline-none text-on-surface"
                  />
                </div>
                <div>
                  <label className="text-xs font-bold text-on-surface-variant mb-1 block">Jinsi</label>
                  <select
                    value={gender}
                    onChange={(e) => setGender(e.target.value)}
                    className="w-full bg-surface-container-low border border-outline-variant/40 rounded-xl px-3.5 py-2.5 text-xs focus:ring-2 focus:ring-primary/20 outline-none text-on-surface cursor-pointer"
                  >
                    <option value="Erkak">Erkak</option>
                    <option value="Ayol">Ayol</option>
                  </select>
                </div>
              </div>
            </div>

            <div className="flex items-center justify-end gap-3 border-t border-surface-container-high pt-4">
              <button
                type="button"
                onClick={() => setShowModal(false)}
                className="px-5 py-2.5 bg-surface-container-high text-on-surface rounded-xl text-xs font-bold hover:bg-surface-container transition-all cursor-pointer"
              >
                Bekor qilish
              </button>
              <button
                type="button"
                onClick={startAnalysis}
                className="px-6 py-2.5 bg-primary text-white rounded-xl text-xs font-bold hover:bg-primary-container transition-all shadow-md flex items-center gap-2 cursor-pointer"
              >
                <span className="material-symbols-outlined text-[18px]">psychology</span> Tahlilni Boshlash
              </button>
            </div>
          </div>
        </div>
      )}

      {/* STATE A: UPLOAD PANEL */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 flex-1 items-stretch">
        {/* Left: Upload Zone */}
        <div className="lg:col-span-8 flex flex-col">
          {isUploading ? (
            <div className="flex-1 bg-surface-container-lowest rounded-[2rem] shadow-xl p-10 flex flex-col items-center justify-center min-h-[460px] border border-outline-variant/30">
              <div className="flex flex-col items-center gap-4 text-center">
                <div className="w-16 h-16 border-4 border-primary border-t-transparent rounded-full animate-spin"></div>
                <h3 className="font-geist text-lg font-bold text-on-surface mt-2">{uploadStatus}</h3>
                <p className="text-xs text-on-surface-variant">AvicennaX AI tahlil modellari hisoblamoqda.</p>
              </div>
            </div>
          ) : (
            <div
              id="dropzone"
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current.click()}
              className={`flex-1 bg-surface-container-lowest rounded-[2rem] shadow-xl p-10 flex flex-col items-center justify-center min-h-[460px] border-2 border-dashed transition-all relative overflow-hidden group cursor-pointer ${
                isDragging
                  ? 'border-primary bg-primary/5'
                  : 'border-primary/20 hover:border-primary/40'
              }`}
            >
              <div className="absolute inset-0 bg-primary/5 opacity-0 group-hover:opacity-100 transition-all duration-300 pointer-events-none"></div>
              <div className="relative z-10 flex flex-col items-center text-center max-w-lg mx-auto">
                <div className="w-24 h-24 rounded-full bg-primary-container/10 flex items-center justify-center mb-8 group-hover:scale-110 transition-transform duration-500">
                  <span className="material-symbols-outlined text-primary text-[48px] animate-bounce" style={{ animationDuration: '3s' }}>
                    cloud_upload
                  </span>
                </div>
                <h2 className="font-geist text-2xl font-bold text-on-surface mb-3">O'pka rentgen suratini bu yerga tashlang</h2>
                <p className="text-sm text-on-surface-variant mb-8 leading-relaxed">
                  yoki kompyuter o'zidan tanlang. PNG, JPG, DICOM (.dcm) va PDF (.pdf) formatlari qo'llab-quvvatlanadi.
                </p>

                <button
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation();
                    fileInputRef.current.click();
                  }}
                  className="bg-primary text-white text-sm font-semibold px-8 py-3.5 rounded-full flex items-center gap-3 hover:bg-primary-container transition-all shadow-md cursor-pointer"
                >
                  <span className="material-symbols-outlined text-[18px]">upload</span> Kompyuterdan tanlash
                </button>
                <input
                  ref={fileInputRef}
                  accept=".png,.jpg,.jpeg,.dcm,.dicom,.pdf,.webp"
                  className="hidden"
                  id="file-input"
                  type="file"
                  onChange={handleFileChange}
                />

                <div className="flex items-center gap-2 text-on-surface-variant/70 mt-10">
                  <span className="material-symbols-outlined text-[16px]">lock</span>
                  <span className="text-[11px] font-medium tracking-wide">Bemor ma'lumotlari HIPAA standarti asosida shifrlangan.</span>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Right: Chatbot Welcome Context */}
        <div className="lg:col-span-4 flex flex-col">
          <div className="bg-surface-container-lowest rounded-[2rem] shadow-lg p-6 flex flex-col h-[460px] lg:h-full border border-primary/10">
            {/* Chatbot Header */}
            <div className="flex items-center gap-3 mb-6 pb-4 border-b border-surface-container-high">
              <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center text-primary">
                <span className="material-symbols-outlined">smart_toy</span>
              </div>
              <div className="flex flex-col">
                <span className="text-sm font-bold text-on-surface">SSV AI Yordamchi</span>
                <span className="text-[10px] text-success uppercase font-semibold">Tibbiy maslahat • Onlayn</span>
              </div>
            </div>

            {/* Chat Area Scrollable */}
            <div className="flex-1 flex flex-col gap-4 overflow-y-auto mb-4 scrollbar-thin">
              {chatMessages.map((msg, idx) => (
                <div
                  key={idx}
                  className={`flex flex-col gap-1 max-w-[85%] ${
                    msg.sender === 'doctor' ? 'self-end items-end ml-auto' : 'items-start'
                  }`}
                >
                  <span className="text-[9px] text-on-surface-variant ml-2 font-semibold font-geist">
                    {msg.name}
                  </span>
                  <div
                    className={`p-3 rounded-2xl shadow-sm text-xs leading-relaxed ${
                      msg.sender === 'doctor'
                        ? 'bg-primary text-white rounded-tr-sm'
                        : 'bg-surface-container-low text-on-surface rounded-tl-sm border border-outline-variant/20'
                    }`}
                  >
                    {msg.text}
                  </div>
                </div>
              ))}

              {isTyping && (
                <div className="flex flex-col gap-1 items-start max-w-[85%]">
                  <span className="text-[9px] text-on-surface-variant ml-2 font-semibold font-geist">SSV AI Yordamchi</span>
                  <div className="bg-surface-container-low p-3 rounded-2xl rounded-tl-sm border border-outline-variant/20 shadow-sm flex items-center gap-1.5">
                    <span className="w-1.5 h-1.5 rounded-full bg-primary animate-bounce"></span>
                    <span className="w-1.5 h-1.5 rounded-full bg-primary animate-bounce" style={{ animationDelay: '0.2s' }}></span>
                    <span className="w-1.5 h-1.5 rounded-full bg-primary animate-bounce" style={{ animationDelay: '0.4s' }}></span>
                  </div>
                </div>
              )}

              <div ref={chatMessagesEndRef} />
            </div>

            {/* Chat Input */}
            <div className="mt-auto">
              <form onSubmit={handleChatSubmit} className="relative flex items-center gap-2">
                <div className="relative flex-1">
                  <input
                    value={chatInput}
                    onChange={(e) => setChatInput(e.target.value)}
                    className="w-full bg-surface-container-high border-none rounded-full py-3.5 pl-4 pr-10 text-xs focus:ring-2 focus:ring-primary/20 outline-none placeholder:text-on-surface-variant/40"
                    placeholder="Simptom yoki savol yozing..."
                    type="text"
                    disabled={isUploading}
                  />
                </div>
                <button
                  type="submit"
                  disabled={isUploading || !chatInput.trim()}
                  className="w-10 h-10 bg-primary text-white rounded-full flex items-center justify-center shadow-md hover:bg-primary-container transition-colors disabled:opacity-50 cursor-pointer"
                >
                  <span className="material-symbols-outlined text-[18px]">send</span>
                </button>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
