// apps/ui/static/js/a3cp.js
// A3CP MVP Demo UI (/a3cp)
// ES module. No globals exported. No inline JS.
// Runtime state owned by A3CPDemoController. DOM handled by A3CPDemoUI.

// Module-scoped init guard (no globals leaked)
let __a3cpDemoInitialized = false;

class A3CPDemoUI {
    constructor(root = document) {
        // Session
        this.userId = root.getElementById("user_id");
        this.performerId = root.getElementById("performer_id");
        this.sessionId = root.getElementById("session_id");
        this.btnStartSession = root.getElementById("btn_start_session");
        this.btnEndSession = root.getElementById("btn_end_session");
        this.btnResetDemo = root.getElementById("btn_reset_demo");

        // Preview
        this.previewVideo = root.getElementById("preview_video");
        this.btnStartPreview = root.getElementById("btn_start_preview");
        this.btnStopPreview = root.getElementById("btn_stop_preview");

        // Capture
        this.recordId = root.getElementById("record_id");
        this.captureId = root.getElementById("capture_id"); // hidden in template
        this.framesSent = root.getElementById("frames_sent");
        this.btnStartCapture = root.getElementById("btn_start_capture");
        this.btnStopCapture = root.getElementById("btn_stop_capture");

        // Debug
        this.debugOut = root.getElementById("debug_out");

        // Error panel
        this.errorPanel = root.getElementById("a3cp-error-panel");
        this.errMsg = root.getElementById("err_msg");
        this.errHttpStatus = root.getElementById("err_http_status");
        this.errCode = root.getElementById("err_code");
        this.btnClearError = root.getElementById("btn_clear_error");
    }

    bind(controller) {
        // Session
        this.btnStartSession?.addEventListener("click", () => controller.onStartSession());
        this.btnEndSession?.addEventListener("click", () => controller.onEndSession());
        this.btnResetDemo?.addEventListener("click", () => controller.onResetDemo());

        // Preview
        this.btnStartPreview?.addEventListener("click", () => controller.onStartPreview());
        this.btnStopPreview?.addEventListener("click", () => controller.onStopPreview());

        // Capture
        this.btnStartCapture?.addEventListener("click", () => controller.onStartCapture());
        this.btnStopCapture?.addEventListener("click", () => controller.onStopCapture());

        // Error
        this.btnClearError?.addEventListener("click", () => controller.onClearError());
    }

    // UI-only: disable buttons/inputs during async operations.
    setBusy(isBusy) {
        const disabled = Boolean(isBusy);

        if (disabled) {
            [
                this.btnStartSession,
                this.btnEndSession,
                this.btnResetDemo,
                this.btnStartPreview,
                this.btnStopPreview,
                this.btnStartCapture,
                this.btnStopCapture,
                this.btnClearError,
            ].forEach((btn) => {
                if (btn) btn.disabled = true;
            });

            [this.userId, this.performerId].forEach((inp) => {
                if (inp) inp.disabled = true;
            });
        } else {
            [this.userId, this.performerId].forEach((inp) => {
                if (inp) inp.disabled = false;
            });
        }
    }


    // UI-only: reflect session status (lock IDs while active).
    // state: { status: "idle"|"active", userId, performerId, sessionId }
    setSessionState(state) {
        if (this.userId && typeof state.userId === "string") this.userId.value = state.userId;
        if (this.performerId && typeof state.performerId === "string")
            this.performerId.value = state.performerId;
        if (this.sessionId && typeof state.sessionId === "string") this.sessionId.value = state.sessionId;

        const isActive = state.status === "active";
        if (this.userId) this.userId.readOnly = isActive;
        if (this.performerId) this.performerId.readOnly = isActive;

        // Buttons: conservative defaults (controller will refine later)
        if (this.btnStartSession) this.btnStartSession.disabled = isActive;
        if (this.btnEndSession) this.btnEndSession.disabled = !isActive;
    }

    // UI-only: preview state reflection.
    // state: { status: "stopped"|"running" }
    setPreviewState(state) {
        const running = state.status === "running";
        if (this.btnStartPreview) this.btnStartPreview.disabled = running;
        if (this.btnStopPreview) this.btnStopPreview.disabled = !running;
    }

    // UI-only: capture state reflection.
    // state: { status: "stopped"|"running" }
    setCaptureState(state) {
        const running = state.status === "running";
        if (this.btnStartCapture) this.btnStartCapture.disabled = running;
        if (this.btnStopCapture) this.btnStopCapture.disabled = !running;

        // Reset must be disabled while capturing (locked invariant)
        if (this.btnResetDemo) this.btnResetDemo.disabled = running;
    }

    setFramesSent(n) {
        if (!this.framesSent) return;
        this.framesSent.value = String(Number.isFinite(n) ? n : 0);
    }

