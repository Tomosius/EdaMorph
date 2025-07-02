// main.ts

import Alpine from 'alpinejs';
import { fetchArrowTable, renderArrowTable } from './tableRenderer';
import { datasetImportComponent } from './datasetImportComponent';
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

// Register Alpine component
Alpine.data("datasetImportComponent", datasetImportComponent);

document.addEventListener('DOMContentLoaded', () => {
  console.log('✅ App initialized with Tailwind + HTMX + Alpine');
  Alpine.start();

  // Render table preview if the div is present
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