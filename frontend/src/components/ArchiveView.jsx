import React from 'react';

export default function ArchiveView({ patients, onSelectPatient }) {
  const patientCount = patients.length;

  return (
    <div className="flex-1 flex flex-col gap-6">
      <div className="flex justify-between items-center">
        <h2 className="font-geist text-2xl font-bold text-primary">Tahlil Tizimi Arxiv</h2>
        <span className="text-xs font-bold text-on-surface-variant uppercase tracking-widest bg-surface-container px-3 py-1.5 rounded-full">
          {patientCount} bemor
        </span>
      </div>
      
      {/* Table Card Container */}
      <div className="bg-surface-container-lowest rounded-3xl shadow-xl overflow-hidden border border-outline-variant/30">
        <table className="w-full border-collapse text-left">
          <thead>
            <tr className="bg-surface-container-low text-xs font-bold text-on-surface-variant uppercase tracking-wider border-b border-outline-variant/50">
              <th className="p-5">ID</th>
              <th className="p-5">Bemor ismi</th>
              <th className="p-5">Yoshi / Jinsi</th>
              <th className="p-5">Tahlillar soni</th>
              <th className="p-5">Oxirgi Tashxis</th>
              <th className="p-5">Ishonchli darajasi</th>
              <th className="p-5">Holati</th>
              <th className="p-5">Harakatlar</th>
            </tr>
          </thead>
          <tbody className="text-sm divide-y divide-outline-variant/20">
            {patients.length > 0 ? (
              patients.map((pat) => {
                const isApproved = pat.status === 'Tasdiqlangan';
                const statusClass = isApproved 
                  ? 'bg-success/15 border-success/30 text-success' 
                  : 'bg-[#eca52b]/15 border-[#eca52b]/30 text-[#854d0e]';
                
                const diagClass = pat.diagnosis === 'Norma'
                  ? 'bg-success/10 text-success'
                  : 'bg-error/10 text-error';

                const scanCount = pat.scans ? pat.scans.length : 1;

                return (
                  <tr 
                    key={pat.id} 
                    onClick={() => onSelectPatient(pat)}
                    className="hover:bg-surface-container-low transition-colors cursor-pointer"
                  >
                    <td className="p-5 font-mono text-xs font-semibold text-primary">{pat.id}</td>
                    <td className="p-5 font-semibold text-on-surface">{pat.name}</td>
                    <td className="p-5 text-on-surface-variant font-medium">{pat.age} yosh / {pat.gender}</td>
                    <td className="p-5">
                      <span className="px-2.5 py-1 rounded-full text-xs font-bold bg-primary/10 text-primary border border-primary/20">
                        {scanCount} ta rentgen
                      </span>
                    </td>
                    <td className="p-5">
                      <span className={`px-2.5 py-1 rounded-full text-xs font-semibold ${diagClass}`}>
                        {pat.diagnosis}
                      </span>
                    </td>
                    <td className="p-5 font-bold text-secondary">{pat.probability}%</td>
                    <td className="p-5">
                      <span className={`px-3 py-1 rounded-full border text-[11px] font-bold ${statusClass}`}>
                        {pat.status}
                      </span>
                    </td>
                    <td className="p-5">
                      <button 
                        onClick={(e) => {
                          e.stopPropagation();
                          onSelectPatient(pat);
                        }}
                        className="px-3 py-1.5 bg-primary text-white rounded-lg text-xs font-semibold hover:bg-primary-container transition-all cursor-pointer"
                      >
                        Bemor Kartochkasi
                      </button>
                    </td>
                  </tr>
                );
              })
            ) : (
              <tr>
                <td colSpan="8" className="p-5 text-center text-on-surface-variant font-medium">
                  Hozircha tahlil natijalari mavjud emas.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
