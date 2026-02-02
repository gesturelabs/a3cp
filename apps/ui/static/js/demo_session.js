// apps/ui/static/js/demo_session.js

import { normalizeError, renderError } from "./error_model.js";
import {
    clearSessionId,
    getSessionId,
    requireSessionIdOrBlock,
    setSessionId,
} from "./session_context.js";

const ENDPOINT_START = "/session_manager/sessions.start";
const ENDPOINT_END = "/session_manager/sessions.end";

// Demo constants (keep stable for Stage 1)
const DEMO = {
    schema_version: "1.0.1",
    user_id: "demo_user",
    performer_id: "demo_user",
};

const elStatus = document.getElementById("session-status");
const elSessionId = document.getElementById("session-id");
const elErr = document.getElementById("error-box");

const btnStart = document.getElementById("btn-start");
const btnEnd = document.getElementById("btn-end");
const btnClearErr = document.getElementById("btn-clear-error");

let currentError = null;

function setUiFromState() {
    const sid = getSessionId();
    elSessionId.value = sid || "";

    if (currentError) elStatus.textContent = "error";
    else if (sid) elStatus.textContent = "active";
    else elStatus.textContent = "idle";

    // Enable/disable based strictly on state
    btnStart.disabled = Boolean(sid); // prevent double start in same tab
    btnEnd.disabled = !sid;
}

function setError(errObj) {
    currentError = errObj;
    renderError(elErr, currentError);
    setUiFromState();
}

function clearErrorOnly() {
    currentError = null;
    renderError(elErr, null);
    setUiFromState();
}

btnClearErr.addEventListener("click", () => clearErrorOnly());

btnStart.addEventListener("click", async () => {
    clearErrorOnly();
    btnStart.disabled = true;

    const payload = {
        schema_version: DEMO.schema_version,
        user_id: DEMO.user_id,
        performer_id: DEMO.performer_id,
        record_id: crypto.randomUUID(),
        timestamp: new Date().toISOString(),
        // Optional SessionStartInput fields omitted for Stage 1
    };

    try {
        const resp = await fetch(ENDPOINT_START, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        });

        const text = await resp.text();

        if (!resp.ok) {
            setError(normalizeError("sessions.start", "Request failed", resp.status, text));
            btnStart.disabled = false;
            return;
        }

        let data;
        try {
            data = JSON.parse(text);
        } catch {
            setError(normalizeError("sessions.start", "Invalid JSON response", 500, text));
            btnStart.disabled = false;
            return;
        }

        if (!data.session_id || typeof data.session_id !== "string") {
            setError(normalizeError("sessions.start", "Missing session_id in response", 500, text));
            btnStart.disabled = false;
            return;
        }

        setSessionId(data.session_id);
        setUiFromState();
    } catch (e) {
        setError(normalizeError("sessions.start", e));
        btnStart.disabled = false;
    }
});

btnEnd.addEventListener("click", async () => {
    clearErrorOnly();

    const gate = requireSessionIdOrBlock("sessions.end");
    if (!gate.ok) {
        setError(gate.error);
        return;
    }

    btnEnd.disabled = true;

    const payload = {
        schema_version: DEMO.schema_version,
        user_id: DEMO.user_id,
        performer_id: DEMO.performer_id,
        record_id: crypto.randomUUID(),
        timestamp: new Date().toISOString(),
        session_id: gate.session_id,
    };

    try {
        const resp = await fetch(ENDPOINT_END, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        });

        const text = await resp.text();

        if (!resp.ok) {
            setError(normalizeError("sessions.end", "Request failed", resp.status, text));
            btnEnd.disabled = false;
            return;
        }

        // success path
        clearSessionId();
        setUiFromState();
    } catch (e) {
        setError(normalizeError("sessions.end", e));
        btnEnd.disabled = false;
    }
});

// Initial render (rehydrate from sessionStorage)
renderError(elErr, null);
setUiFromState();
