/* ============================================================================
   Module 04 — Timetable and Class Scheduling
   Classes, teachers, subjects, rooms and periods in one structured grid,
   with the conflict check surfaced rather than buried.
   ========================================================================= */
window.Views = window.Views || {};

window.Views.timetable = function (root) {
  "use strict";
  var t = I18n.t, D = DATA;

  /* One hue per subject department — identity, assigned by entity */
  var DEPT_SLOT = { "Languages": 0, "Mathematics": 1, "Science": 2,
                    "Humanities": 3, "Arts & Sport": 5 };
  function slotStyle(subject) {
    var i = DEPT_SLOT[subject.dept];
    if (i === undefined) { i = 0; }
    var hue = Charts.seriesColor(i);
    return "--slot-hue:" + hue + ";--slot-bg:color-mix(in srgb, " + hue + " 9%, #fff)";
  }

  var conflicts = 0;
  D.timetable.forEach(function (r) {
    if (r.cells) { r.cells.forEach(function (c) { if (c && c.conflict) { conflicts += 1; } }); }
  });

  var head = "<tr><th scope=\"col\">Period</th>" +
    D.weekdays.map(function (d) { return '<th scope="col">' + UI.esc(d) + "</th>"; }).join("") + "</tr>";

  var body = D.timetable.map(function (row) {
    var label = '<th scope="row">' + UI.esc(row.period.label) +
      "<span>" + UI.esc(row.period.time) + "</span></th>";

    if (!row.cells) {
      return "<tr>" + label + '<td colspan="' + D.weekdays.length + '">' +
        '<div class="slot slot--break"><span class="slot__subject">' +
        UI.esc(row.period.label) + "</span></div></td></tr>";
    }

    return "<tr>" + label + row.cells.map(function (c) {
      if (!c) {
        return '<td><div class="slot slot--free"><div class="slot__meta">Free period</div></div></td>';
      }
      return "<td><div class=\"slot" + (c.conflict ? " slot--conflict" : "") +
        '" style="' + slotStyle(c.subject) + '">' +
        '<div class="slot__subject">' + UI.esc(c.subject.short) +
        (c.conflict ? " " + Icon("alert", { size: 11 }) : "") + "</div>" +
        '<div class="slot__meta">' + UI.esc(c.teacher.name.split(" ")[0]) + " " +
        UI.esc(c.teacher.name.split(" ")[1] || "") + "<br>" + UI.esc(c.room) + "</div></div></td>";
    }).join("") + "</tr>";
  }).join("");

  root.innerHTML =
    UI.pageHead({
      moduleNo: "04",
      title: t("mod.timetable"),
      lede: t("purpose.timetable"),
      actions:
        UI.select({ label: t("n.class"), value: "Grade 9 A",
          options: ["KG2 A", "Grade 1 A", "Grade 5 A", "Grade 7 B", "Grade 9 A", "Grade 11 A", "Grade 12 B"] }) +
        UI.btn({ label: t("act.print"), icon: "printer", demo: "print" }) +
        UI.btn({ label: t("act.editTimetable"), icon: "settings", variant: "primary", demo: "edit-timetable" })
    }) +

    '<div class="grid grid--kpi">' +
      UI.stat({ label: "Classes scheduled", icon: "grid", value: "30",
        note: "KG1 – Grade 12, sections A and B" }) +
      UI.stat({ label: "Teaching periods per week", icon: "clock", value: "180",
        note: "6 periods × 5 days × 6 grades" }) +
      UI.stat({ label: "Rooms in use", icon: "door", value: String(D.rooms.length),
        note: "Including labs and specialist rooms" }) +
      UI.stat({ label: "Scheduling conflicts", icon: "alert", value: String(conflicts),
        note: "Teacher, class and room checks" }) +
    "</div>" +

    (conflicts ? UI.notice({
      tone: "critical", icon: "alert",
      title: conflicts + " scheduling conflict detected",
      text: "Wednesday, Period 4 — the assigned teacher is already timetabled with another class in this period.",
      aside: UI.btn({ label: "Resolve", size: "sm", demo: "resolve-conflict" })
    }) : "") +

    UI.card({
      title: "Weekly timetable — Grade 9 A",
      sub: D.meta.currentYear + " · Term 2 · " + t("demo.readOnly"),
      flush: true,
      body: '<div class="tablewrap"><div class="timetable"><table>' +
        "<thead>" + head + "</thead><tbody>" + body + "</tbody></table></div></div>",
      foot: '<div class="row-tight">' +
        Object.keys(DEPT_SLOT).map(function (dept) {
          return '<span class="row-tight" style="gap:6px"><span class="legend__key" style="background:' +
            Charts.seriesColor(DEPT_SLOT[dept]) + '"></span><span class="text-xs secondary">' +
            UI.esc(dept) + "</span></span>";
        }).join("") + "</div>"
    }) +

    '<div class="grid grid--2">' +
      UI.card({
        title: "Teacher assignments",
        sub: "Teacher-to-subject and teacher-to-class relationships",
        flush: true,
        body: '<div class="tablewrap"><table class="data"><thead><tr>' +
          '<th scope="col">' + UI.esc(t("n.teacher")) + "</th>" +
          '<th scope="col">' + UI.esc(t("n.subject")) + "</th>" +
          '<th scope="col" class="num">Periods</th>' +
          '<th scope="col">' + UI.esc(t("n.room")) + "</th></tr></thead><tbody>" +
          D.teachers.slice(0, 8).map(function (tc, i) {
            var subj = D.subjects.filter(function (s) { return s.id === tc.subject; })[0];
            return "<tr><td>" + UI.person(tc.name, tc.position, "sm") + "</td>" +
              "<td>" + UI.esc(subj ? subj.name : "—") + "</td>" +
              '<td class="num">' + (16 + (i % 5) * 2) + "</td>" +
              '<td class="muted">' + UI.esc(D.rooms[i % D.rooms.length]) + "</td></tr>";
          }).join("") + "</tbody></table></div>"
      }) +
      UI.card({
        title: "Period configuration",
        sub: "Periods, breaks and the daily bell schedule",
        body: '<dl class="meta-list">' + D.periods.map(function (p) {
          return '<div class="meta-row"><dt>' +
            (p.isBreak ? UI.pill(p.label, "", "clock") : UI.esc(p.label)) +
            '</dt><dd class="tnum">' + UI.esc(p.time) + "</dd></div>";
        }).join("") + "</dl>",
        foot: Icon("info", { size: 13 }) + " Substitute handling and room allocation follow the same schedule"
      }) +
    "</div>";
};
