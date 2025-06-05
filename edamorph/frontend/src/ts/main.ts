// ✅ Ensure Alpine loads before anything else
import Alpine from 'alpinejs';
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

// ✅ DOM must be ready before Alpine initializes
document.addEventListener('DOMContentLoaded', () => {
  console.log('✅ App initialized with Tailwind + HTMX + Alpine');
  Alpine.start(); // ✅ Start inside DOMContentLoaded
});