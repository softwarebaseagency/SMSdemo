/* ============================================================================
   Lezan SMS — Shell, navigation and hash router

   Exactly the ten modules named in the proposal, grouped the way a real
   product would group them. Every module is deep-linkable (#/students), so
   back/forward and shared links behave.
   ========================================================================= */
(function (global) {
  "use strict";

  var t = I18n.t;

  /* ---- The ten modules — no more, no fewer ---------------------------- */
  var NAV = [
    { group: "nav.overview", items: [
      { id: "reports",    no: "10", key: "mod.reports.short",    full: "mod.reports",    icon: "chartBar" }
    ]},
    { group: "nav.lifecycle", items: [
      { id: "admissions", no: "01", key: "mod.admissions.short", full: "mod.admissions", icon: "inbox" },
      { id: "students",   no: "02", key: "mod.students.short",   full: "mod.students",   icon: "userSquare" },
      { id: "attendance", no: "03", key: "mod.attendance.short", full: "mod.attendance", icon: "calendarCheck" }
    ]},
    { group: "nav.academics", items: [
      { id: "timetable",  no: "04", key: "mod.timetable.short",  full: "mod.timetable",  icon: "clock" },
      { id: "exams",      no: "05", key: "mod.exams.short",      full: "mod.exams",      icon: "award" }
    ]},
    { group: "nav.finance", items: [
      { id: "fees",       no: "06", key: "mod.fees.short",       full: "mod.fees",       icon: "wallet" }
    ]},
    { group: "nav.people", items: [
      { id: "staff",      no: "07", key: "mod.staff.short",      full: "mod.staff",      icon: "briefcase" },
      { id: "portal",     no: "08", key: "mod.portal.short",     full: "mod.portal",     icon: "portal" },
      { id: "comms",      no: "09", key: "mod.comms.short",      full: "mod.comms",      icon: "megaphone" }
    ]}
  ];

  var MODULES = {};
  NAV.forEach(function (g) { g.items.forEach(function (i) { MODULES[i.id] = i; }); });

  var DEFAULT_ROUTE = "reports";
  var main = document.getElementById("main");
  var sidebar = document.getElementById("sidebar");

  /* ======================================================================
     Sidebar
     =================================================================== */
  function paintNav() {
    document.getElementById("navScroll").innerHTML = NAV.map(function (g) {
      return '<div class="navgroup"><p class="navgroup__label">' + UI.esc(t(g.group)) + "</p>" +
        g.items.map(function (i) {
          return '<button class="navitem" type="button" data-route="' + i.id + '">' +
            '<span class="navitem__num">' + i.no + "</span>" +
            Icon(i.icon, { size: 18, cls: "navitem__icon" }) +
            '<span class="navitem__label">' + UI.esc(t(i.key)) + "</span></button>";
        }).join("") + "</div>";
    }).join("");

    document.getElementById("navScroll").addEventListener("click", function (e) {
      var b = e.target.closest("[data-route]");
      if (!b) { return; }
      go(b.getAttribute("data-route"));
      if (window.matchMedia("(max-width: 1023px)").matches) { closeSidebar(); }
    });
    markActive();
  }

  function markActive() {
    var route = currentRoute();
    document.querySelectorAll("[data-route]").forEach(function (b) {
      if (b.getAttribute("data-route") === route) { b.setAttribute("aria-current", "page"); }
      else { b.removeAttribute("aria-current"); }
    });
  }

  function openSidebar() {
    sidebar.setAttribute("data-open", "true");
    document.getElementById("menuBtn").setAttribute("aria-expanded", "true");
    ensureScrim();
    scrim.setAttribute("data-open", "true");
  }
  function closeSidebar() {
    sidebar.removeAttribute("data-open");
    document.getElementById("menuBtn").setAttribute("aria-expanded", "false");
    if (scrim) { scrim.removeAttribute("data-open"); }
  }

  /* Escape closes the nav drawer — every overlay needs a way out */
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && sidebar.getAttribute("data-open") === "true") {
      closeSidebar();
      document.getElementById("menuBtn").focus();
    }
  });

  /* Widening past the breakpoint turns the drawer back into a fixed rail —
     drop the open state, or the scrim is left dimming a desktop layout. */
  var wide = window.matchMedia("(min-width: 1024px)");
  (wide.addEventListener ? wide.addEventListener.bind(wide, "change") :
    wide.addListener.bind(wide))(function (e) {
    if (e.matches) { closeSidebar(); }
  });
  var scrim = null;
  function ensureScrim() {
    if (scrim) { return; }
    scrim = document.createElement("div");
    scrim.className = "scrim";
    scrim.addEventListener("click", closeSidebar);
    /* The scrim is fixed-position, so it belongs on body — the sidebar is a
       grid child of .app and is not a valid insertBefore reference here. */
    document.body.appendChild(scrim);
  }

  /* ======================================================================
     Router
     =================================================================== */
  function currentRoute() {
    var hash = (location.hash || "").replace(/^#\/?/, "").split("?")[0];
    return MODULES[hash] ? hash : DEFAULT_ROUTE;
  }

  function go(route) {
    if (currentRoute() === route && location.hash) { render(); return; }
    location.hash = "#/" + route;
  }

  function render() {
    var route = currentRoute();
    var mod = MODULES[route];
    var view = global.Views && global.Views[route];

    document.title = t(mod.full) + " · " + t("app.name");
    markActive();

    main.innerHTML = "";
    main.className = "content view-enter";

    if (!view) {
      main.innerHTML = UI.empty({ title: "Module not available", text: "This route has no view registered." });
      return;
    }

    view(main, { module: mod });

    UI.wireDemoActions(main);
    I18n.apply(main);

    /* Move focus to the main region after a route change (screen readers) */
    main.focus({ preventScroll: true });
    window.scrollTo({ top: 0, behavior: "auto" });
  }

  window.addEventListener("hashchange", function () {
    UI.closeDrawer();
    render();
  });

  /* ======================================================================
     Topbar
     =================================================================== */
  function paintTopbar() {
    document.getElementById("menuBtn").innerHTML = Icon("menu", { size: 17 });
    document.getElementById("menuBtn").setAttribute("aria-label", t("act.openMenu"));
    document.getElementById("searchIcon").innerHTML = Icon("search", { size: 15 });
    document.getElementById("langBtn").innerHTML = Icon("globe", { size: 17 });
    document.getElementById("langBtn").setAttribute("aria-label", t("act.language"));
    document.getElementById("bellBtn").innerHTML = Icon("bell", { size: 17 }) +
      '<span class="dot">' + DATA.notifications.length + "</span>";
    document.getElementById("bellBtn").setAttribute("aria-label",
      t("act.notifications") + " (" + DATA.notifications.length + ")");
    document.getElementById("userBtn").innerHTML =
      UI.avatar("Rezan Ibrahim", "sm") + Icon("chevronDown", { size: 13 });
    document.getElementById("userBtn").setAttribute("aria-label", t("act.account"));

    var gs = document.getElementById("globalSearch");
    gs.placeholder = t("act.searchStudents");
    gs.setAttribute("aria-label", t("act.searchStudents"));

    var ys = document.getElementById("yearSelect");
    ys.setAttribute("aria-label", t("n.academicYear"));
    ys.innerHTML = DATA.meta.years.slice().reverse().map(function (y) {
      return '<option value="' + y + '"' + (y === DATA.meta.currentYear ? " selected" : "") + ">" +
        y + (y === DATA.meta.currentYear ? "" : "") + "</option>";
    }).join("");
  }

  /* ---- Popover menus --------------------------------------------------- */
  var openMenu = null;

  function closeMenu() {
    if (!openMenu) { return; }
    openMenu.anchor.setAttribute("aria-expanded", "false");
    openMenu.node.remove();
    openMenu = null;
    document.removeEventListener("click", onDocClick, true);
    document.removeEventListener("keydown", onMenuKey, true);
  }
  function onDocClick(e) {
    if (openMenu && !openMenu.node.contains(e.target) && !openMenu.anchor.contains(e.target)) { closeMenu(); }
  }
  function onMenuKey(e) {
    if (e.key === "Escape" && openMenu) { var a = openMenu.anchor; closeMenu(); a.focus(); }
  }

  function showMenu(anchor, html, onClick) {
    if (openMenu && openMenu.anchor === anchor) { closeMenu(); return; }
    closeMenu();
    var node = document.createElement("div");
    node.className = "menu";
    node.setAttribute("role", "menu");
    node.innerHTML = html;
    document.body.appendChild(node);

    var box = anchor.getBoundingClientRect();
    var width = node.offsetWidth;
    var left = I18n.dir() === "rtl" ? box.left : box.right - width;
    node.style.left = Math.max(8, Math.min(window.innerWidth - width - 8, left)) + "px";
    node.style.top = (box.bottom + window.scrollY + 6) + "px";

    anchor.setAttribute("aria-expanded", "true");
    openMenu = { anchor: anchor, node: node };
    if (onClick) { node.addEventListener("click", onClick); }
    var first = node.querySelector("button, a");
    if (first) { first.focus(); }
    setTimeout(function () {
      document.addEventListener("click", onDocClick, true);
      document.addEventListener("keydown", onMenuKey, true);
    }, 0);
  }

  function wireTopbar() {
    document.getElementById("menuBtn").addEventListener("click", function () {
      if (sidebar.getAttribute("data-open") === "true") { closeSidebar(); } else { openSidebar(); }
    });

    /* Language */
    document.getElementById("langBtn").addEventListener("click", function () {
      var html = '<div class="menu__label">' + UI.esc(t("act.language")) + "</div>" +
        I18n.all().map(function (l) {
          return '<button type="button" role="menuitemradio" data-lang="' + l.code +
            '" aria-checked="' + (l.code === I18n.get()) + '">' + l.meta.native +
            '<span class="muted text-xs" style="margin-inline-start:6px">' + l.meta.short + "</span></button>";
        }).join("");
      showMenu(this, html, function (e) {
        var b = e.target.closest("[data-lang]");
        if (!b) { return; }
        I18n.set(b.getAttribute("data-lang"));
        closeMenu();
      });
    });

    /* Notifications */
    document.getElementById("bellBtn").addEventListener("click", function () {
      var html = '<div class="menu__label">' + UI.esc(t("act.notifications")) + "</div>" +
        '<ul class="list" style="min-width:300px;max-width:340px">' +
        DATA.notifications.map(function (n) {
          return '<li style="padding:10px 12px"><span class="' +
            UI.cls(["pill", "pill--icon", n.tone && "pill--" + n.tone]) + '" style="margin-top:2px">' +
            Icon(n.tone === "critical" ? "alert" : n.tone === "good" ? "checkCircle" : "info", { size: 12 }) +
            "</span><span class=\"list__body\"><span class=\"list__title\">" + UI.esc(n.title) +
            '</span><span class="list__meta">' + UI.esc(n.meta) + "</span></span></li>";
        }).join("") + "</ul>";
      showMenu(this, html);
    });

    /* Account */
    document.getElementById("userBtn").addEventListener("click", function () {
      var html = '<div class="menu__label">Rezan Ibrahim</div>' +
        '<div style="padding:0 12px 8px;font-size:var(--text-xs);color:var(--ink-muted)">' +
        UI.esc(t("role.director")) + " · rezan.director@lezan.edu.krd</div><hr>" +
        '<button type="button" data-demo-action="settings">' + Icon("settings", { size: 15 }) +
        "Settings</button>" +
        '<button type="button" data-demo-action="audit">' + Icon("shield", { size: 15 }) +
        "Audit log</button><hr>" +
        '<button type="button" data-signout>' + Icon("logout", { size: 15 }) +
        UI.esc(t("act.signOut")) + "</button>";
      showMenu(this, html, function (e) {
        if (e.target.closest("[data-signout]")) { location.href = "index.html"; return; }
        var d = e.target.closest("[data-demo-action]");
        if (d) { UI.toast(t("demo.entryDisabled"), "lock"); closeMenu(); }
      });
    });

    /* Global search jumps into the student register with the query applied */
    var gs = document.getElementById("globalSearch");
    gs.addEventListener("keydown", function (e) {
      if (e.key !== "Enter") { return; }
      var q = gs.value.trim();
      global.Views.pendingStudentQuery = q;
      go("students");
      gs.blur();
    });

    /* The year selector is a demo control — it never rewrites the records */
    document.getElementById("yearSelect").addEventListener("change", function () {
      this.value = DATA.meta.currentYear;
      UI.toast(t("demo.entryDisabled"), "lock");
    });

    /* "/" focuses search, the way a data product should behave */
    document.addEventListener("keydown", function (e) {
      if (e.key === "/" && !/^(INPUT|TEXTAREA|SELECT)$/.test(document.activeElement.tagName)) {
        e.preventDefault();
        gs.focus();
      }
    });
  }

  /* ======================================================================
     Boot
     =================================================================== */
  function refreshChrome() {
    paintNav();
    paintTopbar();
    render();
  }

  I18n.restore();
  paintNav();
  paintTopbar();
  wireTopbar();
  I18n.apply();
  I18n.onChange(refreshChrome);

  if (!location.hash) { location.replace("#/" + DEFAULT_ROUTE); }
  render();

  global.App = { go: go, MODULES: MODULES, NAV: NAV };
})(window);
