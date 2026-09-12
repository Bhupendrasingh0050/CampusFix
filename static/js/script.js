/* =====================================================================
   CampusFix — Shared Script (Vanilla JS)

   This file only handles UI interactions: mobile nav, sidebar toggle,
   password show/hide, priority/pill selectors, image preview, basic
   client-side form validation, client-side table filtering, modals,
   toasts, and flash-message dismissal. All real data (complaints,
   users, notifications, stats) is rendered server-side by Flask/Jinja2.
   Every form submits normally to Flask — nothing here fakes a backend.
   ===================================================================== */

document.addEventListener("DOMContentLoaded", () => {
  initMobileNav();
  initSidebarToggle();
  initPasswordToggles();
  initPrioritySelector();
  initPillSelectors();
  initFileUpload();
  initFormValidation();
  initFilters();
  initModalTriggers();
  initAnimatedBars();
  initFlashDismiss();
});

/* ---------------------------------------------------------------------
   1. MOBILE NAV (landing page navbar)
   --------------------------------------------------------------------- */
function initMobileNav() {
  const toggle = document.querySelector(".nav-toggle");
  const links = document.querySelector(".nav-links");
  if (!toggle || !links) return;
  toggle.addEventListener("click", () => {
    links.classList.toggle("nav-links-open");
    links.style.display = links.classList.contains("nav-links-open") ? "flex" : "";
  });
}

/* ---------------------------------------------------------------------
   2. SIDEBAR TOGGLE (dashboard pages -> hamburger menu on mobile)
   --------------------------------------------------------------------- */
function initSidebarToggle() {
  const hamburger = document.querySelector(".hamburger");
  const sidebar = document.querySelector(".sidebar");
  const overlay = document.querySelector(".sidebar-overlay");
  if (!hamburger || !sidebar) return;

  const open = () => { sidebar.classList.add("open"); overlay && overlay.classList.add("show"); };
  const close = () => { sidebar.classList.remove("open"); overlay && overlay.classList.remove("show"); };

  hamburger.addEventListener("click", () => {
    sidebar.classList.contains("open") ? close() : open();
  });
  overlay && overlay.addEventListener("click", close);
}

/* ---------------------------------------------------------------------
   3. PASSWORD SHOW/HIDE
   --------------------------------------------------------------------- */
function initPasswordToggles() {
  document.querySelectorAll(".password-toggle").forEach((btn) => {
    btn.addEventListener("click", () => {
      const input = btn.parentElement.querySelector("input");
      if (!input) return;
      const isHidden = input.type === "password";
      input.type = isHidden ? "text" : "password";
      btn.textContent = isHidden ? "Hide" : "Show";
    });
  });
}

/* ---------------------------------------------------------------------
   4. VISUAL PRIORITY SELECTOR (report-problem.html)
   --------------------------------------------------------------------- */
function initPrioritySelector() {
  const options = document.querySelectorAll(".priority-option");
  if (!options.length) return;
  options.forEach((opt) => {
    opt.addEventListener("click", () => {
      options.forEach((o) => o.classList.remove("selected"));
      opt.classList.add("selected");
      const input = opt.querySelector("input");
      if (input) input.checked = true;
    });
  });
}

/* ---------------------------------------------------------------------
   5. PILL SELECTORS (admin status / priority pickers)
   Each group carries data-pill-group="status" / "priority" and syncs
   its choice into the matching hidden input (#status-input etc.) so
   the surrounding <form> submits real data to Flask.
   --------------------------------------------------------------------- */
function initPillSelectors() {
  document.querySelectorAll(".pill-select").forEach((group) => {
    const buttons = group.querySelectorAll("button");
    const groupName = group.dataset.pillGroup;
    const hiddenInput = groupName ? document.querySelector(`#${groupName}-input`) : null;

    buttons.forEach((btn) => {
      btn.addEventListener("click", () => {
        buttons.forEach((b) => b.classList.remove("active"));
        btn.classList.add("active");
        if (hiddenInput && btn.dataset.value) hiddenInput.value = btn.dataset.value;
      });
    });
  });
}

/* ---------------------------------------------------------------------
   6. FILE UPLOAD PREVIEW (report-problem.html)
   --------------------------------------------------------------------- */
function initFileUpload() {
  const box = document.querySelector(".upload-box");
  const input = document.querySelector("#problem-image");
  const preview = document.querySelector(".file-preview");
  if (!box || !input) return;

  box.addEventListener("click", () => input.click());
  input.addEventListener("change", () => {
    if (input.files.length && preview) {
      const file = input.files[0];
      const sizeMB = (file.size / (1024 * 1024)).toFixed(2);
      preview.textContent = `📎 ${file.name} (${sizeMB} MB) attached`;
      preview.style.display = "flex";
    }
  });
}

/* ---------------------------------------------------------------------
   7. FORM VALIDATION (login / register / report problem / profile)
   Client-side only — the server always re-validates and is the
   final authority. This just gives faster feedback in the browser.
   --------------------------------------------------------------------- */
