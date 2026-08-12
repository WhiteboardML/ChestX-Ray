/**
 * Multilingual Translation System (Uzbek, Russian, English) for AvicennaX AI.
 */

export const translations = {
  uz: {
    // Navigation
    nav_dashboard: "Boshqaruv Paneli",
    nav_patients: "Bemorlar",
    nav_archive: "Rentgen Arxivi",
    nav_analytics: "Analitika & Model",
    nav_settings: "Sozlamalar",
    nav_new_analysis: "Yangi Tahlil Upload",

    // Header & User
    doctor_title: "Bosh Radiolog-Pulmonolog",
    system_status: "AI Tizim Tayyor",

    // Dashboard View
    dash_title: "AvicennaX Radiologik Tahlil Paneli",
    dash_subtitle: "Sun'iy intellekt asosida ko'krak qafasi rentgenogrammalarini tezkor diagnostika qilish va klinik dinamikani tahlil qilish",
    stats_total_scans: "Jami Rentgen Tahlillari",
    stats_pathologies: "Aniqlangan Patologiyalar",
    stats_accuracy: "Model Aniqligi (DenseNet-121)",
    stats_avg_time: "O'rtacha Tahlil Vaqti",

    // Patient Directory (Bemorlar)
    patients_title: "Bemorlar Katalogi va Shaxsiy Kartochkalar",
    patients_subtitle: "Har bir bemor bo'yicha rentgenogrammalar dinamikasi va klinik tarixi",
    btn_register_patient: "Yangi Bemor Qo'shish",
    search_patients_placeholder: "Bemor ismi, ID yoki telefon raqami bo'yicha qidiruv...",
    card_view_history: "Klinik Tarix va Rentgenogrammalar",
    card_new_scan: "Yangi Rentgen Yuklash",

    // Scan Archive (Arxiv)
    archive_title: "Rentgenogrammalar Arxivi va Repozitoriysi",
    archive_subtitle: "Tizimda ro'yxatdan o'tgan barcha rentgenogramma tasvirlari xronologik tartibda (so'nggi sana birinchi)",
    table_date: "Sana va Vaqt",
    table_scan_id: "Rentgen ID",
    table_patient: "Bemor Ma'lumotlari",
    table_preview: "Grad-CAM Tasvir",
    table_diagnosis: "AI Tashxis",
    table_prob: "Ishonchlilik",
    table_status: "Holati",
    table_actions: "Harakatlar",
    btn_details: "Tafsilotlar",

    // Result / Diagnostic View
    result_title: "Rentgenogramma Tahlili va Grad-CAM Vizualizatsiyasi",
    result_urgency_title: "SHOSHILINCH HOLLAT / URGENCY",
    result_urgency_critical: "🚨 O'TA SHOSHILINCH (Zudlik bilan vrach ko'rigi zarur!)",
    result_urgency_high: "⚠️ YUQORI SHOSHILINCHLIK",
    result_urgency_moderate: "⚡ O'RTA SHOSHILINCHLIK",
    result_urgency_normal: "ME'YORDA / NORMAL",
    result_normal_desc: "Sun'iy intellekt o'pka to'qimalarida hech qanday yaqqol patologiyani aniqlamadi. O'pka a'zolari me'yorda.",
    btn_compare: "Taqoslash",
    tab_simple: "Sodda xulosa",
    tab_raw_scores: "Raw Model Score'lar",
    tab_technical: "Rentgenologik hisobot (Texnik)",
    btn_approve: "Hisobotni Tasdiqlash",
    btn_print_pdf: "Chop Etish / PDF",

    // Modals & Chat
    modal_register_title: "Yangi Bemor Ro'yxatdan O'tkazish",
    chat_title: "AI Pulmonolog Yordamchi",
    chat_placeholder: "Tashxis yoki davolash bo'yicha savolingizni yozing...",
    btn_send: "Yuborish"
  },

  ru: {
    // Navigation
    nav_dashboard: "Панель управления",
    nav_patients: "Пациенты",
    nav_archive: "Архив снимков",
    nav_analytics: "Аналитика и Модель",
    nav_settings: "Настройки",
    nav_new_analysis: "Загрузить рентген",

    // Header & User
    doctor_title: "Главный Радиолог-Пульмонолог",
    system_status: "ИИ Система Готова",

    // Dashboard View
    dash_title: "Панель Радиологического Анализа AvicennaX",
    dash_subtitle: "Экспресс-диагностика рентгенограмм грудной клетки и анализ клинической динамики на основе ИИ",
    stats_total_scans: "Всего анализов рентгена",
    stats_pathologies: "Выявленные патологии",
    stats_accuracy: "Точность модели (DenseNet-121)",
    stats_avg_time: "Среднее время анализа",

    // Patient Directory (Bemorlar)
    patients_title: "Каталог пациентов и медицинские карты",
    patients_subtitle: "Динамика рентгенограмм и клиническая история по каждому пациенту",
    btn_register_patient: "Зарегистрировать пациента",
    search_patients_placeholder: "Поиск по имени пациента, ID или телефону...",
    card_view_history: "История и рентгенограммы",
    card_new_scan: "Загрузить новый снимок",

    // Scan Archive (Arxiv)
    archive_title: "Архив и репозиторий рентгенограмм",
    archive_subtitle: "Все зарегистрированные снимки в хронологическом порядке (сначала новые)",
    table_date: "Дата и Время",
    table_scan_id: "ID Снимка",
    table_patient: "Данные пациента",
    table_preview: "Grad-CAM Превью",
    table_diagnosis: "ИИ Диагноз",
    table_prob: "Вероятность",
    table_status: "Статус",
    table_actions: "Действия",
    btn_details: "Подробнее",

    // Result / Diagnostic View
    result_title: "Анализ рентгенограммы и Grad-CAM Визуализация",
    result_urgency_title: "СРОЧНОЕ СОСТОЯНИЕ / URGENCY",
    result_urgency_critical: "🚨 СРОЧНЫЙ ВЫЗОВ (Требуется осмотр врача!)",
    result_urgency_high: "⚠️ ВЫСОКАЯ СРОЧНОСТЬ",
    result_urgency_moderate: "⚡ СРЕДНЯЯ СРОЧНОСТЬ",
    result_urgency_normal: "В НОРМЕ / NORMAL",
    result_normal_desc: "Искусственный интеллект не выявил явных патологических изменений в легочной ткани. Органы грудной клетки в норме.",
    btn_compare: "Сравнить",
    tab_simple: "Краткое заключение",
    tab_raw_scores: "Сырые балы модели",
    tab_technical: "Радиологический отчет (Технический)",
    btn_approve: "Утвердить отчет",
    btn_print_pdf: "Печать / PDF",

    // Modals & Chat
    modal_register_title: "Регистрация нового пациента",
    chat_title: "ИИ Ассистент Пульмонолога",
    chat_placeholder: "Задайте вопрос по диагнозу или протоколу лечения...",
    btn_send: "Отправить"
  },

  en: {
    // Navigation
    nav_dashboard: "Dashboard",
    nav_patients: "Patients",
    nav_archive: "Scan Archive",
    nav_analytics: "Analytics & Model",
    nav_settings: "Settings",
    nav_new_analysis: "Upload Scan",

    // Header & User
    doctor_title: "Chief Radiologist-Pulmonologist",
    system_status: "AI System Ready",

    // Dashboard View
    dash_title: "AvicennaX Radiological Analysis Dashboard",
    dash_subtitle: "AI-powered rapid chest X-ray diagnostics and clinical evolution monitoring",
    stats_total_scans: "Total X-ray Analyses",
    stats_pathologies: "Pathologies Detected",
    stats_accuracy: "Model Accuracy (DenseNet-121)",
    stats_avg_time: "Avg Analysis Time",

    // Patient Directory
    patients_title: "Patient Directory & Medical Cards",
    patients_subtitle: "Clinical timeline history and longitudinal X-ray progression per patient",
    btn_register_patient: "Register New Patient",
    search_patients_placeholder: "Search by patient name, ID, or phone number...",
    card_view_history: "Clinical History & Scans",
    card_new_scan: "Upload New Scan",

    // Scan Archive
    archive_title: "X-ray Scan Archive Repository",
    archive_subtitle: "Chronological repository log of all registered X-ray scans (newest date first)",
    table_date: "Date & Time",
    table_scan_id: "Scan ID",
    table_patient: "Patient Information",
    table_preview: "Grad-CAM Preview",
    table_diagnosis: "AI Diagnosis",
    table_prob: "Probability",
    table_status: "Status",
    table_actions: "Actions",
    btn_details: "View Details",

    // Result / Diagnostic View
    result_title: "X-ray Analysis & Grad-CAM Heatmap Visualization",
    result_urgency_title: "URGENCY LEVEL",
    result_urgency_critical: "🚨 CRITICAL URGENCY (Immediate physician review required!)",
    result_urgency_high: "⚠️ HIGH URGENCY",
    result_urgency_moderate: "⚡ MODERATE URGENCY",
    result_urgency_normal: "NORMAL",
    result_normal_desc: "Artificial intelligence detected no pathology. Lung structures are normal.",
    btn_compare: "Compare Scans",
    tab_simple: "Patient Summary",
    tab_raw_scores: "Raw Model Scores",
    tab_technical: "Radiological Report (Technical)",
    btn_approve: "Approve Report",
    btn_print_pdf: "Print / PDF Report",

    // Modals & Chat
    modal_register_title: "Register New Patient Profile",
    chat_title: "AI Pulmonologist Assistant",
    chat_placeholder: "Ask a medical question regarding diagnosis or treatment...",
    btn_send: "Send"
  }
};

