// API Base URL - use relative path /api in dev (proxied by Vite) or full URL in production
const BASE = import.meta.env.DEV ? '/api' : 'http://localhost:8000/api'

// Utility for consistent error handling
function handleError(status, body) {
    const detail = body?.detail || body?.message || `HTTP ${status}`
    throw new Error(detail)
}

export async function apiPredict(data) {
    try {
        const res = await fetch(`${BASE}/predict`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data),
        })
        if (!res.ok) {
            const err = await res.json().catch(() => ({}))
            handleError(res.status, err)
        }
        return res.json()
    } catch (e) {
        console.error('Prediction error:', e)
        throw e
    }
}

export async function apiCompare(startupA, startupB) {
    try {
        const res = await fetch(`${BASE}/predict/compare`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ startup_a: startupA, startup_b: startupB }),
        })
        if (!res.ok) {
            const err = await res.json().catch(() => ({}))
            handleError(res.status, err)
        }
        return res.json()
    } catch (e) {
        console.error('Compare error:', e)
        throw e
    }
}

export async function apiModelResults() {
    try {
        const res = await fetch(`${BASE}/model/results`)
        if (!res.ok) handleError(res.status, {})
        return res.json()
    } catch (e) {
        console.error('Model results error:', e)
        throw e
    }
}

export async function apiStatus() {
    try {
        const res = await fetch(`${BASE}/status`)
        if (!res.ok) handleError(res.status, {})
        return res.json()
    } catch (e) {
        console.error('Status check error:', e)
        throw e
    }
}

export async function apiDemo() {
    try {
        const res = await fetch(`${BASE}/demo/predict`)
        if (!res.ok) handleError(res.status, {})
        return res.json()
    } catch (e) {
        console.error('Demo error:', e)
        throw e
    }
}

// ─────────────────────────────────────────────────────────────
// Nova AI endpoints
// ─────────────────────────────────────────────────────────────

/**
 * Run ML prediction + Amazon Nova Pro analysis for a startup.
 * @param {Object} startup - StartupInput fields (market, funding, etc.)
 * @returns {{ prediction: Object, analysis: string, nova_model: string }}
 */
export async function apiNovaAnalyze(startup) {
    try {
        const res = await fetch(`${BASE}/nova/analyze`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ startup }),
        })
        if (!res.ok) {
            const err = await res.json().catch(() => ({}))
            handleError(res.status, err)
        }
        return res.json()
    } catch (e) {
        console.error('Nova analyze error:', e)
        throw e
    }
}

/**
 * Send a conversation to the Nova Lite chat advisor.
 * @param {Array<{role: string, content: string}>} messages - Full history
 * @returns {{ response: string, nova_model: string }}
 */
export async function apiNovaChat(messages) {
    try {
        const res = await fetch(`${BASE}/nova/chat`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ messages }),
        })
        if (!res.ok) {
            const err = await res.json().catch(() => ({}))
            handleError(res.status, err)
        }
        return res.json()
    } catch (e) {
        console.error('Nova chat error:', e)
        throw e
    }
}

/**
 * Get a market intelligence report for an industry.
 * @param {string} market - Industry name (e.g. "fintech")
 * @param {string|null} context - Optional focus question
 * @returns {{ market: string, report: string, nova_model: string }}
 */
export async function apiNovaMarket(market, context = null) {
    try {
        const res = await fetch(`${BASE}/nova/market`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ market, context }),
        })
        if (!res.ok) {
            const err = await res.json().catch(() => ({}))
            handleError(res.status, err)
        }
        return res.json()
    } catch (e) {
        console.error('Nova market error:', e)
        throw e
    }
}

/**
 * Analyze a pitch deck / business plan document.
 * @param {string} documentText - Pasted document content
 * @returns {{ analysis: string, char_count: number, nova_model: string }}
 */
export async function apiNovaDocument(documentText) {
    try {
        const res = await fetch(`${BASE}/nova/document`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ document_text: documentText }),
        })
        if (!res.ok) {
            const err = await res.json().catch(() => ({}))
            handleError(res.status, err)
        }
        return res.json()
    } catch (e) {
        console.error('Nova document error:', e)
        throw e
    }
}

/**
 * Analyse a pitch deck image using Amazon Nova Lite's multimodal vision.
 * Converts a File/Blob to base-64 and sends to /api/nova/analyze/image.
 *
 * @param {File} imageFile - Image file from <input type="file">
 * @param {string|null} extraContext - Optional text context from the user
 * @returns {{ analysis: string, image_type: string, nova_model: string, capability_used: string }}
 */
export async function apiNovaAnalyzeImage(imageFile, extraContext = null) {
    // Convert File → base64
    const image_b64 = await new Promise((resolve, reject) => {
        const reader = new FileReader()
        reader.onload = () => {
            // reader.result is "data:<mime>;base64,<data>" — strip the prefix
            const base64 = reader.result.split(",")[1]
            resolve(base64)
        }
        reader.onerror = reject
        reader.readAsDataURL(imageFile)
    })

    try {
        const res = await fetch(`${BASE}/nova/analyze/image`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                image_b64,
                image_media_type: imageFile.type || "image/jpeg",
                extra_context: extraContext || null,
            }),
        })
        if (!res.ok) {
            const err = await res.json().catch(() => ({}))
            handleError(res.status, err)
        }
        return res.json()
    } catch (e) {
        console.error('Nova image analyze error:', e)
        throw e
    }
}

/**
 * Run the 4-step Agentic Investment Research Agent.
 * Uses Nova Pro to chain: Profile → Market → Risk → Thesis.
 *
 * @param {Object} startup - StartupInput fields (market, funding, etc.)
 * @param {Object|null} prediction - Pre-computed ML result (optional)
 * @returns {{ prediction: Object, agent: Object, nova_model: string, agent_steps: number }}
 */
export async function apiNovaAgent(startup, prediction = null) {
    try {
        const body = { startup }
        if (prediction) body.prediction = prediction

        const res = await fetch(`${BASE}/nova/agent`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(body),
        })
        if (!res.ok) {
            const err = await res.json().catch(() => ({}))
            handleError(res.status, err)
        }
        return res.json()
    } catch (e) {
        console.error('Nova agent error:', e)
        throw e
    }
}