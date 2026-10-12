// Fetch the latest table without reloading the page or replacing the search box.
const table = document.getElementById("live-table");
const status = document.getElementById("update-status");
const query = new URLSearchParams(window.location.search).get("q") || "";

async function refreshTable() {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 10000);
  try {
    const response = await fetch(
      `${table.dataset.endpoint}?${new URLSearchParams({ q: query })}`,
      { cache: "no-store", signal: controller.signal }
    );
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const html = await response.text();
    if (table.innerHTML !== html) table.innerHTML = html;
    status.textContent = "Live · Updated " + new Date().toLocaleTimeString();
  } catch (error) {
    status.textContent = "Updates paused: connection unavailable. Retrying automatically…";
  } finally {
    clearTimeout(timeout);
    // Schedule after completion to avoid overlapping requests.
    setTimeout(refreshTable, 2000);
  }
}

refreshTable();
