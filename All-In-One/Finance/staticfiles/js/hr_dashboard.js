/* ==============================
   ENTERPRISE HR DASHBOARD JS (FIXED)
============================== */

document.addEventListener("DOMContentLoaded", function () {

    const sidebar = document.getElementById("sidebar");
    const toggleBtn = document.getElementById("sidebarToggle");
    const profileBtn = document.getElementById("profileBtn");
    const profileMenu = document.getElementById("profileMenu");
    const body = document.body;

    /* ==============================
       SIDEBAR STATE INIT
    ============================== */
    const savedState = localStorage.getItem("sidebar-state");

    if (savedState === "collapsed") {
        sidebar.classList.add("collapsed");
    }

    /* ==============================
       TOGGLE SIDEBAR (MAIN FIX)
    ============================== */
    if (toggleBtn && sidebar) {
        toggleBtn.addEventListener("click", function () {
            sidebar.classList.toggle("collapsed");

            if (sidebar.classList.contains("collapsed")) {
                localStorage.setItem("sidebar-state", "collapsed");
            } else {
                localStorage.setItem("sidebar-state", "expanded");
            }
        });
    }

    /* ==============================
       PROFILE DROPDOWN (SAFE)
    ============================== */
    if (profileBtn && profileMenu) {

        profileBtn.addEventListener("click", function (e) {
            e.stopPropagation();
            profileMenu.classList.toggle("show");
        });

        document.addEventListener("click", function () {
            profileMenu.classList.remove("show");
        });
    }

    /* ==============================
       ACTIVE NAV ITEM
    ============================== */
    const navItems = document.querySelectorAll(".nav-item");

    navItems.forEach(item => {
        item.addEventListener("click", function () {
            navItems.forEach(n => n.classList.remove("active"));
            this.classList.add("active");
        });
    });

    /* ==============================
       GLOBAL ESC CLOSE DROPDOWNS
    ============================== */
    document.addEventListener("keydown", function (e) {
        if (e.key === "Escape") {
            profileMenu?.classList.remove("show");
        }
    });

});