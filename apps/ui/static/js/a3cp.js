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

        // Capture is only actionable when session is active
        if (this.btnStartCapture) this.btnStartCapture.disabled = !isActive;
        if (this.btnStopCapture) this.btnStopCapture.disabled = true; // until capture exists

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
    // UI-only: capture state reflection.
    // state: { status: "stopped"|"running" }
    setCaptureState(state) {
        const running = state.status === "running";

        if (running) {
            // While running, force Start disabled and Stop enabled
            if (this.btnStartCapture) this.btnStartCapture.disabled = true;
            if (this.btnStopCapture) this.btnStopCapture.disabled = false;

            // Reset must be disabled while capturing (locked invariant)
            if (this.btnResetDemo) this.btnResetDemo.disabled = true;
            return;
        }

        // Stopped: do NOT enable Start here (session-state decides).
        // Always disable Stop while stopped.
        if (this.btnStopCapture) this.btnStopCapture.disabled = true;

        // Reset allowed when not capturing (session-state/busy may still disable elsewhere)
        if (this.btnResetDemo) this.btnResetDemo.disabled = false;
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
        this.wsPath = "/api/camera_feed_worker/capture";
        this.sessionStorageKey = "a3cp_demo_session_id";
        this.sessionStorageUserKey = "a3cp_demo_user_id";
        this.sessionStoragePerformerKey = "a3cp_demo_performer_id";



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
        // Phase 6 — Capture runtime fields (not part of state object)
        this._captureId = "";
        this._captureSeq = 1;
        this._framesSent = 0;
        this._captureInterval = null;



        // Phase 6 — WebSocket handle (initially null)
        this._ws = null;
        this._lastJpegBytes = null;




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
        const restoredSessionId = sessionStorage.getItem(this.sessionStorageKey) || "";

        // DOM is the only source of user_id / performer_id (no persistence)
        const domUserId = this.ui.userId?.value?.trim() ?? "";
        const domPerformerId = this.ui.performerId?.value?.trim() ?? domUserId;

        const userId = domUserId;
        const performerId = domPerformerId;

        this.state.session = {
            status: restoredSessionId ? "active" : "idle",
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


        // Initialize auto-follow flag (true only if performer_id is initially empty)
        this._performerAutoFollow =
            (this.ui.performerId?.value?.trim() ?? "") === "";

        // If user edits performer_id, stop auto-follow
        this.ui.performerId?.addEventListener("input", () => {
            if (this.state.session.status !== "idle") return;
            this._performerAutoFollow = false;
            this.state.session.performerId =
                this.ui.performerId?.value?.trim() ?? "";
        });

        // While idle, mirror user_id into performer_id if auto-follow is enabled
        this.ui.userId?.addEventListener("input", () => {
            if (this.state.session.status !== "idle") return;

            const userIdNow = this.ui.userId?.value ?? "";
            this.state.session.userId = userIdNow;

            if (this._performerAutoFollow) {
                this.ui.performerId.value = userIdNow;
                this.state.session.performerId = userIdNow;
            }
        });
        void this._silentValidateRestoredSession();

    }
    _getOrCreateCaptureCanvas() {
        if (!this._captureCanvas) {
            this._captureCanvas = document.createElement("canvas");
        }
        return this._captureCanvas;
    }

    async _encodeCanvasToJpegBytes(canvas, quality = 0.85) {
        const blob = await new Promise((resolve) => {
            canvas.toBlob(resolve, "image/jpeg", quality);
        });
        if (!blob) throw new Error("JPEG encode failed (toBlob returned null)");

        const buf = await blob.arrayBuffer();
        return new Uint8Array(buf);
    }

    _drawPreviewFrameToCanvas() {
        const video = this.ui.previewVideo;
        if (!video) throw new Error("preview_video not found");
        if (video.readyState < 2) throw new Error("preview video not ready");

        const w = Number(video.videoWidth) || 0;
        const h = Number(video.videoHeight) || 0;
        if (!w || !h) throw new Error("preview video has no dimensions");

        const canvas = this._getOrCreateCaptureCanvas();
        canvas.width = w;
        canvas.height = h;

        const ctx = canvas.getContext("2d");
        if (!ctx) throw new Error("canvas 2d context not available");

        ctx.drawImage(video, 0, 0, w, h);
        return canvas;
    }

    _readIdsFromUI() {
        const userId = this.ui.userId?.value?.trim() ?? "";
        const performerIdRaw = this.ui.performerId?.value?.trim() ?? "";
        const performerId = performerIdRaw !== "" ? performerIdRaw : userId;

        return { userId, performerId };
    }


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
                schema_version: this.schemaVersion,
                record_id: crypto.randomUUID(),
                user_id: userId,
                timestamp: new Date().toISOString(),
                performer_id: performerId || undefined,
            };

            const resp = await fetch(this.http.startSessionPath, {
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
                    message: `Start Session failed${detail}`,
                    httpStatus: resp.status,
                });
                return;
            }

            const data = await resp.json();
            const sessionId = (data?.session_id ?? "").toString().trim();
            const serverPerformerId =
                (data?.performer_id ?? performerId ?? "").toString().trim();

            if (!sessionId) {
                this.ui.showError({
                    message: "Start Session failed: missing session_id in response",
                });
                return;
            }


            // Canonicalize from server response (only persisted key allowed)
            sessionStorage.setItem(this.sessionStorageKey, sessionId);

            this.state.session = {
                status: "active",
                userId,
                performerId: serverPerformerId,
                sessionId,
            };

            this.ui.clearError?.();
            this.ui.setSessionState?.(this.state.session);
        } catch (e) {
            this.ui.showError({ message: `Start Session error: ${String(e)}` });
        } finally {
            this.state.busy = false;
            this.ui.setBusy(false);
            this.ui.setSessionState?.(this.state.session);
            this.ui.setPreviewState?.(this.state.preview);
            this.ui.setCaptureState?.(this.state.capture);
        }
    }

    async _silentValidateRestoredSession() {
        const sessionId = (this.state.session.sessionId || "").trim();
        const userId = (this.state.session.userId || "").trim();

        // Strict coherence rule:
        // If we have a stored session_id but no user_id to validate with,
        // treat the client state as invalid and clear the session_id locally.
        if (sessionId && !userId) {
            sessionStorage.removeItem(this.sessionStorageKey);

            this.state.session = {
                status: "idle",
                userId: this.state.session.userId,
                performerId: this.state.session.performerId,
                sessionId: "",
            };

            this.ui.setSessionState?.(this.state.session);
            return;
        }

        if (!sessionId || !userId) return;

        try {
            const resp = await fetch(this.http.validateSessionPath, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ user_id: userId, session_id: sessionId }),
            });

            if (!resp.ok) {
                // Silent by design: do not mutate state on transport errors.
                return;
            }

            const data = await resp.json();
            const status = (data?.status ?? "").toString();

            if (status === "active") {
                const serverPerformerId =
                    (data?.performer_id ?? this.state.session.performerId ?? "")
                        .toString()
                        .trim();

                this.state.session = {
                    status: "active",
                    userId,
                    performerId: serverPerformerId,
                    sessionId,
                };

                sessionStorage.setItem(this.sessionStorageKey, sessionId);
                sessionStorage.setItem(
                    this.sessionStoragePerformerKey,
                    serverPerformerId
                );

                this.ui.setSessionState?.(this.state.session);
                return;
            }

            // "closed" or "invalid" => clear local session
            if (status === "closed" || status === "invalid") {
                sessionStorage.removeItem(this.sessionStorageKey);

                this.state.session = {
                    status: "idle",
                    userId: this.state.session.userId,
                    performerId: this.state.session.performerId,
                    sessionId: "",
                };

                this.ui.setSessionState?.(this.state.session);
            }
        } catch (_) {
            // Silent by design
        }
    }

    async onEndSession() {
        if (this.state.busy) return;
        if (this.state.capture.status === "running") return;

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
                schema_version: this.schemaVersion,
                record_id: crypto.randomUUID(),
                user_id: userId,
                performer_id: performerId,
                session_id: sessionId,
                timestamp: new Date().toISOString(),
                end_time: new Date().toISOString(),
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

            // Treat any 200 ("closed" or "already_closed") as success
            sessionStorage.removeItem(this.sessionStorageKey);


            this.state.session = {
                status: "idle",
                userId,
                performerId,
                sessionId: "",
            };

            this.ui.clearError?.();
            this.ui.setSessionState?.(this.state.session);
        } catch (e) {
            this.ui.showError({ message: `End Session error: ${String(e)}` });
        } finally {
            this.state.busy = false;
            this.ui.setBusy(false);
            this.ui.setSessionState?.(this.state.session);
            this.ui.setPreviewState?.(this.state.preview);
            this.ui.setCaptureState?.(this.state.capture);
        }
    }
    async onResetDemo() {
        if (this.state.busy) return;

        // Hard guard: reset must never run during capture.
        if (this.state.capture.status === "running") {
            this.ui.showError({ message: "Cannot reset while capture is running." });
            return;
        }

        // 1) Best-effort stop preview (must run even when reset is about to go busy)
        try {
            if (this.state.preview.status === "running") {
                await this.onStopPreview();
            }
        } catch (_) {
            // ignore on reset
        }

        // Now enter busy mode for the rest of reset
        this.state.busy = true;
        this.ui.setBusy(true);

        try {
            // 1) Best-effort stop preview
            try {
                if (this.state.preview.status === "running") {
                    await this.onStopPreview();
                }
            } catch (_) {
                // ignore on reset
            }

            // 2) Best-effort end session only if we have a known session_id
            const sessionId = (this.state.session.sessionId || "").trim();
            const userId = (this.state.session.userId || "").trim();
            const performerId = (this.state.session.performerId || "").trim();

            if (sessionId && userId) {
                const payload = {
                    schema_version: this.schemaVersion,
                    record_id: crypto.randomUUID(),
                    user_id: userId,
                    performer_id: performerId || userId,
                    session_id: sessionId,
                    timestamp: new Date().toISOString(),
                    end_time: new Date().toISOString(),
                };

                try {
                    await fetch(this.http.endSessionPath, {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify(payload),
                    });
                } catch (_) {
                    // ignore network errors on reset
                }
            }

            // 3) Clear client persistence
            sessionStorage.removeItem(this.sessionStorageKey);


            // 4) Deterministically reset state (do not replace entire state object)
            this.state.session = { status: "idle", userId: "", performerId: "", sessionId: "" };
            this.state.preview = { status: "stopped" };
            this.state.capture = { status: "stopped" };

            // 5) Clear UI fields
            if (this.ui.userId) this.ui.userId.value = "";
            if (this.ui.performerId) this.ui.performerId.value = "";
            if (this.ui.sessionId) this.ui.sessionId.value = "";

            this.ui.setFramesSent?.(0);
            this.ui.setRecordId?.("");
            this.ui.setCaptureId?.("");
            if (this.ui.debugOut) this.ui.debugOut.textContent = "";

            this.ui.clearError?.();

            // 6) Re-apply state to UI
            this.ui.setSessionState?.(this.state.session);
            this.ui.setPreviewState?.(this.state.preview);
            this.ui.setCaptureState?.(this.state.capture);
        } finally {
            this.state.busy = false;
            this.ui.setBusy(false);

            this.ui.setSessionState?.(this.state.session);
            this.ui.setPreviewState?.(this.state.preview);
            this.ui.setCaptureState?.(this.state.capture);
        }
    }
    async onStartPreview() {
        // Preview-local in-flight guard (do not use global busy)
        if (this._previewBusy) return;

        // Idempotent: if already running, do nothing.
        if (this.state.preview.status === "running") return;

        if (!this.ui.previewVideo) {
            this.ui.showError({ message: "Preview video element not found." });
            return;
        }

        this._previewBusy = true;

        // Disable ONLY preview buttons during this async operation
        if (this.ui.btnStartPreview) this.ui.btnStartPreview.disabled = true;
        if (this.ui.btnStopPreview) this.ui.btnStopPreview.disabled = true;

        try {
            // Defensive cleanup in case a previous stream exists
            if (this._previewStream) {
                try {
                    this._previewStream.getTracks().forEach((t) => t.stop());
                } catch (_) { }
                this._previewStream = null;
            }

            const stream = await navigator.mediaDevices.getUserMedia({
                video: true,
                audio: false,
            });

            // Keep a handle first (slightly more robust)
            this._previewStream = stream;

            // Attach stream to video
            this.ui.previewVideo.srcObject = stream;

            // Some browsers require explicit play()
            try {
                await this.ui.previewVideo.play();
            } catch (_) { }

            this.state.preview = { status: "running" };
            this.ui.clearError?.();
        } catch (e) {
            // Ensure deterministic stopped state on failure
            if (this._previewStream) {
                try {
                    this._previewStream.getTracks().forEach((t) => t.stop());
                } catch (_) { }
            }
            this._previewStream = null;

            if (this.ui.previewVideo) this.ui.previewVideo.srcObject = null;

            this.state.preview = { status: "stopped" };
            this.ui.showError({
                message: `Start Preview failed: ${String(e)}`,
            });
        } finally {
            this._previewBusy = false;
            // Re-apply correct enable/disable from preview state
            this.ui.setPreviewState?.(this.state.preview);
            // Do not touch global busy/session/capture controls here
        }
    }

    async onStopPreview() {
        if (this.state.busy) return;
        if (this.state.capture.status === "running") {
            this.ui.debug?.("Stop Preview: capture running -> calling onStopCapture()");
            try {
                await this.onStopCapture(); // stub ok
            } catch (_) {
                // Even if capture teardown errors, continue stopping preview.
            }
        }

        // Idempotent: if already stopped, do nothing (but ensure video cleared).
        if (!this._previewStream && this.state.preview.status !== "running") {
            if (this.ui.previewVideo) this.ui.previewVideo.srcObject = null;
            this.state.preview = { status: "stopped" };
            this.ui.setPreviewState?.(this.state.preview);
            return;
        }

        if (!this.ui.previewVideo) {
            // Still try to stop tracks even without the element.
            if (this._previewStream) {
                try {
                    this._previewStream.getTracks().forEach((t) => t.stop());
                } catch (_) { }
                this._previewStream = null;
            }
            this.state.preview = { status: "stopped" };
            this.ui.setPreviewState?.(this.state.preview);
            return;
        }

        this.state.busy = true;
        this.ui.setBusy(true);

        try {
            const stream = this._previewStream || this.ui.previewVideo.srcObject;

            if (stream && typeof stream.getTracks === "function") {
                stream.getTracks().forEach((track) => {
                    try {
                        track.stop();
                    } catch (_) { }
                });
            }

            this._previewStream = null;

            // Clear video element.
            this.ui.previewVideo.pause?.();
            this.ui.previewVideo.srcObject = null;

            this.state.preview = { status: "stopped" };
            this.ui.clearError?.();
            this.ui.setPreviewState?.(this.state.preview);
        } catch (e) {
            this.ui.showError({ message: `Stop Preview error: ${String(e)}` });
        } finally {
            this.state.busy = false;
            this.ui.setBusy(false);
            this.ui.setSessionState?.(this.state.session);
            this.ui.setPreviewState?.(this.state.preview);
            this.ui.setCaptureState?.(this.state.capture);
        }
    }

    async onStartCapture() {
        this.ui.debug?.("onStartCapture() invoked");
        if (this.state.busy) return;

        // Step 6.1: Require active session
        const sessionId = (this.state.session.sessionId || "").trim();
        const userId = (this.state.session.userId || "").trim();

        if (!sessionId || !userId) {
            this.ui.showError({
                message: "Start Capture requires an active session (user_id + session_id)."
            });
            return;
        }

        // Step 6.2: Ensure preview is running
        if (this.state.preview.status !== "running") {
            await this.onStartPreview();

            if (this.state.preview.status !== "running") {
                this.ui.showError({
                    message: "Start Capture blocked: preview is not running."
                });
                return;
            }
        }

        // Step 6.3: Generate capture_id + initialize counters (no WS yet)
        this._captureId = crypto.randomUUID();
        this._captureSeq = 1;
        this._framesSent = 0;

        this.ui.setCaptureId?.(this._captureId);
        this.ui.setFramesSent?.(0);
        this.ui.clearError?.();

        // NEW: mark capture running so Stop button activates
        this.state.capture = { status: "running" };
        this.ui.setCaptureState?.(this.state.capture);

        // Step 6.4: Open WebSocket (no protocol messages yet)
        try {
            const wsScheme = window.location.protocol === "https:" ? "wss" : "ws";
            const wsUrl = `${wsScheme}://${window.location.host}${this.wsPath}`;

            this.ui.debug?.(`WS connecting: ${wsUrl}`);

            this._ws = new WebSocket(wsUrl);

            this._ws.onopen = async () => {
                this.ui.debug?.("WS open");

                const recordId = crypto.randomUUID();
                this.ui.setRecordId?.(recordId);

                // Derive width/height from the actual preview stream if available
                const width = Number(this.ui.previewVideo?.videoWidth) || 640;
                const height = Number(this.ui.previewVideo?.videoHeight) || 480;

                const now = new Date().toISOString();

                const msg = {
                    schema_version: this.schemaVersion,
                    record_id: recordId,
                    user_id: this.state.session.userId,
                    session_id: this.state.session.sessionId,
                    timestamp: now,            // BaseSchema.timestamp
                    modality: "image",
                    source: "ui",
                    event: "capture.open",
                    capture_id: this._captureId,

                    // Required open-only fields
                    timestamp_start: now,
                    fps_target: 15,
                    width,
                    height,
                    encoding: "jpeg",
                };



                this._ws.send(JSON.stringify(msg));
                try {
                    const canvas = this._drawPreviewFrameToCanvas();
                    const jpegBytes = await this._encodeCanvasToJpegBytes(canvas);
                    this._lastJpegBytes = jpegBytes;
                    // ---- NEW STEP (send meta only) ----
                    const recordIdMeta = crypto.randomUUID();
                    this.ui.setRecordId?.(recordIdMeta);

                    const now = new Date().toISOString();

                    const meta = {
                        schema_version: this.schemaVersion,
                        record_id: recordIdMeta,
                        user_id: this.state.session.userId,
                        session_id: this.state.session.sessionId,
                        timestamp: now,
                        modality: "image",
                        source: "ui",
                        event: "capture.frame_meta",
                        capture_id: this._captureId,
                        seq: 1,
                        timestamp_frame: now,
                        byte_length: jpegBytes.byteLength,
                    };

                    this._ws.send(JSON.stringify(meta));

                    this._ws.send(jpegBytes);

                    this._captureSeq = 2;          // since we just sent seq=1
                    this._framesSent = 1;
                    this.ui.setFramesSent?.(this._framesSent);

                } catch (e) {
                    this.ui.showError({ message: `JPEG encode failed: ${String(e)}` });
                }


                // interval starts here (only if try succeeded)
                if (this._captureInterval) {
                    clearInterval(this._captureInterval);
                    this._captureInterval = null;
                }

                this._captureInterval = setInterval(async () => {
                    if (!this._ws || this._ws.readyState !== WebSocket.OPEN) return;
                    if (this._tickInFlight) return;
                    this._tickInFlight = true;

                    try {
                        const canvas = this._drawPreviewFrameToCanvas();
                        const jpegBytes = await this._encodeCanvasToJpegBytes(canvas);

                        const recordIdMeta = crypto.randomUUID();
                        this.ui.setRecordId?.(recordIdMeta);

                        const now = new Date().toISOString();
                        const seq = this._captureSeq;

                        const meta = {
                            schema_version: this.schemaVersion,
                            record_id: recordIdMeta,
                            user_id: this.state.session.userId,
                            session_id: this.state.session.sessionId,
                            timestamp: now,
                            modality: "image",
                            source: "ui",
                            event: "capture.frame_meta",
                            capture_id: this._captureId,
                            seq,
                            timestamp_frame: now,
                            byte_length: jpegBytes.byteLength,
                        };

                        this._ws.send(JSON.stringify(meta));
                        this._ws.send(jpegBytes);

                        this._captureSeq += 1;
                        this._framesSent += 1;
                        this.ui.setFramesSent?.(this._framesSent);
                    } catch (e) {
                        this.ui.showError({ message: `Capture tick failed: ${String(e)}` });
                    }
                    finally {
                        this._tickInFlight = false;
                    }
                }, 150);

            };

            this._ws.onmessage = (ev) => {
                if (typeof ev.data !== "string") return;

                this.ui.debug?.(`WS msg: ${ev.data}`);

                try {
                    const msg = JSON.parse(ev.data);
                    if (msg?.event === "capture.abort") {
                        this.ui.showError({
                            message: "Capture aborted by server",
                            errorCode: msg?.error_code || "",
                        });
                    }
                } catch (_) {
                    // ignore
                }
            };

            this._ws.onclose = (ev) => {
                // NEW: mark capture stopped
                if (this.state.capture.status !== "stopped") {
                    this.state.capture = { status: "stopped" };
                    this.ui.setCaptureState?.(this.state.capture);
                }

                if (this._captureInterval) {
                    clearInterval(this._captureInterval);
                    this._captureInterval = null;
                    this.ui.debug?.("capture interval cleared");
                }

                this.ui.debug?.(
                    `WS close code=${ev.code} clean=${ev.wasClean} reason=${ev.reason || "(none)"}`
                );
                if (ev.code !== 1000) {
                    this.ui.showError({
                        message: `WebSocket closed (code=${ev.code}). See Debug for details.`,
                    });
                }
            };

            this._ws.onerror = () => {
                // onerror is non-diagnostic; onclose usually contains the actionable code
                this.ui.debug?.("WS error event (non-diagnostic).");
            };
        } catch (e) {
            this.ui.showError({ message: `WebSocket open failed: ${String(e)}` });
            this._ws = null;

            // Revert capture state (WS never established)
            this.state.capture = { status: "stopped" };
            this.ui.setCaptureState?.(this.state.capture);

            return;
        }


    }
    async onStopCapture() {
        // Idempotent stop: safe to call multiple times
        // 1) stop interval immediately
        if (this._captureInterval) {
            clearInterval(this._captureInterval);
            this._captureInterval = null;
            this.ui.debug?.("capture interval cleared (manual stop)");
        }

        // 2) Mark capture stopped deterministically (UI should unblock Reset immediately)
        if (this.state.capture.status !== "stopped") {
            this.state.capture = { status: "stopped" };
            this.ui.setCaptureState?.(this.state.capture);
        }

        // 3) If WS is open, send capture.close then close socket cleanly (1000)
        const ws = this._ws;
        if (ws && ws.readyState === WebSocket.OPEN) {
            const recordIdClose = crypto.randomUUID();
            this.ui.setRecordId?.(recordIdClose);

            const now = new Date().toISOString();

            const closeMsg = {
                schema_version: this.schemaVersion,
                record_id: recordIdClose,
                user_id: this.state.session.userId,
                session_id: this.state.session.sessionId,
                timestamp: now,
                modality: "image",
                source: "ui",
                event: "capture.close",
                capture_id: this._captureId,
                timestamp_end: now,
            };

            try {
                ws.send(JSON.stringify(closeMsg));
                this.ui.debug?.("Sent capture.close");
            } catch (_) {
                // ignore; we still attempt to close
            }

            try {
                ws.close(1000);
            } catch (_) {
                // ignore
            }
        }

        // 4) Clear capture runtime handles (do not touch preview)
        this._tickInFlight = false;
        this._ws = null;
        this._captureId = "";
    }

    async onClearError() {
        this.ui.clearError?.();
    }
}
