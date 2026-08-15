import React, { useState, useEffect } from 'react';
import { translations } from '../i18n';

export default function StatsView({ lang = 'uz' }) {
  const t = translations[lang] || translations.uz;
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch('/api/stats/dashboard')
      .then((res) => {
        if (!res.ok) throw new Error("Statistikalarni yuklashda xatolik yuz berdi");
        return res.json();
      })
      .then((data) => {
        setStats(data);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center min-h-[400px]">
        <span className="w-10 h-10 border-4 border-primary border-t-transparent rounded-full animate-spin" />
        <p className="text-xs text-on-surface-variant mt-3 font-geist font-medium">Statistika ma'lumotlari yuklanmoqda...</p>
      </div>
    );
  }

  if (error || !stats) {
    return (
      <div className="flex-1 flex items-center justify-center min-h-[400px]">
        <div className="p-5 bg-error/10 border border-error/20 text-error rounded-2xl max-w-md text-center">
          <span className="material-symbols-outlined text-[36px] mb-2">error</span>
          <p className="text-sm font-bold">Xatolik yuz berdi</p>
          <p className="text-xs mt-1 text-error/80">{error || "Ma'lumot topilmadi"}</p>
        </div>
      </div>
    );
  }

  // Calculate approval metrics
  const totalApprovals = stats.approval_stats.Tasdiqlangan + stats.approval_stats.Rad etilgan;
  const accuracyRate = totalApprovals > 0 
    ? ((stats.approval_stats.Tasdiqlangan / totalApprovals) * 100).toFixed(1)
    : "100";

  // Prepare pathology array for custom SVG bar charts
  const pathData = Object.entries(stats.pathology_distribution)
    .map(([name, count]) => ({ name, count }))
    .sort((a, b) => b.count - a.count);

  const maxCount = pathData.length > 0 ? Math.max(...pathData.map(d => d.count)) : 1;

  // Prepare urgency array for donut charts
  const urgencyData = [
    { label: "O'ta shoshilinch", code: "CRITICAL", count: stats.urgency_distribution.CRITICAL, color: "#ef4444" },
    { label: "Yuqori shoshilinch", code: "HIGH", count: stats.urgency_distribution.HIGH, color: "#f59e0b" },
    { label: "O'rta shoshilinch", code: "MODERATE", count: stats.urgency_distribution.MODERATE, color: "#eab308" },
    { label: "Me'yorda", code: "NORMAL", count: stats.urgency_distribution.NORMAL, color: "#10b981" }
  ].filter(u => u.count > 0);

  const totalUrgentCases = urgencyData.reduce((sum, u) => sum + u.count, 0) || 1;

  // Donut chart calculations
  let accumulatedAngle = 0;
  const radius = 50;
  const circumference = 2 * Math.PI * radius;

  return (
    <div className="flex-1 flex flex-col gap-6">
      
      {/* Overview Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        
        {/* Total Scans Card */}
        <div className="bg-surface-container-lowest border border-outline-variant/30 rounded-3xl p-5 shadow-sm hover:shadow-md transition-all flex items-center gap-4 group">
          <div className="w-12 h-12 rounded-full bg-primary/10 text-primary flex items-center justify-center group-hover:scale-110 transition-transform">
            <span className="material-symbols-outlined text-[24px]">folder_open</span>
          </div>
          <div>
            <p className="text-[11px] font-bold text-on-surface-variant uppercase tracking-wider">Jami Tahlillar</p>
            <p className="text-2xl font-geist font-extrabold text-on-surface mt-0.5">{stats.total_scans}</p>
          </div>
        </div>

        {/* Unique Patients Card */}
        <div className="bg-surface-container-lowest border border-outline-variant/30 rounded-3xl p-5 shadow-sm hover:shadow-md transition-all flex items-center gap-4 group">
          <div className="w-12 h-12 rounded-full bg-secondary/15 text-secondary flex items-center justify-center group-hover:scale-110 transition-transform">
            <span className="material-symbols-outlined text-[24px]">groups</span>
          </div>
          <div>
            <p className="text-[11px] font-bold text-on-surface-variant uppercase tracking-wider">Jami Bemorlar</p>
            <p className="text-2xl font-geist font-extrabold text-on-surface mt-0.5">{stats.total_patients}</p>
          </div>
        </div>

        {/* Critical Cases Card */}
        <div className="bg-surface-container-lowest border border-outline-variant/30 rounded-3xl p-5 shadow-sm hover:shadow-md transition-all flex items-center gap-4 group">
          <div className="w-12 h-12 rounded-full bg-error/10 text-error flex items-center justify-center group-hover:scale-110 transition-transform">
            <span className="material-symbols-outlined text-[24px]">warning</span>
          </div>
          <div>
            <p className="text-[11px] font-bold text-on-surface-variant uppercase tracking-wider">Kritik Patologiyalar</p>
            <p className="text-2xl font-geist font-extrabold text-on-surface mt-0.5">
              {stats.urgency_distribution.CRITICAL + stats.urgency_distribution.HIGH}
            </p>
          </div>
        </div>

        {/* Diagnostic Accuracy Card */}
        <div className="bg-surface-container-lowest border border-outline-variant/30 rounded-3xl p-5 shadow-sm hover:shadow-md transition-all flex items-center gap-4 group">
          <div className="w-12 h-12 rounded-full bg-success/10 text-success flex items-center justify-center group-hover:scale-110 transition-transform">
            <span className="material-symbols-outlined text-[24px]">task_alt</span>
          </div>
          <div>
            <p className="text-[11px] font-bold text-on-surface-variant uppercase tracking-wider">AI Tasdiqlash Koeffitsienti</p>
            <p className="text-2xl font-geist font-extrabold text-on-surface mt-0.5">{accuracyRate}%</p>
          </div>
        </div>

      </div>

      {/* Main Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-stretch">
        
        {/* Left Chart: Pathology Distribution Bar Chart */}
        <div className="lg:col-span-7 bg-surface-container-lowest border border-outline-variant/30 rounded-[2rem] shadow-sm p-6 flex flex-col">
          <div className="flex items-center justify-between mb-6 pb-3 border-b border-surface-container-high">
            <div className="flex items-center gap-2">
              <span className="material-symbols-outlined text-primary">bar_chart</span>
              <h3 className="font-geist text-base font-bold text-on-surface">Tahlil qilingan patologiyalar taqsimoti</h3>
            </div>
            <span className="text-[10px] bg-primary/10 text-primary px-2.5 py-1 rounded-full font-bold uppercase">AI Model</span>
          </div>

          {pathData.length === 0 ? (
            <div className="flex-1 flex items-center justify-center py-10">
              <p className="text-xs text-on-surface-variant">Hozircha tahlillar mavjud emas.</p>
            </div>
          ) : (
            <div className="space-y-4 flex-1">
              {pathData.map((d) => {
                const percentage = ((d.count / maxCount) * 100).toFixed(0);
                return (
                  <div key={d.name} className="flex flex-col gap-1.5">
                    <div className="flex items-center justify-between text-xs font-semibold">
                      <span className="text-on-surface">{d.name}</span>
                      <span className="text-on-surface-variant font-geist">{d.count} ta scan ({percentage}%)</span>
                    </div>
                    <div className="w-full h-3 bg-surface-container-low rounded-full overflow-hidden">
                      <div 
                        className="h-full bg-primary rounded-full transition-all duration-1000 ease-out" 
                        style={{ width: `${percentage}%` }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* Right Chart: Urgency Level Donut Chart */}
        <div className="lg:col-span-5 bg-surface-container-lowest border border-outline-variant/30 rounded-[2rem] shadow-sm p-6 flex flex-col">
          <div className="flex items-center justify-between mb-6 pb-3 border-b border-surface-container-high">
            <div className="flex items-center gap-2">
              <span className="material-symbols-outlined text-secondary">donut_large</span>
              <h3 className="font-geist text-base font-bold text-on-surface">Shoshilinchlik darajalari</h3>
            </div>
            <span className="text-[10px] bg-secondary/15 text-secondary px-2.5 py-1 rounded-full font-bold uppercase">Clinical Status</span>
          </div>

          <div className="flex flex-col sm:flex-row items-center justify-around gap-6 flex-1">
            {/* SVG Donut */}
            <div className="relative w-36 h-36 flex items-center justify-center">
              <svg width="100%" height="100%" viewBox="0 0 120 120" className="transform -rotate-90">
                {urgencyData.length === 0 ? (
                  <circle cx="60" cy="60" r={radius} fill="none" stroke="#e2e8f0" strokeWidth="12" />
                ) : (
                  urgencyData.map((u, idx) => {
                    const percent = u.count / totalUrgentCases;
                    const strokeDashoffset = circumference - (percent * circumference);
                    const strokeDasharray = `${circumference} ${circumference}`;
                    const offset = accumulatedAngle;
                    accumulatedAngle += percent * circumference;
                    
                    return (
                      <circle
                        key={idx}
                        cx="60"
                        cy="60"
                        r={radius}
                        fill="none"
                        stroke={u.color}
                        strokeWidth="12"
                        strokeDasharray={strokeDasharray}
                        strokeDashoffset={-offset}
                        className="transition-all duration-500 hover:stroke-[14px]"
                      />
                    );
                  })
                )}
              </svg>
              <div className="absolute flex flex-col items-center justify-center text-center">
                <span className="text-xl font-geist font-extrabold text-on-surface">{stats.total_scans}</span>
                <span className="text-[9px] text-on-surface-variant uppercase font-bold tracking-wider">Jami</span>
              </div>
            </div>

            {/* Legends */}
            <div className="flex flex-col gap-2.5 text-xs font-semibold w-full sm:w-auto">
              {urgencyData.map((u, idx) => (
                <div key={idx} className="flex items-center gap-2.5 justify-between sm:justify-start">
                  <div className="flex items-center gap-2">
                    <span className="w-3 h-3 rounded-full shrink-0" style={{ backgroundColor: u.color }} />
                    <span className="text-on-surface">{u.label}</span>
                  </div>
                  <span className="text-on-surface-variant font-geist">({u.count} ta)</span>
                </div>
              ))}
            </div>
          </div>
        </div>

      </div>

      {/* Case Approval Tracking Section */}
      <div className="bg-surface-container-lowest border border-outline-variant/30 rounded-[2rem] shadow-sm p-6">
        <div className="flex items-center justify-between mb-6 pb-3 border-b border-surface-container-high">
          <div className="flex items-center gap-2">
            <span className="material-symbols-outlined text-success">analytics</span>
            <h3 className="font-geist text-base font-bold text-on-surface">Shifokorlar tomonidan tasdiqlangan klinik holatlar</h3>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Approved */}
          <div className="bg-success/5 border border-success/20 rounded-2xl p-4 flex flex-col justify-between">
            <span className="text-xs font-bold text-success flex items-center gap-1.5">
              <span className="material-symbols-outlined text-[16px]">check_circle</span>
              Tasdiqlangan
            </span>
            <span className="text-3xl font-geist font-extrabold text-on-surface mt-2">{stats.approval_stats.Tasdiqlangan} ta</span>
          </div>

          {/* Corrected */}
          <div className="bg-error/5 border border-error/20 rounded-2xl p-4 flex flex-col justify-between">
            <span className="text-xs font-bold text-error flex items-center gap-1.5">
              <span className="material-symbols-outlined text-[16px]">cancel</span>
              Rad etilgan / Vrach to'g'rilagan
            </span>
            <span className="text-3xl font-geist font-extrabold text-on-surface mt-2">{stats.approval_stats["Rad etilgan"]} ta</span>
          </div>

          {/* Pending Review */}
          <div className="bg-warning/5 border border-amber-500/20 rounded-2xl p-4 flex flex-col justify-between">
            <span className="text-xs font-bold text-amber-600 flex items-center gap-1.5">
              <span className="material-symbols-outlined text-[16px]">pending</span>
              Ko'rik kutilmoqda
            </span>
            <span className="text-3xl font-geist font-extrabold text-on-surface mt-2">{stats.approval_stats["Ko'rik kutilmoqda"]} ta</span>
          </div>
        </div>
      </div>

    </div>
  );
}
