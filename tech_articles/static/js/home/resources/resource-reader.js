/**
 * ResourceReader — secure in-browser file viewer.
 *
 * Architecture: registry pattern.
 * Adding a new file type requires only implementing a viewer class that
 * exposes an async `render(container, url)` method, then registering it
 * in VIEWER_REGISTRY below.
 *
 * Internationalisation: all user-visible strings come from Django's
 * JavaScript catalogue (gettext / ngettext / interpolate are globally
 * available after {% url 'javascript-catalog' %} is loaded).
 */

"use strict";

/* =========================================================================
   Viewer implementations
   ========================================================================= */

/**
 * PDFViewer — renders each page of a PDF file onto a <canvas> element using
 * PDF.js. No native browser PDF controls are shown, preventing the built-in
 * download button.
 */
class PDFViewer {
  async render(container, url) {
    if (!window.pdfjsLib) {
      throw new Error(gettext("PDF.js library is not loaded."));
    }

    pdfjsLib.GlobalWorkerOptions.workerSrc =
      "https://cdnjs.cloudflare.com/ajax/libs/pdf.js/4.0.379/pdf.worker.min.mjs";

    const loadingTask = pdfjsLib.getDocument({ url, disableRange: false });
    const pdf = await loadingTask.promise;

    for (let pageNum = 1; pageNum <= pdf.numPages; pageNum++) {
      const page = await pdf.getPage(pageNum);
      const scale = this._computeScale();
      const viewport = page.getViewport({ scale });

      const wrapper = document.createElement("div");
      wrapper.className =
        "mx-auto mb-6 rounded-lg overflow-hidden shadow-2xl";
      wrapper.style.maxWidth = `${viewport.width}px`;

      const canvas = document.createElement("canvas");
      canvas.width = viewport.width;
      canvas.height = viewport.height;
      canvas.style.cssText =
        "display:block;width:100%;user-select:none;-webkit-user-drag:none;";

      const ctx = canvas.getContext("2d");
      await page.render({ canvasContext: ctx, viewport }).promise;

      wrapper.appendChild(canvas);
      container.appendChild(wrapper);
    }
  }

  /** Choose a rendering scale that fits the available viewport width. */
  _computeScale() {
    const viewportWidth = window.innerWidth;
    if (viewportWidth >= 1024) return 1.6;
    if (viewportWidth >= 768) return 1.3;
    return 1.0;
  }
}

/**
 * ImageViewer — renders a single image with security attributes applied.
 */
class ImageViewer {
  async render(container, url) {
    const img = document.createElement("img");
    img.alt = "";
    img.className =
      "block mx-auto max-w-full max-h-[80vh] rounded-lg shadow-2xl object-contain";
    img.style.cssText =
      "user-select:none;-webkit-user-drag:none;pointer-events:none;";
    img.setAttribute("draggable", "false");
    img.src = url;

    await new Promise((resolve, reject) => {
      img.onload = resolve;
      img.onerror = () =>
        reject(new Error(gettext("Failed to load image.")));
    });

    container.appendChild(img);
  }
}

/**
 * TextViewer — fetches a plain-text file and displays its content in a
 * styled <pre> block.
 */
class TextViewer {
  async render(container, url) {
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(gettext("Failed to load text file."));
    }
    const text = await response.text();

    const pre = document.createElement("pre");
    pre.className =
      "text-text-secondary text-sm leading-relaxed whitespace-pre-wrap break-words p-6 bg-surface-dark rounded-lg overflow-auto max-h-[70vh]";
    pre.style.cssText = "user-select:none;-webkit-user-select:none;";
    pre.textContent = text;

    container.appendChild(pre);
  }
}

/**
 * UnsupportedViewer — shown when no viewer is registered for the file type.
 */
class UnsupportedViewer {
  async render(container) {
    const div = document.createElement("div");
    div.className =
      "flex flex-col items-center justify-center gap-4 py-16 text-text-secondary";
    div.innerHTML = `
      <svg class="w-16 h-16 opacity-40" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
          d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
      </svg>
      <p class="text-lg font-medium">${gettext("Preview not available")}</p>
      <p class="text-sm text-center max-w-xs">${gettext("This file type cannot be previewed in the browser.")}</p>
    `;
    container.appendChild(div);
  }
}

