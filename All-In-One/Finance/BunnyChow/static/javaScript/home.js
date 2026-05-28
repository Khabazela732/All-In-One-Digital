// Stunning Loading Animation (FIRST - Critical)
// Circular Progress Loading (0-100%)
// Circular Progress Loading (0-100%)
document.addEventListener('DOMContentLoaded', () => {
    // =========================
    // ELEMENTS
    // =========================
    const loader = document.getElementById('loader');
    const pageContent = document.getElementById('page-content');
    const progressFill = document.querySelector('.progress-fill');
    const progressText = document.querySelector('.progress-text');

    // =========================
    // SAFETY CHECK
    // =========================
    if (!loader || !progressFill || !progressText) {
        console.error('Loader elements missing');
        return;
    }

    // =========================
    // SETTINGS
    // =========================
    let progress = 0;
    const maxProgress = 100;
    const radius = 85;
    const circumference = 2 * Math.PI * radius;

    // Lock scrolling while loading
    document.body.style.overflow = 'hidden';

    // =========================
    // INITIAL SVG RING
    // =========================
    progressFill.style.strokeDasharray = circumference;
    progressFill.style.strokeDashoffset = circumference;
    progressText.textContent = '0%';

    // =========================
    // PROGRESS ANIMATION
    // =========================
    const progressInterval = setInterval(() => {
        progress += 2;

        if (progress >= maxProgress) {
            progress = maxProgress;
        }

        // Update circular ring
        const offset =
            circumference -
            (progress / 100) * circumference;

        progressFill.style.strokeDashoffset =
            offset;

        // Update percentage text
        progressText.textContent =
            `${progress}%`;

        // Finish loader
        if (progress === maxProgress) {
            clearInterval(progressInterval);

            setTimeout(() => {
                loader.classList.add('hidden');

                // only if page-content exists
                if (pageContent) {
                    pageContent.classList.add(
                        'page-visible'
                    );
                }

                document.body.style.overflow =
                    'auto';
            }, 800);
        }
    }, 50);
});


// Mobile menu toggle
const navToggle = document.querySelector('.nav-toggle');
const navMenu = document.querySelector('.nav-menu');

if (navToggle && navMenu) {
    navToggle.addEventListener('click', () => {
        navMenu.classList.toggle('active');
    });
}


// Close mobile menu on regular nav link click (excluding dropdown toggles)
document.querySelectorAll('.nav-menu .nav-link').forEach(link => {
    // Skip if this link has a dropdown menu
    if (link.parentElement.classList.contains('dropdown')) {
        return;
    }
    
    link.addEventListener('click', () => {
        navMenu.classList.remove('active');
    });
});


// Smooth scrolling
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        // Skip if this is a dropdown toggle
        if (this.parentElement.classList.contains('dropdown')) {
            return;
        }
        
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    });
});


// Hero animation on load (AFTER loader)
window.addEventListener('load', () => {
    const heroTitle = document.querySelector('.hero-title');
    if (heroTitle) {
        heroTitle.style.opacity = '0';
        heroTitle.style.transform = 'translateY(30px)';
        heroTitle.style.transition = 'all 1s ease';
        setTimeout(() => {
            heroTitle.style.opacity = '1';
            heroTitle.style.transform = 'translateY(0)';
        }, 200);
    }
});


// ===== DROPDOWN FUNCTIONALITY - Works for ALL 3 dropdowns =====
document.querySelectorAll('.nav-item.dropdown .nav-link').forEach(dropdownLink => {
    dropdownLink.addEventListener('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        
        // Get the dropdown menu for THIS specific dropdown
        const dropdownMenu = this.nextElementSibling;
        
        // Toggle the show class
        const isOpen = dropdownMenu.classList.toggle('show');
        
        // Update active state for arrow rotation
        if (isOpen) {
            this.classList.add('active');
        } else {
            this.classList.remove('active');
        }
        
        // Close all OTHER dropdowns when opening one
        document.querySelectorAll('.nav-item.dropdown .nav-link').forEach(otherLink => {
            if (otherLink !== this) {
                otherLink.classList.remove('active');
            }
        });
        document.querySelectorAll('.dropdown-menu.show').forEach(menu => {
            if (menu !== dropdownMenu) {
                menu.classList.remove('show');
            }
        });
    });
});


