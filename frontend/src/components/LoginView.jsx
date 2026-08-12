import React, { useState } from 'react';

export default function LoginView({ onLoginSuccess }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [showPass, setShowPass] = useState(false);

  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const res = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: email.trim().toLowerCase(), password })
      });
      if (res.ok) {
        const user = await res.json();
        sessionStorage.setItem('avicenna_user_email', user.email);
        onLoginSuccess(user);
      } else {
        const err = await res.json();
        setError(err.detail || 'Email yoki parol noto\'g\'ri.');
      }
    } catch {
      setError('Serverga ulanib bo\'lmadi. Iltimos qayta urinib ko\'ring.');
    }
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#0f172a] via-[#1e3a8a] to-[#0f2357] flex items-center justify-center p-4 relative overflow-hidden">
      {/* Background blobs */}
      <div className="absolute top-0 left-0 w-[500px] h-[500px] bg-blue-600/20 rounded-full blur-3xl -translate-x-1/2 -translate-y-1/2 pointer-events-none" />
      <div className="absolute bottom-0 right-0 w-[400px] h-[400px] bg-teal-500/15 rounded-full blur-3xl translate-x-1/4 translate-y-1/4 pointer-events-none" />

      <div className="w-full max-w-md relative z-10">
        {/* Brand */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-3xl bg-white/10 backdrop-blur-sm border border-white/20 mb-4 shadow-xl">
            <span className="material-symbols-outlined text-white text-[36px]">radiology</span>
          </div>
          <h1 className="text-3xl font-bold text-white font-geist tracking-tight">
            AvicennaX <span className="text-teal-300">AI</span>
          </h1>
          <p className="text-sm text-blue-200 mt-1">Chest X-Ray Diagnostics Platform</p>
        </div>

        {/* Login Card */}
        <div className="bg-white/10 backdrop-blur-xl border border-white/20 rounded-3xl p-8 shadow-2xl">
          <div className="mb-6">
            <h2 className="text-lg font-bold text-white font-geist">Tizimga kirish</h2>
            <p className="text-xs text-blue-200/80 mt-1">
              Login va parol klinika administratori tomonidan beriladi.
            </p>
          </div>

          <form onSubmit={handleLogin} className="flex flex-col gap-4">
            {/* Email */}
            <div className="flex flex-col gap-1.5">
              <label className="text-xs font-bold text-white/60 uppercase tracking-wider">Email</label>
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="doctor@clinic.uz"
                className="w-full bg-white/10 border border-white/20 rounded-2xl px-4 py-3 text-sm text-white placeholder-white/30 focus:outline-none focus:ring-2 focus:ring-teal-400/60 transition"
              />
            </div>

            {/* Password */}
            <div className="flex flex-col gap-1.5">
              <label className="text-xs font-bold text-white/60 uppercase tracking-wider">Parol</label>
              <div className="relative">
                <input
                  type={showPass ? 'text' : 'password'}
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  className="w-full bg-white/10 border border-white/20 rounded-2xl px-4 py-3 text-sm text-white placeholder-white/30 focus:outline-none focus:ring-2 focus:ring-teal-400/60 transition pr-12"
                />
                <button
                  type="button"
                  onClick={() => setShowPass((v) => !v)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-white/40 hover:text-white transition cursor-pointer"
                >
                  <span className="material-symbols-outlined text-[18px]">
                    {showPass ? 'visibility_off' : 'visibility'}
                  </span>
                </button>
              </div>
            </div>

            {/* Error */}
            {error && (
              <div className="bg-red-500/20 border border-red-400/30 text-red-200 text-xs font-medium px-4 py-2.5 rounded-xl flex items-center gap-2">
                <span className="material-symbols-outlined text-[16px]">error</span>
                {error}
              </div>
            )}

            {/* Submit */}
            <button
              type="submit"
              disabled={loading}
              className="w-full py-3.5 rounded-2xl bg-teal-400 hover:bg-teal-300 text-[#0f172a] text-sm font-bold transition-all shadow-lg disabled:opacity-60 flex items-center justify-center gap-2 cursor-pointer mt-1"
            >
              {loading && (
                <span className="w-4 h-4 border-2 border-[#0f172a]/30 border-t-[#0f172a] rounded-full animate-spin" />
              )}
              Kirish
            </button>
          </form>
        </div>

        {/* Footer note */}
        <p className="text-center text-white/30 text-xs mt-6">
          Muammo bo'lsa, klinika administratoriga murojaat qiling.
        </p>
        <p className="text-center text-white/20 text-[10px] mt-1">
          © 2026 AvicennaX AI · Chest X-Ray Diagnostics
        </p>
      </div>
    </div>
  );
}
