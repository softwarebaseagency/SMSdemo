/* ============================================================================
   Module 09 — Communication and Notifications
   Announcements, the template library that drives automatic messages, and
   delivery across email, SMS, WhatsApp and in-system.
   ========================================================================= */
window.Views = window.Views || {};

window.Views.comms = function (root) {
  "use strict";
  var t = I18n.t, D = DATA, F = Fmt;

  var totalSent = D.channels.reduce(function (a, c) { return a + c.sent; }, 0);

  root.innerHTML =
    UI.pageHead({
      moduleNo: "09",
      title: t("mod.comms"),
      lede: t("purpose.comms"),
      actions:
        UI.select({ label: "Channel", options: ["All channels", "Email", "SMS", "WhatsApp", "In-system"] }) +
        UI.btn({ label: "Templates", icon: "file", demo: "templates" }) +
        UI.btn({ label: t("act.newAnnouncement"), icon: "plus", variant: "primary", demo: "new-announcement" })
    }) +

    '<div class="grid grid--kpi">' +
      UI.stat({ label: "Messages sent", icon: "megaphone", value: F.int(totalSent),
        note: D.meta.currentYear + " to date" }) +
      UI.stat({ label: "Delivery rate", icon: "checkCircle", value: "97.8", unit: "%",
        delta: 0.6, note: t("k.vsLastMonth") }) +
      UI.stat({ label: "Active templates", icon: "file", value: String(D.templates.length),
        note: "Trigger-driven" }) +
      UI.stat({ label: t("s.scheduled"), icon: "clock", value: "1",
        note: "Parent–teacher meetings" }) +
    "</div>" +

    UI.card({
      title: t("c.deliveryChannels"),
      sub: "Delivery depends on the integrations selected at implementation",
      body: '<div class="channels">' + D.channels.map(function (c) {
        return '<article class="channel"><div class="channel__top">' +
          '<span class="channel__icon">' + Icon(c.icon, { size: 15 }) + "</span>" +
          '<span class="channel__name">' + UI.esc(c.name) + "</span></div>" +
          '<div class="channel__value tnum">' + F.int(c.sent) + "</div>" +
          '<div class="channel__meta">Delivered ' + F.pct(c.rate) + "</div>" +
          UI.track(c.rate, c.rate >= 97 ? "good" : "warn") +
        "</article>";
      }).join("") + "</div>"
    }) +

    '<div class="grid grid--side">' +
      UI.card({
        title: "Announcement composer",
        sub: t("demo.readOnly"),
        body:
          '<div class="composer">' +
            '<dl style="margin:0">' +
              '<div class="composer__row"><dt>To</dt><dd>' +
                UI.pill("All guardians", "info", "users") +
                UI.pill("Grade 1 – 12", "") +
              "</dd></div>" +
              '<div class="composer__row"><dt>Channel</dt><dd>' +
                UI.pill("Email", "info", "mail") +
                UI.pill("SMS", "info", "phone") +
                UI.pill("Portal", "info", "portal") +
              "</dd></div>" +
              '<div class="composer__row"><dt>Subject</dt>' +
                '<dd class="strong">Term 2 parent–teacher meetings</dd></div>' +
            "</dl>" +
            '<div class="composer__text">' +
              "Dear <span class=\"tok\">{{guardian_name}}</span>,<br><br>" +
              "Parent–teacher meetings for <span class=\"tok\">{{student_name}}</span> " +
              "(<span class=\"tok\">{{class}}</span>) will be held on " +
              "<span class=\"tok\">{{meeting_date}}</span>. Please confirm your preferred slot " +
              "through the parent portal.<br><br>" +
              "<span class=\"tok\">{{school_name}}</span>" +
            "</div>" +
            '<div class="composer__foot">' +
              UI.btn({ label: "Send now", icon: "arrowRight", variant: "primary", size: "sm", demo: "send" }) +
              UI.btn({ label: "Schedule", icon: "clock", size: "sm", demo: "schedule" }) +
              '<span class="push text-xs muted">Reaches 1,046 guardian accounts</span>' +
            "</div>" +
          "</div>" +
          '<div style="margin-top:16px">' + UI.notice({
            tone: "brand", icon: "lock", title: t("demo.entryDisabled"),
            text: "The composer is shown for layout only — nothing is sent from this preview."
          }) + "</div>",
        foot: Icon("info", { size: 13 }) +
          " Merge fields resolve per recipient at send time"
      }) +

      UI.card({
        title: "Announcements",
        sub: "School notices, reminders and result notifications",
        flush: true,
        body: '<div class="tablewrap"><table class="data"><thead><tr>' +
          '<th scope="col">Announcement</th>' +
          '<th scope="col">Audience</th>' +
          '<th scope="col">Channel</th>' +
          '<th scope="col" class="num">Reach</th>' +
          '<th scope="col">' + UI.esc(t("n.status")) + "</th>" +
          "</tr></thead><tbody>" +
          D.announcements.map(function (a) {
            return "<tr><td class=\"wrap\"><div class=\"strong\">" + UI.esc(a.title) + "</div>" +
              '<div class="text-xs muted">' + UI.esc(a.when) + "</div></td>" +
              '<td class="muted">' + UI.esc(a.audience) + "</td>" +
              '<td class="muted">' + UI.esc(a.channel) + "</td>" +
              '<td class="num">' + F.int(a.reach) + "</td>" +
              "<td>" + UI.statusPill(a.status) + "</td></tr>";
          }).join("") + "</tbody></table></div>"
      }) +
    "</div>" +

    UI.card({
      title: "Notification templates",
      sub: "Each template fires from a defined trigger — no manual sending required",
      flush: true,
      body: '<div class="tablewrap"><table class="data"><thead><tr>' +
        '<th scope="col">Template</th><th scope="col">Trigger</th>' +
        '<th scope="col">Channel</th><th scope="col" class="num">Sent this year</th>' +
        '<th scope="col">' + UI.esc(t("n.status")) + "</th></tr></thead><tbody>" +
        D.templates.map(function (tpl) {
          return "<tr><td class=\"strong\">" + UI.esc(tpl.name) + "</td>" +
            '<td class="muted">' + UI.esc(tpl.trigger) + "</td>" +
            "<td>" + tpl.channel.split(" · ").map(function (c) {
              return UI.pill(c, "info", c === "SMS" ? "phone" : c === "Email" ? "mail" :
                c === "WhatsApp" ? "message" : "portal");
            }).join(" ") + "</td>" +
            '<td class="num tnum">' + F.int(tpl.uses) + "</td>" +
            "<td>" + UI.statusPill("active") + "</td></tr>";
        }).join("") + "</tbody></table></div>",
      foot: Icon("info", { size: 13 }) +
        " Communication history is retained where configured"
    });
};
