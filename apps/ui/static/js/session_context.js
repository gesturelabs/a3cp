// apps/ui/static/js/session_context.js
// Demo-only: session continuity within a tab via sessionStorage.
// No localStorage. Cleared on End Session / Reset Demo.

const KEY = "a3cp_demo_session_id";

export function getSessionId() {
    try {
        const v = sessionStorage.getItem(KEY);
        return v && v.trim() ? v.trim() : null;
    } catch {
        return null;
    }
}

export function setSessionId(id) {
    if (typeof id !== "string") throw new TypeError("session_id must be a string");
    const trimmed = id.trim();
    if (!trimmed) throw new Error("session_id cannot be empty");
    sessionStorage.setItem(KEY, trimmed);
}

export function clearSessionId() {
    try {
        sessionStorage.removeItem(KEY);
    } catch {
        // ignore
    }
}

export function requireSessionIdOrBlock(actionName) {
    const sid = getSessionId();
    if (sid) return { ok: true, session_id: sid };
    return {
        ok: false,
        error: {
            action: actionName || "unknown_action",
            message: "Start a session first.",
            code: "MISSING_SESSION_ID",
        },
    };
}