/**
 * Pathology Name Translator Helper
 */
export const getPathologyTranslation = (name, lang = 'uz') => {
  const dict = {
    Norma: { uz: "Norma (Me'yorda)", ru: "Норма", en: "Normal" },
    Atelectasis: { uz: "Atelektaz", ru: "Ателектаз", en: "Atelectasis" },
    Consolidation: { uz: "Konsolidatsiya", ru: "Консолидация", en: "Consolidation" },
    Infiltration: { uz: "Infiltratsiya", ru: "Инфильтрация", en: "Infiltration" },
    Pneumothorax: { uz: "Pnevmotoraks", ru: "Пневмоторакс", en: "Pneumothorax" },
    Edema: { uz: "O'pka shishi", ru: "Отек легких", en: "Edema" },
    Emphysema: { uz: "Emfizema", ru: "Эмфизема", en: "Emphysema" },
    Fibrosis: { uz: "Fibroz", ru: "Фиброз", en: "Fibrosis" },
    Effusion: { uz: "Plevral efuziya", ru: "Плевральный выпот", en: "Pleural Effusion" },
    Pneumonia: { uz: "Pnevmoniya", ru: "Пневмония", en: "Pneumonia" },
    Pleural_Thickening: { uz: "Plevra qalinlashishi", ru: "Утолщение плевры", en: "Pleural Thickening" },
    Cardiomegaly: { uz: "Kardiomegaliya", ru: "Кардиомегалия", en: "Cardiomegaly" },
    Nodule: { uz: "O'pka tuguni", ru: "Узелок легкого", en: "Lung Nodule" },
    Mass: { uz: "Hajmli hosila", ru: "Объемное образование", en: "Lung Mass" },
    Hernia: { uz: "Churra", ru: "Грыжа", en: "Hernia" },
    "Lung Lesion": { uz: "O'pka zararlanishi", ru: "Поражение легких", en: "Lung Lesion" },
    Fracture: { uz: "Qovurg'a sinishi", ru: "Перелом ребра", en: "Rib Fracture" },
    "Lung Opacity": { uz: "O'pka xiralashishi", ru: "Затемнение легкого", en: "Lung Opacity" },
    "Enlarged Cardiomediastinum": { uz: "Kengaygan kardiomediastinum", ru: "Расширение средостения", en: "Enlarged Cardiomediastinum" }
  };

  if (!name) return "";
  if (dict[name] && dict[name][lang]) {
    return dict[name][lang];
  }
  return name;
};
