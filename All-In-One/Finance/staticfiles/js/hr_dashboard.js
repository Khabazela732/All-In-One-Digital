document.addEventListener("DOMContentLoaded", function () {

    const sidebar = document.getElementById("sidebar");
    const toggleBtn = document.getElementById("sidebarToggle");
    const themeToggle = document.getElementById("themeToggle");
    const searchInput = document.querySelector("input[name='search']");
    const tableRows = document.querySelectorAll(".employee-table tbody tr");

    const profileBtn = document.getElementById("profileBtn");
    const profileMenu = document.getElementById("profileMenu");

    const body = document.body;


    /* ==============================
       SIDEBAR STATE (PERSISTENT)
    ============================== */
    const savedSidebar = localStorage.getItem("sidebar-state");

    if (savedSidebar === "collapsed") {
        sidebar?.classList.add("collapsed");
    }

    if (toggleBtn && sidebar) {
        toggleBtn.addEventListener("click", function () {
            sidebar.classList.toggle("collapsed");

            localStorage.setItem(
                "sidebar-state",
                sidebar.classList.contains("collapsed") ? "collapsed" : "expanded"
            );
        });
    }


    /* ==============================
       DARK / LIGHT MODE TOGGLE
    ============================== */
    const savedTheme = localStorage.getItem("theme");

    if (savedTheme) {
        body.setAttribute("data-theme", savedTheme);
        updateThemeIcon(savedTheme);
    }

    if (themeToggle) {
        themeToggle.addEventListener("click", function () {

            let currentTheme = body.getAttribute("data-theme");

            let newTheme = currentTheme === "dark" ? "light" : "dark";

            body.setAttribute("data-theme", newTheme);

            localStorage.setItem("theme", newTheme);

            updateThemeIcon(newTheme);
        });
    }

    function updateThemeIcon(theme) {
        if (!themeToggle) return;

        const icon = themeToggle.querySelector("i");

        if (theme === "dark") {
            icon.className = "fas fa-moon";
        } else {
            icon.className = "fas fa-sun";
        }
    }


    /* ==============================
       PROFILE DROPDOWN
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
       HYBRID SEARCH (FRONTEND FILTER)
       - only filters current page
       - backend still handles full search
    ============================== */
    if (searchInput) {

        searchInput.addEventListener("input", function () {

            const value = this.value.toLowerCase();

            tableRows.forEach(row => {

                const text = row.innerText.toLowerCase();

                if (text.includes(value)) {
                    row.style.display = "";
                } else {
                    row.style.display = "none";
                }

            });

        });

    }


    /* ==============================
       ESC KEY HANDLING
    ============================== */
    document.addEventListener("keydown", function (e) {

        if (e.key === "Escape") {
            profileMenu?.classList.remove("show");
        }

    });

});