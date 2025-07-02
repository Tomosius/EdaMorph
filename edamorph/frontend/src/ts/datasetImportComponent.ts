// datasetImportComponent.ts

/**
 * Alpine.js component for handling file import for EdaMorph
 * - Handles file upload to FastAPI backend
 * - Redirects to "/" after successful import
 */
export function datasetImportComponent() {
  return {
    dataset: "",
    loading: false,

    handleFile(event: Event) {
      const input = event.target as HTMLInputElement;
      const file = input.files?.[0];
      if (!file) return;
      this.loading = true;

      // Prepare file for upload
      const formData = new FormData();
      formData.append("file", file);

      // POST file to FastAPI /import endpoint
      fetch('/import', {
        method: 'POST',
        body: formData,
      })
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          this.dataset = data.name;
          window.location.href = "/";
        } else {
          alert(data.detail || "Import failed!");
        }
      })
      .catch(() => alert("Import failed!"))
      .finally(() => {
        this.loading = false;
        input.value = ""; // Allow re-import of same file
      });
    }
  }
}