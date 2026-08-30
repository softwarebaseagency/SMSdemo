/* ============================================================================
   Module 03 — Attendance Management
   Daily recording by class, plus the class/grade/school summaries and the
   trend reporting management asks for.
   ========================================================================= */
window.Views = window.Views || {};

window.Views.attendance = function (root) {
  "use strict";
  var t = I18n.t, D = DATA, F = Fmt;

  var counts = { present: 0, absent: 0, late: 0, excused: 0 };
  D.roster.forEach(function (r) { counts[r.status] += 1; });
  var rate = (counts.present / D.roster.length) * 100;

  root.innerHTML =
    UI.pageHead({
      moduleNo: "03",
      title: t("mod.attendance"),
      lede: t("purpose.attendance"),
      actions:
        UI.select({ label: t("n.class"), value: D.rosterClass,
          options: ["KG2 A", "Grade 1 A", "Grade 3 B", D.rosterClass, "Grade 7 B", "Grade 9 A", "Grade 11 A"] }) +
        UI.btn({ label: t("act.export"), icon: "download", demo: "export" }) +
        UI.btn({ label: t("act.takeAttendance"), icon: "checkCircle", variant: "primary", demo: "take-attendance" })
    }) +

    '<div class="grid grid--kpi">' +
      UI.stat({ label: t("k.attendanceToday"), icon: "calendarCheck",
        value: F.dec(D.totals.attendanceToday), unit: "%", delta: 1.1, note: t("k.vsLastWeek"),
        spark: Charts.spark(D.sparks.attendance, { color: Charts.seriesColor(5) }) }) +
      UI.stat({ label: t("s.absent"), icon: "xCircle", value: "65",
        note: "Across all classes today" }) +
      UI.stat({ label: t("s.late"), icon: "clock", value: "23", note: "Across all classes today" }) +
      UI.stat({ label: t("k.avgAttendance"), icon: "trend", value: "94.4", unit: "%",
        note: "Term 2 to date" }) +
    "</div>" +

    '<div class="grid grid--wide">' +
      UI.chartCard({
        id: "attendanceTrend",
        title: t("c.attendanceTrend"),
        sub: "Term 2 · " + t("n.allDivisions")
      }) +
      UI.card({
        title: "Today at a glance",
        sub: D.rosterClass + " · " + new Date(2027, 1, 24).toDateString(),
        body:
          '<div style="text-align:center;padding:8px 0 18px">' +
            '<div class="hero-figure">' + F.pct(rate) + "</div>" +
            '<div class="text-xs muted" style="margin-top:4px">' +
            UI.esc(t("s.present")) + " · " + counts.present + " " + UI.esc(t("t.of")) + " " +
            D.roster.length + "</div>" +
          "</div>" +
          '<dl class="meta-list">' +
            ["present", "absent", "late", "excused"].map(function (k) {
              return '<div class="meta-row"><dt>' + UI.statusPill(k) + "</dt><dd>" + counts[k] + "</dd></div>";
            }).join("") +
          "</dl>",
        foot: Icon("lock", { size: 13 }) + " Corrections require the attendance-edit permission"
      }) +
    "</div>" +

    UI.card({
      title: "Daily register — " + D.rosterClass,
      sub: "Recorded by Bahar Nuri at 08:20 · " + t("demo.readOnly"),
      body: '<div class="roster">' + D.roster.map(function (r) {
        var icon = r.status === "present" ? "check" : r.status === "absent" ? "close" :
                   r.status === "late" ? "clock" : "info";
        return '<div class="roster__item" data-status="' + r.status + '">' +
          UI.avatar(r.name, "sm") +
          /* the name can truncate — keep the full text reachable on hover */
          '<span class="roster__body"><span class="roster__name" title="' + UI.esc(r.name) + '">' +
          UI.esc(r.name) + "</span>" +
          '<span class="roster__id">' + UI.esc(r.id) + "</span></span>" +
          '<span class="roster__mark" data-status="' + r.status + '" role="img" aria-label="' +
          UI.esc(t(UI.STATUS[r.status].key)) + '">' + Icon(icon, { size: 13 }) + "</span></div>";
      }).join("") + "</div>",
      foot:
        '<div class="row-tight">' +
          ["present", "absent", "late", "excused"].map(function (k) {
            return UI.statusPill(k) + '<span class="tnum">' + counts[k] + "</span>";
          }).join('<span class="muted">·</span>') +
        "</div>"
    }) +

    UI.chartCard({
      id: "heatmap",
      title: t("c.attendanceHeatmap"),
      sub: "Week of 22 – 26 February 2027 · rate per class per day"
    });

  UI.mountCharts(root, {
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
    },
    heatmap: {
      type: "heatmap",
      title: t("c.attendanceHeatmap"),
      columns: D.weekdays,
      rows: D.heatmap,
      rowLabel: t("n.class"),
      valueLabel: "Attendance"
    }
  });
};
