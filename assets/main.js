function initMobileMenu() {
  const toggle = document.querySelector("[data-menu-toggle]");
  const menu = document.querySelector("[data-mobile-menu]");

  if (!toggle || !menu) {
    return;
  }

  toggle.addEventListener("click", () => {
    const isHidden = menu.hasAttribute("hidden");

    if (isHidden) {
      menu.removeAttribute("hidden");
      toggle.setAttribute("aria-expanded", "true");
    } else {
      menu.setAttribute("hidden", "hidden");
      toggle.setAttribute("aria-expanded", "false");
    }
  });
}

function initActiveNavigation() {
  const path = window.location.pathname.split("/").pop() || "index.html";
  const links = document.querySelectorAll("[data-nav]");

  links.forEach((link) => {
    const target = link.getAttribute("href");

    if (target === path) {
      link.classList.add("is-active");
    }
  });
}

function initRevealAnimations() {
  const revealItems = document.querySelectorAll(".reveal");

  if (!revealItems.length) {
    return;
  }

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-visible");
          observer.unobserve(entry.target);
        }
      });
    },
    {
      rootMargin: "0px 0px -8% 0px",
      threshold: 0.12,
    }
  );

  revealItems.forEach((item) => observer.observe(item));
}

function initScreenViewer() {
  const triggerList = Array.from(document.querySelectorAll("[data-screen-trigger]"));
  const viewer = document.querySelector("[data-screen-viewer]");
  const viewerImage = document.querySelector("[data-screen-viewer-image]");
  const viewerBody = document.querySelector("[data-screen-viewer-body]");
  let activeIndex = -1;

  if (!triggerList.length || !viewer || !viewerImage || !viewerBody) {
    return;
  }

  function openAt(index) {
    const normalizedIndex = ((index % triggerList.length) + triggerList.length) % triggerList.length;
    const trigger = triggerList[normalizedIndex];

    if (!trigger) {
      return;
    }

    const image = trigger.querySelector("img");
    const href = trigger.getAttribute("href");

    if (!image || !href) {
      return;
    }

    activeIndex = normalizedIndex;
    viewerImage.setAttribute("src", href);
    viewerImage.setAttribute("alt", image.getAttribute("alt") || "");

    if (!viewer.open) {
      viewer.showModal();
    }

    viewerBody.scrollTop = 0;
    viewerBody.scrollLeft = 0;
  }

  triggerList.forEach((trigger, index) => {
    trigger.addEventListener("click", (event) => {
      event.preventDefault();
      openAt(index);
    });
  });

  viewer.addEventListener("click", (event) => {
    if (event.target === viewer) {
      viewer.close();
    }
  });

  document.addEventListener("keydown", (event) => {
    if (!viewer.open || activeIndex < 0) {
      return;
    }

    if (event.key === "ArrowRight") {
      event.preventDefault();
      openAt(activeIndex + 1);
    }

    if (event.key === "ArrowLeft") {
      event.preventDefault();
      openAt(activeIndex - 1);
    }
  });
}

function initScreenFilters() {
  const filterButtons = Array.from(document.querySelectorAll("[data-screen-filter]"));
  const sections = Array.from(document.querySelectorAll("[data-screen-section]"));

  if (!filterButtons.length || !sections.length) {
    return;
  }

  function applyFilter(filterValue) {
    sections.forEach((section) => {
      const sectionCategory = section.getAttribute("data-screen-section");
      section.hidden = filterValue !== "all" && sectionCategory !== filterValue;
    });

    filterButtons.forEach((button) => {
      const isActive = button.getAttribute("data-screen-filter") === filterValue;
      button.classList.toggle("is-active", isActive);
      button.setAttribute("aria-pressed", String(isActive));
    });
  }

  filterButtons.forEach((button) => {
    button.addEventListener("click", () => {
      const filterValue = button.getAttribute("data-screen-filter") || "all";
      applyFilter(filterValue);
    });
  });

  applyFilter("all");
}

function initDemoDialog() {
  const triggers = Array.from(document.querySelectorAll("[data-demo-trigger]"));

  if (!triggers.length) {
    return;
  }

  const dialog = document.createElement("dialog");
  dialog.className = "demo-dialog";
  dialog.innerHTML = `
    <div class="demo-dialog-panel">
      <div class="demo-dialog-head">
        <div>
          <div class="demo-dialog-kicker">Demo status</div>
          <h2 class="demo-dialog-title">Demo <strong>Coming Soon</strong></h2>
        </div>
        <form method="dialog">
          <button class="btn btn-ghost" value="close" aria-label="Close demo status">Close</button>
        </form>
      </div>
      <p class="demo-dialog-copy">
        The interactive MachinaOS demo is still being finalized. We are polishing the flows so the public preview reflects the actual product quality.
      </p>
      <div class="demo-dialog-card">
        <strong>What to expect</strong>
        <div>Live orchestration screens, guided workflows, and a production-grade walkthrough will be available soon.</div>
      </div>
      <div class="demo-dialog-actions">
        <a class="btn btn-demo" href="screens.html">Browse Screens</a>
        <a class="btn btn-ghost" href="demo-guide.html">Open Demo Guide</a>
      </div>
    </div>
  `;

  document.body.appendChild(dialog);

  triggers.forEach((trigger) => {
    trigger.addEventListener("click", (event) => {
      event.preventDefault();
      dialog.showModal();
    });
  });

  dialog.addEventListener("click", (event) => {
    if (event.target === dialog) {
      dialog.close();
    }
  });
}

initMobileMenu();
initActiveNavigation();
initRevealAnimations();
initScreenViewer();
initScreenFilters();
initDemoDialog();