// Close dropdown when clicking outside
document.addEventListener('click', function(e) {
    // Check if click is outside all dropdowns
    if (!e.target.closest('.nav-item.dropdown')) {
        // Close all dropdowns
        document.querySelectorAll('.dropdown-menu.show').forEach(menu => {
            menu.classList.remove('show');
        });
        document.querySelectorAll('.nav-link.active').forEach(link => {
            link.classList.remove('active');
        });
    }
});


// Close dropdown when clicking a dropdown link (like "Open Vacancies")
document.querySelectorAll('.dropdown-link').forEach(link => {
    link.addEventListener('click', function() {
        // Close all dropdowns
        document.querySelectorAll('.dropdown-menu.show').forEach(menu => {
            menu.classList.remove('show');
        });
        document.querySelectorAll('.nav-link.active').forEach(link => {
            link.classList.remove('active');
        });
    });
});

document.addEventListener("DOMContentLoaded", () => {
    const titleElement = document.getElementById("typing-title");
    const subtitleElement = document.getElementById("typing-subtitle");

    if (titleElement) {
        titleElement.textContent =
            "Enterprise Human Resource & Recruitment Management Platform";
    }

    if (subtitleElement) {
        subtitleElement.textContent =
            "Streamline recruitment, employee onboarding, workforce management, vacancy publishing, candidate applications, HR analytics, and organizational operations through one secure and intelligent digital platform.";
    }

    // fade in title
    setTimeout(() => {
        titleElement?.classList.add("show-text");
    }, 300);

    // fade in subtitle slightly after
    setTimeout(() => {
        subtitleElement?.classList.add("show-text");
    }, 700);
});

document.addEventListener("DOMContentLoaded", () => {

    const slider = document.getElementById("featuresSlider");
    const cards = document.querySelectorAll(".feature-link");
    const dots = document.querySelectorAll(".dot");

    const prevBtn = document.querySelector(".prev-btn");
    const nextBtn = document.querySelector(".next-btn");

    let currentIndex = 0;
    let autoSlide;

    const slideDelay = 3500;
    const gap = 32;

    // =========================
    // CARD WIDTH
    // =========================
    function getCardWidth() {
        return cards[0].offsetWidth + gap;
    }

    // =========================
    // UPDATE DOTS + ACTIVE CARD
    // =========================
    function updateUI() {

        cards.forEach(card => {
            card.querySelector(".feature-card")
                .classList.remove("active-card");
        });

        dots.forEach(dot => {
            dot.classList.remove("active-dot");
        });

        cards[currentIndex]
            .querySelector(".feature-card")
            .classList.add("active-card");

        dots[currentIndex]
            .classList.add("active-dot");
    }

    // =========================
    // MOVE SLIDER
    // =========================
    function moveSlider() {

        const moveAmount =
            currentIndex * getCardWidth();

        slider.style.transform =
            `translateX(-${moveAmount}px)`;

        updateUI();
    }

    // =========================
    // NEXT
    // =========================
    function nextSlide() {

        currentIndex++;

        if (currentIndex >= cards.length) {
            currentIndex = 0;
        }

        moveSlider();
    }

    // =========================
    // PREVIOUS
    // =========================
    function prevSlide() {

        currentIndex--;

        if (currentIndex < 0) {
            currentIndex = cards.length - 1;
        }

        moveSlider();
    }

    // =========================
    // AUTO SLIDE
    // =========================
    function startAutoSlide() {

        stopAutoSlide();

        autoSlide = setInterval(() => {
            nextSlide();
        }, slideDelay);
    }

    function stopAutoSlide() {
        clearInterval(autoSlide);
    }

    // =========================
    // PAUSE ON HOVER
    // =========================
    cards.forEach(card => {

        card.addEventListener("mouseenter", () => {
            stopAutoSlide();
        });

        card.addEventListener("mouseleave", () => {
            startAutoSlide();
        });

    });

    // =========================
    // BUTTONS
    // =========================
    nextBtn.addEventListener("click", () => {

        nextSlide();
        startAutoSlide();

    });

    prevBtn.addEventListener("click", () => {

        prevSlide();
        startAutoSlide();

    });

    // =========================
    // DOTS
    // =========================
    dots.forEach((dot, index) => {

        dot.addEventListener("click", () => {

            currentIndex = index;

            moveSlider();

            startAutoSlide();

        });

    });

    // =========================
    // RESPONSIVE
    // =========================
    window.addEventListener("resize", moveSlider);

    // =========================
    // INIT
    // =========================
    updateUI();
    startAutoSlide();

});

