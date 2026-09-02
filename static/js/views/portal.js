/* ============================================================================
   Module 08 — Parent and Student Portal
   Rendered as a preview of what a guardian actually sees, so the difference
   between the staff console and the portal is obvious at a glance.
   ========================================================================= */
window.Views = window.Views || {};

window.Views.portal = function (root) {
  "use strict";
  var t = I18n.t, D = DATA, F = Fmt;

  var child = D.ledgerStudent;
  var history = D.historyFor(child);
  var owed = history.reduce(function (a, h) { return a + h.outstanding; }, 0);

  var CAPABILITIES = [
    { name: "View student profile", on: true,  note: "Approved fields only" },
    { name: "Attendance summaries", on: true,  note: "Monthly and term totals" },
    { name: "Grades and report cards", on: true, note: "After results are released" },
    { name: "Invoices and balances", on: true, note: "Including previous years" },
    { name: "Download receipts", on: true,  note: "PDF" },
    { name: "Announcements", on: true,  note: "School and class level" },
    { name: "Submit documents", on: true,  note: "Registration checklist only" },
    { name: "Edit student record", on: false, note: "Staff only" },
    { name: "View other students", on: false, note: "Blocked by account scope" },
    { name: "View internal notes", on: false, note: "Staff only" },
    { name: "Apply discounts", on: false, note: "Finance only" },
    { name: "See staff records", on: false, note: "Staff only" }
  ];

  root.innerHTML =
    UI.pageHead({
      moduleNo: "08",
      title: t("mod.portal"),
      lede: t("purpose.portal"),
      actions:
        UI.select({ label: "Account", value: "Guardian", options: ["Guardian", "Student"] }) +
        UI.btn({ label: "Portal settings", icon: "settings", demo: "portal-settings" })
    }) +

    '<div class="grid grid--kpi">' +
      UI.stat({ label: "Guardian accounts", icon: "users", value: "1,046",
        note: "Linked to 1,284 students" }) +
      UI.stat({ label: "Student accounts", icon: "user", value: "612",
        note: "Grade 7 and above" }) +
      UI.stat({ label: "Active in the last 30 days", icon: "trend", value: "78", unit: "%",
        delta: 6.2, note: t("k.vsLastMonth") }) +
      UI.stat({ label: "Documents submitted", icon: "fileCheck", value: "284",
        note: "Through the portal this year" }) +
    "</div>" +

    UI.notice({
      tone: "info", icon: "shield",
      title: "Access is limited strictly to the relevant student account",
      text: "Portal capabilities are configured by school management and can be introduced in stages. Guardians never reach internal staff-only records or administrative functions."
    }) +

    '<div class="grid grid--side">' +
      UI.card({
        title: "Portal capabilities",
        sub: "Configurable per deployment stage",
        flush: true,
        body: '<ul class="checklist" style="padding:8px 20px">' + CAPABILITIES.map(function (c) {
          return '<li><span class="checklist__mark" data-state="' + (c.on ? "done" : "missing") + '">' +
            Icon(c.on ? "check" : "close", { size: 11 }) + "</span>" +
            '<span class="checklist__name">' + UI.esc(c.name) + "</span>" +
            '<span class="checklist__meta">' + UI.esc(c.note) + "</span></li>";
        }).join("") + "</ul>"
      }) +

      UI.card({
        title: "Guardian view — preview",
        sub: "What " + child.guardian + " sees when signing in",
        body:
          '<div class="portal-frame">' +
            '<div class="portal-frame__bar">' +
              '<span class="portal-frame__dots"><i></i><i></i><i></i></span>' +
              '<span class="portal-frame__url">' + Icon("lock", { size: 11 }) +
              "portal.school.edu.krd/guardian</span>" +
            "</div>" +
            '<div class="portal-frame__screen">' +
              '<div class="portal-topbar">' +
                '<span class="sidebar__crest" aria-hidden="true" style="width:28px;height:28px;font-size:10px">SMS</span>' +
                '<span><span class="text-sm strong">Parent Portal</span>' +
                '<span class="text-xs muted" style="display:block">' + UI.esc(child.guardian) + "</span></span>" +
                '<span class="push">' + UI.avatar(child.guardian, "sm") + "</span>" +
              "</div>" +

              '<div class="portal-body">' +
                UI.card({
                  body: '<div class="person">' + UI.avatar(child.name, "lg") +
                    '<span style="min-width:0"><span class="strong">' + UI.esc(child.name) + "</span>" +
                    '<span class="person__meta" style="display:block">' + UI.esc(child.id) + " · " +
                    UI.esc(child.className) + "</span>" +
                    '<span class="row-tight" style="margin-top:6px">' + UI.statusPill(child.status) + "</span></span>" +
                    "</div>"
                }) +

                '<div class="grid grid--3" style="gap:10px">' +
                  UI.stat({ label: "Attendance", value: F.dec(child.attendance), unit: "%",
                    note: "This term" }) +
                  UI.stat({ label: "Average", value: F.dec(child.average), unit: "/100",
                    note: "Term 1 final" }) +
                  UI.stat({ label: t("n.outstanding"), value: F.money(owed), unit: t("n.iqd"),
                    note: "All years" }) +
                "</div>" +

                UI.card({
                  title: "Invoices",
                  flush: true,
                  body: '<ul class="list">' +
                    history.slice().reverse().slice(0, 3).map(function (h) {
                      return "<li><span class=\"list__body\"><span class=\"list__title\">" +
                        "Tuition " + UI.esc(h.year) + "</span>" +
                        '<span class="list__meta">' + UI.esc(h.grade) + " · " +
                        F.int(h.charges) + " " + UI.esc(t("n.iqd")) + "</span></span>" +
                        '<span class="list__aside">' +
                        (h.outstanding > 0
                          ? UI.statusPill("overdue") + '<div class="owed tnum" style="margin-top:4px">' +
                            F.int(h.outstanding) + "</div>"
                          : UI.statusPill("paid")) + "</span></li>";
                    }).join("") + "</ul>"
                }) +

                UI.card({
                  title: "Announcements",
                  flush: true,
                  body: '<ul class="list">' + D.announcements.slice(1, 4).map(function (a) {
                    return "<li><span class=\"list__body\"><span class=\"list__title\">" +
                      UI.esc(a.title) + '</span><span class="list__meta">' +
                      UI.esc(a.when) + "</span></span></li>";
                  }).join("") + "</ul>"
                }) +
              "</div>" +
            "</div>" +
          "</div>",
        foot: Icon("info", { size: 13 }) +
          " Previous-year balances remain visible to the guardian, exactly as they are to Finance"
      }) +
    "</div>";
};
