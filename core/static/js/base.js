document.addEventListener("DOMContentLoaded", function () {
  // Initialize Bootstrap components
  var tooltipTriggerList = [].slice.call(
    document.querySelectorAll('[data-bs-toggle="tooltip"]')
  );
  tooltipTriggerList.forEach(function (tooltipTriggerEl) {
    new bootstrap.Tooltip(tooltipTriggerEl);
  });

  // Smooth scroll for anchor links
  document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
    anchor.addEventListener("click", function (e) {
      e.preventDefault();
      const target = document.querySelector(this.getAttribute("href"));
      if (target) {
        target.scrollIntoView({ behavior: "smooth", block: "start" });
      }
    });
  });

  // Add active class to current nav link
  const currentPath = window.location.pathname;
  document.querySelectorAll(".navbar-nav .nav-link").forEach((link) => {
    const href = link.getAttribute("href");
    if (
      href === currentPath ||
      (href.includes("products") && currentPath.includes("products"))
    ) {
      link.classList.add("active");
    }
  });

  // Close mobile menu when clicking a link or outside
  const checkbox = document.getElementById("check");
  const mainNav = document.querySelector(".main-nav");
  const navbarCollapse = document.querySelector(".navbar-collapse");

  document.querySelectorAll(".main-nav .nav-link").forEach((link) => {
    link.addEventListener("click", () => {
      checkbox.checked = false;
    });
  });

  document.addEventListener("click", (e) => {
    if (
      !mainNav.contains(e.target) &&
      !document.querySelector(".open-menu").contains(e.target)
    ) {
      checkbox.checked = false;
    }
  });
});
