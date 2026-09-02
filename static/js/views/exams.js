/* ============================================================================
   Module 05 — Examinations and Grade Management
   Exam setup, marks entry with locking, grade distribution and the report
   card. Closed years stay readable but are protected from editing.
   ========================================================================= */
window.Views = window.Views || {};

window.Views.exams = function (root) {
  "use strict";
  var t = I18n.t, D = DATA, F = Fmt;

  var rc = D.reportCard;
  var subjects = D.marksheetSubjects.map(function (id) {
    return D.subjects.filter(function (s) { return s.id === id; })[0];
  });

  root.innerHTML =
    UI.pageHead({
      moduleNo: "05",
      title: t("mod.exams"),
      lede: t("purpose.exams"),
      actions:
        UI.select({ label: "Term", value: "Term 2", options: ["Term 1", "Term 2", "Full year"] }) +
        UI.btn({ label: t("act.export"), icon: "download", demo: "export" }) +
        UI.btn({ label: t("act.publishResults"), icon: "checkCircle", variant: "primary", demo: "publish" })
    }) +

    '<div class="grid grid--kpi">' +
      UI.stat({ label: "School average", icon: "award", value: "76.8", unit: "/ 100",
        delta: 1.9, note: t("k.vsLastYear") }) +
      UI.stat({ label: "Pass rate", icon: "checkCircle", value: "89.6", unit: "%",
        delta: 2.3, note: t("k.vsLastYear") }) +
      UI.stat({ label: "Marks entered", icon: "file", value: "68", unit: "%",
        note: "Term 2 continuous assessment" }) +
      UI.stat({ label: "Results published", icon: "shield", value: "2",
        note: "Term 1 mid-term and final" }) +
    "</div>" +

    UI.notice({
      tone: "brand", icon: "lock",
      title: "Promotion never erases the prior year",
      text: "Grades, attendance, invoices and outstanding balances from earlier years stay attached to the same permanent student profile."
    }) +

    '<div class="grid grid--wide">' +
      UI.chartCard({
        id: "gradeDistribution",
        title: t("c.gradeDistribution"),
        sub: "Term 1 final · Grade 1 – Grade 12 · " + F.int(1284) + " " + t("n.students")
      }) +
      UI.chartCard({
        id: "subjectAverages",
        title: t("c.subjectPerformance"),
        sub: "Term 1 final · all grades"
      }) +
    "</div>" +

    UI.card({
      title: "Examinations",
      sub: D.meta.currentYear + " · assessment setup, weighting and entry status",
      flush: true,
      body: '<div class="tablewrap"><table class="data"><thead><tr>' +
        '<th scope="col">Examination</th>' +
        '<th scope="col">Term</th>' +
        '<th scope="col">Grades</th>' +
        '<th scope="col">Window</th>' +
        '<th scope="col" class="num">Weight</th>' +
        '<th scope="col">Marks entered</th>' +
        '<th scope="col">' + UI.esc(t("n.status")) + "</th>" +
        "</tr></thead><tbody>" +
        D.exams.map(function (e) {
          return "<tr><td><div class=\"strong\">" + UI.esc(e.name) + "</div>" +
            '<div class="text-xs muted mono">' + UI.esc(e.id) + "</div></td>" +
            "<td>" + UI.esc(e.term) + "</td>" +
            '<td class="muted">' + UI.esc(e.grades) + "</td>" +
            '<td class="muted">' + UI.esc(e.window) + "</td>" +
            '<td class="num">' + e.weight + "%</td>" +
            '<td style="min-width:132px">' +
              '<div class="row-tight" style="gap:8px">' +
                '<span style="flex:1 1 66px">' +
                UI.track(e.entered, e.entered === 100 ? "good" : e.entered > 0 ? "warn" : "") + "</span>" +
                '<span class="text-xs tnum">' + e.entered + "%</span></div></td>" +
            "<td>" + UI.statusPill(e.status) + "</td></tr>";
        }).join("") + "</tbody></table></div>"
    }) +

    '<div class="grid grid--wide">' +
      UI.card({
        title: "Marks entry — " + D.marksheetClass,
        sub: "Term 2 continuous assessment · entry locked after approval",
        flush: true,
        body: '<div class="tablewrap"><table class="data"><thead><tr>' +
          '<th scope="col">' + UI.esc(t("n.student")) + "</th>" +
          subjects.map(function (s) {
            return '<th scope="col" class="num" title="' + UI.esc(s.name) + '">' +
              UI.esc(s.short) + "</th>";
          }).join("") +
          '<th scope="col" class="num">Average</th>' +
          '<th scope="col" class="num">' + UI.esc(t("n.grade")) + "</th>" +
          "</tr></thead><tbody>" +
          D.marksheet.map(function (m) {
            return "<tr><td>" + UI.person(m.name, m.id, "sm") + "</td>" +
              D.marksheetSubjects.map(function (sid) {
                var v = m.marks[sid];
                return '<td class="num' + (v < 60 ? " owed" : "") + '">' + v + "</td>";
              }).join("") +
              '<td class="num strong">' + F.dec(m.average) + "</td>" +
              '<td class="num">' + UI.pill(m.grade, m.average >= 70 ? "good" :
                m.average >= 60 ? "warning" : "critical") + "</td></tr>";
          }).join("") + "</tbody></table></div>",
        foot: Icon("lock", { size: 13 }) + " " + UI.esc(t("demo.noEntry"))
      }) +

      UI.card({
        title: "Report card preview",
        sub: "Generated from the marks above",
        body:
          '<div class="reportcard">' +
            '<div class="reportcard__head">' +
              '<span class="crest" aria-hidden="true">SMS</span>' +
              "<span><span class=\"reportcard__school\">" + UI.esc(t("app.name")) + "</span>" +
              '<span class="reportcard__term">Term 1 Final · ' + D.meta.currentYear + "</span></span>" +
              '<span class="reportcard__grade"><b>' + D.letterFor(rc.student.average) + "</b>" +
              "<span>" + F.dec(rc.student.average) + " / 100</span></span>" +
            "</div>" +
            '<div style="padding:16px">' +
              '<div class="row-tight" style="margin-bottom:12px">' +
                UI.person(rc.student.name, rc.student.id, "sm") +
                '<span class="push">' + UI.pill(D.marksheetClass, "info") + "</span>" +
              "</div>" +
              '<table class="invoice__lines"><thead><tr>' +
                "<th>" + UI.esc(t("n.subject")) + "</th>" +
                '<th class="num">Mark</th><th class="num">' + UI.esc(t("n.grade")) + "</th>" +
              "</tr></thead><tbody>" +
              rc.rows.map(function (r) {
                return "<tr><td>" + UI.esc(r.subject) +
                  '<div class="text-xs muted">' + UI.esc(r.teacher) + "</div></td>" +
                  '<td class="num">' + r.mark + "</td>" +
                  '<td class="num strong">' + r.grade + "</td></tr>";
              }).join("") + "</tbody></table>" +
            "</div>" +
          "</div>",
        foot:
          UI.btn({ label: t("act.print"), icon: "printer", size: "sm", demo: "print" }) +
          UI.btn({ label: "Transcript", icon: "file", size: "sm", demo: "transcript" })
      }) +
    "</div>";

  UI.mountCharts(root, {
    gradeDistribution: {
      type: "columns",
      title: t("c.gradeDistribution"),
      categories: D.charts.gradeDistribution.categories,
      series: D.charts.gradeDistribution.series,
      categoryLabel: t("n.grade"),
      stacked: false,
      summary: "The distribution centres on the C band, with 89.6% at grade D or above.",
      label: F.int
    },
    subjectAverages: {
      type: "bars",
      title: t("c.subjectPerformance"),
      rows: D.charts.subjectAverages,
      categoryLabel: t("n.subject"),
      valueLabel: "Average mark",
      labelWidth: 132,
      label: function (v) { return F.dec(v); }
    }
  });
};
