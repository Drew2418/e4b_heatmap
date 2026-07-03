document.addEventListener("DOMContentLoaded", () => {
  const overlays = document.querySelectorAll(".panel-overlay");
  const modal = document.getElementById("wo-modal");
  const modalTitle = document.getElementById("wo-modal-title");
  const modalBody = document.getElementById("wo-modal-body");
  const closeBtn = document.getElementById("wo-modal-close");
  const areaSlug = document.body.dataset.area;

  function openModal() { modal.classList.add("open"); }
  function closeModal() { modal.classList.remove("open"); }

  overlays.forEach((el) => {
    el.addEventListener("click", () => {
      const panelId = el.dataset.panelId;
      const panelLabel = el.dataset.panelLabel;

      modalTitle.textContent = `${panelLabel} — Work Orders`;
      modalBody.innerHTML = "<p>Loading…</p>";
      openModal();

      fetch(`/api/panel/${areaSlug}/${encodeURIComponent(panelId)}`)
        .then((res) => res.json())
        .then((orders) => {
          if (orders.length === 0) {
            modalBody.innerHTML = "<p>No work orders logged for this panel.</p>";
            return;
          }
          const rows = orders
            .map(
              (o) => `
              <tr>
                <td>${o.wo_number}</td>
                <td>${o.description}</td>
                <td>${o.pos}</td>
                <td><span class="status-badge status-${o.status}">${o.status}</span></td>
              </tr>`
            )
            .join("");
          modalBody.innerHTML = `
            <table class="wo-table">
              <thead>
                <tr><th>WO #</th><th>Description</th><th>POS</th><th>Status</th></tr>
              </thead>
              <tbody>${rows}</tbody>
            </table>`;
        })
        .catch(() => {
          modalBody.innerHTML = "<p>Could not load work orders. Check that the server is running.</p>";
        });
    });
  });

  closeBtn.addEventListener("click", closeModal);
  modal.addEventListener("click", (e) => {
    if (e.target === modal) closeModal();
  });
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") closeModal();
  });
});
