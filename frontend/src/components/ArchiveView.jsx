import React, { useState, useEffect } from 'react';
import { translations, getPathologyTranslation } from '../i18n';

export default function ArchiveView({ onSelectPatient, lang = 'uz' }) {
  const t = translations[lang] || translations.uz;
  const [scans, setScans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [pathologyFilter, setPathologyFilter] = useState('barchasi');
  const [sortOrder, setSortOrder] = useState('newest'); // 'newest' | 'oldest'
  const [selectedScanModal, setSelectedScanModal] = useState(null);

  const fetchScans = async () => {
    try {
      setLoading(true);
      const res = await fetch('/api/scans');
      if (res.ok) {
        const data = await res.json();
        setScans(data);
      }
    } catch (e) {
      console.error("Arxiv skanerlarini yuklashda xatolik:", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchScans();
  }, []);

  // Compute stats
  const totalScans = scans.length;
  const approvedScans = scans.filter((s) => s.status === 'Tasdiqlangan').length;
  const pathologyScans = scans.filter((s) => s.diagnosis !== 'Norma').length;
  const heatmapScans = scans.filter((s) => s.heatmap_image).length;

  // Filter & Sort scans strictly (Newest date first by default)
  const filteredScans = scans
    .filter((scan) => {
      const matchesSearch =
        scan.scan_id?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        scan.patient_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        scan.patient_id?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        scan.diagnosis?.toLowerCase().includes(searchTerm.toLowerCase());

      if (!matchesSearch) return false;

      if (pathologyFilter === 'patologiya') return scan.diagnosis !== 'Norma';
      if (pathologyFilter === 'norma') return scan.diagnosis === 'Norma';
      if (pathologyFilter === 'tasdiqlangan') return scan.status === 'Tasdiqlangan';
      return true;
    })
    .sort((a, b) => {
      const getVal = (item) => {
        const ts = String(item.timestamp || '');
        if (ts.includes('Bugun')) return '9999-99-99 ' + ts;
        if (ts.includes('Kecha')) return '9999-99-98 ' + ts;
        return ts;
      };
      const valA = getVal(a);
      const valB = getVal(b);
      return sortOrder === 'newest' ? valB.localeCompare(valA) : valA.localeCompare(valB);
    });

  return (
    <div className="flex-1 flex flex-col gap-6">
      {/* Archive Repository Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-surface-container-lowest p-6 rounded-3xl border border-outline-variant/30 shadow-sm">
        <div>
          <div className="flex items-center gap-3">
            <h2 className="font-geist text-2xl font-bold text-primary">Rentgenogrammalar Arxivi (Sana tartibida)</h2>
            <span className="bg-primary/10 text-primary text-xs font-bold px-3 py-1 rounded-full border border-primary/20">
              {totalScans} ta tahlil jurnali
            </span>
          </div>
          <p className="text-xs text-on-surface-variant mt-1">
            Barcha o'tkazilgan rentgen tahlillarining xronologik arxivi (Eng so'nggi sana birinchi)
          </p>
        </div>

        <div className="flex items-center gap-2">
          {/* Date Sort Toggle */}
          <button
            onClick={() => setSortOrder(sortOrder === 'newest' ? 'oldest' : 'newest')}
            className="px-3 py-2 bg-primary/10 text-primary hover:bg-primary/20 rounded-2xl text-xs font-bold flex items-center gap-1.5 transition-all cursor-pointer border border-primary/20"
          >
            <span className="material-symbols-outlined text-base">swap_vert</span>
            <span>{sortOrder === 'newest' ? 'So\'nggi sana birinchi ⬇' : 'Eski sana birinchi ⬆'}</span>
          </button>

          <button
            onClick={fetchScans}
            className="px-4 py-2 bg-surface-container-high hover:bg-surface-container-highest text-on-surface rounded-2xl text-xs font-bold flex items-center gap-2 transition-all cursor-pointer"
          >
            <span className="material-symbols-outlined text-lg">refresh</span>
            Yangilash
          </button>
        </div>
      </div>

      {/* Summary Metrics Bar */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-surface-container-lowest p-4 rounded-2xl border border-outline-variant/30 shadow-sm flex items-center gap-3">
          <div className="p-3 bg-primary/10 text-primary rounded-xl">
            <span className="material-symbols-outlined">folder_zip</span>
          </div>
          <div>
            <div className="text-xs text-on-surface-variant font-medium">Jami Rentgenlar</div>
            <div className="font-geist font-bold text-xl text-on-surface">{totalScans} ta</div>
          </div>
        </div>

        <div className="bg-surface-container-lowest p-4 rounded-2xl border border-outline-variant/30 shadow-sm flex items-center gap-3">
          <div className="p-3 bg-success/10 text-success rounded-xl">
            <span className="material-symbols-outlined">verified</span>
          </div>
          <div>
            <div className="text-xs text-on-surface-variant font-medium">Tasdiqlangan Hisobotlar</div>
            <div className="font-geist font-bold text-xl text-success">{approvedScans} ta</div>
          </div>
        </div>

        <div className="bg-surface-container-lowest p-4 rounded-2xl border border-outline-variant/30 shadow-sm flex items-center gap-3">
          <div className="p-3 bg-error/10 text-error rounded-xl">
            <span className="material-symbols-outlined">radiology</span>
          </div>
          <div>
            <div className="text-xs text-on-surface-variant font-medium">Patologiyalar</div>
            <div className="font-geist font-bold text-xl text-error">{pathologyScans} holat</div>
          </div>
        </div>

        <div className="bg-surface-container-lowest p-4 rounded-2xl border border-outline-variant/30 shadow-sm flex items-center gap-3">
          <div className="p-3 bg-secondary/10 text-secondary rounded-xl">
            <span className="material-symbols-outlined">thermostat</span>
          </div>
          <div>
            <div className="text-xs text-on-surface-variant font-medium">Grad-CAM Xaritalari</div>
            <div className="font-geist font-bold text-xl text-secondary">{heatmapScans} visual</div>
          </div>
        </div>
      </div>

      {/* Controls: Search & Filter */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-4 bg-surface-container-lowest p-4 rounded-2xl border border-outline-variant/30">
        <div className="relative w-full sm:w-80">
          <span className="material-symbols-outlined absolute left-3.5 top-1/2 -translate-y-1/2 text-on-surface-variant text-lg">
            search
          </span>
          <input
            type="text"
            placeholder="Skaner ID, Bemor ismi yoki diagnostika..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2 bg-surface-container-low border border-outline-variant/50 rounded-xl text-xs font-medium focus:outline-none focus:border-primary text-on-surface placeholder:text-on-surface-variant/60"
          />
        </div>

        <div className="flex items-center gap-2 overflow-x-auto w-full sm:w-auto">
          <button
            onClick={() => setPathologyFilter('barchasi')}
            className={`px-3.5 py-1.5 rounded-xl text-xs font-bold transition-all cursor-pointer ${
              pathologyFilter === 'barchasi'
                ? 'bg-primary text-white shadow-sm'
                : 'bg-surface-container-high text-on-surface-variant hover:bg-surface-container-highest'
            }`}
          >
            Barchasi ({totalScans})
          </button>
          <button
            onClick={() => setPathologyFilter('patologiya')}
            className={`px-3.5 py-1.5 rounded-xl text-xs font-bold transition-all cursor-pointer ${
              pathologyFilter === 'patologiya'
                ? 'bg-error text-white shadow-sm'
                : 'bg-error/10 text-error hover:bg-error/20'
            }`}
          >
            Patologiyalar ({pathologyScans})
          </button>
          <button
            onClick={() => setPathologyFilter('norma')}
            className={`px-3.5 py-1.5 rounded-xl text-xs font-bold transition-all cursor-pointer ${
              pathologyFilter === 'norma'
                ? 'bg-success text-white shadow-sm'
                : 'bg-success/10 text-success hover:bg-success/20'
            }`}
          >
            Normadagilar ({totalScans - pathologyScans})
          </button>
          <button
            onClick={() => setPathologyFilter('tasdiqlangan')}
            className={`px-3.5 py-1.5 rounded-xl text-xs font-bold transition-all cursor-pointer ${
              pathologyFilter === 'tasdiqlangan'
                ? 'bg-secondary text-white shadow-sm'
                : 'bg-secondary/10 text-secondary hover:bg-secondary/20'
            }`}
          >
            Tasdiqlangan ({approvedScans})
          </button>
        </div>
      </div>

      {/* Archive Scans Table (Chronological Log) */}
      <div className="bg-surface-container-lowest rounded-3xl shadow-xl overflow-hidden border border-outline-variant/30">
        <div className="overflow-x-auto">
          <table className="w-full border-collapse text-left">
            <thead>
              <tr className="bg-surface-container-low text-xs font-bold text-on-surface-variant uppercase tracking-wider border-b border-outline-variant/50">
                <th className="p-4">O'tkazilgan Sana & Vaqt ⬇</th>
                <th className="p-4">Skaner ID</th>
                <th className="p-4">Bemor</th>
                <th className="p-4">Grad-CAM Visual</th>
                <th className="p-4">AI Diagnostik Natija</th>
                <th className="p-4">AI Score (%)</th>
                <th className="p-4">Ekspert Tasdig'i</th>
                <th className="p-4 text-right">Harakatlar</th>
              </tr>
            </thead>
            <tbody className="text-sm divide-y divide-outline-variant/20">
              {loading ? (
                <tr>
                  <td colSpan="8" className="p-8 text-center text-on-surface-variant font-medium">
                    Skanerlar arxivi yuklanmoqda...
                  </td>
                </tr>
              ) : filteredScans.length > 0 ? (
                filteredScans.map((scan, idx) => {
                  const isApproved = scan.status === 'Tasdiqlangan';
                  const isNormal = scan.diagnosis === 'Norma';

                  return (
                    <tr
                      key={scan.scan_id || idx}
                      className="hover:bg-surface-container-low transition-colors"
                    >
                      {/* Date & Time */}
                      <td className="p-4">
                        <div className="font-semibold text-xs text-on-surface">{scan.timestamp}</div>
                      </td>

                      {/* Scan ID */}
                      <td className="p-4">
                        <span className="font-mono font-bold text-xs text-primary">{scan.scan_id || 'SCAN-REG'}</span>
                      </td>

                      {/* Patient Info */}
                      <td className="p-4">
                        <div className="font-bold text-on-surface">{scan.patient_name}</div>
                        <div className="text-xs text-on-surface-variant font-mono">
                          {scan.patient_id} • {scan.patient_age} yosh
                        </div>
                      </td>

                      {/* Visual Heatmap Thumbnail */}
                      <td className="p-4">
                        {scan.heatmap_image ? (
                          <div
                            onClick={() => setSelectedScanModal(scan)}
                            className="w-12 h-12 rounded-xl overflow-hidden border border-outline-variant/40 relative cursor-pointer group shadow-sm"
                          >
                            <img
                              src={scan.heatmap_image}
                              alt="Heatmap Preview"
                              className="w-full h-full object-cover group-hover:scale-110 transition-transform"
                            />
                            <div className="absolute inset-0 bg-black/30 opacity-0 group-hover:opacity-100 flex items-center justify-center transition-opacity">
                              <span className="material-symbols-outlined text-white text-base">visibility</span>
                            </div>
                          </div>
                        ) : (
                          <span className="text-xs text-on-surface-variant italic">Mavjud emas</span>
                        )}
                      </td>

                      {/* Diagnosis & Urgency */}
                      <td className="p-4">
                        <div className="flex flex-col gap-1 items-start">
                          <span
                            className={`px-3 py-1 rounded-full text-xs font-bold inline-block ${
                              isNormal ? 'bg-success/10 text-success' : 'bg-error/10 text-error'
                            }`}
                          >
                            {scan.diagnosis}
                          </span>
                          {!isNormal && (
                            <span className="text-[10px] font-bold text-error bg-error/10 px-2 py-0.5 rounded-md border border-error/20 flex items-center gap-1">
                              <span>🚨</span>
                              <span>{scan.urgency?.urgency_badge || "Shoshilinch!"}</span>
                            </span>
                          )}
                        </div>
                      </td>

                      {/* Probability Score */}
                      <td className="p-4 font-bold text-secondary">{scan.probability}%</td>

                      {/* Approval Status */}
                      <td className="p-4">
                        <div>
                          <span
                            className={`px-2.5 py-0.5 rounded-full border text-[11px] font-bold inline-block ${
                              isApproved
                                ? 'bg-success/15 border-success/30 text-success'
                                : 'bg-amber-500/15 border-amber-500/30 text-amber-700'
                            }`}
                          >
                            {scan.status || 'Kutilmoqda'}
                          </span>
                          {scan.approved_by && (
                            <div className="text-[10px] text-on-surface-variant font-medium mt-0.5">
                              {scan.approved_by}
                            </div>
                          )}
                        </div>
                      </td>

                      {/* Actions */}
                      <td className="p-4 text-right">
                        <div className="flex items-center justify-end gap-2">
                          <button
                            onClick={() => setSelectedScanModal(scan)}
                            title="Skanerni ko'rish"
                            className="p-2 bg-surface-container-high hover:bg-surface-container-highest text-on-surface rounded-xl text-xs font-bold transition-all cursor-pointer"
                          >
                            <span className="material-symbols-outlined text-base">preview</span>
                          </button>

                          <button
                            onClick={() => window.open(`/api/pdf/${scan.patient_id}`, '_blank')}
                            title="PDF Hisobot"
                            className="p-2 bg-primary/10 text-primary hover:bg-primary/20 rounded-xl text-xs font-bold transition-all cursor-pointer"
                          >
                            <span className="material-symbols-outlined text-base">picture_as_pdf</span>
                          </button>
                        </div>
                      </td>
                    </tr>
                  );
                })
              ) : (
                <tr>
                  <td colSpan="8" className="p-8 text-center text-on-surface-variant font-medium">
                    Skanerlar arxivida hech qanday rentgen yozuvi topilmadi.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Scan Quick View Modal */}
      {selectedScanModal && (
        <div className="fixed inset-0 z-50 bg-black/65 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-surface-container-lowest rounded-3xl max-w-3xl w-full p-6 border border-outline-variant/30 shadow-2xl overflow-hidden animate-in fade-in zoom-in duration-200">
            <div className="flex items-center justify-between pb-4 border-b border-outline-variant/30">
              <div>
                <h3 className="font-geist text-lg font-bold text-primary flex items-center gap-2">
                  <span className="material-symbols-outlined text-xl">folder_zip</span>
                  Rentgenogramma va Grad-CAM Vizualizatsiyasi ({selectedScanModal.scan_id || 'SCAN'})
                </h3>
                <p className="text-xs text-on-surface-variant font-medium">
                  Bemor: <span className="font-bold text-on-surface">{selectedScanModal.patient_name}</span> ({selectedScanModal.patient_id}) • {selectedScanModal.timestamp}
                </p>
              </div>

              <button
                onClick={() => setSelectedScanModal(null)}
                className="p-2 hover:bg-surface-container-high rounded-full transition-colors cursor-pointer"
              >
                <span className="material-symbols-outlined">close</span>
              </button>
            </div>

            {/* Images Side-by-side View */}
            <div className="py-4 space-y-4">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {/* Original Image */}
                <div className="bg-surface-container-low p-3 rounded-2xl border border-outline-variant/20 flex flex-col items-center">
                  <span className="text-xs font-bold text-on-surface-variant mb-2">Original Rentgenogramma</span>
                  {selectedScanModal.original_image ? (
                    <img
                      src={selectedScanModal.original_image}
                      alt="Original X-ray"
                      className="w-full h-52 object-contain rounded-xl bg-black"
                    />
                  ) : (
                    <div className="w-full h-52 rounded-xl bg-black/20 flex items-center justify-center text-xs text-on-surface-variant">
                      Tasvir mavjud emas
                    </div>
                  )}
                </div>

                {/* Grad-CAM Heatmap Image */}
                <div className="bg-surface-container-low p-3 rounded-2xl border border-outline-variant/20 flex flex-col items-center">
                  <span className="text-xs font-bold text-secondary mb-2">Grad-CAM Issiqlik Xaritasi (Heatmap)</span>
                  {selectedScanModal.heatmap_image ? (
                    <img
                      src={selectedScanModal.heatmap_image}
                      alt="Grad-CAM Heatmap"
                      className="w-full h-52 object-contain rounded-xl bg-black"
                    />
                  ) : (
                    <div className="w-full h-52 rounded-xl bg-black/20 flex items-center justify-center text-xs text-on-surface-variant">
                      Heatmap mavjud emas
                    </div>
                  )}
                </div>
              </div>

              {/* Diagnosis Summary */}
              <div className="bg-surface-container-low p-4 rounded-2xl border border-outline-variant/20 flex items-center justify-between">
                <div>
                  <div className="text-xs text-on-surface-variant font-medium">Tashxis:</div>
                  <div className="font-geist font-bold text-base text-error">{selectedScanModal.diagnosis}</div>
                </div>
                <div>
                  <div className="text-xs text-on-surface-variant font-medium">AI Ishonchlilik Score:</div>
                  <div className="font-geist font-bold text-base text-secondary">{selectedScanModal.probability}%</div>
                </div>
                <div>
                  <div className="text-xs text-on-surface-variant font-medium">Holati:</div>
                  <div className="font-bold text-xs text-success">{selectedScanModal.status || 'Tasdiqlangan'}</div>
                </div>
              </div>
            </div>

            {/* Modal Actions */}
            <div className="pt-4 border-t border-outline-variant/30 flex items-center justify-end gap-3">
              <button
                onClick={() => setSelectedScanModal(null)}
                className="px-4 py-2 bg-surface-container-high text-on-surface rounded-xl text-xs font-bold hover:bg-surface-container-highest cursor-pointer"
              >
                Yopish
              </button>
              <button
                onClick={() => window.open(`/api/pdf/${selectedScanModal.patient_id}`, '_blank')}
                className="px-5 py-2 bg-primary text-white rounded-xl text-xs font-bold hover:bg-primary-container shadow-md flex items-center gap-1.5 cursor-pointer"
              >
                <span className="material-symbols-outlined text-base">picture_as_pdf</span>
                PDF Hisobotini Yuklash
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
