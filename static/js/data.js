/* ============================================================================
   Lezan SMS — Illustrative dataset
   Every record here is fabricated for demonstration. Names, IDs, marks and
   amounts are invented and do not describe any real student, family or staff
   member. Generation is seeded, so the demo looks identical on every reload.
   ========================================================================= */
(function (global) {
  "use strict";

  /* ---- Seeded PRNG (mulberry32) — stable demo, no random churn --------- */
  function rng(seed) {
    var a = seed >>> 0;
    return function () {
      a |= 0; a = (a + 0x6D2B79F5) | 0;
      var t = Math.imul(a ^ (a >>> 15), 1 | a);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }
  var R = rng(20260829);
  function pick(list) { return list[Math.floor(R() * list.length)]; }
  function int(min, max) { return min + Math.floor(R() * (max - min + 1)); }
  function chance(p) { return R() < p; }

  /* ---- Name pools ------------------------------------------------------ */
  var MALE = ["Aram", "Rebin", "Hemn", "Karwan", "Dilan", "Zana", "Botan", "Peshraw",
    "Hawkar", "Shwan", "Rawand", "Halgurd", "Diyar", "Serwan", "Barzan", "Aland",
    "Sirwan", "Rekan", "Balen", "Azad", "Hoshyar", "Kamaran", "Rozhgar", "Soran",
    "Bahoz", "Dashty", "Lawen", "Haval", "Yusuf", "Omar", "Hassan", "Ranj"];

  var FEMALE = ["Lana", "Rezan", "Shilan", "Avan", "Nma", "Roj", "Hana", "Zhyan",
    "Bahar", "Nazdar", "Chnar", "Awaz", "Payman", "Delan", "Hawnaz", "Rangin",
    "Sazan", "Vian", "Helin", "Nian", "Trifa", "Zhala", "Berivan", "Lava",
    "Rojin", "Shanya", "Darya", "Mariam", "Zainab", "Sara", "Alan", "Bahra"];

  var FAMILY = ["Ahmed", "Muhammed", "Rashid", "Hussein", "Salih", "Omar", "Karim",
    "Aziz", "Jamal", "Sabir", "Tahir", "Hamid", "Nuri", "Faris", "Ibrahim",
    "Qadir", "Mahmood", "Bakr", "Sadiq", "Anwar", "Shirwan", "Kamal", "Mustafa",
    "Khalid", "Younis", "Rasul", "Latif", "Sherko", "Baban", "Nawzad"];

  /* ---- School structure ------------------------------------------------ */
  var YEARS = ["2022-2023", "2023-2024", "2024-2025", "2025-2026", "2026-2027"];
  var CURRENT_YEAR = "2026-2027";

  var DIVISIONS = [
    { id: "kg", key: "n.kindergarten", label: "Kindergarten", grades: ["KG1", "KG2", "KG3"], tuition: 2600000 },
    { id: "el", key: "n.elementary",   label: "Elementary",
      grades: ["Grade 1", "Grade 2", "Grade 3", "Grade 4", "Grade 5", "Grade 6"], tuition: 3200000 },
    { id: "hs", key: "n.highschool",   label: "High School",
      grades: ["Grade 7", "Grade 8", "Grade 9", "Grade 10", "Grade 11", "Grade 12"], tuition: 3900000 }
  ];

  var GRADE_INDEX = {};
  DIVISIONS.forEach(function (d) {
    d.grades.forEach(function (g) { GRADE_INDEX[g] = d; });
  });
  var ALL_GRADES = DIVISIONS.reduce(function (acc, d) { return acc.concat(d.grades); }, []);

  var SECTIONS = ["A", "B"];

  var SUBJECTS = [
    { id: "eng", name: "English Language",  short: "English",   dept: "Languages" },
    { id: "kur", name: "Kurdish Language",  short: "Kurdish",   dept: "Languages" },
    { id: "ara", name: "Arabic Language",   short: "Arabic",    dept: "Languages" },
    { id: "mat", name: "Mathematics",       short: "Maths",     dept: "Mathematics" },
    { id: "sci", name: "General Science",   short: "Science",   dept: "Science" },
    { id: "phy", name: "Physics",           short: "Physics",   dept: "Science" },
    { id: "che", name: "Chemistry",         short: "Chemistry", dept: "Science" },
    { id: "bio", name: "Biology",           short: "Biology",   dept: "Science" },
    { id: "ict", name: "Computer Science",  short: "Computing", dept: "Science" },
    { id: "his", name: "History",           short: "History",   dept: "Humanities" },
    { id: "geo", name: "Geography",         short: "Geography", dept: "Humanities" },
    { id: "isl", name: "Islamic Studies",   short: "Islamic",   dept: "Humanities" },
    { id: "art", name: "Art & Design",      short: "Art",       dept: "Arts & Sport" },
    { id: "pe",  name: "Physical Education", short: "PE",       dept: "Arts & Sport" }
  ];

  var ROOMS = ["B1-04", "B1-05", "B1-07", "B2-01", "B2-02", "B2-06", "Lab 1", "Lab 2",
    "ICT Suite", "Art Room", "Sports Hall", "Library"];

  /* A subject is taught where it can be taught — chemistry needs a lab, PE
     needs the hall. Random room assignment reads as a bug to a school. */
  var CLASSROOMS = ["B1-04", "B1-05", "B1-07", "B2-01", "B2-02", "B2-06"];
  var ROOMS_FOR = {
    phy: ["Lab 1", "Lab 2"], che: ["Lab 1", "Lab 2"], bio: ["Lab 1", "Lab 2"],
    sci: ["Lab 1", "Lab 2"],
    ict: ["ICT Suite"],
    art: ["Art Room"],
    pe:  ["Sports Hall"],
    his: CLASSROOMS.concat(["Library"]), geo: CLASSROOMS.concat(["Library"]),
    isl: CLASSROOMS, eng: CLASSROOMS, kur: CLASSROOMS, ara: CLASSROOMS, mat: CLASSROOMS
  };
  function roomFor(subjectId) {
    var pool = ROOMS_FOR[subjectId] || CLASSROOMS;
    return pool[Math.floor(R() * pool.length)];
  }

  /* ---- Staff ----------------------------------------------------------- */
  var DEPARTMENTS = ["Languages", "Mathematics", "Science", "Humanities",
    "Arts & Sport", "Administration", "Finance", "Support"];

  var STAFF = [
    ["Nma Karim",        "Head of English",        "Languages",     "eng", "LZ-T-041", "2019-09-01"],
    ["Karwan Sabir",     "English Teacher",        "Languages",     "eng", "LZ-T-052", "2021-09-01"],
    ["Shilan Tahir",     "Kurdish Teacher",        "Languages",     "kur", "LZ-T-018", "2017-09-01"],
    ["Rebin Hussein",    "Arabic Teacher",         "Languages",     "ara", "LZ-T-063", "2022-09-01"],
    ["Aram Qadir",       "Head of Mathematics",    "Mathematics",   "mat", "LZ-T-009", "2015-09-01"],
    ["Bahar Nuri",       "Mathematics Teacher",    "Mathematics",   "mat", "LZ-T-071", "2023-09-01"],
    ["Hemn Salih",       "Physics Teacher",        "Science",       "phy", "LZ-T-027", "2018-09-01"],
    ["Zhyan Rashid",     "Chemistry Teacher",      "Science",       "che", "LZ-T-034", "2019-09-01"],
    ["Diyar Aziz",       "Biology Teacher",        "Science",       "bio", "LZ-T-046", "2020-09-01"],
    ["Lana Jamal",       "Science Teacher (KG/EL)", "Science",      "sci", "LZ-T-055", "2021-09-01"],
    ["Peshraw Faris",    "Computer Science",       "Science",       "ict", "LZ-T-067", "2022-09-01"],
    ["Avan Mahmood",     "History Teacher",        "Humanities",    "his", "LZ-T-030", "2018-09-01"],
    ["Soran Bakr",       "Geography Teacher",      "Humanities",    "geo", "LZ-T-058", "2021-09-01"],
    ["Hawnaz Anwar",     "Islamic Studies",        "Humanities",    "isl", "LZ-T-022", "2017-09-01"],
    ["Rangin Kamal",     "Art & Design",           "Arts & Sport",  "art", "LZ-T-061", "2022-09-01"],
    ["Botan Mustafa",    "Physical Education",     "Arts & Sport",  "pe",  "LZ-T-044", "2020-09-01"],
    ["Rezan Ibrahim",    "School Director",        "Administration", null, "LZ-A-001", "2014-08-15"],
    ["Chnar Sadiq",      "Registrar",              "Administration", null, "LZ-A-006", "2016-08-20"],
    ["Halgurd Younis",   "Academic Coordinator",   "Administration", null, "LZ-A-011", "2018-08-25"],
    ["Nazdar Rasul",     "Finance Manager",        "Finance",       null, "LZ-F-003", "2016-09-05"],
    ["Sirwan Latif",     "Accountant / Cashier",   "Finance",       null, "LZ-F-008", "2020-09-10"],
    ["Trifa Sherko",     "School Nurse",           "Support",       null, "LZ-S-014", "2019-09-15"],
    ["Rawand Baban",     "IT Administrator",       "Support",       null, "LZ-S-019", "2021-09-01"],
    ["Delan Nawzad",     "Front Desk",             "Support",       null, "LZ-S-023", "2022-09-01"]
  ].map(function (row, i) {
    return {
      id: row[4],
      name: row[0],
      position: row[1],
      department: row[2],
      subject: row[3],
      since: row[5],
      email: row[0].toLowerCase().replace(/\s+/g, ".") + "@lezan.edu.krd",
      phone: "0750 " + (300 + i) + " " + (1000 + i * 37).toString().slice(0, 4),
      active: i !== 23,
      classes: 0
    };
  });

  var TEACHERS = STAFF.filter(function (s) { return s.subject; });

  /* ---- Students -------------------------------------------------------- */
  var STATUS_WEIGHTS = [
    ["enrolled", 0.86], ["paymentPending", 0.06], ["docsPending", 0.04],
    ["underReview", 0.02], ["waitlist", 0.02]
  ];
  function weightedStatus() {
    var r = R(), acc = 0;
    for (var i = 0; i < STATUS_WEIGHTS.length; i++) {
      acc += STATUS_WEIGHTS[i][1];
      if (r < acc) { return STATUS_WEIGHTS[i][0]; }
    }
    return "enrolled";
  }

  var STUDENTS = [];
  var seq = 100;

  ALL_GRADES.forEach(function (grade) {
    var div = GRADE_INDEX[grade];
    var perGrade = div.id === "kg" ? 5 : 4;
    SECTIONS.forEach(function (section) {
      for (var i = 0; i < perGrade; i++) {
        var isMale = chance(0.51);
        var first = isMale ? pick(MALE) : pick(FEMALE);
        var father = pick(FAMILY);
        var family = pick(FAMILY);
        /* "Nma Karim Karim" reads as a bug — keep father and family distinct */
        while (family === father) { family = pick(FAMILY); }
        seq += int(1, 3);

        var gradeNo = ALL_GRADES.indexOf(grade);
        var yearsHere = Math.min(int(1, 5), gradeNo + 1);
        var joinedYear = YEARS[YEARS.length - yearsHere];

        var tuition = div.tuition + (chance(0.3) ? 200000 : 0);
        var discountPct = chance(0.16) ? pick([10, 15, 20, 25]) : 0;
        var scholarship = chance(0.05);
        var netCharge = Math.round(tuition * (1 - discountPct / 100) / 1000) * 1000;

        /* Prior-year debt is the proposal's headline concern — some students
           carry a genuine balance forward through promotion. */
        var priorBalance = chance(0.18) ? int(2, 14) * 100000 : 0;
        var paidRatio = chance(0.55) ? 1 : (chance(0.5) ? R() * 0.55 + 0.35 : R() * 0.3);
        var paid = Math.round(netCharge * paidRatio / 50000) * 50000;
        if (paid > netCharge) { paid = netCharge; }

        var attendance = Math.round((88 + R() * 11) * 10) / 10;
        if (chance(0.07)) { attendance = Math.round((72 + R() * 12) * 10) / 10; }

        STUDENTS.push({
          id: "LZ-" + String(seq).padStart(5, "0"),
          name: first + " " + father + " " + family,
          firstName: first,
          gender: isMale ? "M" : "F",
          division: div.id,
          divisionLabel: div.label,
          grade: grade,
          section: section,
          className: grade + " " + section,
          status: weightedStatus(),
          joinedYear: joinedYear,
          yearsEnrolled: yearsHere,
          guardian: pick(["Mr.", "Mrs."]) + " " + father + " " + family,
          guardianPhone: "0750 " + int(200, 799) + " " + int(1000, 9999),
          guardianEmail: (father + "." + family).toLowerCase() + "@example.krd",
          address: pick(["Ankawa", "Dream City", "Italian Village", "Naz City",
            "Setaqan", "Brayati", "Zanko", "Gulan Street", "Shorsh", "Empire World"]) + ", Erbil",
          dob: (2026 - (5 + gradeNo)) + "-" + String(int(1, 12)).padStart(2, "0") +
               "-" + String(int(1, 28)).padStart(2, "0"),
          tuition: tuition,
          discountPct: discountPct,
          scholarship: scholarship,
          charges: netCharge,
          paid: paid,
          priorBalance: priorBalance,
          get outstanding() { return this.charges - this.paid + this.priorBalance; },
          attendance: attendance,
          average: Math.round((62 + R() * 34) * 10) / 10,
          docsComplete: chance(0.88)
        });
      }
    });
  });

  /* Freeze a plain `outstanding` number so the objects serialise/sort cleanly */
  STUDENTS = STUDENTS.map(function (s) {
    var o = {}; for (var k in s) { o[k] = s[k]; }
    o.outstanding = s.charges - s.paid + s.priorBalance;
    return o;
  });

  /* ---- Enrolment history: one permanent ID, a record per year ---------- */
  function historyFor(student) {
    var out = [];
    var gradeNo = ALL_GRADES.indexOf(student.grade);
    for (var i = 0; i < student.yearsEnrolled; i++) {
      var back = student.yearsEnrolled - 1 - i;
      var g = ALL_GRADES[Math.max(0, gradeNo - back)];
      var d = GRADE_INDEX[g];
      var year = YEARS[YEARS.length - student.yearsEnrolled + i];
      var isCurrent = year === CURRENT_YEAR;
      var charges = isCurrent ? student.charges
        : Math.round(d.tuition * (1 - student.discountPct / 100) * (0.86 + i * 0.04) / 1000) * 1000;
      var paidAmt = isCurrent ? student.paid : charges;

      /* the carried debt sits on the year before last */
      if (!isCurrent && back === 1 && student.priorBalance > 0) {
        paidAmt = charges - student.priorBalance;
      }
      out.push({
        year: year,
        grade: g,
        division: d.label,
        section: student.section,
        outcome: isCurrent ? "active" : (back === 0 ? "promoted" : "promoted"),
        charges: charges,
        paid: paidAmt,
        outstanding: charges - paidAmt,
        attendance: isCurrent ? student.attendance : Math.round((88 + R() * 10) * 10) / 10,
        average: isCurrent ? student.average : Math.round((60 + R() * 35) * 10) / 10
      });
    }
    return out;
  }

  /* ---- Applications (module 01) ---------------------------------------- */
  var APP_STATUSES = ["draft", "docsPending", "underReview", "approved", "paymentPending", "enrolled", "waitlist", "rejected"];
  var APPLICATIONS = [];
  for (var a = 0; a < 26; a++) {
    var male = chance(0.5);
    var f = male ? pick(MALE) : pick(FEMALE);
    var fam = pick(FAMILY);
    var g2 = pick(ALL_GRADES);
    var st = APP_STATUSES[Math.min(APP_STATUSES.length - 1,
      Math.floor(Math.pow(R(), 0.85) * APP_STATUSES.length))];
    APPLICATIONS.push({
      ref: "APP-2627-" + String(1040 + a * 3).padStart(4, "0"),
      name: f + " " + pick(FAMILY) + " " + fam,
      grade: g2,
      division: GRADE_INDEX[g2].label,
      divisionId: GRADE_INDEX[g2].id,
      status: st,
      guardian: pick(["Mr.", "Mrs."]) + " " + pick(FAMILY) + " " + fam,
      phone: "0770 " + int(200, 799) + " " + int(1000, 9999),
      submitted: "2026-0" + int(6, 8) + "-" + String(int(1, 28)).padStart(2, "0"),
      docs: int(3, 6),
      docsRequired: 6,
      source: pick(["Online form", "Walk-in", "Referral", "Returning family"])
    });
  }

  var PIPELINE = [
    { key: "s.draft",          count: 18 },
    { key: "s.docsPending",    count: 31 },
    { key: "s.underReview",    count: 24 },
    { key: "s.approved",       count: 19 },
    { key: "s.paymentPending", count: 12 },
    { key: "s.enrolled",       count: 96 }
  ];

  var DOC_CHECKLIST = [
    { name: "Birth certificate",             state: "done",    meta: "Uploaded 12 Aug 2026" },
    { name: "Previous school transcript",    state: "done",    meta: "Uploaded 12 Aug 2026" },
    { name: "Guardian ID copy",              state: "done",    meta: "Uploaded 14 Aug 2026" },
    { name: "Residency card",                state: "pending", meta: "Requested 20 Aug 2026" },
    { name: "Medical / vaccination record",  state: "missing", meta: "Reminder sent twice" },
    { name: "Four passport photographs",     state: "missing", meta: "Not received" }
  ];

  /* ---- Attendance (module 03) ------------------------------------------ */
  var ROSTER_CLASS = "Grade 5 A";
  var ROSTER = STUDENTS.filter(function (s) { return s.className === ROSTER_CLASS; });
  while (ROSTER.length < 22) {
    var m2 = chance(0.5);
    ROSTER.push({
      id: "LZ-0" + int(1000, 1999),
      name: (m2 ? pick(MALE) : pick(FEMALE)) + " " + pick(FAMILY) + " " + pick(FAMILY),
      className: ROSTER_CLASS
    });
  }
  ROSTER = ROSTER.slice(0, 22).map(function (s, i) {
    var st2 = "present";
    if (i === 3 || i === 14) { st2 = "absent"; }
    else if (i === 7) { st2 = "late"; }
    else if (i === 18) { st2 = "excused"; }
    return { id: s.id, name: s.name, status: st2 };
  });

  var WEEKDAYS = ["Sun", "Mon", "Tue", "Wed", "Thu"];
  var HEATMAP_CLASSES = ["KG2 A", "Grade 1 A", "Grade 3 B", "Grade 5 A", "Grade 7 B",
    "Grade 9 A", "Grade 11 A", "Grade 12 B"];
  var HEATMAP = HEATMAP_CLASSES.map(function (cls) {
    return {
      label: cls,
      values: WEEKDAYS.map(function (d, i) {
        var base = 94 - (i === 4 ? 5 : 0);
        return Math.round((base + R() * 6 - 3) * 10) / 10;
      })
    };
  });

  /* ---- Timetable (module 04) ------------------------------------------- */
  var PERIODS = [
    { label: "Period 1", time: "08:15 – 09:00" },
    { label: "Period 2", time: "09:05 – 09:50" },
    { label: "Break",    time: "09:50 – 10:10", isBreak: true },
    { label: "Period 3", time: "10:10 – 10:55" },
    { label: "Period 4", time: "11:00 – 11:45" },
    { label: "Lunch",    time: "11:45 – 12:25", isBreak: true },
    { label: "Period 5", time: "12:25 – 13:10" },
    { label: "Period 6", time: "13:15 – 14:00" }
  ];

  var TIMETABLE_SUBJECTS = ["mat", "eng", "phy", "kur", "che", "bio", "ara", "ict", "his", "geo", "art", "pe"];
  var TIMETABLE = PERIODS.map(function (p) {
    if (p.isBreak) { return { period: p, cells: null }; }
    return {
      period: p,
      cells: WEEKDAYS.map(function () {
        if (chance(0.06)) { return null; }
        var sid = pick(TIMETABLE_SUBJECTS);
        var subj = SUBJECTS.filter(function (s) { return s.id === sid; })[0];
        var teacher = TEACHERS.filter(function (t) { return t.subject === sid; })[0] || pick(TEACHERS);
        return { subject: subj, teacher: teacher, room: roomFor(sid), conflict: false };
      })
    };
  });
  /* one deliberate conflict, so the conflict-check UI has something to show */
  TIMETABLE[4].cells[2].conflict = true;

  /* ---- Examinations (module 05) ---------------------------------------- */
  var EXAMS = [
    { id: "EX-2627-014", name: "Mid-Term Examination", term: "Term 1", grades: "Grade 7 – Grade 12",
      window: "12 – 20 Nov 2026", status: "published", weight: 30, entered: 100 },
    { id: "EX-2627-021", name: "Term 1 Final Examination", term: "Term 1", grades: "Grade 1 – Grade 12",
      window: "07 – 18 Jan 2027", status: "locked", weight: 40, entered: 100 },
    { id: "EX-2627-028", name: "Continuous Assessment — Term 2", term: "Term 2", grades: "Grade 1 – Grade 12",
      window: "Ongoing", status: "active", weight: 30, entered: 68 },
    { id: "EX-2627-033", name: "Mid-Term Examination", term: "Term 2", grades: "Grade 7 – Grade 12",
      window: "22 – 30 Mar 2027", status: "scheduled", weight: 30, entered: 0 },
    { id: "EX-2627-040", name: "KG Readiness Assessment", term: "Term 2", grades: "KG1 – KG3",
      window: "05 – 09 Apr 2027", status: "scheduled", weight: 100, entered: 0 }
  ];

  var MARKSHEET_CLASS = "Grade 9 A";
  var MARKSHEET_SUBJECTS = ["eng", "mat", "phy", "che", "bio", "kur"];
  /* Section A first, then the rest of the grade — deduped by student ID, or
     the same child appears twice in one marks table. */
  var MARKSHEET_SEEN = {};
  var MARKSHEET = STUDENTS.filter(function (s) { return s.className === MARKSHEET_CLASS; })
    .concat(STUDENTS.filter(function (s) { return s.grade === "Grade 9"; }))
    .filter(function (s) {
      if (MARKSHEET_SEEN[s.id]) { return false; }
      MARKSHEET_SEEN[s.id] = true;
      return true;
    })
    .slice(0, 9)
    .map(function (s) {
      var marks = {};
      MARKSHEET_SUBJECTS.forEach(function (sid) { marks[sid] = int(41, 99); });
      var vals = MARKSHEET_SUBJECTS.map(function (sid) { return marks[sid]; });
      var avg = Math.round(vals.reduce(function (x, y) { return x + y; }, 0) / vals.length * 10) / 10;
      return { id: s.id, name: s.name, marks: marks, average: avg, grade: letterFor(avg) };
    });

  function letterFor(v) {
    if (v >= 90) { return "A"; }
    if (v >= 80) { return "B"; }
    if (v >= 70) { return "C"; }
    if (v >= 60) { return "D"; }
    return "F";
  }

  var REPORT_CARD = {
    student: MARKSHEET[0],
    rows: MARKSHEET_SUBJECTS.map(function (sid) {
      var subj = SUBJECTS.filter(function (s) { return s.id === sid; })[0];
      var m = MARKSHEET[0].marks[sid];
      return { subject: subj.name, mark: m, grade: letterFor(m), teacher:
        (TEACHERS.filter(function (t) { return t.subject === sid; })[0] || TEACHERS[0]).name };
    })
  };

  /* ---- Fees (module 06) ------------------------------------------------ */
  var LEDGER_STUDENT = STUDENTS.filter(function (s) {
    return s.priorBalance > 0 && s.yearsEnrolled >= 3;
  })[0] || STUDENTS[12];

  var INVOICE = {
    number: "INV-2627-00418",
    issued: "01 Sep 2026",
    due: "30 Sep 2026",
    student: LEDGER_STUDENT,
    lines: [
      { desc: "Tuition — " + CURRENT_YEAR + ", " + LEDGER_STUDENT.grade, qty: 1, amount: LEDGER_STUDENT.tuition },
      { desc: "Registration fee", qty: 1, amount: 250000 },
      { desc: "Books & learning materials", qty: 1, amount: 180000 },
      { desc: "Transportation — Ankawa route", qty: 1, amount: 640000 }
    ],
    discountPct: LEDGER_STUDENT.discountPct
  };

  var PAYMENTS = [
    { ref: "RCP-2627-01922", date: "12 Feb 2027", method: "Bank transfer", amount: 900000, by: "Sirwan Latif" },
    { ref: "RCP-2627-01640", date: "14 Dec 2026", method: "Cash", amount: 750000, by: "Sirwan Latif" },
    { ref: "RCP-2627-01188", date: "02 Nov 2026", method: "Card", amount: 600000, by: "Nazdar Rasul" },
    { ref: "RCP-2627-00734", date: "18 Sep 2026", method: "Bank transfer", amount: 1200000, by: "Sirwan Latif" },
    { ref: "RCP-2526-04471", date: "22 May 2026", method: "Cash", amount: 400000, by: "Sirwan Latif" }
  ];

  /* Financial continuity across years — the proposal's worked example */
  var CONTINUITY = [
    { year: "2023-2024", charges: 2800000, paid: 2800000 },
    { year: "2024-2025", charges: 3000000, paid: 3000000 },
    { year: "2025-2026", charges: 3200000, paid: 2700000 },
    { year: "2026-2027", charges: 3500000, paid: 1000000 }
  ].map(function (r) { r.outstanding = r.charges - r.paid; return r; });

  /* ---- Communications (module 09) -------------------------------------- */
  var ANNOUNCEMENTS = [
    { title: "Term 2 parent–teacher meetings", audience: "All guardians", channel: "Email · SMS",
      when: "Scheduled 04 Mar 2027, 09:00", status: "scheduled", reach: 1284 },
    { title: "Term 1 results are now published", audience: "Guardians · Grade 1–12", channel: "Portal · Email",
      when: "Sent 24 Jan 2027", status: "sent", reach: 1102 },
    { title: "Fee instalment 2 reminder", audience: "Guardians with balance", channel: "SMS · WhatsApp",
      when: "Sent 18 Jan 2027", status: "sent", reach: 218 },
    { title: "Kurdish Language Day celebration", audience: "All guardians · Staff", channel: "Email · Portal",
      when: "Sent 12 Jan 2027", status: "sent", reach: 1308 },
    { title: "Missing registration documents", audience: "42 applicant families", channel: "SMS",
      when: "Sent 09 Jan 2027", status: "sent", reach: 42 },
    { title: "Snow-day closure notice", audience: "All guardians · Staff", channel: "SMS · WhatsApp · Email",
      when: "Sent 22 Dec 2026", status: "sent", reach: 1308 }
  ];

  var TEMPLATES = [
    { name: "Application received", trigger: "On application submit", channel: "Email", uses: 214 },
    { name: "Missing document reminder", trigger: "3 days after checklist gap", channel: "SMS", uses: 168 },
    { name: "Admission approved", trigger: "On approval", channel: "Email · SMS", uses: 96 },
    { name: "Invoice issued", trigger: "On invoice generation", channel: "Email", uses: 1284 },
    { name: "Payment receipt", trigger: "On payment recorded", channel: "Email · WhatsApp", uses: 986 },
    { name: "Overdue payment notice", trigger: "7 days past due date", channel: "SMS", uses: 341 },
    { name: "Absence alert", trigger: "On unexcused absence", channel: "SMS", uses: 452 },
    { name: "Results published", trigger: "On result release", channel: "Portal · Email", uses: 3 }
  ];

  var CHANNELS = [
    { name: "Email",    icon: "mail",    sent: 4820, rate: 98.4 },
    { name: "SMS",      icon: "phone",   sent: 2140, rate: 96.1 },
    { name: "WhatsApp", icon: "message", sent: 1655, rate: 94.7 },
    { name: "In-system", icon: "bell",   sent: 3402, rate: 100 }
  ];

  var NOTIFICATIONS = [
    { title: "9 applications are missing documents", meta: "Admissions · 12 minutes ago", tone: "warning" },
    { title: "Instalment 2 is now overdue for 34 students", meta: "Finance · 1 hour ago", tone: "critical" },
    { title: "Term 2 continuous assessment is 68% entered", meta: "Academics · 3 hours ago", tone: "" },
    { title: "Grade 11 A timetable conflict resolved", meta: "Scheduling · Yesterday", tone: "good" },
    { title: "Nazdar Rasul approved a 300,000 IQD discount", meta: "Audit · Yesterday", tone: "warning" }
  ];

  /* ---- Audit trail (modules 07 & 10) ----------------------------------- */
  var AUDIT = [
    { when: "29 Aug 2026 · 14:22", who: "Nazdar Rasul", role: "Finance Manager",
      what: "Discount changed from 0 IQD to 300,000 IQD", target: "Student LZ-00138", tone: "warning" },
    { when: "29 Aug 2026 · 11:47", who: "Chnar Sadiq", role: "Registrar",
      what: "Application approved and moved to Payment Pending", target: "APP-2627-1093", tone: "good" },
    { when: "28 Aug 2026 · 16:08", who: "Rezan Ibrahim", role: "Director",
      what: "Academic year 2025-2026 closed — records set to read-only", target: "Year 2025-2026", tone: "critical" },
    { when: "28 Aug 2026 · 15:31", who: "Halgurd Younis", role: "Academic Coordinator",
      what: "Grade changed after publication (Physics, 62 → 68)", target: "Student LZ-00412", tone: "warning" },
    { when: "28 Aug 2026 · 09:12", who: "Rawand Baban", role: "System Administrator",
      what: "Role permissions updated — Accountant lost Export Data", target: "Role: Accountant", tone: "" },
    { when: "27 Aug 2026 · 17:55", who: "Sirwan Latif", role: "Accountant",
      what: "Payment reversed — receipt RCP-2627-00981", target: "Student LZ-00287", tone: "critical" },
    { when: "27 Aug 2026 · 13:20", who: "Chnar Sadiq", role: "Registrar",
      what: "Bulk promotion confirmed for 412 students", target: "2025-2026 → 2026-2027", tone: "good" }
  ];

  var ROLES_MATRIX = [
    { role: "Director / School Management", access: "Cross-functional visibility; approvals by policy", users: 2, level: "Full" },
    { role: "Registrar / Admissions", access: "Applications, student records, enrolment", users: 3, level: "Scoped" },
    { role: "Finance Manager", access: "Full finance operations and financial reporting", users: 1, level: "Scoped" },
    { role: "Accountant / Cashier", access: "Payments, receipts, selected invoices", users: 2, level: "Limited" },
    { role: "Teacher", access: "Assigned classes, attendance, academic entry", users: 16, level: "Limited" },
    { role: "Academic Coordinator", access: "Academic records, examinations, grades", users: 2, level: "Scoped" },
    { role: "System Administrator", access: "Technical administration and user management", users: 1, level: "Technical" }
  ];

  /* ---- Chart datasets -------------------------------------------------- */
  var CHARTS = {
    /* Stacked columns — one bar per year, three divisions */
    enrolment: {
      categories: YEARS,
      series: [
        { name: "n.kindergarten", values: [186, 204, 221, 238, 252] },
        { name: "n.elementary",   values: [402, 431, 466, 498, 531] },
        { name: "n.highschool",   values: [368, 392, 428, 471, 501] }
      ]
    },
    /* Two lines, one axis, same unit (million IQD) */
    collections: {
      categories: ["Sep", "Oct", "Nov", "Dec", "Jan", "Feb", "Mar", "Apr", "May", "Jun"],
      series: [
        { name: "n.expected",  values: [820, 1490, 2010, 2480, 3120, 3610, 4020, 4380, 4610, 4820] },
        { name: "n.collected", values: [640, 1180, 1620, 1980, 2540, 3010, 3380, 3690, 3910, 4104] }
      ],
      unit: "M IQD"
    },
    divisionSplit: [
      { name: "n.kindergarten", value: 252 },
      { name: "n.elementary",   value: 531 },
      { name: "n.highschool",   value: 501 }
    ],
    byGrade: {
      categories: ALL_GRADES,
      series: [{ name: "n.students", values: ALL_GRADES.map(function (g) {
        return GRADE_INDEX[g].id === "kg" ? int(76, 92) : int(78, 106);
      }) }]
    },
    attendanceTrend: {
      categories: ["W1", "W2", "W3", "W4", "W5", "W6", "W7", "W8", "W9", "W10", "W11", "W12"],
      series: [{ name: "k.avgAttendance", values: [96.2, 95.8, 94.1, 95.5, 93.2, 94.8, 92.4, 93.9, 95.1, 94.6, 93.8, 94.9] }],
      target: 95,
      unit: "%"
    },
    aging: [
      { name: "0 – 30 days",  value: 214000000 },
      { name: "31 – 60 days", value: 148000000 },
      { name: "61 – 90 days", value: 92000000 },
      { name: "90+ days",     value: 61000000 },
      { name: "Previous years", value: 118000000 }
    ],
    applications: {
      categories: ["Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug"],
      series: [{ name: "act.newApplication", values: [12, 19, 28, 41, 58, 74, 63] }]
    },
    gradeDistribution: {
      categories: ["A (90–100)", "B (80–89)", "C (70–79)", "D (60–69)", "F (< 60)"],
      series: [{ name: "n.students", values: [186, 341, 402, 228, 127] }]
    },
    paymentMethods: [
      { name: "Bank transfer", value: 1842 },
      { name: "Cash",          value: 1206 },
      { name: "Card",          value: 418 },
      { name: "Online",        value: 164 }
    ],
    staffByDepartment: DEPARTMENTS.map(function (d) {
      return { name: d, value: STAFF.filter(function (s) { return s.department === d; }).length };
    }).filter(function (d) { return d.value > 0; }),
    subjectAverages: [
      { name: "English Language", value: 82.4 },
      { name: "Mathematics",      value: 74.1 },
      { name: "Kurdish Language", value: 86.9 },
      { name: "Physics",          value: 69.8 },
      { name: "Chemistry",        value: 72.3 },
      { name: "Biology",          value: 78.6 },
      { name: "Computer Science", value: 84.2 }
    ]
  };

  /* ---- Sparkline series for the stat tiles ----------------------------- */
  var SPARKS = {
    students:   [1108, 1142, 1171, 1189, 1206, 1231, 1248, 1259, 1268, 1274, 1279, 1284],
    apps:       [12, 19, 28, 41, 58, 74, 63, 52, 44, 38, 31, 27],
    attendance: [96.2, 95.8, 94.1, 95.5, 93.2, 94.8, 92.4, 93.9, 95.1, 94.6, 93.8, 94.9],
    outstanding:[812, 786, 742, 771, 728, 694, 712, 683, 661, 648, 655, 633],
    collection: [62, 66, 69, 71, 74, 76, 79, 81, 83, 84, 85, 85.1],
    overdue:    [18, 22, 27, 31, 29, 34, 38, 41, 39, 36, 35, 34]
  };

  /* ---- Public surface -------------------------------------------------- */
  global.DATA = {
    meta: {
      school: "Lezan English Private School & Kindergarten",
      city: "Erbil, Kurdistan Region — Iraq",
      currentYear: CURRENT_YEAR,
      years: YEARS,
      updated: "29 Aug 2026 · 14:40"
    },
    divisions: DIVISIONS,
    grades: ALL_GRADES,
    gradeIndex: GRADE_INDEX,
    sections: SECTIONS,
    subjects: SUBJECTS,
    rooms: ROOMS,
    departments: DEPARTMENTS,
    staff: STAFF,
    teachers: TEACHERS,
    students: STUDENTS,
    historyFor: historyFor,
    applications: APPLICATIONS,
    pipeline: PIPELINE,
    docChecklist: DOC_CHECKLIST,
    roster: ROSTER,
    rosterClass: ROSTER_CLASS,
    weekdays: WEEKDAYS,
    heatmap: HEATMAP,
    heatmapClasses: HEATMAP_CLASSES,
    periods: PERIODS,
    timetable: TIMETABLE,
    exams: EXAMS,
    marksheet: MARKSHEET,
    marksheetClass: MARKSHEET_CLASS,
    marksheetSubjects: MARKSHEET_SUBJECTS,
    reportCard: REPORT_CARD,
    letterFor: letterFor,
    ledgerStudent: LEDGER_STUDENT,
    invoice: INVOICE,
    payments: PAYMENTS,
    continuity: CONTINUITY,
    announcements: ANNOUNCEMENTS,
    templates: TEMPLATES,
    channels: CHANNELS,
    notifications: NOTIFICATIONS,
    audit: AUDIT,
    rolesMatrix: ROLES_MATRIX,
    charts: CHARTS,
    sparks: SPARKS,

    /* Aggregates the dashboards lead with */
    totals: (function () {
      var enrolled = STUDENTS.filter(function (s) { return s.status === "enrolled"; });
      return {
        students: 1284,
        enrolled: enrolled.length,
        expected: 4820000000,
        collected: 4104000000,
        outstanding: 633000000,
        priorYear: 118000000,
        collectionRate: 85.1,
        attendanceToday: 94.9,
        newApplications: 27,
        missingDocs: 42,
        overdueInvoices: 34,
        staff: STAFF.filter(function (s) { return s.active; }).length
      };
    })()
  };
})(window);
