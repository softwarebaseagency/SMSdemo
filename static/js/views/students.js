/* ============================================================================
   Module 02 — Student Records
   One permanent student identity; each academic year adds an enrolment
   record rather than replacing the student. The detail drawer is the place
   that continuity becomes visible.
   ========================================================================= */
window.Views = window.Views || {};

window.Views.students = function (root) {
  "use strict";
  var t = I18n.t, D = DATA, F = Fmt;

  var withDebt = D.students.filter(function (s) { return s.outstanding > 0; }).length;
  var carried = D.students.filter(function (s) { return s.priorBalance > 0; }).length;

  root.innerHTML =
    UI.pageHead({
      moduleNo: "02",
      title: t("mod.students"),
      lede: t("purpose.students"),
      actions:
        UI.select({ label: t("n.division"), options: [
          t("n.allDivisions"), t("n.kindergarten"), t("n.elementary"), t("n.highschool")] }) +
        UI.btn({ label: t("act.export"), icon: "download", demo: "export" }) +
        UI.btn({ label: t("act.addStudent"), icon: "plus", variant: "primary", demo: "add-student" })
    }) +

    '<div class="grid grid--kpi">' +
      UI.stat({ label: t("k.totalStudents"), icon: "users", value: F.int(D.totals.students),
        delta: 4.2, note: t("k.vsLastYear"), spark: Charts.spark(D.sparks.students) }) +
      UI.stat({ label: "Records in the register", icon: "userSquare", value: F.int(D.students.length),
        note: "Shown below · " + D.meta.currentYear }) +
      UI.stat({ label: "With an open balance", icon: "wallet", value: F.int(withDebt),
        note: "Across all academic years" }) +
      UI.stat({ label: "Carrying previous-year debt", icon: "history", value: F.int(carried),
        note: t("demo.continuity") }) +
    "</div>" +

    UI.notice({
      tone: "brand", icon: "shield",
      title: t("demo.continuity"),
      text: t("demo.continuityNote")
    }) +

    '<div class="grid grid--wide">' +
      UI.chartCard({ id: "byGrade", title: t("c.studentsByGrade"), sub: D.meta.currentYear }) +
      UI.chartCard({ id: "divisionSplit", title: t("c.studentsByDivision"), sub: D.meta.currentYear }) +
    "</div>" +

    UI.card({
      title: "Student register",
      sub: "Select any row to open the permanent record and its enrolment history",
      flush: true,
      body: '<div id="studentsTable"></div>'
    });

  UI.mountCharts(root, {
    byGrade: {
      type: "columns",
      title: t("c.studentsByGrade"),
      categories: D.charts.byGrade.categories,
      series: D.charts.byGrade.series,
      categoryLabel: t("n.grade"),
      stacked: false,
      rotateTicks: true,
      totalLabels: false,
      summary: "Class sizes stay between 76 and 106 across all fifteen grades.",
      label: F.int
    },
    divisionSplit: {
      type: "donut",
      title: t("c.studentsByDivision"),
      rows: D.charts.divisionSplit,
      categoryLabel: t("n.division"),
      valueLabel: t("n.students"),
      centerValue: F.int(1284),
      centerLabel: t("n.students"),
      label: F.int
    }
  });

  /* ---- The permanent record ------------------------------------------- */
  function openStudent(s) {
    var history = D.historyFor(s);
    var totalCharges = history.reduce(function (a, h) { return a + h.charges; }, 0);
    var totalPaid = history.reduce(function (a, h) { return a + h.paid; }, 0);
    var totalOwed = totalCharges - totalPaid;

    var tabs = [
      { id: "profile",    label: "Profile" },
      { id: "enrolment",  label: "Enrolment history" },
      { id: "academic",   label: "Academic" },
      { id: "financial",  label: "Financial" }
    ];

    function panel(id) {
      if (id === "profile") {
        return '<div class="kv">' +
          UI.field(t("n.studentId"), s.id, "Permanent — never reissued") +
          UI.field("Date of birth", s.dob) +
          UI.field("Gender", s.gender === "M" ? "Male" : "Female") +
          UI.field(t("n.division"), s.divisionLabel) +
          UI.field(t("n.grade"), s.grade) +
          UI.field(t("n.class"), s.className) +
          UI.field(t("n.guardian"), s.guardian) +
          UI.field("Guardian phone", s.guardianPhone) +
          UI.field("Guardian email", s.guardianEmail) +
          UI.field("Address", s.address) +
          UI.field("First enrolled", s.joinedYear) +
          UI.field("Years at school", String(s.yearsEnrolled)) +
        "</div>";
      }

      if (id === "enrolment") {
        return '<div class="enrollment-chain">' + history.slice().reverse().map(function (h) {
          return '<div class="enrollment-chain__item">' +
            '<span class="enrollment-chain__year tnum">' + UI.esc(h.year) + "</span>" +
            '<span class="enrollment-chain__body">' +
              '<span class="enrollment-chain__grade">' + UI.esc(h.grade) + " " + UI.esc(h.section) +
              ' <span class="muted text-xs">· ' + UI.esc(h.division) + "</span></span>" +
              '<span class="enrollment-chain__meta">Attendance ' + F.pct(h.attendance) +
              " · Average " + F.dec(h.average) + "</span>" +
            "</span>" +
            '<span class="enrollment-chain__aside">' +
              UI.statusPill(h.outcome === "active" ? "active" : "promoted") +
              (h.outstanding > 0
                ? '<div class="owed text-xs tnum" style="margin-top:4px">' + F.moneyFull(h.outstanding) + "</div>"
                : '<div class="settled text-xs" style="margin-top:4px">' + UI.esc(t("s.paid")) + "</div>") +
            "</span></div>";
        }).join("") + "</div>" +
        '<div style="margin-top:16px">' + UI.notice({
          tone: "info", icon: "info",
          title: "One identity across " + history.length + " academic years",
          text: "Promotion added a new enrolment record each year. The student ID, and everything attached to it, never changed."
        }) + "</div>";
      }

      if (id === "academic") {
        return '<dl class="meta-list">' +
          '<div class="meta-row"><dt>Current average</dt><dd>' + F.dec(s.average) + " / 100</dd></div>" +
          '<div class="meta-row"><dt>Letter grade</dt><dd>' + D.letterFor(s.average) + "</dd></div>" +
          '<div class="meta-row"><dt>Attendance rate</dt><dd>' + F.pct(s.attendance) + "</dd></div>" +
          '<div class="meta-row"><dt>Progression</dt><dd>' + UI.esc(t("s.promoted")) + "</dd></div>" +
        "</dl>" +
        '<hr class="divider" style="margin:20px 0">' +
        '<h4 class="card__title" style="margin-bottom:10px">Average by year</h4>' +
        history.slice().reverse().map(function (h) {
          return '<div style="margin-bottom:12px"><div class="stage__top">' +
            '<span class="stage__name tnum">' + UI.esc(h.year) + "</span>" +
            '<span class="stage__count">' + F.dec(h.average) + "</span></div>" +
            UI.track(h.average, h.average >= 70 ? "good" : h.average >= 60 ? "warn" : "crit") + "</div>";
        }).join("");
      }

      /* financial */
      return '<div class="carryforward">' +
        '<div class="row-tight"><strong>' + UI.esc(t("demo.continuity")) + "</strong>" +
        UI.pill(s.id, "brand") + "</div>" +
        '<p class="text-xs secondary" style="margin-top:4px">' + UI.esc(t("demo.continuityNote")) + "</p>" +
        '<div class="carryforward__years">' +
          '<div class="carryforward__year carryforward__year--head">' +
            "<span>" + UI.esc(t("n.academicYear")) + "</span><span>Charges</span>" +
            "<span>" + UI.esc(t("s.paid")) + "</span><span>" + UI.esc(t("n.outstanding")) + "</span></div>" +
          history.map(function (h) {
            return '<div class="carryforward__year"><b>' + UI.esc(h.year) + "</b>" +
              "<span>" + F.int(h.charges) + "</span>" +
              "<span>" + F.int(h.paid) + "</span>" +
              '<span class="' + (h.outstanding > 0 ? "owed" : "settled") + '">' +
              (h.outstanding > 0 ? F.int(h.outstanding) : "0") + "</span></div>";
          }).join("") +
          '<div class="carryforward__year carryforward__year--total">' +
            "<b>" + UI.esc(t("n.total")) + "</b><span>" + F.int(totalCharges) + "</span>" +
            "<span>" + F.int(totalPaid) + "</span>" +
            '<span class="' + (totalOwed > 0 ? "owed" : "settled") + '">' + F.int(totalOwed) + "</span></div>" +
        "</div></div>" +
        '<p class="text-xs muted" style="margin-top:10px">' + UI.esc(t("n.iqd")) +
        " · previous-year balances are shown separately from current-year charges.</p>";
    }

    UI.openDrawer({
      eyebrow: t("mod.label") + " 02 · " + t("mod.students.short"),
      title: s.name,
      sub: s.className + " · " + s.divisionLabel,
      body:
        '<div class="studenthead">' +
          UI.avatar(s.name, "lg") +
          '<div style="flex:1 1 200px;min-width:0">' +
            '<div class="strong">' + UI.esc(s.name) + "</div>" +
            '<div class="studenthead__id">' + UI.esc(s.id) + "</div>" +
            '<div class="row-tight" style="margin-top:8px">' +
              UI.statusPill(s.status) +
              UI.pill(s.className, "info") +
              (s.discountPct ? UI.pill(s.discountPct + "% discount", "brand") : "") +
              (s.scholarship ? UI.pill("Scholarship", "good", "award") : "") +
            "</div>" +
          "</div>" +
          '<div style="text-align:end">' +
            '<div class="text-xs muted">' + UI.esc(t("n.outstanding")) + "</div>" +
            '<div class="' + (totalOwed > 0 ? "owed" : "settled") +
            '" style="font-size:var(--text-lg)">' + F.money(totalOwed) + "</div>" +
            '<div class="text-xs muted">' + UI.esc(t("n.iqd")) + "</div>" +
          "</div>" +
        "</div>" +
        UI.tabs(tabs, "profile") +
        '<div style="padding:20px" id="studentPanel">' + panel("profile") + "</div>",
      foot:
        UI.btn({ label: t("act.print"), icon: "printer", demo: "print" }) +
        UI.btn({ label: "Account statement", icon: "receipt", demo: "statement" }) +
        '<span class="push text-xs muted">' + UI.esc(t("demo.readOnly")) + "</span>",
      onMount: function (drawer) {
        UI.wireTabs(drawer, function (id) {
          drawer.querySelector("#studentPanel").innerHTML = panel(id);
        });
        UI.wireDemoActions(drawer);
      }
    });
  }

  var table = UI.dataTable(document.getElementById("studentsTable"), {
    rows: D.students,
    pageSize: 12,
    defaultSort: "name",
    searchPlaceholder: t("act.searchStudents"),
    columns: [
      { field: "id", label: t("n.studentId"),
        render: function (s) { return '<span class="mono">' + UI.esc(s.id) + "</span>"; } },
      { field: "name", label: t("n.student"), wrap: true,
        render: function (s) { return UI.person(s.name, s.guardian, "sm"); } },
      { field: "className", label: t("n.class") },
      { field: "divisionLabel", label: t("n.division"),
        render: function (s) { return '<span class="muted">' + UI.esc(s.divisionLabel) + "</span>"; } },
      { field: "status", label: t("n.status"),
        render: function (s) { return UI.statusPill(s.status); } },
      { field: "attendance", label: "Attendance", num: true,
        render: function (s) {
          var tone = s.attendance >= 92 ? "good" : s.attendance >= 85 ? "warning" : "critical";
          return '<span class="' + UI.cls(["pill", "pill--icon", "pill--" + tone]) + '">' +
            Icon(tone === "good" ? "checkCircle" : "alert", { size: 12 }) + F.pct(s.attendance) + "</span>";
        } },
      { field: "outstanding", label: t("n.outstanding"), num: true,
        render: function (s) {
          if (s.outstanding <= 0) {
            return '<span class="settled">' + UI.esc(t("s.paid")) + "</span>";
          }
          return '<span class="owed">' + F.int(s.outstanding) + "</span>" +
            (s.priorBalance > 0
              ? '<div class="text-xs muted tnum">incl. ' + F.int(s.priorBalance) + " prior</div>"
              : "");
        } }
    ],
    onRow: openStudent
  });

  /* A query typed in the global search arrives here */
  if (window.Views.pendingStudentQuery) {
    var q = window.Views.pendingStudentQuery;
    window.Views.pendingStudentQuery = null;
    var input = document.querySelector("#studentsTable [data-table-search]");
    if (input) {
      input.value = q;
      input.dispatchEvent(new Event("input"));
    }
  }
};
