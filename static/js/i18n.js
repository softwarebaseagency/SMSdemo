/* ============================================================================
   Lezan SMS — Interface language
   English / Kurdish (Sorani) / Arabic, with a full RTL layout flip.
   Chrome is translated (navigation, titles, KPI labels, actions, statuses);
   record data stays in its source script, as it would in the real system.
   ========================================================================= */
(function (global) {
  "use strict";

  var LANGS = {
    en: { name: "English",  native: "English", dir: "ltr", short: "EN" },
    ku: { name: "Kurdish",  native: "کوردی",   dir: "rtl", short: "KU" },
    ar: { name: "Arabic",   native: "العربية", dir: "rtl", short: "AR" }
  };

  var DICT = {
    /* ---- Product & shell ------------------------------------------------ */
    "app.name":            ["Lezan SMS", "سیستەمی لەزان", "نظام ليزان"],
    "app.school":          ["Lezan English Private School & Kindergarten",
                            "قوتابخانەی ئەهلی ئینگلیزی لەزان و باخچەی ساوایان",
                            "مدرسة ليزان الأهلية الإنجليزية وروضة الأطفال"],
    "app.schoolShort":     ["Lezan Private School", "قوتابخانەی ئەهلی لەزان", "مدرسة ليزان الأهلية"],
    "app.tagline":         ["School Management System", "سیستەمی بەڕێوەبردنی قوتابخانە", "نظام إدارة المدرسة"],
    "app.byBase":          ["Built by Base Agency", "دروستکراوە لەلایەن بەیس ئەیجەنسی", "من تطوير بيس إيجنسي"],
    "app.demo":            ["Demo preview", "پێشبینینی نموونەیی", "معاينة تجريبية"],

    /* ---- Navigation groups ---------------------------------------------- */
    "nav.overview":        ["Overview", "گشتی", "نظرة عامة"],
    "nav.lifecycle":       ["Student lifecycle", "خولی قوتابی", "دورة حياة الطالب"],
    "nav.academics":       ["Academics", "خوێندن", "الشؤون الأكاديمية"],
    "nav.finance":         ["Finance", "دارایی", "المالية"],
    "nav.people":          ["People & access", "کەسان و دەستپێگەیشتن", "الأشخاص والصلاحيات"],

    /* ---- The ten modules ------------------------------------------------ */
    "mod.admissions":      ["Admissions & Registration", "وەرگرتن و تۆمارکردن", "القبول والتسجيل"],
    "mod.students":        ["Student Records", "تۆماری قوتابیان", "سجلات الطلاب"],
    "mod.attendance":      ["Attendance Management", "بەڕێوەبردنی ئامادەبوون", "إدارة الحضور"],
    "mod.timetable":       ["Timetable & Class Scheduling", "خشتەی وانە و پۆلەکان", "الجدول الدراسي وتنظيم الصفوف"],
    "mod.exams":           ["Examinations & Grade Management", "تاقیکردنەوە و نمرەکان", "الامتحانات وإدارة الدرجات"],
    "mod.fees":            ["Fees & Payment Management", "کرێ و پارەدان", "الرسوم وإدارة المدفوعات"],
    "mod.staff":           ["Teacher & Staff Records", "تۆماری مامۆستا و کارمەندان", "سجلات المعلمين والموظفين"],
    "mod.portal":          ["Parent & Student Portal", "پۆرتاڵی دایک‌وباوک و قوتابی", "بوابة أولياء الأمور والطلاب"],
    "mod.comms":           ["Communication & Notifications", "پەیوەندی و ئاگادارکردنەوە", "التواصل والإشعارات"],
    "mod.reports":         ["Operational Reports & Dashboards", "ڕاپۆرت و داشبۆردی کارگێڕی", "التقارير التشغيلية ولوحات المتابعة"],

    "mod.admissions.short":["Admissions", "وەرگرتن", "القبول"],
    "mod.students.short":  ["Students", "قوتابیان", "الطلاب"],
    "mod.attendance.short":["Attendance", "ئامادەبوون", "الحضور"],
    "mod.timetable.short": ["Timetable", "خشتە", "الجدول"],
    "mod.exams.short":     ["Examinations", "تاقیکردنەوە", "الامتحانات"],
    "mod.fees.short":      ["Fees & Payments", "کرێ و پارەدان", "الرسوم"],
    "mod.staff.short":     ["Staff", "کارمەندان", "الموظفون"],
    "mod.portal.short":    ["Portal", "پۆرتاڵ", "البوابة"],
    "mod.comms.short":     ["Communication", "پەیوەندی", "التواصل"],
    "mod.reports.short":   ["Dashboards", "داشبۆرد", "لوحات المتابعة"],

    "mod.label":           ["Module", "مۆدیوول", "الوحدة"],

    /* ---- Module purposes (from the proposal) ---------------------------- */
    "purpose.admissions":  ["Manage the full student intake process, from first application through confirmed registration.",
                            "بەڕێوەبردنی تەواوی پرۆسەی وەرگرتنی قوتابی، لە داواکاری یەکەمەوە تا تۆمارکردنی پەسەندکراو.",
                            "إدارة عملية استقبال الطلاب بالكامل، من الطلب الأول حتى التسجيل المعتمد."],
    "purpose.students":    ["One permanent, searchable and auditable profile for every student, for the whole time they are with Lezan.",
                            "یەک پرۆفایلی هەمیشەیی و گەڕانپێکراو بۆ هەر قوتابییەک، بە درێژایی ماوەی مانەوەی لە لەزان.",
                            "ملف دائم واحد قابل للبحث والتدقيق لكل طالب طوال فترة وجوده في ليزان."],
    "purpose.attendance":  ["Reliable daily attendance recording and reporting for students, classes and management.",
                            "تۆمارکردن و ڕاپۆرتی ڕۆژانەی ئامادەبوون بۆ قوتابیان، پۆلەکان و بەڕێوەبەرایەتی.",
                            "تسجيل الحضور اليومي وإعداد التقارير للطلاب والصفوف والإدارة."],
    "purpose.timetable":   ["Organise classes, teachers, subjects, rooms and periods into one structured timetable.",
                            "ڕێکخستنی پۆل، مامۆستا، بابەت، ژوور و کاتەکان لە یەک خشتەی ڕێکخراودا.",
                            "تنظيم الصفوف والمعلمين والمواد والقاعات والحصص في جدول واحد منظّم."],
    "purpose.exams":       ["Control examinations, marks, grading rules, report cards and academic progression.",
                            "کۆنترۆڵی تاقیکردنەوە، نمرە، یاساکانی هەڵسەنگاندن، کارتی ئەنجام و بەرەوپێشچوونی خوێندن.",
                            "التحكم في الامتحانات والدرجات وقواعد التقييم وبطاقات النتائج والترفيع الأكاديمي."],
    "purpose.fees":        ["A complete student financial ledger with reliable visibility over charges, collections and outstanding balances.",
                            "تۆماری دارایی تەواوی قوتابی لەگەڵ ڕوونی لەسەر بڕەکان، کۆکردنەوە و پاشماوەی نەدراو.",
                            "سجل مالي كامل للطالب مع رؤية موثوقة للرسوم والتحصيل والأرصدة المستحقة."],
    "purpose.staff":       ["Essential records for the teachers and staff who take part in school operations.",
                            "تۆماری پێویست بۆ مامۆستا و کارمەندانی بەشدار لە کارەکانی قوتابخانە.",
                            "السجلات الأساسية للمعلمين والموظفين المشاركين في العمليات المدرسية."],
    "purpose.portal":      ["Secure self-service access to approved information, without exposing internal administrative controls.",
                            "دەستپێگەیشتنی پارێزراو بە زانیاری پەسەندکراو، بەبێ کردنەوەی کۆنترۆڵە ناوخۆییەکان.",
                            "وصول ذاتي آمن إلى المعلومات المعتمدة دون كشف أدوات التحكم الإدارية الداخلية."],
    "purpose.comms":       ["Structured school-to-parent, school-to-student and internal communication.",
                            "پەیوەندی ڕێکخراو لەگەڵ دایک‌وباوک، قوتابیان و بەشە ناوخۆییەکان.",
                            "تواصل منظّم بين المدرسة وأولياء الأمور والطلاب والأقسام الداخلية."],
    "purpose.reports":     ["Role-appropriate management visibility over operational, academic and financial performance.",
                            "ڕوونی بەڕێوەبردن بەپێی ڕۆڵ بەسەر کارایی کارگێڕی، خوێندن و دارایی.",
                            "رؤية إدارية حسب الدور على الأداء التشغيلي والأكاديمي والمالي."],

    /* ---- Common actions -------------------------------------------------- */
    "act.search":          ["Search", "گەڕان", "بحث"],
    "act.searchStudents":  ["Search students, ID or guardian", "گەڕان بۆ قوتابی، ناسنامە یان سەرپەرشتیار", "ابحث عن طالب أو رقم أو ولي أمر"],
    "act.export":          ["Export", "هەناردن", "تصدير"],
    "act.print":           ["Print", "چاپ", "طباعة"],
    "act.filter":          ["Filter", "پاڵاوتن", "تصفية"],
    "act.newApplication":  ["New application", "داواکاری نوێ", "طلب جديد"],
    "act.addStudent":      ["Add student", "زیادکردنی قوتابی", "إضافة طالب"],
    "act.recordPayment":   ["Record payment", "تۆمارکردنی پارەدان", "تسجيل دفعة"],
    "act.newAnnouncement": ["New announcement", "ڕاگەیاندنی نوێ", "إعلان جديد"],
    "act.takeAttendance":  ["Take attendance", "تۆمارکردنی ئامادەبوون", "أخذ الحضور"],
    "act.addStaff":        ["Add staff member", "زیادکردنی کارمەند", "إضافة موظف"],
    "act.publishResults":  ["Publish results", "بڵاوکردنەوەی ئەنجامەکان", "نشر النتائج"],
    "act.editTimetable":   ["Edit timetable", "دەستکاری خشتە", "تعديل الجدول"],
    "act.viewAll":         ["View all", "بینینی هەموو", "عرض الكل"],
    "act.close":           ["Close", "داخستن", "إغلاق"],
    "act.openMenu":        ["Open navigation", "کردنەوەی ڕێنیشاندەر", "فتح القائمة"],
    "act.notifications":   ["Notifications", "ئاگادارکردنەوەکان", "الإشعارات"],
    "act.account":         ["Account", "هەژمار", "الحساب"],
    "act.signOut":         ["Sign out", "چوونەدەرەوە", "تسجيل الخروج"],
    "act.language":        ["Language", "زمان", "اللغة"],
    "act.chart":           ["Chart", "هێڵکاری", "رسم بياني"],
    "act.table":           ["Table", "خشتە", "جدول"],
    "act.previous":        ["Previous page", "پەڕەی پێشوو", "الصفحة السابقة"],
    "act.next":            ["Next page", "پەڕەی داهاتوو", "الصفحة التالية"],
    "act.skipToContent":   ["Skip to main content", "بازدان بۆ ناوەڕۆک", "تخطي إلى المحتوى"],

    /* ---- Common nouns ---------------------------------------------------- */
    "n.academicYear":      ["Academic year", "ساڵی خوێندن", "السنة الدراسية"],
    "n.student":           ["Student", "قوتابی", "الطالب"],
    "n.students":          ["Students", "قوتابیان", "الطلاب"],
    "n.studentId":         ["Student ID", "ناسنامەی قوتابی", "رقم الطالب"],
    "n.guardian":          ["Guardian", "سەرپەرشتیار", "ولي الأمر"],
    "n.division":          ["Division", "بەش", "القسم"],
    "n.grade":             ["Grade", "پۆل", "الصف"],
    "n.class":             ["Class", "پۆل", "الشعبة"],
    "n.section":           ["Section", "بەش", "الشعبة"],
    "n.status":            ["Status", "دۆخ", "الحالة"],
    "n.balance":           ["Balance", "پاشماوە", "الرصيد"],
    "n.outstanding":       ["Outstanding", "نەدراو", "المستحق"],
    "n.collected":         ["Collected", "کۆکراوە", "المُحصّل"],
    "n.expected":          ["Expected", "چاوەڕوانکراو", "المتوقع"],
    "n.teacher":           ["Teacher", "مامۆستا", "المعلم"],
    "n.subject":           ["Subject", "بابەت", "المادة"],
    "n.room":              ["Room", "ژوور", "القاعة"],
    "n.date":              ["Date", "بەروار", "التاريخ"],
    "n.amount":            ["Amount", "بڕ", "المبلغ"],
    "n.total":             ["Total", "کۆی گشتی", "الإجمالي"],
    "n.actions":           ["Actions", "کردارەکان", "الإجراءات"],
    "n.kindergarten":      ["Kindergarten", "باخچەی ساوایان", "رياض الأطفال"],
    "n.elementary":        ["Elementary", "سەرەتایی", "الابتدائي"],
    "n.highschool":        ["High School", "ئامادەیی", "الثانوي"],
    "n.allDivisions":      ["All divisions", "هەموو بەشەکان", "جميع الأقسام"],
    "n.iqd":               ["IQD", "دینار", "د.ع"],

    /* ---- Statuses -------------------------------------------------------- */
    "s.enrolled":          ["Enrolled", "تۆمارکراو", "مسجّل"],
    "s.approved":          ["Approved", "پەسەندکراو", "معتمد"],
    "s.underReview":       ["Under review", "لە پێداچوونەوەدا", "قيد المراجعة"],
    "s.docsPending":       ["Documents pending", "بەڵگەنامە چاوەڕوانە", "مستندات معلّقة"],
    "s.paymentPending":    ["Payment pending", "پارەدان چاوەڕوانە", "دفعة معلّقة"],
    "s.draft":             ["Draft", "ڕەشنووس", "مسودة"],
    "s.waitlist":          ["Waitlisted", "لە لیستی چاوەڕوانی", "قائمة الانتظار"],
    "s.rejected":          ["Rejected", "ڕەتکراوە", "مرفوض"],
    "s.present":           ["Present", "ئامادە", "حاضر"],
    "s.absent":            ["Absent", "ئامادەنەبوو", "غائب"],
    "s.late":              ["Late", "دواکەوتوو", "متأخر"],
    "s.excused":           ["Excused", "بە مۆڵەت", "بعذر"],
    "s.paid":              ["Paid", "دراوە", "مدفوع"],
    "s.partial":           ["Partial", "بەشێکی دراوە", "جزئي"],
    "s.overdue":           ["Overdue", "بەسەرچووە", "متأخر السداد"],
    "s.active":            ["Active", "چالاک", "نشط"],
    "s.published":         ["Published", "بڵاوکراوەتەوە", "منشور"],
    "s.scheduled":         ["Scheduled", "خشتەکراو", "مجدول"],
    "s.sent":              ["Sent", "نێردراوە", "مُرسل"],
    "s.locked":            ["Locked", "داخراو", "مقفل"],
    "s.promoted":          ["Promoted", "بەرزکراوەتەوە", "مُرفّع"],
    "s.graduated":         ["Graduated", "دەرچووە", "متخرج"],
    "s.repeated":          ["Repeated year", "ساڵی دووبارەکردەوە", "أعاد السنة"],

    /* ---- Dashboard / KPI labels ------------------------------------------ */
    "k.totalStudents":     ["Total enrolled students", "کۆی قوتابیانی تۆمارکراو", "إجمالي الطلاب المسجلين"],
    "k.newApplications":   ["New applications", "داواکاری نوێ", "الطلبات الجديدة"],
    "k.attendanceToday":   ["Attendance today", "ئامادەبوونی ئەمڕۆ", "حضور اليوم"],
    "k.outstandingTotal":  ["Total outstanding", "کۆی نەدراو", "إجمالي المستحقات"],
    "k.collectionRate":    ["Collection rate", "ڕێژەی کۆکردنەوە", "نسبة التحصيل"],
    "k.expectedRevenue":   ["Expected fee revenue", "داهاتی چاوەڕوانکراو", "الإيرادات المتوقعة"],
    "k.collectedRevenue":  ["Collected this year", "کۆکراوە ئەم ساڵە", "المُحصّل هذا العام"],
    "k.priorYearBalance":  ["Previous-year balances", "پاشماوەی ساڵانی پێشوو", "أرصدة الأعوام السابقة"],
    "k.missingDocs":       ["Missing documents", "بەڵگەنامەی کەمە", "مستندات ناقصة"],
    "k.staffCount":        ["Teaching & support staff", "مامۆستا و کارمەندان", "الكادر التعليمي والإداري"],
    "k.overdueInvoices":   ["Overdue invoices", "پسوڵەی بەسەرچوو", "فواتير متأخرة"],
    "k.avgAttendance":     ["Average attendance", "ناوەندی ئامادەبوون", "متوسط الحضور"],

    "k.vsLastYear":        ["vs last year", "بەراورد بە ساڵی ڕابردوو", "مقارنة بالعام الماضي"],
    "k.vsLastMonth":       ["vs last month", "بەراورد بە مانگی ڕابردوو", "مقارنة بالشهر الماضي"],
    "k.vsLastWeek":        ["vs last week", "بەراورد بە هەفتەی ڕابردوو", "مقارنة بالأسبوع الماضي"],
    "k.ofTarget":          ["of target", "لە ئامانج", "من الهدف"],

    /* ---- Chart / card titles --------------------------------------------- */
    "c.enrollmentTrend":   ["Enrolment by academic year", "تۆمارکردن بەپێی ساڵی خوێندن", "التسجيل حسب السنة الدراسية"],
    "c.collectionsTrend":  ["Collections against expected revenue", "کۆکردنەوە بەراورد بە داهاتی چاوەڕوانکراو", "التحصيل مقابل الإيرادات المتوقعة"],
    "c.studentsByDivision":["Students by division", "قوتابیان بەپێی بەش", "الطلاب حسب القسم"],
    "c.studentsByGrade":   ["Students by grade", "قوتابیان بەپێی پۆل", "الطلاب حسب الصف"],
    "c.attendanceTrend":   ["Attendance rate over the term", "ڕێژەی ئامادەبوون لە خولدا", "نسبة الحضور خلال الفصل"],
    "c.outstandingAging":  ["Outstanding balance by age", "پاشماوەی نەدراو بەپێی تەمەن", "المستحقات حسب مدة التأخير"],
    "c.admissionsPipeline":["Admissions pipeline", "قۆناغەکانی وەرگرتن", "مسار القبول"],
    "c.applicationsTrend": ["Applications received", "داواکاری وەرگیراو", "الطلبات المستلمة"],
    "c.gradeDistribution": ["Grade distribution", "دابەشبوونی نمرەکان", "توزيع الدرجات"],
    "c.paymentMethods":    ["Payment method breakdown", "دابەشبوونی شێوازی پارەدان", "توزيع طرق الدفع"],
    "c.attendanceHeatmap": ["Attendance by class and day", "ئامادەبوون بەپێی پۆل و ڕۆژ", "الحضور حسب الصف واليوم"],
    "c.staffByDepartment": ["Staff by department", "کارمەندان بەپێی بەش", "الموظفون حسب القسم"],
    "c.deliveryChannels":  ["Delivery by channel", "گەیاندن بەپێی کەناڵ", "الإرسال حسب القناة"],
    "c.recentActivity":    ["Recent audit activity", "چالاکی دوایین پشکنین", "نشاط التدقيق الأخير"],
    "c.subjectPerformance":["Average mark by subject", "ناوەندی نمرە بەپێی بابەت", "متوسط الدرجات حسب المادة"],

    /* ---- Demo notices ---------------------------------------------------- */
    "demo.readOnly":       ["Read-only demo", "نموونەی تەنیا خوێندنەوە", "عرض للقراءة فقط"],
    "demo.noEntry":        ["This is a visual demo. Records are illustrative and data entry is disabled.",
                            "ئەمە نموونەیەکی بینراوە. تۆمارەکان نموونەیین و تۆمارکردنی داتا ناچالاکە.",
                            "هذه معاينة بصرية. السجلات توضيحية وإدخال البيانات معطّل."],
    "demo.entryDisabled":  ["Data entry is disabled in this demo.", "تۆمارکردنی داتا لەم نموونەیەدا ناچالاکە.", "إدخال البيانات معطّل في هذه المعاينة."],
    "demo.continuity":     ["Financial continuity", "بەردەوامی دارایی", "الاستمرارية المالية"],
    "demo.continuityNote": ["Outstanding obligations stay attached to the permanent student ID across promotion, class movement and re-enrolment.",
                            "ئەرکە داراییە نەدراوەکان بە ناسنامەی هەمیشەیی قوتابییەوە دەمێننەوە لە کاتی بەرزکردنەوە، گواستنەوەی پۆل و تۆمارکردنەوەدا.",
                            "تبقى الالتزامات المالية مرتبطة برقم الطالب الدائم عبر الترفيع وتغيير الصف وإعادة التسجيل."],

    /* ---- Sign-in --------------------------------------------------------- */
    "login.title":         ["Sign in to Lezan SMS", "چوونەژوورەوە بۆ سیستەمی لەزان", "تسجيل الدخول إلى نظام ليزان"],
    "login.lede":          ["One controlled platform for the student journey — from application and registration through attendance, academics, finance, promotion and graduation.",
                            "یەک سەکۆی کۆنترۆڵکراو بۆ گەشتی قوتابی — لە داواکاری و تۆمارکردنەوە تا ئامادەبوون، خوێندن، دارایی، بەرزکردنەوە و دەرچوون.",
                            "منصة واحدة محكومة لرحلة الطالب — من الطلب والتسجيل إلى الحضور والدراسة والمالية والترفيع والتخرج."],
    "login.email":         ["Email or username", "ئیمەیل یان ناوی بەکارهێنەر", "البريد الإلكتروني أو اسم المستخدم"],
    "login.password":      ["Password", "وشەی نهێنی", "كلمة المرور"],
    "login.remember":      ["Keep me signed in", "چوونەژوورەوەم بهێڵەرەوە", "أبقني مسجلاً"],
    "login.forgot":        ["Forgot password?", "وشەی نهێنیت لەبیرچووە؟", "نسيت كلمة المرور؟"],
    "login.submit":        ["Sign in", "چوونەژوورەوە", "تسجيل الدخول"],
    "login.signingIn":     ["Signing in", "چوونەژوورەوە...", "جارٍ تسجيل الدخول"],
    "login.showPassword":  ["Show password", "پیشاندانی وشەی نهێنی", "إظهار كلمة المرور"],
    "login.hidePassword":  ["Hide password", "شاردنەوەی وشەی نهێنی", "إخفاء كلمة المرور"],
    "login.orRole":        ["Or explore as", "یان بگەڕێ وەک", "أو استعرض بصفة"],
    "login.hint":          ["No credentials needed — this is a demo. Select a role or sign straight in.",
                            "پێویست بە زانیاری چوونەژوورەوە ناکات — ئەمە نموونەیە. ڕۆڵێک هەڵبژێرە یان ڕاستەوخۆ بچۆ ژوورەوە.",
                            "لا حاجة لبيانات اعتماد — هذه معاينة. اختر دوراً أو ادخل مباشرة."],
    "login.quote":         ["One student identity. <em>Every year of their record.</em>",
                            "یەک ناسنامەی قوتابی. <em>هەموو ساڵێکی تۆمارەکەی.</em>",
                            "هوية طالب واحدة. <em>وكل سنة من سجله.</em>"],
    "login.quoteSub":      ["Promotion adds a new enrolment record — it never recreates the student, and never hides what is still owed from a previous year.",
                            "بەرزکردنەوە تۆمارێکی نوێی تۆمارکردن زیاد دەکات — هەرگیز قوتابییەکە لە نوێوە دروست ناکاتەوە و ئەوەی لە ساڵی پێشوو ماوە ناشارێتەوە.",
                            "الترفيع يضيف سجل تسجيل جديداً — ولا يعيد إنشاء الطالب، ولا يخفي ما تبقّى من العام السابق."],
    "login.tenModules":    ["Ten core modules", "دە مۆدیوولی سەرەکی", "عشر وحدات أساسية"],
    "login.languages":     ["Languages", "زمانەکان", "اللغات"],

    /* ---- Roles ----------------------------------------------------------- */
    "role.director":       ["Director", "بەڕێوەبەر", "المدير"],
    "role.registrar":      ["Registrar", "تۆمارکار", "المسجّل"],
    "role.finance":        ["Finance Manager", "بەڕێوەبەری دارایی", "مدير المالية"],
    "role.teacher":        ["Teacher", "مامۆستا", "معلم"],

    /* ---- Table / misc ---------------------------------------------------- */
    "t.showing":           ["Showing", "پیشاندانی", "عرض"],
    "t.of":                ["of", "لە", "من"],
    "t.noResults":         ["No matching records", "هیچ تۆمارێکی هاوتا نییە", "لا توجد سجلات مطابقة"],
    "t.noResultsHint":     ["Try a different search term or clear the filters.", "وشەیەکی تری بگەڕێ یان پاڵاوتنەکان بسڕەوە.", "جرّب مصطلح بحث آخر أو امسح عوامل التصفية."],
    "t.sortBy":            ["Sort by", "ڕیزکردن بەپێی", "ترتيب حسب"],
    "t.viewAsTable":       ["View chart data as a table", "بینینی داتای هێڵکاری وەک خشتە", "عرض بيانات الرسم كجدول"],
    "t.lastUpdated":       ["Last updated", "دوایین نوێکردنەوە", "آخر تحديث"]
  };

  var ORDER = ["en", "ku", "ar"];
  var current = "en";
  var listeners = [];

  function idx(lang) { var i = ORDER.indexOf(lang); return i < 0 ? 0 : i; }

  /** Translate a key. Falls back to English, then to the key itself. */
  function t(key) {
    var row = DICT[key];
    if (!row) { return key; }
    return row[idx(current)] || row[0] || key;
  }

  function get() { return current; }
  function dir() { return LANGS[current].dir; }
  function meta(lang) { return LANGS[lang || current]; }
  function all() { return ORDER.map(function (k) { return { code: k, meta: LANGS[k] }; }); }

  function set(lang) {
    if (!LANGS[lang] || lang === current) { return; }
    current = lang;
    try { localStorage.setItem("lezan.lang", lang); } catch (e) { /* private mode */ }
    apply();
    listeners.forEach(function (fn) { fn(lang); });
  }

  function onChange(fn) { listeners.push(fn); }

  /** Stamp dir/lang on the document and fill every [data-i18n] node. */
  function apply(root) {
    var scope = root || document;
    var m = LANGS[current];
    if (!root) {
      document.documentElement.lang = current;
      document.documentElement.dir = m.dir;
    }
    scope.querySelectorAll("[data-i18n]").forEach(function (el) {
      var key = el.getAttribute("data-i18n");
      var attr = el.getAttribute("data-i18n-attr");
      var value = t(key);
      if (attr) { el.setAttribute(attr, value.replace(/<[^>]+>/g, "")); }
      else if (el.hasAttribute("data-i18n-html")) { el.innerHTML = value; }
      else { el.textContent = value; }
    });
  }

  function restore() {
    var saved = null;
    try { saved = localStorage.getItem("lezan.lang"); } catch (e) { /* private mode */ }
    current = (saved && LANGS[saved]) ? saved : "en";
    apply();
    return current;
  }

  global.I18n = {
    t: t, set: set, get: get, dir: dir, meta: meta, all: all,
    apply: apply, restore: restore, onChange: onChange
  };
})(window);