/* =========================================================================
   Viewer registry — add new file types here, no other changes needed.
   ========================================================================= */

const VIEWER_REGISTRY = {
  pdf: PDFViewer,
  image: ImageViewer,
  text: TextViewer,
};

/* =========================================================================
   Main ResourceReader class
   ========================================================================= */

class ResourceReader {
  /**
   * @param {Object} config
   * @param {string} config.resourceId      - UUID of the resource
   * @param {string} config.readUrlEndpoint - API endpoint returning { url, file_type }
   * @param {string} config.fileType        - hint from server (pdf | image | text | unsupported)
   * @param {string} config.homeUrl         - fallback URL for the back button
   */
  constructor(config) {
    this.resourceId = config.resourceId;
    this.readUrlEndpoint = config.readUrlEndpoint;
    this.fileType = config.fileType;
    this.homeUrl = config.homeUrl;

    this._container = document.getElementById("reader-viewer");
    this._loadingEl = document.getElementById("reader-loading");
    this._errorEl = document.getElementById("reader-error");
    this._errorMsgEl = document.getElementById("reader-error-msg");
    this._backBtn = document.getElementById("reader-back-btn");
  }

  /** Initialise event handlers and start loading the resource. */
  init() {
    this._bindSecurityHandlers();
    this._bindBackButton();
    this._loadContent();
  }

  /* ------------------------------------------------------------------
     Security — best-effort browser-side protections.
     Note: OS-level screen recording cannot be prevented from JS.
  ------------------------------------------------------------------ */

  _bindSecurityHandlers() {
    // Disable right-click context menu
    document.addEventListener("contextmenu", (e) => e.preventDefault());

    // Block common save / print keyboard shortcuts
    document.addEventListener("keydown", (e) => {
      const blocked =
        e.key === "PrintScreen" ||
        (e.ctrlKey && ["p", "s", "u"].includes(e.key.toLowerCase())) ||
        (e.metaKey && ["p", "s"].includes(e.key.toLowerCase()));
      if (blocked) {
        e.preventDefault();
        e.stopPropagation();
      }
    });

    // Prevent browser print dialog
    window.addEventListener("beforeprint", (e) => e.preventDefault());

    // Prevent drag-and-drop of the page content
    document.addEventListener("dragstart", (e) => e.preventDefault());
  }

  /* ------------------------------------------------------------------
     Back button — history.back() with home-page fallback.
  ------------------------------------------------------------------ */

  _bindBackButton() {
    if (!this._backBtn) return;
    this._backBtn.addEventListener("click", () => {
      if (window.history.length > 1) {
        window.history.back();
      } else {
        window.location.href = this.homeUrl;
      }
    });
  }

  /* ------------------------------------------------------------------
     Content loading
  ------------------------------------------------------------------ */

  async _loadContent() {
    this._showLoading();

    try {
      const { url, file_type: fileType } = await this._fetchReadUrl();

      // Server-side type wins; fall back to the hint passed at boot.
      const resolvedType = fileType || this.fileType;
      const ViewerClass = VIEWER_REGISTRY[resolvedType] || UnsupportedViewer;
      const viewer = new ViewerClass();

      await viewer.render(this._container, url);
      this._hideLoading();
    } catch (err) {
      this._showError(
        err.message || gettext("An error occurred while loading the resource.")
      );
    }
  }

  async _fetchReadUrl() {
    const response = await fetch(this.readUrlEndpoint, {
      credentials: "same-origin",
      headers: { "X-Requested-With": "XMLHttpRequest" },
    });

    if (response.status === 403) {
      throw new Error(gettext("You do not have permission to access this resource."));
    }
    if (!response.ok) {
      throw new Error(gettext("Failed to load the resource. Please try again."));
    }

    return response.json();
  }

  /* ------------------------------------------------------------------
     UI helpers
  ------------------------------------------------------------------ */

  _showLoading() {
    this._loadingEl?.classList.remove("hidden");
    this._errorEl?.classList.add("hidden");
  }

  _hideLoading() {
    this._loadingEl?.classList.add("hidden");
  }

  _showError(message) {
    this._hideLoading();
    if (this._errorMsgEl) this._errorMsgEl.textContent = message;
    this._errorEl?.classList.remove("hidden");
  }
}
