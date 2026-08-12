import React, { useState } from 'react';

export default function PatientsView({ patients, onSelectPatient, onRegisterNewPatient }) {
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('barchasi');
  const [selectedPatientModal, setSelectedPatientModal] = useState(null);
  const [showAddModal, setShowAddModal] = useState(false);

  // New Patient Form state
  const [newPatientForm, setNewPatientForm] = useState({
    name: '',
    age: '',
    gender: 'Erkak',
    phone: '',
    medical_status: 'Nazoratda',
  });

  const handleCreateSubmit = async (e) => {
    e.preventDefault();
    if (!newPatientForm.name || !newPatientForm.age) return;

    try {
      const res = await fetch('/api/patients', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: newPatientForm.name,
          age: parseInt(newPatientForm.age, 10),
          gender: newPatientForm.gender,
          phone: newPatientForm.phone || '+998 90 123-45-67',
          medical_status: newPatientForm.medical_status,
        }),
      });
      if (res.ok) {
        const created = await res.json();
        if (onRegisterNewPatient) onRegisterNewPatient(created);
        setShowAddModal(false);
        setNewPatientForm({
          name: '',
          age: '',
          gender: 'Erkak',
          phone: '',
          medical_status: 'Nazoratda',
        });
      }
    } catch (err) {
      console.error("Yangi bemor registratsiyasida xatolik:", err);
    }
  };

  // Filter patients
  const filteredPatients = patients.filter((patient) => {
    const matchesSearch =
      patient.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      patient.id?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      patient.phone?.toLowerCase().includes(searchTerm.toLowerCase());

    if (!matchesSearch) return false;

    if (statusFilter === 'nazoratda') return (patient.medical_status || 'Nazoratda') === 'Nazoratda';
    if (statusFilter === 'statsionar') return patient.medical_status === 'Statsionar';
    if (statusFilter === 'chiqarilgan') return patient.medical_status === 'Chiqarilgan';
    if (statusFilter === 'patologiya') return patient.diagnosis && patient.diagnosis !== 'Norma';
    return true;
  });

  return (
    <div className="flex-1 flex flex-col gap-6">
      {/* Header & New Patient Register Button */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-surface-container-lowest p-6 rounded-3xl border border-outline-variant/30 shadow-sm">
        <div>
          <div className="flex items-center gap-3">
            <h2 className="font-geist text-2xl font-bold text-primary">Bemorlar Kartotekasi va Registratsiyasi</h2>
            <span className="bg-primary/10 text-primary text-xs font-bold px-3 py-1 rounded-full border border-primary/20">
              {patients.length} bemor ro'yxatda
            </span>
          </div>
          <p className="text-xs text-on-surface-variant mt-1">
            Tizimda ro'yxatdan o'tgan bemorlarning shaxsiy kartochkalari, umumiy statusi va anamnezi
          </p>
        </div>

        <button
          onClick={() => setShowAddModal(true)}
          className="px-5 py-2.5 bg-primary text-white rounded-2xl text-xs font-bold flex items-center gap-2 hover:bg-primary-container transition-all shadow-md cursor-pointer self-start md:self-auto"
        >
          <span className="material-symbols-outlined text-lg">person_add</span>
          Yangi Bemor Ro'yxatdan O'tkazish
        </button>
      </div>

      {/* Filter & Search Bar */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-4 bg-surface-container-lowest p-4 rounded-2xl border border-outline-variant/30">
        <div className="relative w-full sm:w-80">
          <span className="material-symbols-outlined absolute left-3.5 top-1/2 -translate-y-1/2 text-on-surface-variant text-lg">
            search
          </span>
          <input
            type="text"
            placeholder="Bemor ismi, ID yoki telefon..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2 bg-surface-container-low border border-outline-variant/50 rounded-xl text-xs font-medium focus:outline-none focus:border-primary text-on-surface placeholder:text-on-surface-variant/60"
          />
        </div>

        <div className="flex items-center gap-2 overflow-x-auto w-full sm:w-auto">
          <button
            onClick={() => setStatusFilter('barchasi')}
            className={`px-3.5 py-1.5 rounded-xl text-xs font-bold transition-all cursor-pointer ${
              statusFilter === 'barchasi'
                ? 'bg-primary text-white shadow-sm'
                : 'bg-surface-container-high text-on-surface-variant hover:bg-surface-container-highest'
            }`}
          >
            Barchasi ({patients.length})
          </button>
          <button
            onClick={() => setStatusFilter('nazoratda')}
            className={`px-3.5 py-1.5 rounded-xl text-xs font-bold transition-all cursor-pointer ${
              statusFilter === 'nazoratda'
                ? 'bg-amber-500 text-white shadow-sm'
                : 'bg-amber-500/10 text-amber-700 hover:bg-amber-500/20'
            }`}
          >
            Nazoratda ({patients.filter((p) => (p.medical_status || 'Nazoratda') === 'Nazoratda').length})
          </button>
          <button
            onClick={() => setStatusFilter('statsionar')}
            className={`px-3.5 py-1.5 rounded-xl text-xs font-bold transition-all cursor-pointer ${
              statusFilter === 'statsionar'
                ? 'bg-error text-white shadow-sm'
                : 'bg-error/10 text-error hover:bg-error/20'
            }`}
          >
            Statsionar ({patients.filter((p) => p.medical_status === 'Statsionar').length})
          </button>
          <button
            onClick={() => setStatusFilter('patologiya')}
            className={`px-3.5 py-1.5 rounded-xl text-xs font-bold transition-all cursor-pointer ${
              statusFilter === 'patologiya'
                ? 'bg-secondary text-white shadow-sm'
                : 'bg-secondary/10 text-secondary hover:bg-secondary/20'
            }`}
          >
            Patologiya Aniqlangan ({patients.filter((p) => p.diagnosis && p.diagnosis !== 'Norma').length})
          </button>
        </div>
      </div>

      {/* Patient Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {filteredPatients.length > 0 ? (
          filteredPatients.map((patient) => {
            const scanCount = patient.scans ? patient.scans.length : (patient.diagnosis ? 1 : 0);
            const medStatus = patient.medical_status || 'Nazoratda';
            const isNormal = patient.diagnosis === 'Norma' || !patient.diagnosis;

            const initials = patient.name
              ? patient.name
                  .split(' ')
                  .map((n) => n[0])
                  .join('')
                  .toUpperCase()
                  .slice(0, 2)
              : 'BM';

            return (
              <div
                key={patient.id}
                className="bg-surface-container-lowest rounded-3xl p-6 border border-outline-variant/30 hover:border-primary/40 shadow-sm hover:shadow-xl transition-all duration-300 flex flex-col justify-between relative overflow-hidden"
              >
                {/* Header Band */}
                <div
                  className={`absolute top-0 right-0 left-0 h-1.5 ${
                    medStatus === 'Statsionar'
                      ? 'bg-error'
                      : !isNormal
                      ? 'bg-amber-500'
                      : 'bg-success'
                  }`}
                />

                {/* Patient Profile Details */}
                <div>
                  <div className="flex items-start justify-between gap-3 mb-4 pt-1">
                    <div className="flex items-center gap-3">
                      <div className="w-12 h-12 rounded-2xl bg-primary/10 text-primary border border-primary/20 flex items-center justify-center font-geist font-bold text-base shadow-sm">
                        {initials}
                      </div>
                      <div>
                        <h3 className="font-geist text-base font-bold text-on-surface">
                          {patient.name}
                        </h3>
                        <div className="flex items-center gap-2 text-xs text-on-surface-variant font-medium mt-0.5">
                          <span className="font-mono text-primary font-bold">{patient.id}</span>
                          <span>•</span>
                          <span>{patient.age} yosh</span>
                          <span>•</span>
                          <span>{patient.gender}</span>
                        </div>
                      </div>
                    </div>

                    <span
                      className={`px-2.5 py-1 rounded-full text-[11px] font-bold border ${
                        medStatus === 'Statsionar'
                          ? 'bg-error/15 border-error/30 text-error'
                          : medStatus === 'Chiqarilgan'
                          ? 'bg-success/15 border-success/30 text-success'
                          : 'bg-amber-500/15 border-amber-500/30 text-amber-700'
                      }`}
                    >
                      {medStatus}
                    </span>
                  </div>

                  {/* Medical Summary Details */}
                  <div className="bg-surface-container-low p-4 rounded-2xl border border-outline-variant/20 mb-4 space-y-2">
                    <div className="flex items-center justify-between text-xs text-on-surface-variant">
                      <span className="font-semibold">Oxirgi Diagnostika:</span>
                      <span
                        className={`font-bold px-2 py-0.5 rounded-md text-[11px] ${
                          isNormal ? 'bg-success/10 text-success' : 'bg-error/10 text-error'
                        }`}
                      >
                        {patient.diagnosis || "Tahlil qilinmagan"}
                      </span>
                    </div>

                    <div className="flex items-center justify-between text-xs text-on-surface-variant">
                      <span className="font-semibold">Telefon raqami:</span>
                      <span className="font-mono font-medium text-on-surface">{patient.phone || '+998 90 123-45-67'}</span>
                    </div>

                    <div className="flex items-center justify-between text-xs text-on-surface-variant">
                      <span className="font-semibold">Rentgenogrammalar:</span>
                      <span className="font-bold text-primary">{scanCount} ta o'tkazilgan</span>
                    </div>
                  </div>
                </div>

                {/* Action Buttons */}
                <div className="pt-3 border-t border-outline-variant/20 flex items-center justify-between gap-2">
                  <button
                    onClick={() => setSelectedPatientModal(patient)}
                    className="flex-1 py-2 px-3 bg-surface-container-high hover:bg-surface-container-highest text-on-surface rounded-xl text-xs font-bold transition-all flex items-center justify-center gap-1 cursor-pointer"
                  >
                    <span className="material-symbols-outlined text-base">badge</span>
                    Tibbiy Karta
                  </button>

                  <button
                    onClick={() => onSelectPatient(patient)}
                    className="flex-1 py-2 px-3 bg-primary text-white rounded-xl text-xs font-bold hover:bg-primary-container transition-all flex items-center justify-center gap-1 cursor-pointer shadow-sm"
                  >
                    <span>Rentgen Tahlili</span>
                    <span className="material-symbols-outlined text-base">arrow_forward</span>
                  </button>
                </div>
              </div>
            );
          })
        ) : (
          <div className="col-span-full bg-surface-container-lowest rounded-3xl p-12 text-center border border-outline-variant/30">
            <span className="material-symbols-outlined text-4xl text-on-surface-variant mb-2">
              group_off
            </span>
            <p className="font-semibold text-on-surface">Ushbu mezon bo'yicha bemor topilmadi</p>
          </div>
        )}
      </div>

      {/* Patient Profile Modal */}
      {selectedPatientModal && (
        <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-surface-container-lowest rounded-3xl max-w-2xl w-full p-6 border border-outline-variant/30 shadow-2xl overflow-hidden animate-in fade-in zoom-in duration-200">
            <div className="flex items-center justify-between pb-4 border-b border-outline-variant/30">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 rounded-2xl bg-primary/10 text-primary border border-primary/20 flex items-center justify-center font-bold text-lg">
                  {selectedPatientModal.name
                    ? selectedPatientModal.name
                        .split(' ')
                        .map((n) => n[0])
                        .join('')
                        .toUpperCase()
                        .slice(0, 2)
                    : 'BM'}
                </div>
                <div>
                  <h3 className="font-geist text-xl font-bold text-on-surface">
                    {selectedPatientModal.name}
                  </h3>
                  <p className="text-xs text-on-surface-variant font-mono">
                    ID: {selectedPatientModal.id} • Registered: {selectedPatientModal.created_at || '2026-08-01'}
                  </p>
                </div>
              </div>
              <button
                onClick={() => setSelectedPatientModal(null)}
                className="p-2 hover:bg-surface-container-high rounded-full transition-colors cursor-pointer"
              >
                <span className="material-symbols-outlined">close</span>
              </button>
            </div>

            <div className="py-4 space-y-4">
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 bg-surface-container-low p-4 rounded-2xl border border-outline-variant/20">
                <div>
                  <div className="text-[11px] text-on-surface-variant font-medium">Yoshi</div>
                  <div className="font-bold text-sm text-on-surface">{selectedPatientModal.age} yosh</div>
                </div>
                <div>
                  <div className="text-[11px] text-on-surface-variant font-medium">Jinsi</div>
                  <div className="font-bold text-sm text-on-surface">{selectedPatientModal.gender}</div>
                </div>
                <div>
                  <div className="text-[11px] text-on-surface-variant font-medium">Telefon</div>
                  <div className="font-bold text-sm font-mono text-on-surface">{selectedPatientModal.phone || '+998 90 123-45-67'}</div>
                </div>
                <div>
                  <div className="text-[11px] text-on-surface-variant font-medium">Klinik Holat</div>
                  <div className="font-bold text-sm text-primary">{selectedPatientModal.medical_status || 'Nazoratda'}</div>
                </div>
              </div>

              <div>
                <h4 className="font-bold text-sm text-on-surface mb-2 flex items-center gap-2">
                  <span className="material-symbols-outlined text-primary text-lg">history</span>
                  Bemorning Rentgenologik Diagnostika Tarixi
                </h4>

                <div className="space-y-2 max-h-48 overflow-y-auto pr-1">
                  {selectedPatientModal.scans && selectedPatientModal.scans.length > 0 ? (
                    selectedPatientModal.scans.map((scan, idx) => (
                      <div
                        key={idx}
                        className="p-3 bg-surface-container-low rounded-xl border border-outline-variant/20 flex items-center justify-between text-xs"
                      >
                        <div>
                          <div className="font-bold text-on-surface">{scan.diagnosis} ({scan.probability}%)</div>
                          <div className="text-on-surface-variant text-[11px]">{scan.timestamp}</div>
                        </div>
                        <span className="px-2 py-1 rounded-md bg-success/15 text-success font-bold text-[11px]">
                          {scan.status || 'Tasdiqlangan'}
                        </span>
                      </div>
                    ))
                  ) : (
                    <p className="text-xs text-on-surface-variant italic p-3 bg-surface-container-low rounded-xl">
                      Ushbu bemor uchun hali rentgenogramma tahlili yuklanmagan.
                    </p>
                  )}
                </div>
              </div>
            </div>

            <div className="pt-4 border-t border-outline-variant/30 flex items-center justify-end gap-3">
              <button
                onClick={() => setSelectedPatientModal(null)}
                className="px-4 py-2 bg-surface-container-high text-on-surface rounded-xl text-xs font-bold hover:bg-surface-container-highest cursor-pointer"
              >
                Yopish
              </button>
              <button
                onClick={() => {
                  onSelectPatient(selectedPatientModal);
                  setSelectedPatientModal(null);
                }}
                className="px-5 py-2 bg-primary text-white rounded-xl text-xs font-bold hover:bg-primary-container shadow-md cursor-pointer"
              >
                Diagnostika Oynasini Ochish
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Add New Patient Modal */}
      {showAddModal && (
        <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-surface-container-lowest rounded-3xl max-w-md w-full p-6 border border-outline-variant/30 shadow-2xl animate-in fade-in zoom-in duration-200">
            <div className="flex items-center justify-between pb-3 border-b border-outline-variant/30 mb-4">
              <h3 className="font-geist text-lg font-bold text-primary flex items-center gap-2">
                <span className="material-symbols-outlined">person_add</span>
                Yangi Bemor Ro'yxatdan O'tkazish
              </h3>
              <button
                onClick={() => setShowAddModal(false)}
                className="p-1.5 hover:bg-surface-container-high rounded-full transition-colors cursor-pointer"
              >
                <span className="material-symbols-outlined text-lg">close</span>
              </button>
            </div>

            <form onSubmit={handleCreateSubmit} className="space-y-4 text-xs">
              <div>
                <label className="block font-bold text-on-surface mb-1">Bemorning To'liq Ismi (F.I.SH)</label>
                <input
                  type="text"
                  required
                  placeholder="Masalan: Karimov Farrux Olimovich"
                  value={newPatientForm.name}
                  onChange={(e) => setNewPatientForm({ ...newPatientForm, name: e.target.value })}
                  className="w-full p-2.5 bg-surface-container-low border border-outline-variant/50 rounded-xl text-sm focus:outline-none focus:border-primary text-on-surface"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-bold text-on-surface mb-1">Yoshi</label>
                  <input
                    type="number"
                    required
                    placeholder="35"
                    value={newPatientForm.age}
                    onChange={(e) => setNewPatientForm({ ...newPatientForm, age: e.target.value })}
                    className="w-full p-2.5 bg-surface-container-low border border-outline-variant/50 rounded-xl text-sm focus:outline-none focus:border-primary text-on-surface"
                  />
                </div>

                <div>
                  <label className="block font-bold text-on-surface mb-1">Jinsi</label>
                  <select
                    value={newPatientForm.gender}
                    onChange={(e) => setNewPatientForm({ ...newPatientForm, gender: e.target.value })}
                    className="w-full p-2.5 bg-surface-container-low border border-outline-variant/50 rounded-xl text-sm focus:outline-none focus:border-primary text-on-surface font-medium"
                  >
                    <option value="Erkak">Erkak</option>
                    <option value="Ayol">Ayol</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block font-bold text-on-surface mb-1">Telefon Raqami</label>
                <input
                  type="text"
                  placeholder="+998 90 123-45-67"
                  value={newPatientForm.phone}
                  onChange={(e) => setNewPatientForm({ ...newPatientForm, phone: e.target.value })}
                  className="w-full p-2.5 bg-surface-container-low border border-outline-variant/50 rounded-xl text-sm focus:outline-none focus:border-primary text-on-surface"
                />
              </div>

              <div>
                <label className="block font-bold text-on-surface mb-1">Klinik Holati</label>
                <select
                  value={newPatientForm.medical_status}
                  onChange={(e) => setNewPatientForm({ ...newPatientForm, medical_status: e.target.value })}
                  className="w-full p-2.5 bg-surface-container-low border border-outline-variant/50 rounded-xl text-sm focus:outline-none focus:border-primary text-on-surface font-medium"
                >
                  <option value="Nazoratda">Nazoratda (Ambulator)</option>
                  <option value="Statsionar">Statsionar (Shifoxonada)</option>
                  <option value="Chiqarilgan">Chiqarilgan</option>
                </select>
              </div>

              <div className="pt-3 border-t border-outline-variant/30 flex items-center justify-end gap-2">
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="px-4 py-2 bg-surface-container-high text-on-surface rounded-xl font-bold hover:bg-surface-container-highest cursor-pointer"
                >
                  Bekor qilish
                </button>
                <button
                  type="submit"
                  className="px-5 py-2 bg-primary text-white rounded-xl font-bold hover:bg-primary-container shadow-md cursor-pointer"
                >
                  Saqlash
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
