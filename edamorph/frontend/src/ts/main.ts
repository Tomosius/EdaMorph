// main.ts

// ✅ Ensure Alpine loads before anything else
import Alpine from 'alpinejs';

// Arrow Table (Apache Arrow)
import { fetchArrowTable, renderArrowTable } from './tableRenderer';

import 'htmx.org';
import '../css/input.css';
import '../css/custom.css';
import './custom_typescript';

declare global {
  interface Window {
    Alpine: typeof Alpine;
  }
}

window.Alpine = Alpine;

// ✅ DOM must be ready before Alpine initializes and table preview renders
document.addEventListener('DOMContentLoaded', () => {
  console.log('✅ App initialized with Tailwind + HTMX + Alpine');
  Alpine.start();

  // 👇 Table preview: only runs if preview div is present!
  const previewDiv = document.getElementById("arrow-table-preview");
  if (previewDiv) {
    fetchArrowTable("/arrow_preview")
      .then(table => {
        renderArrowTable(table, {
          domId: "arrow-table-preview",
          rowPageSize: 10,
        });
      })
      .catch(err => {
        previewDiv.innerHTML =
          "<div class='text-red-600'>Failed to load preview.</div>";
        console.error("Arrow table preview failed:", err);
      });
  }
});