function initFormValidation() {
  document.querySelectorAll("form[data-validate]").forEach((form) => {
    form.addEventListener("submit", (e) => {
      let valid = true;
      form.querySelectorAll("[required]").forEach((field) => {
        const errorEl = field.parentElement.querySelector(".field-error");
        const empty = !field.value || (field.type === "checkbox" && !field.checked);
        if (empty) {
          valid = false;
          field.classList.add("input-error");
          if (errorEl) errorEl.classList.add("show");
        } else {
          field.classList.remove("input-error");
          if (errorEl) errorEl.classList.remove("show");
        }
      });

      // Password match check (register page)
      const pass = form.querySelector("#password");
      const confirm = form.querySelector("#confirm-password");
      if (pass && confirm && pass.value !== confirm.value) {
        valid = false;
        confirm.classList.add("input-error");
        const errorEl = confirm.parentElement.querySelector(".field-error");
        if (errorEl) { errorEl.textContent = "Passwords do not match."; errorEl.classList.add("show"); }
      }

      if (!valid) {
        e.preventDefault();
        showToast("Please fill all required fields correctly.", "error");
      }
    });
  });
}

/* ---------------------------------------------------------------------
   8. SEARCH / CATEGORY / STATUS / PRIORITY / DEPARTMENT FILTERING
   Filters the server-rendered rows already present in the DOM
   (my-complaints.html / admin-complaints.html). No data is invented
   here — it just shows/hides rows Flask already rendered.
   --------------------------------------------------------------------- */
function initFilters() {
  const searchInput = document.querySelector("[data-filter-search]");
  const categorySelect = document.querySelector("[data-filter-category]");
  const statusSelect = document.querySelector("[data-filter-status]");
  const prioritySelect = document.querySelector("[data-filter-priority]");
  const departmentSelect = document.querySelector("[data-filter-department]");
  const container = document.querySelector("[data-filter-target]");
  if (!container) return;

  function applyFilters() {
    const search = (searchInput?.value || "").toLowerCase();
    const category = categorySelect?.value || "all";
    const status = statusSelect?.value || "all";
    const priority = prioritySelect?.value || "all";
    const department = departmentSelect?.value || "all";

    container.querySelectorAll("[data-row]").forEach((row) => {
      const matchesSearch = !search
        || row.dataset.title.toLowerCase().includes(search)
        || row.dataset.id.toLowerCase().includes(search);
      const matchesCategory = category === "all" || row.dataset.category === category;
      const matchesStatus = status === "all" || row.dataset.status === status;
      const matchesPriority = priority === "all" || row.dataset.priority === priority;
      const matchesDepartment = department === "all" || row.dataset.department === department;
      row.style.display = (matchesSearch && matchesCategory && matchesStatus && matchesPriority && matchesDepartment) ? "" : "none";
    });
  }

  [searchInput, categorySelect, statusSelect, prioritySelect, departmentSelect].forEach((el) => {
    el && el.addEventListener("input", applyFilters);
    el && el.addEventListener("change", applyFilters);
  });
}

/* ---------------------------------------------------------------------
   9. MODAL DIALOGS (confirmations, etc.)
   --------------------------------------------------------------------- */
function initModalTriggers() {
  document.querySelectorAll("[data-modal-open]").forEach((btn) => {
    btn.addEventListener("click", () => {
      const modal = document.querySelector(btn.dataset.modalOpen);
      modal && modal.classList.add("show");
    });
  });
  document.querySelectorAll("[data-modal-close]").forEach((btn) => {
    btn.addEventListener("click", () => {
      const modal = btn.closest(".modal-overlay");
      modal && modal.classList.remove("show");
    });
  });
}

/* ---------------------------------------------------------------------
   10. TOAST NOTIFICATIONS (client-side UI feedback only)
   --------------------------------------------------------------------- */
function showToast(message, type = "info") {
  let container = document.querySelector(".toast-container");
  if (!container) {
    container = document.createElement("div");
    container.className = "toast-container";
    document.body.appendChild(container);
  }
  const toast = document.createElement("div");
  toast.className = `toast toast-${type}`;
  toast.textContent = message;
  container.appendChild(toast);
  requestAnimationFrame(() => toast.classList.add("show"));
  setTimeout(() => {
    toast.classList.remove("show");
    setTimeout(() => toast.remove(), 250);
  }, 3200);
}

/* ---------------------------------------------------------------------
   11. ANIMATE CSS BAR CHARTS ON LOAD (admin-dashboard.html)
   --------------------------------------------------------------------- */
function initAnimatedBars() {
  document.querySelectorAll(".bar-fill").forEach((bar) => {
    const target = bar.style.width;
    bar.style.width = "0%";
    requestAnimationFrame(() => {
      setTimeout(() => { bar.style.width = target; }, 100);
    });
  });
}

/* ---------------------------------------------------------------------
   12. DISMISS FLASK FLASH MESSAGES
   --------------------------------------------------------------------- */
function initFlashDismiss() {
  document.querySelectorAll(".flash-close").forEach((btn) => {
    btn.addEventListener("click", () => {
      const flash = btn.closest(".flash");
      flash && flash.remove();
    });
  });

  // Auto-dismiss success/info flashes after a few seconds
  document.querySelectorAll(".flash-success, .flash-info").forEach((flash) => {
    setTimeout(() => { flash.style.opacity = "0"; setTimeout(() => flash.remove(), 300); }, 5000);
  });
}
