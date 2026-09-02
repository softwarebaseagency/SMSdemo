/* ============================================================================
   Module 07 — Teacher and Staff Records
   Profiles, department and role assignment, and the links into timetable and
   academic responsibilities. Includes the role/permission matrix, since staff
   access is what schools raise as a concern.
   ========================================================================= */
window.Views = window.Views || {};

window.Views.staff = function (root) {
  "use strict";
  var t = I18n.t, D = DATA, F = Fmt;

  var LEVEL_TONE = { Full: "critical", Scoped: "warning", Limited: "good", Technical: "info" };

  root.innerHTML =
    UI.pageHead({
      moduleNo: "07",
      title: t("mod.staff"),
      lede: t("purpose.staff"),
      actions:
        UI.select({ label: "Department", options: ["All departments"].concat(D.departments) }) +
        UI.btn({ label: t("act.export"), icon: "download", demo: "export" }) +
        UI.btn({ label: t("act.addStaff"), icon: "plus", variant: "primary", demo: "add-staff" })
    }) +

    '<div class="grid grid--kpi">' +
      UI.stat({ label: t("k.staffCount"), icon: "briefcase", value: String(D.totals.staff),
        note: D.staff.length - D.totals.staff + " inactive" }) +
      UI.stat({ label: "Teaching staff", icon: "users", value: String(D.teachers.length),
        note: "Across " + D.subjects.length + " subjects" }) +
      UI.stat({ label: "Departments", icon: "layers", value: String(D.departments.length),
        note: "Academic and support" }) +
      UI.stat({ label: "Average tenure", icon: "history", value: "5.8", unit: "yrs",
        note: "Since first appointment" }) +
    "</div>" +

    '<div class="grid grid--wide">' +
      UI.chartCard({
        id: "staffByDepartment",
        title: t("c.staffByDepartment"),
        sub: "Active staff on the current roll"
      }) +
      UI.card({
        title: "Access levels",
        sub: "Role-based access with granular action permissions",
        body: '<dl class="meta-list">' + Object.keys(LEVEL_TONE).map(function (level) {
          var n = D.rolesMatrix.filter(function (r) { return r.level === level; })
            .reduce(function (a, r) { return a + r.users; }, 0);
          return '<div class="meta-row"><dt>' + UI.pill(level, LEVEL_TONE[level]) +
            "</dt><dd>" + n + " users</dd></div>";
        }).join("") + "</dl>",
        foot: Icon("shield", { size: 13 }) + " Least privilege: users only see what their role requires"
      }) +
    "</div>" +

    UI.card({
      title: "Roles and permissions",
      sub: "A role provides the baseline; granular permissions refine it further",
      flush: true,
      body: '<div class="tablewrap"><table class="data"><thead><tr>' +
        '<th scope="col">Role</th><th scope="col">Typical access principle</th>' +
        '<th scope="col" class="num">Users</th><th scope="col">Level</th>' +
        "</tr></thead><tbody>" +
        D.rolesMatrix.map(function (r) {
          return "<tr><td class=\"strong\">" + UI.esc(r.role) + "</td>" +
            '<td class="wrap muted">' + UI.esc(r.access) + "</td>" +
            '<td class="num">' + r.users + "</td>" +
            "<td>" + UI.pill(r.level, LEVEL_TONE[r.level]) + "</td></tr>";
        }).join("") + "</tbody></table></div>",
      foot: Icon("info", { size: 13 }) +
        " Permission and role changes are written to the audit log"
    }) +

    UI.card({
      title: "Teaching staff",
      sub: "Profiles, subject assignment and employment status",
      body: '<div class="staffgrid">' + D.teachers.map(function (s) {
        var subj = D.subjects.filter(function (x) { return x.id === s.subject; })[0];
        return '<article class="staffcard">' +
          '<div class="person">' + UI.avatar(s.name) +
            '<span style="min-width:0"><span class="person__name">' + UI.esc(s.name) + "</span>" +
            '<span class="person__meta" style="display:block">' + UI.esc(s.position) + "</span></span>" +
          "</div>" +
          '<div class="staffcard__tags">' +
            UI.pill(s.department, "info") +
            (subj ? UI.pill(subj.short, "") : "") +
            (s.active ? UI.statusPill("active") : UI.pill("Inactive", "critical")) +
          "</div>" +
          '<dl class="meta-list" style="gap:6px">' +
            '<div class="meta-row"><dt class="text-xs">Staff ID</dt><dd class="text-xs mono">' +
              UI.esc(s.id) + "</dd></div>" +
            '<div class="meta-row"><dt class="text-xs">Since</dt><dd class="text-xs">' +
              UI.esc(s.since.slice(0, 4)) + "</dd></div>" +
          "</dl>" +
          '<div class="text-xs muted" style="overflow-wrap:anywhere">' + UI.esc(s.email) + "</div>" +
        "</article>";
      }).join("") + "</div>"
    }) +

    UI.card({
      title: "All staff",
      sub: "Teaching, administration, finance and support",
      flush: true,
      body: '<div id="staffTable"></div>'
    });

  UI.mountCharts(root, {
    staffByDepartment: {
      type: "bars",
      title: t("c.staffByDepartment"),
      rows: D.charts.staffByDepartment,
      categoryLabel: "Department",
      valueLabel: "Staff",
      labelWidth: 124,
      label: F.int
    }
  });

  UI.dataTable(document.getElementById("staffTable"), {
    rows: D.staff,
    pageSize: 10,
    defaultSort: "name",
    searchPlaceholder: "Search staff, role or department",
    columns: [
      { field: "id", label: "Staff ID",
        render: function (s) { return '<span class="mono">' + UI.esc(s.id) + "</span>"; } },
      { field: "name", label: "Name", wrap: true,
        render: function (s) { return UI.person(s.name, s.position, "sm"); } },
      { field: "department", label: "Department",
        render: function (s) { return UI.pill(s.department, "info"); } },
      { field: "email", label: "Email", wrap: true,
        render: function (s) { return '<span class="muted">' + UI.esc(s.email) + "</span>"; } },
      { field: "phone", label: "Phone",
        render: function (s) { return '<span class="muted tnum">' + UI.esc(s.phone) + "</span>"; } },
      { field: "since", label: "Since", num: true,
        render: function (s) { return '<span class="muted">' + UI.esc(s.since) + "</span>"; } },
      { field: "active", label: t("n.status"),
        render: function (s) {
          return s.active ? UI.statusPill("active") : UI.pill("Inactive", "critical", "xCircle");
        } }
    ],
    onRow: function (s) {
      var subj = D.subjects.filter(function (x) { return x.id === s.subject; })[0];
      UI.openDrawer({
        eyebrow: t("mod.label") + " 07 · " + t("mod.staff.short"),
        title: s.name,
        sub: s.position + " · " + s.department,
        body: '<div style="padding:20px">' +
          '<div class="row-tight" style="margin-bottom:16px">' +
            (s.active ? UI.statusPill("active") : UI.pill("Inactive", "critical", "xCircle")) +
            UI.pill(s.department, "info") +
            (subj ? UI.pill(subj.name, "") : "") +
          "</div>" +
          '<div class="kv">' +
            UI.field("Staff ID", s.id) +
            UI.field("Position", s.position) +
            UI.field("Department", s.department) +
            UI.field("Subject", subj ? subj.name : "—") +
            UI.field("Email", s.email) +
            UI.field("Phone", s.phone) +
            UI.field("Appointed", s.since) +
            UI.field("Employment status", s.active ? "Active" : "Inactive") +
          "</div>" +
          '<hr class="divider" style="margin:20px 0">' +
          UI.notice({ tone: "info", icon: "lock",
            title: "Staff information is permission-controlled",
            text: "Contact and employment details are visible only to roles authorised to see them." }) +
        "</div>",
        foot:
          UI.btn({ label: "View timetable", icon: "clock", demo: "timetable" }) +
          '<span class="push text-xs muted">' + UI.esc(t("demo.readOnly")) + "</span>",
        onMount: function (d) { UI.wireDemoActions(d); }
      });
    }
  });
};