    setRecordId(recordId) {
        if (this.recordId) this.recordId.value = recordId || "";
    }

    setCaptureId(captureId) {
        if (this.captureId) this.captureId.value = captureId || "";
    }

    // opts: { message: string, httpStatus?: number|string, errorCode?: string }
    showError(opts) {
        if (!this.errorPanel) return;

        const message = opts?.message ?? "";
        const httpStatus = opts?.httpStatus ?? "";
        const errorCode = opts?.errorCode ?? "";

        if (this.errMsg) this.errMsg.textContent = String(message);
        if (this.errHttpStatus) this.errHttpStatus.textContent = httpStatus === "" ? "" : String(httpStatus);
        if (this.errCode) this.errCode.textContent = errorCode === "" ? "" : String(errorCode);

        this.errorPanel.style.display = "";
        this.errorPanel.open = true;
    }

    clearError() {
        if (this.errMsg) this.errMsg.textContent = "";
        if (this.errHttpStatus) this.errHttpStatus.textContent = "";
        if (this.errCode) this.errCode.textContent = "";
        if (this.errorPanel) {
            this.errorPanel.open = false;
            this.errorPanel.style.display = "none";
        }
    }

    debug(line) {
        if (!this.debugOut) return;
        const s = typeof line === "string" ? line : String(line);
        this.debugOut.textContent = (this.debugOut.textContent || "") + s + "\n";
    }
}

function initOnce() {
    if (__a3cpDemoInitialized) return;
    __a3cpDemoInitialized = true;

    const ui = new A3CPDemoUI(document);
    const controller = new A3CPDemoController(ui);
    controller.init();
}

document.addEventListener("DOMContentLoaded", initOnce);


class A3CPDemoController {
    constructor(ui) {
        this.ui = ui;

        // Locked invariants
        this.schemaVersion = "1.0.1";
        this.wsPath = "/camera_feed_worker/capture";
        this.sessionStorageKey = "a3cp_demo_session_id";
        // Phase 2 HTTP endpoints (adjust if your session_manager routes differ)
        this.http = {
            startSessionPath: "/session_manager/sessions.start",
            endSessionPath: "/session_manager/sessions.end",
            validateSessionPath: "/session_manager/sessions.validate",
        };


        // Runtime state (Phase 1: placeholders)
        this.state = {
            session: { status: "idle", userId: "", performerId: "", sessionId: "" },
            preview: { status: "stopped" },
            capture: { status: "stopped" },
            busy: false,
        };
    }

    init() {
        this.ui.bind(this);

        // Phase 1: deterministic initial UI state (no network).
        // Defaults: idle session, preview stopped, capture stopped, frames=0, no error.
        this.ui.clearError?.();
        this.ui.setFramesSent?.(0);
        this.ui.setRecordId?.("");
        this.ui.setCaptureId?.("");

        // Initialize from current input values if present.
        const userId = this.ui.userId?.value?.trim() ?? "";
        const performerId = this.ui.performerId?.value?.trim() ?? userId;

        // Phase 2 (step 1): restore session_id from sessionStorage on load
        const restoredSessionId = sessionStorage.getItem(this.sessionStorageKey) || "";


        this.state.session = {
            status: "idle",
            userId,
            performerId,
            sessionId: restoredSessionId,
        };

        this.state.preview = { status: "stopped" };
        this.state.capture = { status: "stopped" };
        this.state.busy = false;

        this.ui.setBusy?.(false);
        this.ui.setSessionState?.(this.state.session);
        this.ui.setPreviewState?.(this.state.preview);
        this.ui.setCaptureState?.(this.state.capture);

        // Phase 2 (step 2): while session is idle, keep performer_id defaulting to user_id
        this.ui.userId?.addEventListener("input", () => {
            if (this.state.session.status !== "idle") return;
            const userIdNow = this.ui.userId?.value?.trim() ?? "";
            const performerNow = this.ui.performerId?.value?.trim() ?? "";
            if (performerNow === "") {
                this.ui.performerId.value = userIdNow;
                this.state.session.performerId = userIdNow;
            }
            this.state.session.userId = userIdNow;
        });
        void this._silentValidateRestoredSession();

    }

    _readIdsFromUI() {
        const userId = this.ui.userId?.value?.trim() ?? "";
        const performerIdRaw = this.ui.performerId?.value?.trim() ?? "";
        const performerId = performerIdRaw !== "" ? performerIdRaw : userId;

        return { userId, performerId };
    }


    // Event handlers (Phase 1: stubs)
    async onStartSession() {
        if (this.state.busy) return;
        if (this.state.capture.status === "running") return;

        this.state.busy = true;
        this.ui.setBusy(true);

        try {
            const { userId, performerId } = this._readIdsFromUI();
            if (!userId) {
                this.ui.showError({ message: "user_id is required" });
                return;
            }

            const payload = {
                schema_version: this.schemaVersion,                 // "1.0.1"
                record_id: crypto.randomUUID(),                      // new per message
                user_id: userId,
                timestamp: new Date().toISOString(),                 // ISO 8601 UTC
                performer_id: performerId || undefined,              // optional
                // omit optional fields for now:
                // is_training_data, session_notes, training_intent_label
            };

            const resp = await fetch(this.http.startSessionPath, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload),
            });

