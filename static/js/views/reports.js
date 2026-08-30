/* ============================================================================
   Module 10 — Operational Reports and Dashboards
   The landing view: role-appropriate visibility over operational, academic
   and financial performance in one place.
   ========================================================================= */
window.Views = window.Views || {};

window.Views.reports = function (root, ctx) {
  "use strict";
  var t = I18n.t, D = DATA, F = Fmt;

  var kpis = [
    UI.stat({
      label: t("k.totalStudents"), icon: "users",
      value: F.int(D.totals.students), delta: 4.2, note: t("k.vsLastYear"),
      spark: Charts.spark(D.sparks.students)
    }),
    UI.stat({
      label: t("k.collectionRate"), icon: "wallet",
      value: F.dec(D.totals.collectionRate), unit: "%", delta: 2.8, note: t("k.vsLastYear"),
      spark: Charts.spark(D.sparks.collection, { color: Charts.seriesColor(2) })
    }),
    UI.stat({
      label: t("k.attendanceToday"), icon: "calendarCheck",
      value: F.dec(D.totals.attendanceToday), unit: "%", delta: 1.1, note: t("k.vsLastWeek"),
      spark: Charts.spark(D.sparks.attendance, { color: Charts.seriesColor(5) })
    }),
    UI.stat({
      label: t("k.outstandingTotal"), icon: "alert",
      value: F.money(D.totals.outstanding), unit: t("n.iqd"),
      delta: -6.4, goodWhen: "down", note: t("k.vsLastMonth"),
      spark: Charts.spark(D.sparks.outstanding, { color: Charts.seriesColor(1) })
    })
  ].join("");

  root.innerHTML =
    UI.pageHead({
      moduleNo: "10",
      title: t("mod.reports"),
      lede: t("purpose.reports"),
      actions:
        UI.select({ label: t("n.division"), options: [
          t("n.allDivisions"), t("n.kindergarten"), t("n.elementary"), t("n.highschool")
        ] }) +
        UI.btn({ label: t("act.export"), icon: "download", demo: "export" }) +
        UI.btn({ label: t("act.print"), icon: "printer", variant: "primary", demo: "print" })
    }) +

    UI.notice({
      tone: "brand", icon: "info",
      title: t("demo.readOnly"),
      text: t("demo.noEntry"),
      aside: '<span class="badge">' + Icon("clock", { size: 11 }) + " " +
             UI.esc(t("t.lastUpdated")) + " " + UI.ltr(D.meta.updated) + "</span>"
    }) +

    '<div class="grid grid--kpi">' + kpis + "</div>" +

    '<div class="grid grid--wide">' +
      UI.chartCard({
        id: "enrolment",
        title: t("c.enrollmentTrend"),
        sub: D.meta.years[0] + " – " + D.meta.currentYear + " · " + t("n.students")
      }) +
      UI.chartCard({
        id: "divisionSplit",
        title: t("c.studentsByDivision"),
        sub: D.meta.currentYear
      }) +
    "</div>" +

    '<div class="grid grid--wide">' +
      UI.chartCard({
        id: "collections",
        title: t("c.collectionsTrend"),
        sub: D.meta.currentYear + " · " + t("n.iqd") + " (millions)"
      }) +
      UI.chartCard({
        id: "aging",
        title: t("c.outstandingAging"),
        sub: t("n.outstanding") + " · " + t("n.iqd")
      }) +
    "</div>" +

    '<div class="grid grid--wide">' +
      UI.chartCard({
        id: "attendanceTrend",
        title: t("c.attendanceTrend"),
        sub: "Term 2 · " + t("n.allDivisions")
      }) +
      UI.card({
        title: t("c.recentActivity"),
        sub: "Sensitive actions are logged with who, when and what changed",
        flush: true,
        body: '<div style="padding:20px 20px 4px"><ul class="timeline">' +
          D.audit.slice(0, 5).map(function (a) {
            return '<li data-tone="' + UI.esc(a.tone) + '">' +
              '<div class="list__title">' + UI.esc(a.what) + "</div>" +
              '<div class="list__meta">' + UI.esc(a.who) + " · " + UI.esc(a.role) +
              " · " + UI.esc(a.target) + "</div>" +
              '<div class="list__meta">' + UI.esc(a.when) + "</div></li>";
          }).join("") + "</ul></div>",
        foot: UI.btn({ label: t("act.viewAll"), size: "sm", icon: "arrowRight", demo: "audit" })
      }) +
    "</div>";

  UI.mountCharts(root, {
    enrolment: {
      type: "columns",
      title: t("c.enrollmentTrend"),
      categories: D.charts.enrolment.categories,
      series: D.charts.enrolment.series,
      categoryLabel: t("n.academicYear"),
      stacked: true,
      summary: "Enrolment has grown every year across all three divisions.",
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
    },
    collections: {
      type: "line",
      title: t("c.collectionsTrend"),
      categories: D.charts.collections.categories,
      series: D.charts.collections.series,
      categoryLabel: "Month",
      unit: "",
      summary: "Collections track expected revenue at 85% by June.",
      label: function (v) { return F.int(v) + "M"; }
    },
    aging: {
      type: "bars",
      title: t("c.outstandingAging"),
      rows: D.charts.aging,
      ordinal: true,               /* buckets are ordered — one hue, stepped */
      categoryLabel: "Age",
      valueLabel: t("n.outstanding"),
      labelWidth: 116,
      label: F.money
    },
    attendanceTrend: {
      type: "line",
      title: t("c.attendanceTrend"),
      categories: D.charts.attendanceTrend.categories,
      series: D.charts.attendanceTrend.series,
      categoryLabel: "Week",
      unit: "%",
      zeroBased: false,
      target: D.charts.attendanceTrend.target,
      targetLabel: "Target",
      summary: "Attendance holds between 92% and 96% across the term.",
      label: function (v) { return F.pct(v); }
    }
  });
};
