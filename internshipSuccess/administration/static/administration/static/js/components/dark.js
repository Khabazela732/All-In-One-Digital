const THEME_KEY = "theme";

function toggleDarkTheme() {
    setTheme("light");
}

/**
 * Set theme for mazer
 * @param {"dark"|"light"} theme
 * @param {boolean} persist 
 */
function setTheme(theme, persist = false) {
    document.body.classList.remove("dark", "light");
    document.body.classList.add(theme);
    document.documentElement.setAttribute('data-bs-theme', theme);

    if (persist) {
        localStorage.setItem(THEME_KEY, theme);
    }

    // If DataTable has already been initialized, redraw it to apply new theme styles
    if ($.fn.DataTable.isDataTable('#induction-posts')) {
        $('#induction-posts').DataTable().draw();
    }
}

/**
 * Init theme from setTheme()
 */
function initTheme() {
    // If the user manually set a theme, we'll load that
    const storedTheme = localStorage.getItem(THEME_KEY);
    if (storedTheme) {
        return setTheme(storedTheme);
    }
    // Detect if the user set his preferred color scheme to dark
    if (!window.matchMedia) {
        return;
    }

    // Media query to detect dark preference
    const mediaQuery = window.matchMedia("(prefers-color-scheme: dark)");

    // Register change listener
    mediaQuery.addEventListener("change", (e) =>
        setTheme(e.matches ? "dark" : "light", true)
    );
    return setTheme("light", true);
}

window.addEventListener('DOMContentLoaded', () => {
    const toggler = document.getElementById("toggle-dark");
    const theme = localStorage.getItem(THEME_KEY);

    if (toggler) {
        toggler.checked = theme === "dark";

        toggler.addEventListener("input", (e) => {
            setTheme(e.target.checked ? "dark" : "light", true);
        });
    }

    // Initialize DataTable
    $('#induction-posts').DataTable();
});

initTheme();
