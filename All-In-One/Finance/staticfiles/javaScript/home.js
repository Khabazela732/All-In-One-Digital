// Stunning Loading Animation (FIRST - Critical)
// Circular Progress Loading (0-100%)
document.addEventListener('DOMContentLoaded', () => {
    const loader = document.getElementById('loader');
    const pageContent = document.getElementById('page-content');
    const letters = document.querySelectorAll('.letter');
    const progressFill = document.querySelector('.progress-fill');
    const progressText = document.querySelector('.progress-text');
    
    let progress = 0;
    const maxProgress = 100;
    const circumference = 534; // 2 * π * 85
    
    // Subtitle & typewriter (unchanged)
    letters.forEach((letter, index) => {
        letter.style.animationDelay = `${2.8 + (index * 0.15)}s`;
    });
    
    // Progress animation (3s duration)
    const progressInterval = setInterval(() => {
        progress += 2; // Speed control
        if (progress >= maxProgress) {
            progress = maxProgress;
            clearInterval(progressInterval);
            
            // Final delay before page reveal
            setTimeout(() => {
                loader.classList.add('hidden');
                pageContent.classList.add('page-visible');
                document.body.style.overflow = 'auto';
            }, 800); // 0.8s celebration hold
        }
        
        // Update ring & text
        const offset = circumference - (progress / 100) * circumference;
        progressFill.style.strokeDashoffset = offset;
        progressText.textContent = `${Math.floor(progress)}%`;
    }, 50); // ~60fps smooth
    
    document.body.style.overflow = 'hidden';
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

    const titleText =
    "Enterprise Human Resource & Recruitment Management Platform";

const subtitleText =
    "Streamline recruitment, employee onboarding, workforce management, vacancy publishing, candidate applications, HR analytics, and organizational operations through one secure and intelligent digital platform.";

    const titleElement =
        document.getElementById("typing-title");

    const subtitleElement =
        document.getElementById("typing-subtitle");

    let titleIndex = 0;
    let subtitleIndex = 0;

    let isDeleting = false;

    function typeEffect() {

        // TITLE TYPING
        if (!isDeleting) {

            titleElement.textContent =
                titleText.substring(0, titleIndex);

            subtitleElement.textContent =
                subtitleText.substring(0, subtitleIndex);

            titleIndex++;
            subtitleIndex++;

            // FINISHED TYPING
            if (
                titleIndex > titleText.length &&
                subtitleIndex > subtitleText.length
            ) {

                isDeleting = true;

                setTimeout(typeEffect, 2000);

                return;
            }

        } else {

            // DELETE EFFECT
            titleElement.textContent =
                titleText.substring(0, titleIndex);

            subtitleElement.textContent =
                subtitleText.substring(0, subtitleIndex);

            titleIndex--;
            subtitleIndex--;

            // FINISHED DELETING
            if (titleIndex < 0 && subtitleIndex < 0) {

                isDeleting = false;

                setTimeout(typeEffect, 800);

                return;
            }
        }

        const speed = isDeleting ? 40 : 80;

        setTimeout(typeEffect, speed);
    }

    typeEffect();

});

document.addEventListener("DOMContentLoaded", () => {
    const slider =
        document.getElementById("featuresSlider");
    const cards =
        document.querySelectorAll(".feature-card");
    const dots =
        document.querySelectorAll(".dot");
    const prevBtn =
        document.querySelector(".prev-btn");
    const nextBtn =
        document.querySelector(".next-btn");
    let currentIndex = 0;
    let autoSlide;
    const gap = 32;

    // CARD WIDTH
    function getCardWidth() {
        return cards[0].offsetWidth + gap;
    }

    // UPDATE SLIDER
    function updateSlider() {
        const cardWidth = getCardWidth();
        slider.style.transform =
            `translateX(-${currentIndex * cardWidth}px)`;

        // ACTIVE CARD
        cards.forEach(card => {
            card.classList.remove("active-card");
        });
        cards[currentIndex]
            .classList.add("active-card");

        // ACTIVE DOT
        dots.forEach(dot => {
            dot.classList.remove("active-dot");
        });
        dots[currentIndex]
            .classList.add("active-dot");
    }

    // NEXT SLIDE
    function nextSlide() {
        currentIndex++;
        if (currentIndex >= cards.length) {
            currentIndex = 0;
        }
        updateSlider();
    }

    // PREVIOUS SLIDE
    function prevSlide() {
        currentIndex--;
        if (currentIndex < 0) {
            currentIndex = cards.length - 1;
        }
        updateSlider();
    }

    // START AUTO SLIDE
    function startAutoSlide() {
        autoSlide = setInterval(() => {
            nextSlide();
        }, 4000);
    }

    // STOP AUTO SLIDE
    function stopAutoSlide() {
        clearInterval(autoSlide);
    }

    // BUTTON EVENTS
    nextBtn.addEventListener("click", () => {
        stopAutoSlide();
        nextSlide();
        startAutoSlide();
    });

    prevBtn.addEventListener("click", () => {
        stopAutoSlide();
        prevSlide();
        startAutoSlide();
    });

    // DOT EVENTS
    dots.forEach((dot, index) => {
        dot.addEventListener("click", () => {
            stopAutoSlide();

            currentIndex = index;
            updateSlider();
            startAutoSlide();
        });
    });
    // PAUSE ON HOVER
    slider.addEventListener("mouseenter", stopAutoSlide);
    slider.addEventListener("mouseleave", startAutoSlide);
    // RESPONSIVE UPDATE
    window.addEventListener("resize", updateSlider);

    // INITIALIZE
    updateSlider();
    startAutoSlide();
});

