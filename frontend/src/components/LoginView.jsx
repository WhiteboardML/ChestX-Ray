import React, { useState } from 'react';

export default function LoginView({ onLoginSuccess }) {
  const [tab, setTab] = useState('login'); // 'login' | 'register'

  // Login state
  const [loginEmail, setLoginEmail] = useState('');
  const [loginPassword, setLoginPassword] = useState('');
  const [loginError, setLoginError] = useState('');
  const [loginLoading, setLoginLoading] = useState(false);

  // Register state
  const [regEmail, setRegEmail] = useState('');
  const [regUsername, setRegUsername] = useState('');
  const [regPassword, setRegPassword] = useState('');
  const [regPassword2, setRegPassword2] = useState('');
  const [regError, setRegError] = useState('');
  const [regLoading, setRegLoading] = useState(false);
  const [regSuccess, setRegSuccess] = useState(false);

  const [showPass, setShowPass] = useState(false);

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoginError('');
    setLoginLoading(true);
    try {
      const res = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: loginEmail.trim().toLowerCase(), password: loginPassword })
      });
      if (res.ok) {
        const user = await res.json();
        // Persist email in sessionStorage so page refresh keeps the session
        sessionStorage.setItem('avicenna_user_email', user.email);
        onLoginSuccess(user);
      } else {
        const err = await res.json();
        setLoginError(err.detail || 'Email yoki parol noto\'g\'ri.');
      }
    } catch {
      setLoginError('Serverga ulanib bo\'lmadi. Iltimos qayta urinib ko\'ring.');
    }
    setLoginLoading(false);
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setRegError('');
    if (regPassword !== regPassword2) {
      setRegError('Parollar mos emas.');
      return;
    }
    if (regPassword.length < 6) {
      setRegError('Parol kamida 6 ta belgidan iborat bo\'lishi kerak.');
      return;
    }
    setRegLoading(true);
    try {
      const res = await fetch('/api/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: regEmail.trim().toLowerCase(), username: regUsername.trim(), password: regPassword })
      });
      if (res.ok) {
        setRegSuccess(true);
        setTimeout(() => {
          setTab('login');
          setLoginEmail(regEmail.trim().toLowerCase());
          setRegSuccess(false);
        }, 2000);
      } else {
        const err = await res.json();
        setRegError(err.detail || 'Ro\'yxatdan o\'tishda xatolik yuz berdi.');
      }
    } catch {
      setRegError('Serverga ulanib bo\'lmadi. Iltimos qayta urinib ko\'ring.');
    }
    setRegLoading(false);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#0f172a] via-[#1e3a8a] to-[#0f2357] flex items-center justify-center p-4 relative overflow-hidden">
      {/* Background decorative blobs */}
      <div className="absolute top-0 left-0 w-[500px] h-[500px] bg-blue-600/20 rounded-full blur-3xl -translate-x-1/2 -translate-y-1/2 pointer-events-none" />
      <div className="absolute bottom-0 right-0 w-[400px] h-[400px] bg-teal-500/15 rounded-full blur-3xl translate-x-1/4 translate-y-1/4 pointer-events-none" />

      <div className="w-full max-w-md relative z-10">
        {/* Brand */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-3xl bg-white/10 backdrop-blur-sm border border-white/20 mb-4 shadow-xl">
            <span className="material-symbols-outlined text-white text-[36px]">radiology</span>
          </div>
          <h1 className="text-3xl font-bold text-white font-geist tracking-tight">AvicennaX <span className="text-teal-300">AI</span></h1>
          <p className="text-sm text-blue-200 mt-1">Chest X-Ray Diagnostics Platform</p>
        </div>

        {/* Card */}
        <div className="bg-white/10 backdrop-blur-xl border border-white/20 rounded-3xl p-8 shadow-2xl">
          {/* Tabs */}
          <div className="flex bg-white/10 rounded-2xl p-1 mb-6 gap-1">
            <button
              onClick={() => { setTab('login'); setLoginError(''); }}
              className={`flex-1 py-2.5 rounded-xl text-sm font-bold transition-all cursor-pointer ${
                tab === 'login' ? 'bg-white text-[#1e3a8a] shadow-md' : 'text-white/70 hover:text-white'
              }`}
            >
              Kirish
            </button>
            <button
              onClick={() => { setTab('register'); setRegError(''); }}
              className={`flex-1 py-2.5 rounded-xl text-sm font-bold transition-all cursor-pointer ${
                tab === 'register' ? 'bg-white text-[#1e3a8a] shadow-md' : 'text-white/70 hover:text-white'
              }`}
            >
              Ro'yxatdan o'tish
            </button>
          </div>

          {/* LOGIN FORM */}
          {tab === 'login' && (
            <form onSubmit={handleLogin} className="flex flex-col gap-4">
              <div className="flex flex-col gap-1.5">
                <label className="text-xs font-bold text-white/70 uppercase tracking-wider">Email</label>
                <input
                  type="email"
                  required
                  value={loginEmail}
                  onChange={(e) => setLoginEmail(e.target.value)}
                  placeholder="doctor@clinic.uz"
                  className="w-full bg-white/10 border border-white/20 rounded-2xl px-4 py-3 text-sm text-white placeholder-white/30 focus:outline-none focus:ring-2 focus:ring-teal-400/60 transition"
                />
              </div>

              <div className="flex flex-col gap-1.5">
                <label className="text-xs font-bold text-white/70 uppercase tracking-wider">Parol</label>
                <div className="relative">
                  <input
                    type={showPass ? 'text' : 'password'}
                    required
                    value={loginPassword}
                    onChange={(e) => setLoginPassword(e.target.value)}
                    placeholder="••••••••"
                    className="w-full bg-white/10 border border-white/20 rounded-2xl px-4 py-3 text-sm text-white placeholder-white/30 focus:outline-none focus:ring-2 focus:ring-teal-400/60 transition pr-12"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPass((v) => !v)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-white/40 hover:text-white transition"
                  >
                    <span className="material-symbols-outlined text-[18px]">{showPass ? 'visibility_off' : 'visibility'}</span>
                  </button>
                </div>
              </div>

              {loginError && (
                <div className="bg-red-500/20 border border-red-400/30 text-red-200 text-xs font-medium px-4 py-2.5 rounded-xl flex items-center gap-2">
                  <span className="material-symbols-outlined text-[16px]">error</span>
                  {loginError}
                </div>
              )}

              <button
                type="submit"
                disabled={loginLoading}
                className="w-full py-3.5 rounded-2xl bg-teal-400 hover:bg-teal-300 text-[#0f172a] text-sm font-bold transition-all shadow-lg disabled:opacity-60 flex items-center justify-center gap-2 cursor-pointer mt-1"
              >
                {loginLoading && <span className="w-4 h-4 border-2 border-[#0f172a]/30 border-t-[#0f172a] rounded-full animate-spin" />}
                Kirish
              </button>
            </form>
          )}

          {/* REGISTER FORM */}
          {tab === 'register' && (
            <form onSubmit={handleRegister} className="flex flex-col gap-4">
              {regSuccess ? (
                <div className="py-8 flex flex-col items-center gap-3 text-center">
                  <div className="w-14 h-14 rounded-full bg-teal-400/20 flex items-center justify-center">
                    <span className="material-symbols-outlined text-teal-300 text-[32px]">check_circle</span>
                  </div>
                  <p className="text-white font-bold">Muvaffaqiyatli ro'yxatdan o'tdingiz!</p>
                  <p className="text-white/60 text-xs">Kirish sahifasiga yo'naltirilmoqda...</p>
                </div>
              ) : (
                <>
                  <div className="flex flex-col gap-1.5">
                    <label className="text-xs font-bold text-white/70 uppercase tracking-wider">To'liq ism (Username)</label>
                    <input
                      type="text"
                      required
                      value={regUsername}
                      onChange={(e) => setRegUsername(e.target.value)}
                      placeholder="Dr. Karimov"
                      className="w-full bg-white/10 border border-white/20 rounded-2xl px-4 py-3 text-sm text-white placeholder-white/30 focus:outline-none focus:ring-2 focus:ring-teal-400/60 transition"
                    />
                  </div>

                  <div className="flex flex-col gap-1.5">
                    <label className="text-xs font-bold text-white/70 uppercase tracking-wider">Email</label>
                    <input
                      type="email"
                      required
                      value={regEmail}
                      onChange={(e) => setRegEmail(e.target.value)}
                      placeholder="doctor@clinic.uz"
                      className="w-full bg-white/10 border border-white/20 rounded-2xl px-4 py-3 text-sm text-white placeholder-white/30 focus:outline-none focus:ring-2 focus:ring-teal-400/60 transition"
                    />
                  </div>

                  <div className="flex flex-col gap-1.5">
                    <label className="text-xs font-bold text-white/70 uppercase tracking-wider">Parol</label>
                    <div className="relative">
                      <input
                        type={showPass ? 'text' : 'password'}
                        required
                        value={regPassword}
                        onChange={(e) => setRegPassword(e.target.value)}
                        placeholder="Kamida 6 belgi"
                        className="w-full bg-white/10 border border-white/20 rounded-2xl px-4 py-3 text-sm text-white placeholder-white/30 focus:outline-none focus:ring-2 focus:ring-teal-400/60 transition pr-12"
                      />
                      <button
                        type="button"
                        onClick={() => setShowPass((v) => !v)}
                        className="absolute right-3 top-1/2 -translate-y-1/2 text-white/40 hover:text-white transition"
                      >
                        <span className="material-symbols-outlined text-[18px]">{showPass ? 'visibility_off' : 'visibility'}</span>
                      </button>
                    </div>
                  </div>

                  <div className="flex flex-col gap-1.5">
                    <label className="text-xs font-bold text-white/70 uppercase tracking-wider">Parolni tasdiqlang</label>
                    <input
                      type={showPass ? 'text' : 'password'}
                      required
                      value={regPassword2}
                      onChange={(e) => setRegPassword2(e.target.value)}
                      placeholder="••••••••"
                      className="w-full bg-white/10 border border-white/20 rounded-2xl px-4 py-3 text-sm text-white placeholder-white/30 focus:outline-none focus:ring-2 focus:ring-teal-400/60 transition"
                    />
                  </div>

                  {regError && (
                    <div className="bg-red-500/20 border border-red-400/30 text-red-200 text-xs font-medium px-4 py-2.5 rounded-xl flex items-center gap-2">
                      <span className="material-symbols-outlined text-[16px]">error</span>
                      {regError}
                    </div>
                  )}

                  <button
                    type="submit"
                    disabled={regLoading}
                    className="w-full py-3.5 rounded-2xl bg-teal-400 hover:bg-teal-300 text-[#0f172a] text-sm font-bold transition-all shadow-lg disabled:opacity-60 flex items-center justify-center gap-2 cursor-pointer mt-1"
                  >
                    {regLoading && <span className="w-4 h-4 border-2 border-[#0f172a]/30 border-t-[#0f172a] rounded-full animate-spin" />}
                    Ro'yxatdan o'tish
                  </button>
                </>
              )}
            </form>
          )}
        </div>

        <p className="text-center text-white/30 text-xs mt-6">
          © 2026 AvicennaX AI · Chest X-Ray Diagnostics
        </p>
      </div>
    </div>
  );
}