            if (!resp.ok) {
                // try to surface server detail if present
                let detail = "";
                try {
                    const err = await resp.json();
                    detail = err?.detail ? `: ${String(err.detail)}` : "";
                } catch (_) { }
                this.ui.showError({
                    message: `Start Session failed${detail}`,
                    httpStatus: resp.status,
                });
                return;
            }

            const data = await resp.json();
            const sessionId = (data?.session_id ?? "").toString().trim();
            if (!sessionId) {
                this.ui.showError({
                    message: "Start Session failed: missing session_id in response",
                });
                return;
            }

            sessionStorage.setItem(this.sessionStorageKey, sessionId);

            this.state.session = {
                status: "active",
                userId,
                performerId,
                sessionId,
            };

            this.ui.clearError?.();
            this.ui.setSessionState?.(this.state.session);
        } catch (e) {
            this.ui.showError({ message: `Start Session error: ${String(e)}` });
        } finally {
            this.state.busy = false;
            this.ui.setBusy(false);
            // Re-apply state-based button logic
            this.ui.setSessionState?.(this.state.session);
            this.ui.setPreviewState?.(this.state.preview);
            this.ui.setCaptureState?.(this.state.capture);
        }
    }

    async _silentValidateRestoredSession() {
        const sessionId = (this.state.session.sessionId || "").trim();
        const userId = (this.state.session.userId || "").trim();

        if (!sessionId || !userId) return;

        try {
            const resp = await fetch(this.http.validateSessionPath, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ user_id: userId, session_id: sessionId }),
            });

            if (!resp.ok) {
                // If validation endpoint is unavailable or errors, do nothing (silent).
                return;
            }

            const data = await resp.json();
            const status = (data?.status ?? "").toString();

            if (status === "active") {
                // Treat as active session; lock IDs
                this.state.session.status = "active";
                this.ui.setSessionState?.(this.state.session);
                return;
            }

            // closed or invalid => clear
            sessionStorage.removeItem(this.sessionStorageKey);
            this.state.session = {
                status: "idle",
                userId: this.state.session.userId,
                performerId: this.state.session.performerId,
                sessionId: "",
            };
            this.ui.setSessionState?.(this.state.session);
        } catch (_) {
            // Silent by design
        }
    }



    async onEndSession() {
        if (this.state.busy) return;
        if (this.state.capture.status === "running") return; // do not end while capturing

        this.state.busy = true;
        this.ui.setBusy(true);

        try {
            const sessionId = (this.state.session.sessionId || "").trim();
            const userId = (this.state.session.userId || "").trim();

            if (!sessionId || !userId) {
                this.ui.showError({ message: "No active session to end" });
                return;
            }
            const performerId = (this.state.session.performerId || "").trim();

            const payload = {
                schema_version: this.schemaVersion,        // "1.0.1"
                record_id: crypto.randomUUID(),
                user_id: userId,
                performer_id: performerId,
                session_id: sessionId,
                timestamp: new Date().toISOString(),       // message creation time
                end_time: new Date().toISOString(),        // end_time (UTC)
            };

            const resp = await fetch(this.http.endSessionPath, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload),
            });

            if (!resp.ok) {
                let detail = "";
                try {
                    const err = await resp.json();
                    detail = err?.detail ? `: ${String(err.detail)}` : "";
                } catch (_) { }
                this.ui.showError({
                    message: `End Session failed${detail}`,
                    httpStatus: resp.status,
                });
                return;
            }

            // success: clear persistence and reset controller session state
            sessionStorage.removeItem(this.sessionStorageKey);

            this.state.session = {
                status: "idle",
                userId: this.ui.userId?.value?.trim() ?? userId,
                performerId: this.ui.performerId?.value?.trim() ?? (this.state.session.performerId || ""),
                sessionId: "",
            };

            this.ui.clearError?.();
            this.ui.setSessionState?.(this.state.session);
        } catch (e) {
            this.ui.showError({ message: `End Session error: ${String(e)}` });
        } finally {
            this.state.busy = false;
            this.ui.setBusy(false);
            // Re-apply state-based button logic
            this.ui.setSessionState?.(this.state.session);
            this.ui.setPreviewState?.(this.state.preview);
            this.ui.setCaptureState?.(this.state.capture);

        }
    }

    async onResetDemo() { }
    async onStartPreview() { }
    async onStopPreview() { }

    async onStartCapture() { }
    async onStopCapture() { }

    async onClearError() { }
}
