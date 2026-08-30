/* ============================================================================
   Module 01 — Admissions and Registration
   Application intake through confirmed registration, with the document
   checklist and status flow the proposal describes.
   ========================================================================= */
window.Views = window.Views || {};

window.Views.admissions = function (root) {
  "use strict";
  var t = I18n.t, D = DATA, F = Fmt;

  var totalInPipeline = D.pipeline.reduce(function (s, p) { return s + p.count; }, 0);

  root.innerHTML =
    UI.pageHead({
      moduleNo: "01",
      title: t("mod.admissions"),
      lede: t("purpose.admissions"),
      actions:
        UI.btn({ label: t("act.export"), icon: "download", demo: "export" }) +
        UI.btn({ label: t("act.newApplication"), icon: "plus", variant: "primary", demo: "new-application" })
    }) +

    '<div class="grid grid--kpi">' +
      UI.stat({ label: t("k.newApplications"), icon: "inbox",
        value: F.int(D.totals.newApplications), delta: 12.5, note: t("k.vsLastMonth"),
        spark: Charts.spark(D.sparks.apps) }) +
      UI.stat({ label: t("s.underReview"), icon: "clock", value: "24",
        note: "Awaiting registrar decision" }) +
      UI.stat({ label: t("k.missingDocs"), icon: "file",
        value: F.int(D.totals.missingDocs), delta: -8.0, goodWhen: "down", note: t("k.vsLastMonth") }) +
      UI.stat({ label: t("s.enrolled"), icon: "checkCircle", value: "96",
        note: D.meta.currentYear + " intake" }) +
    "</div>" +

    '<div class="grid grid--3">' +
      UI.card({
        title: t("c.admissionsPipeline"),
        sub: "Draft → Documents Pending → Under Review → Approved → Payment Pending → Enrolled",
        body: '<div class="stages">' + D.pipeline.map(function (p, i) {
          var pct = (p.count / totalInPipeline) * 100;
          return "<div><div class=\"stage__top\">" +
            '<span class="stage__name">' + UI.esc(t(p.key)) + "</span>" +
            '<span class="stage__count">' + F.int(p.count) + "</span>" +
            '<span class="stage__pct">' + F.pct(pct, 0) + "</span></div>" +
            /* One hue, deepening along the ordered funnel */
            '<div class="track"><div class="track__fill" style="width:' + pct.toFixed(1) +
            "%;background:" + Charts.seqColor(2 + Math.round(i / (D.pipeline.length - 1) * 3)) +
            '"></div></div></div>';
        }).join("") + "</div>",
        foot: Icon("info", { size: 13 }) + " " + UI.esc(totalInPipeline) +
              " applications in the " + D.meta.currentYear + " cycle"
      }) +
      UI.chartCard({
        id: "applications",
        title: t("c.applicationsTrend"),
        sub: "Feb – Aug 2026"
      }) +
      UI.card({
        title: "Registration checklist",
        sub: "APP-2627-1093 · Dilan Rashid Hussein · Grade 4",
        body: '<ul class="checklist">' + D.docChecklist.map(function (d) {
          var icon = d.state === "done" ? "check" : d.state === "missing" ? "close" : "clock";
          return '<li><span class="checklist__mark" data-state="' + d.state + '">' +
            Icon(icon, { size: 11 }) + "</span>" +
            '<span class="checklist__name">' + UI.esc(d.name) + "</span>" +
            '<span class="checklist__meta">' + UI.esc(d.meta) + "</span></li>";
        }).join("") + "</ul>",
        foot: Icon("lock", { size: 13 }) +
          " Registration fee required before Fully Enrolled — managers can approve an exception, and the approval is logged"
      }) +
    "</div>" +

    /* Full width: seven columns need the room, or the demo opens on a
       horizontally-scrolled table with its status column cut off. */
    UI.card({
      title: "Applications",
      sub: "Sortable and filterable — this demo does not accept new entries",
      flush: true,
      body: '<div id="appsTable"></div>'
    });

  UI.mountCharts(root, {
    applications: {
      type: "columns",
      title: t("c.applicationsTrend"),
      categories: D.charts.applications.categories,
      series: D.charts.applications.series,
      categoryLabel: "Month",
      stacked: false,
      summary: "Applications peak in July, before the academic year opens.",
      label: F.int
    }
  });

  UI.dataTable(document.getElementById("appsTable"), {
    rows: D.applications,
    pageSize: 8,
    defaultSort: "submitted",
    defaultDir: "desc",
    searchPlaceholder: "Search applicant, reference or guardian",
    columns: [
      { field: "ref", label: "Reference",
        render: function (r) { return '<span class="mono">' + UI.esc(r.ref) + "</span>"; } },
      { field: "name", label: t("n.student"), wrap: true,
        render: function (r) { return UI.person(r.name, r.guardian, "sm"); } },
      { field: "grade", label: t("n.grade"),
        render: function (r) {
          return UI.esc(r.grade) + ' <span class="muted text-xs">· ' + UI.esc(r.division) + "</span>";
        } },
      { field: "status", label: t("n.status"),
        render: function (r) { return UI.statusPill(r.status); } },
      { field: "docs", label: "Documents", num: true,
        sortValue: function (r) { return r.docs / r.docsRequired; },
        render: function (r) {
          var complete = r.docs >= r.docsRequired;
          return '<span class="' + UI.cls(["pill", "pill--icon", complete ? "pill--good" : "pill--warning"]) + '">' +
            Icon(complete ? "checkCircle" : "alert", { size: 12 }) + r.docs + "/" + r.docsRequired + "</span>";
        } },
      { field: "source", label: "Source",
        render: function (r) { return '<span class="muted">' + UI.esc(r.source) + "</span>"; } },
      { field: "submitted", label: "Submitted", num: true,
        render: function (r) { return '<span class="muted">' + UI.esc(r.submitted) + "</span>"; } }
    ],
    onRow: function (r) {
      UI.openDrawer({
        eyebrow: t("mod.label") + " 01 · " + t("mod.admissions.short"),
        title: r.name,
        sub: r.ref + " · " + r.grade + " · " + r.division,
        body:
          '<div style="padding:20px">' +
            '<div class="row-tight" style="margin-bottom:16px">' +
              UI.statusPill(r.status) +
              UI.pill(r.source, "info", "info") +
              UI.pill("Submitted " + r.submitted, "", "clock") +
            "</div>" +
            '<div class="kv">' +
              UI.field(t("n.guardian"), r.guardian) +
              UI.field("Contact", r.phone) +
              UI.field(t("n.grade") + " applied for", r.grade) +
              UI.field(t("n.division"), r.division) +
            "</div>" +
            '<hr class="divider" style="margin:20px 0">' +
            '<h3 class="card__title" style="margin-bottom:12px">Document checklist</h3>' +
            '<ul class="checklist">' + D.docChecklist.slice(0, r.docsRequired).map(function (d, i) {
              var state = i < r.docs ? "done" : (i === r.docs ? "pending" : "missing");
              var icon = state === "done" ? "check" : state === "missing" ? "close" : "clock";
              return '<li><span class="checklist__mark" data-state="' + state + '">' +
                Icon(icon, { size: 11 }) + '</span><span class="checklist__name">' +
                UI.esc(d.name) + "</span></li>";
            }).join("") + "</ul>" +
          "</div>",
        foot:
          UI.btn({ label: "Approve", icon: "checkCircle", variant: "primary", demo: "approve" }) +
          UI.btn({ label: "Request documents", icon: "mail", demo: "request-docs" }) +
          '<span class="push text-xs muted">' + UI.esc(t("demo.readOnly")) + "</span>",
        onMount: function (d) { UI.wireDemoActions(d); }
      });
    }
  });
};
