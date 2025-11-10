document.addEventListener("DOMContentLoaded", function () {
  const modal = document.getElementById("registerModal");
  const btn = document.querySelector(".registerAccount");
  const span = document.querySelector(".close");
  const mainContent = document.querySelector("main");

  // Only attach modal behavior if modal actually exists
  if (btn && modal && mainContent) {
    btn.onclick = function () {
      modal.style.display = "flex";
      mainContent.classList.add("blurred");
    };
  }

  if (span && modal && mainContent) {
    span.onclick = function () {
      modal.style.display = "none";
      mainContent.classList.remove("blurred");
    };
  }

  window.onclick = function (event) {
    if (event.target === modal) {
      modal.style.display = "none";
      mainContent.classList.remove("blurred");
    }
  };

  // Redirects
  document.querySelectorAll(".redirect-books").forEach(item => {
    item.addEventListener("click", e => {
      e.preventDefault();
      e.stopPropagation();
      window.location.href = "/records/";
    });
  });

  document.querySelectorAll(".redirect-about").forEach(item => {
    item.addEventListener("click", e => {
      e.preventDefault();
      e.stopPropagation();
      window.location.href = "/about/";
    });
  });

  document.querySelectorAll(".redirect-records").forEach(item => {
    item.addEventListener("click", e => {
      e.preventDefault();
      e.stopPropagation();
      window.location.href = "/records/";
    });
  });
    document.querySelectorAll(".redirect-analytics").forEach(item => {
    item.addEventListener("click", e => {
      e.preventDefault();
      e.stopPropagation();
      window.location.href = "/analytics/";
    });
  });
});
