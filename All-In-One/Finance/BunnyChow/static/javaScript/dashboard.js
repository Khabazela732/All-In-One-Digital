// Mobile sidebar toggle
document.querySelector('.menu-toggle').addEventListener('click', () => {
    document.querySelector('.sidebar').classList.toggle('open');
});

    const userWrapper = document.querySelector('.user-profile-wrapper');
    const dropdown = document.querySelector('.user-dropdown');

    userWrapper.addEventListener('click', function (e) {
        // If clicked inside the icon/name, toggle the dropdown
        if (!dropdown.contains(e.target)) {
            userWrapper.classList.toggle('open');
        }
        // Prevent closing when clicking inside dropdown
        if (dropdown.contains(e.target)) {
            return;
        }
    });

    // Close dropdown if user clicks outside (optional)
    document.addEventListener('click', function (e) {
        if (!userWrapper.contains(e.target)) {
            userWrapper.classList.remove('open');
        }
    });

// Sample Chart.js revenue chart
const ctx = document.getElementById('revenueChart').getContext('2d');
new Chart(ctx, {
    type: 'line',
    data: {
        labels: ['10AM', '11AM', '12PM', '1PM', '2PM', '3PM'],
        datasets: [{
            label: 'Revenue',
            data: [1200, 1900, 3000, 2500, 4200, 5800],
            borderColor: '#ff6b35',
            backgroundColor: 'rgba(255,107,53,0.1)',
            tension: 0.4,
            fill: true
        }]
    },
    options: { responsive: true, scales: { y: { beginAtZero: true } } }
});

// Live order updates simulation
setInterval(() => {
    const statuses = document.querySelectorAll('.status');
    statuses.forEach(status => {
        if (status.textContent === 'Preparing') {
            status.textContent = 'Out for Delivery';
            status.className = 'status out-for-delivery';
        } else if (status.textContent === 'Out for Delivery') {
            status.textContent = 'Completed';
            status.className = 'status completed';
        }
    });
}, 10000);

document.addEventListener("DOMContentLoaded", () => {
  const sidebar = document.getElementById("sidebar");
  const toggle  = document.getElementById("sidebar-toggle");
  const main    = document.getElementById("main-content");

  toggle.addEventListener("click", () => {
    const isCollapsed = sidebar.classList.toggle("collapsed");

    if (isCollapsed) {
      toggle.innerHTML = '<i class="fas fa-arrow-right"></i>';
    } else {
      toggle.innerHTML = '<i class="fas fa-bars"></i>';
    }
  });
});