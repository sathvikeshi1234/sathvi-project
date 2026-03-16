document.addEventListener('DOMContentLoaded', () => {
  
  const includes = document.querySelectorAll('[data-include]');

  includes.forEach(async (el) => {
    const includePath = el.getAttribute('data-include'); 
    if (!includePath) return;

    // Build the file path for STATIC
    const path = `/static/${includePath}.html`;

    try {
      const res = await fetch(path);

      if (!res.ok) {
        console.error("Include file not found:", path);
        return;
      }

      const html = await res.text();
      el.innerHTML = html;

      // auto-activate current sidebar link
      if (includePath.includes("sidebar")) {
        const currentPage = document.body.getAttribute("data-page");
        if (currentPage) {
          const link = el.querySelector(`.nav-item[data-page="${currentPage}"]`);
          if (link) link.classList.add("active");
        }
      }

    } catch (err) {
      console.error("Failed to load include:", path, err);
    }
  });


});
