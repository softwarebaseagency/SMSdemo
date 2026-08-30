/* ============================================================================
   Module 06 — Fees and Payment Management
   The complete student financial ledger. This is where the proposal's core
   rule has to be visible: previous-year balances are shown separately from
   current-year charges, and they survive promotion.
   ========================================================================= */
window.Views = window.Views || {};

window.Views.fees = function (root) {
  "use strict";
  var t = I18n.t, D = DATA, F = Fmt;

  var inv = D.invoice;
  var subtotal = inv.lines.reduce(function (a, l) { return a + l.amount; }, 0);
  var discount = Math.round(subtotal * inv.discountPct / 100);
  var currentDue = subtotal - discount;
  var prior = D.ledgerStudent.priorBalance || 500000;
  var grand = currentDue + prior;

  var debtors = D.students
    .filter(function (s) { return s.outstanding > 0; })
    .sort(function (a, b) { return b.outstanding - a.outstanding; });

  root.innerHTML =
    UI.pageHead({
      moduleNo: "06",
      title: t("mod.fees"),
      lede: t("purpose.fees"),
      actions:
        UI.select({ label: t("n.academicYear"), value: D.meta.currentYear,
          options: D.meta.years.slice().reverse() }) +
        UI.btn({ label: t("act.export"), icon: "download", demo: "export" }) +
        UI.btn({ label: t("act.recordPayment"), icon: "plus", variant: "primary", demo: "record-payment" })
    }) +

    /* One hero figure per view — the number finance leads with */
    UI.card({
      className: "",
      body:
        '<div class="row" style="gap:32px;align-items:flex-end">' +
          "<div>" +
            '<div class="stat__label">' + Icon("alert", { size: 14 }) + " " +
            UI.esc(t("k.outstandingTotal")) + "</div>" +
            '<div class="hero-figure">' + F.money(D.totals.outstanding) +
            ' <span style="font-size:var(--text-md);font-weight:600;color:var(--ink-muted)">' +
            UI.esc(t("n.iqd")) + "</span></div>" +
            '<div class="text-xs muted tnum" style="margin-top:2px">' +
            F.int(D.totals.outstanding) + " · " + UI.esc(D.meta.currentYear) +
            " and all prior years</div>" +
          "</div>" +
          '<div class="row" style="gap:28px;flex:1 1 auto">' +
            '<div><div class="text-xs secondary">' + UI.esc(t("k.expectedRevenue")) + "</div>" +
              '<div class="strong tnum" style="font-size:var(--text-lg)">' +
              F.money(D.totals.expected) + "</div></div>" +
            '<div><div class="text-xs secondary">' + UI.esc(t("k.collectedRevenue")) + "</div>" +
              '<div class="strong tnum" style="font-size:var(--text-lg)">' +
              F.money(D.totals.collected) + "</div></div>" +
            '<div><div class="text-xs secondary">' + UI.esc(t("k.priorYearBalance")) + "</div>" +
              '<div class="owed tnum" style="font-size:var(--text-lg)">' +
              F.money(D.totals.priorYear) + "</div></div>" +
            '<div style="flex:1 1 200px;min-width:180px">' +
              '<div class="row-tight" style="justify-content:space-between">' +
                '<span class="text-xs secondary">' + UI.esc(t("k.collectionRate")) + "</span>" +
                '<span class="strong tnum text-sm">' + F.pct(D.totals.collectionRate) + "</span></div>" +
              '<div style="margin-top:6px">' + UI.track(D.totals.collectionRate, "good") + "</div>" +
              '<div class="text-xs muted" style="margin-top:4px">85% ' + UI.esc(t("k.ofTarget")) + "</div>" +
            "</div>" +
          "</div>" +
        "</div>"
    }) +

    '<div class="grid grid--wide">' +
      UI.chartCard({
        id: "collections",
        title: t("c.collectionsTrend"),
        sub: D.meta.currentYear + " · " + t("n.iqd") + " (millions)"
      }) +
      UI.chartCard({
        id: "paymentMethods",
        title: t("c.paymentMethods"),
        sub: "Receipts issued this academic year"
      }) +
    "</div>" +

    '<div class="grid grid--wide">' +
      UI.chartCard({
        id: "aging",
        title: t("c.outstandingAging"),
        sub: t("n.outstanding") + " · " + t("n.iqd")
      }) +
      UI.card({
        title: t("demo.continuity"),
        sub: "Worked example — the same student across four years",
        body:
          '<div class="carryforward">' +
            '<div class="carryforward__years">' +
              '<div class="carryforward__year carryforward__year--head">' +
                "<span>" + UI.esc(t("n.academicYear")) + "</span><span>Charges</span>" +
                "<span>" + UI.esc(t("s.paid")) + "</span><span>" + UI.esc(t("n.outstanding")) + "</span></div>" +
              D.continuity.map(function (r) {
                return '<div class="carryforward__year"><b>' + UI.esc(r.year) + "</b>" +
                  "<span>" + F.int(r.charges) + "</span><span>" + F.int(r.paid) + "</span>" +
                  '<span class="' + (r.outstanding > 0 ? "owed" : "settled") + '">' +
                  F.int(r.outstanding) + "</span></div>";
              }).join("") +
              '<div class="carryforward__year carryforward__year--total">' +
                "<b>" + UI.esc(t("n.total")) + "</b>" +
                "<span>" + F.int(D.continuity.reduce(function (a, r) { return a + r.charges; }, 0)) + "</span>" +
                "<span>" + F.int(D.continuity.reduce(function (a, r) { return a + r.paid; }, 0)) + "</span>" +
                '<span class="owed">' +
                F.int(D.continuity.reduce(function (a, r) { return a + r.outstanding; }, 0)) + "</span></div>" +
            "</div>" +
          "</div>" +
          '<p class="text-xs secondary" style="margin-top:12px">' + UI.esc(t("demo.continuityNote")) + "</p>",
        foot: Icon("shield", { size: 13 }) +
          " Promotion must never create a financially clean record while prior obligations exist"
      }) +
    "</div>" +

    '<div class="grid grid--side">' +
      UI.card({
        title: "Invoice preview",
        sub: inv.number,
        body:
          '<div class="invoice">' +
            '<div class="invoice__head">' +
              '<div style="flex:1 1 auto;min-width:0">' +
                UI.person(inv.student.name, inv.student.id, "sm") +
                '<div class="text-xs muted" style="margin-top:6px">' +
                UI.esc(inv.student.className) + " · " + UI.esc(inv.student.divisionLabel) + "</div>" +
              "</div>" +
              '<div style="text-align:end">' +
                '<span class="invoice__no">' + UI.esc(inv.number) + "</span>" +
                '<div class="text-xs muted" style="margin-top:6px">Issued ' + UI.esc(inv.issued) + "</div>" +
                '<div class="text-xs muted">Due ' + UI.esc(inv.due) + "</div>" +
              "</div>" +
            "</div>" +
            '<table class="invoice__lines"><thead><tr><th>Description</th>' +
            '<th class="num">' + UI.esc(t("n.amount")) + "</th></tr></thead><tbody>" +
            inv.lines.map(function (l) {
              return "<tr><td>" + UI.esc(l.desc) + '</td><td class="num">' + F.int(l.amount) + "</td></tr>";
            }).join("") + "</tbody></table>" +
            '<dl class="invoice__totals">' +
              '<div class="invoice__total-row"><dt>Subtotal</dt><dd>' + F.int(subtotal) + "</dd></div>" +
              (discount ? '<div class="invoice__total-row"><dt>Discount (' + inv.discountPct +
                "%)</dt><dd>− " + F.int(discount) + "</dd></div>" : "") +
              '<div class="invoice__total-row"><dt>Current year due</dt><dd>' + F.int(currentDue) + "</dd></div>" +
              '<div class="invoice__total-row invoice__total-row--carry"><dt>' +
                UI.esc(t("k.priorYearBalance")) + ' <span class="badge">' +
                Icon("history", { size: 10 }) + " carried forward</span></dt><dd>" + F.int(prior) + "</dd></div>" +
              '<div class="invoice__total-row invoice__total-row--grand"><dt>' +
                UI.esc(t("n.total")) + " payable</dt><dd>" + F.int(grand) + " " +
                UI.esc(t("n.iqd")) + "</dd></div>" +
            "</dl>" +
          "</div>",
        foot:
          UI.btn({ label: t("act.print"), icon: "printer", size: "sm", demo: "print" }) +
          UI.btn({ label: "Send to guardian", icon: "mail", size: "sm", demo: "send-invoice" })
      }) +

      UI.card({
        title: "Outstanding balances",
        sub: "Sorted by amount due — previous-year debt is shown separately",
        flush: true,
        body: '<div id="feesTable"></div>'
      }) +
    "</div>" +

    UI.card({
      title: "Recent payments",
      sub: "Receipts, methods and who recorded them",
      flush: true,
      body: '<div class="tablewrap"><table class="data"><thead><tr>' +
        '<th scope="col">Receipt</th><th scope="col">' + UI.esc(t("n.date")) + "</th>" +
        '<th scope="col">Method</th><th scope="col">Recorded by</th>' +
        '<th scope="col" class="num">' + UI.esc(t("n.amount")) + "</th>" +
        '<th scope="col">' + UI.esc(t("n.status")) + "</th></tr></thead><tbody>" +
        D.payments.map(function (p) {
          return '<tr><td><span class="mono">' + UI.esc(p.ref) + "</span></td>" +
            '<td class="muted">' + UI.esc(p.date) + "</td>" +
            "<td>" + UI.pill(p.method, "info", p.method === "Cash" ? "wallet" :
              p.method === "Card" ? "receipt" : "swap") + "</td>" +
            "<td>" + UI.esc(p.by) + "</td>" +
            '<td class="num strong">' + F.int(p.amount) + "</td>" +
            "<td>" + UI.statusPill("paid") + "</td></tr>";
        }).join("") + "</tbody></table></div>"
    });

  UI.mountCharts(root, {
    collections: {
      type: "line",
      title: t("c.collectionsTrend"),
      categories: D.charts.collections.categories,
      series: D.charts.collections.series,
      categoryLabel: "Month",
      summary: "Collections track expected revenue at 85% by June.",
      label: function (v) { return F.int(v) + "M"; }
    },
    paymentMethods: {
      type: "donut",
      title: t("c.paymentMethods"),
      rows: D.charts.paymentMethods,
      categoryLabel: "Method",
      valueLabel: "Receipts",
      centerValue: F.int(D.charts.paymentMethods.reduce(function (a, r) { return a + r.value; }, 0)),
      centerLabel: "Receipts",
      label: F.int
    },
    aging: {
      type: "bars",
      title: t("c.outstandingAging"),
      rows: D.charts.aging,
      ordinal: true,
      categoryLabel: "Age",
      valueLabel: t("n.outstanding"),
      labelWidth: 116,
      label: F.money
    }
  });

  UI.dataTable(document.getElementById("feesTable"), {
    rows: debtors,
    pageSize: 8,
    defaultSort: "outstanding",
    defaultDir: "desc",
    searchPlaceholder: t("act.searchStudents"),
    columns: [
      { field: "name", label: t("n.student"), wrap: true,
        render: function (s) { return UI.person(s.name, s.id + " · " + s.className, "sm"); } },
      { field: "charges", label: "Current year", num: true,
        render: function (s) { return F.int(s.charges - s.paid); } },
      { field: "priorBalance", label: "Previous years", num: true,
        render: function (s) {
          return s.priorBalance > 0
            ? '<span class="owed">' + F.int(s.priorBalance) + "</span>"
            : '<span class="muted">—</span>';
        } },
      { field: "outstanding", label: t("n.total"), num: true,
        render: function (s) { return '<span class="strong">' + F.int(s.outstanding) + "</span>"; } },
      { field: "status", label: t("n.status"), sortable: false,
        render: function (s) {
          if (s.priorBalance > 0) { return UI.statusPill("overdue"); }
          return s.paid > 0 ? UI.statusPill("partial") : UI.statusPill("paymentPending");
        } }
    ],
    onRow: function (s) {
      var history = D.historyFor(s);
      UI.openDrawer({
        eyebrow: t("mod.label") + " 06 · " + t("mod.fees.short"),
        title: s.name,
        sub: s.id + " · " + s.className,
        body: '<div style="padding:20px">' +
          '<div class="carryforward">' +
            '<div class="row-tight"><strong>' + UI.esc(t("demo.continuity")) + "</strong></div>" +
            '<div class="carryforward__years">' +
              '<div class="carryforward__year carryforward__year--head">' +
                "<span>" + UI.esc(t("n.academicYear")) + "</span><span>Charges</span>" +
                "<span>" + UI.esc(t("s.paid")) + "</span><span>" + UI.esc(t("n.outstanding")) + "</span></div>" +
              history.map(function (h) {
                return '<div class="carryforward__year"><b>' + UI.esc(h.year) + "</b>" +
                  "<span>" + F.int(h.charges) + "</span><span>" + F.int(h.paid) + "</span>" +
                  '<span class="' + (h.outstanding > 0 ? "owed" : "settled") + '">' +
                  F.int(h.outstanding) + "</span></div>";
              }).join("") +
            "</div></div>" +
          '<p class="text-xs secondary" style="margin-top:12px">' +
          UI.esc(t("demo.continuityNote")) + "</p></div>",
        foot:
          UI.btn({ label: t("act.recordPayment"), icon: "plus", variant: "primary", demo: "record-payment" }) +
          UI.btn({ label: "Statement", icon: "receipt", demo: "statement" }) +
          '<span class="push text-xs muted">' + UI.esc(t("demo.readOnly")) + "</span>",
        onMount: function (d) { UI.wireDemoActions(d); }
      });
    }
  });
};
