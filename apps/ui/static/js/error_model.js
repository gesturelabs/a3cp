// ui/static/js/error_model.js

export function normalizeError(action, err, httpStatus = null, raw = null) {
    if (httpStatus !== null) {
        return {
            kind: "http",
            action,
            httpStatus,
            message: err || "Request failed",
            raw: raw || null,
        };
    }
    return {
        kind: "network",
        action,
        httpStatus: null,
        message: err?.message ? err.message : String(err),
        raw: null,
    };
}

export function renderError(targetEl, error) {
    if (!targetEl) return;
    if (!error) {
        targetEl.innerHTML = "";
        return;
    }
    const status = error.httpStatus !== null ? `HTTP ${error.httpStatus}` : "Network error";
    const raw = error.raw ? `<pre class="mt-2">${escapeHtml(error.raw)}</pre>` : "";
    targetEl.innerHTML = `
    <div>
      <div><strong>${escapeHtml(error.action)}</strong></div>
      <div>${escapeHtml(status)} — ${escapeHtml(error.message)}</div>
      ${raw}
    </div>
  `;
}

function escapeHtml(s) {
    return String(s)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}
