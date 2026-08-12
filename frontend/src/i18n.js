/**
 * Multilingual Translation System (Uzbek, Russian, English) for AvicennaX AI.
 */

export const translations = {
  uz: {
    // Navigation
    nav_dashboard: "Asosiy Panel",
    nav_patients: "Bemorlar",
    nav_archive: "Arxiv",
    nav_analytics: "Yo'riqnoma",
    nav_settings: "Sozlamalar",
    nav_new_analysis: "Yangi tahlil",

    // Header & System
    doctor_title: "Bosh Radiolog-Pulmonolog",
    system_status: "Yangi rentgenogramma va patologiyani aniqlash tizimi",

    // Dashboard & Upload
    dash_title: "Asosiy ish paneli",
    dash_dropzone_title: "O'pka rentgen suratini bu yerga tashlang",
    dash_dropzone_desc: "yoki kompyuter o'zidan tanlang. PNG, JPG, DICOM (.dcm) va PDF (.pdf) formatlari qo'llab-quvvatlanadi.",
    dash_btn_select_file: "Kompyuterdan tanlash",
    dash_privacy_notice: "Bemor ma'lumotlari HIPAA standarti asosida shifrlangan.",
    dash_ai_calculating: "AvicennaX AI tahlil modellari hisoblamoqda.",
    
    // Patient Match Modal
    modal_card_title: "Bemor Kartochkasi Ma'lumotlari",
    modal_card_subtitle: "Rentgen tahlilini bemor tarixiga biriktiring",
    modal_match_found: "Tizimda mos bemorlar topildi",
    modal_create_new: "Yangi bemor sifatida yaratish",
    modal_ask_select_existing: "Mavjud kartochkani tanlaysizmi yoki yangi yaratasizmi?",
    label_last_name: "Familiya",
    label_first_name: "Ism",
    label_age: "Yosh",
    label_gender: "Jinsi",
    gender_male: "Erkak",
    gender_female: "Ayol",
    btn_cancel: "Bekor qilish",
    btn_start_analysis: "Tahlilni Boshlash",
    placeholder_last_name: "Masalan: Azizov",
    placeholder_first_name: "Masalan: Bekzod",

    // Patient Directory (Bemorlar)
    patients_title: "Bemorlar Katalogi va Shaxsiy Kartochkalar",
    patients_subtitle: "Har bir bemor bo'yicha rentgenogrammalar dinamikasi va klinik tarixi",
    btn_register_patient: "Yangi Bemor Qo'shish",
    search_patients_placeholder: "Bemor ismi, ID yoki telefon raqami bo'yicha qidiruv...",
    card_view_history: "Klinik Tarix va Rentgenogrammalar",
    card_new_scan: "Yangi Rentgen Yuklash",
    patient_status_monitoring: "Nazoratda",
    patient_status_hospitalized: "Statsionar",
    patient_status_discharged: "Chiqarilgan",

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
    status_approved: "Tasdiqlangan",
    status_pending: "Ko'rik kutilmoqda",

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
    label_opacity: "Qatlam Shaffofligi",

    // Modals & Chat
    modal_register_title: "Yangi Bemor Ro'yxatdan O'tkazish",
    chat_assistant_name: "SSV AI Yordamchi",
    chat_status_online: "Tibbiy maslahat • Onlayn",
    chat_placeholder: "Simptom yoki savol yozing...",
    btn_send: "Yuborish"
  },

  ru: {
    // Navigation
    nav_dashboard: "Главная Панель",
    nav_patients: "Пациенты",
    nav_archive: "Архив снимков",
    nav_analytics: "Инструкция",
    nav_settings: "Настройки",
    nav_new_analysis: "Новый анализ",

    // Header & System
    doctor_title: "Главный Радиолог-Пульмонолог",
    system_status: "Система распознавания рентгенограмм и патологий",

    // Dashboard & Upload
    dash_title: "Главная рабочая панель",
    dash_dropzone_title: "Перетащите рентгеновский снимок сюда",
    dash_dropzone_desc: "или выберите с компьютера. Поддерживаются форматы PNG, JPG, DICOM (.dcm) и PDF (.pdf).",
    dash_btn_select_file: "Выбрать с компьютера",
    dash_privacy_notice: "Данные пациентов зашифрованы по стандарту HIPAA.",
    dash_ai_calculating: "Модели ИИ AvicennaX выполняют вычисления.",

    // Patient Match Modal
    modal_card_title: "Данные карточки пациента",
    modal_card_subtitle: "Привяжите рентгенологический анализ к истории пациента",
    modal_match_found: "В системе найдены совпадающие пациенты",
    modal_create_new: "Создать как нового пациента",
    modal_ask_select_existing: "Выберите существующую карту или создайте новую?",
    label_last_name: "Фамилия",
    label_first_name: "Имя",
    label_age: "Возраст",
    label_gender: "Пол",
    gender_male: "Мужской",
    gender_female: "Женский",
    btn_cancel: "Отмена",
    btn_start_analysis: "Начать Анализ",
    placeholder_last_name: "Например: Азизов",
    placeholder_first_name: "Например: Бекзод",

    // Patient Directory (Bemorlar)
    patients_title: "Каталог пациентов и медицинские карты",
    patients_subtitle: "Динамика рентгенограмм и клиническая история по каждому пациенту",
    btn_register_patient: "Зарегистрировать пациента",
    search_patients_placeholder: "Поиск по имени пациента, ID или телефону...",
    card_view_history: "История и снимки",
    card_new_scan: "Загрузить новый снимок",
    patient_status_monitoring: "На наблюдении",
    patient_status_hospitalized: "Стационар",
    patient_status_discharged: "Выписан",

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
    status_approved: "Утверждено",
    status_pending: "Ожидает осмотра",

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
    label_opacity: "Прозрачность слоя",

    // Modals & Chat
    modal_register_title: "Регистрация нового пациента",
    chat_assistant_name: "ИИ Ассистент Минздрава",
    chat_status_online: "Медицинская консультация • Онлайн",
    chat_placeholder: "Введите симптом или вопрос...",
    btn_send: "Отправить"
  },

  en: {
    // Navigation
    nav_dashboard: "Dashboard",
    nav_patients: "Patients",
    nav_archive: "Archive",
    nav_analytics: "Guide",
    nav_settings: "Settings",
    nav_new_analysis: "New Analysis",

    // Header & System
    doctor_title: "Chief Radiologist-Pulmonologist",
    system_status: "Chest X-ray and Pathology Recognition System",

    // Dashboard & Upload
    dash_title: "Main Workspace Panel",
    dash_dropzone_title: "Drag and drop chest X-ray image here",
    dash_dropzone_desc: "or choose from your computer. Formats supported: PNG, JPG, DICOM (.dcm), and PDF (.pdf).",
    dash_btn_select_file: "Select from Computer",
    dash_privacy_notice: "Patient data is encrypted under HIPAA standards.",
    dash_ai_calculating: "AvicennaX AI inference models are processing.",

    // Patient Match Modal
    modal_card_title: "Patient Demographic Information",
    modal_card_subtitle: "Attach X-ray analysis to existing patient timeline",
    modal_match_found: "Matching patients found in system",
    modal_create_new: "Create as new patient",
    modal_ask_select_existing: "Select an existing card or register new?",
    label_last_name: "Last Name",
    label_first_name: "First Name",
    label_age: "Age",
    label_gender: "Gender",
    gender_male: "Male",
    gender_female: "Female",
    btn_cancel: "Cancel",
    btn_start_analysis: "Start Analysis",
    placeholder_last_name: "Example: Azizov",
    placeholder_first_name: "Example: Bekzod",

    // Patient Directory (Bemorlar)
    patients_title: "Patient Directory & Medical Cards",
    patients_subtitle: "Longitudinal X-ray timeline progression and clinical history per patient",
    btn_register_patient: "Register New Patient",
    search_patients_placeholder: "Search by patient name, ID, or phone number...",
    card_view_history: "Clinical History & Scans",
    card_new_scan: "Upload New Scan",
    patient_status_monitoring: "Outpatient",
    patient_status_hospitalized: "Inpatient",
    patient_status_discharged: "Discharged",

    // Scan Archive (Arxiv)
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
    status_approved: "Approved",
    status_pending: "Pending Review",

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
    label_opacity: "Overlay Opacity",

    // Modals & Chat
    modal_register_title: "Register New Patient Profile",
    chat_assistant_name: "MOH AI Assistant",
    chat_status_online: "Medical Advice • Online",
    chat_placeholder: "Type symptom or question...",
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
