from typing import Dict, Any


class ReportGenerator:
    """
    Service to compile patient diagnostic reports as printable HTML documents.
    """

    @staticmethod
    def compile_html_report(patient: Dict[str, Any]) -> str:
        """
        Generate a styled HTML diagnostic report based on patient profiles and scan predictions.
        """
        # Filter feasible scores (>= 0.05 or matching the primary diagnosis)
        raw_scores = patient.get('raw_scores', [])
        feasible_scores = [
            p for p in raw_scores
            if p.get('score', 0) >= 0.05 or p.get('disease') == patient.get('diagnosis') or p.get('disease_uz') == patient.get('diagnosis')
        ]
        
        # Fallback to top 3 scores if no score meets the 0.05 threshold
        if not feasible_scores:
            feasible_scores = sorted(raw_scores, key=lambda x: x.get('score', 0), reverse=True)[:3]
        else:
            feasible_scores = sorted(feasible_scores, key=lambda x: x.get('score', 0), reverse=True)

        raw_scores_rows = "".join([
            f"<tr>"
            f"<td><strong>{p.get('disease_uz', p['disease'])}</strong> <span style='color:#64748b; font-size:11px;'>({p['disease']})</span></td>"
            f"<td>{p['score']:.4f} ({p['score']*100:.1f}%)</td>"
            f"</tr>"
            for p in feasible_scores
        ])

        html_content = f"""<!DOCTYPE html>
<html lang="uz">
<head>
    <meta charset="UTF-8">
    <title>Tibbiy Diagnostika Hisoboti - {patient['id']}</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 40px; color: #1f2937; line-height: 1.6; background: #fff; }}
        .header {{ border-bottom: 2px solid #2563eb; padding-bottom: 15px; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center; }}
        .title {{ font-size: 22px; font-weight: 700; color: #1e40af; }}
        .badge {{ background-color: #dbeafe; color: #1e40af; padding: 6px 14px; border-radius: 20px; font-size: 12px; font-weight: 700; uppercase; }}
        .section {{ margin-bottom: 20px; padding: 16px; background: #f8fafc; border-radius: 12px; border: 1px solid #e2e8f0; }}
        .section-title {{ font-size: 13px; font-weight: 700; color: #475569; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 10px; }}
        .field {{ margin-bottom: 8px; font-size: 14px; }}
        .field-label {{ font-weight: 600; color: #64748b; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
        th, td {{ border: 1px solid #e2e8f0; padding: 10px 14px; text-align: left; font-size: 13px; }}
        th {{ background-color: #f1f5f9; font-weight: 700; color: #334155; }}
        .footer {{ margin-top: 40px; border-top: 1px solid #cbd5e1; padding-top: 15px; font-size: 12px; color: #64748b; display: flex; justify-content: space-between; }}
    </style>
</head>
<body onload="window.print()">
    <div class="header">
        <div>
            <div class="title">AvicennaX AI - Chest X-ray Diagnostika Hisoboti</div>
            <div style="font-size: 12px; color: #64748b;">SSV AI Standardi • TorchXRayVision DenseNet-121</div>
        </div>
        <span class="badge">{patient.get('status', "Ko'rik kutilmoqda")}</span>
    </div>

    <div class="section">
        <div class="section-title">Bemor Ma'lumotlari</div>
        <div class="field"><span class="field-label">ID:</span> {patient['id']}</div>
        <div class="field"><span class="field-label">F.I.SH.:</span> {patient['name']}</div>
        <div class="field"><span class="field-label">Yosh / Jins:</span> {patient['age']} yosh, {patient['gender']}</div>
        <div class="field"><span class="field-label">Yuklangan vaqt:</span> {patient.get('upload_time', 'N/A')}</div>
    </div>

    <div class="section">
        <div class="section-title">AI Tahlil Natijasi</div>
        <div class="field"><span class="field-label">Asosiy Diagnostik Xulosa:</span> <strong>{patient['diagnosis']}</strong> ({patient['probability']}%)</div>
        <div class="field"><span class="field-label">Sodda Tushuntirish:</span> {patient['findings'].get('simple_lang', '')}</div>
    </div>

    <div class="section">
        <div class="section-title">Asosiy Ehtimoliy Patologiyalar (Feasible Findings)</div>
        <table>
            <thead>
                <tr>
                    <th>Patologiya Nomi (Kasallik)</th>
                    <th>Tibbiy Ehtimollik (Score / %)</th>
                </tr>
            </thead>
            <tbody>
                {raw_scores_rows}
            </tbody>
        </table>
    </div>

    <div class="footer">
        <div>Tasdiqladi: {patient.get('approved_by') or 'Kutilmoqda'}</div>
        <div>Vaqt: {patient.get('approved_time') or 'N/A'}</div>
    </div>
</body>
</html>"""
        return html_content
