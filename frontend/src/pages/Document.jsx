import { useState, useRef } from "react"
import { apiNovaDocument, apiNovaAnalyzeImage } from "../api"
import NovaReport from "../components/NovaReport"
import "./Document.css"

const PLACEHOLDER = `Paste your pitch deck or business plan here...

Example:
Company: AgroSync
Industry: AgriTech / Precision Farming
Founded: 2022, Nairobi, Kenya

Problem: 65% of sub-Saharan African smallholder farmers lose 30%+ of yield due to
poor soil management and late pest detection.

Solution: AgroSync provides AI-powered soil sensors + mobile app for real-time 
crop health monitoring. ($49 hardware + $12/month subscription)

Market: 33M smallholder farms in SSA. $4.2B addressable market growing at 18% CAGR.

Traction: 1,200 paying farms. $85K ARR. 94% retention. Partnered with Kenya Co-op Bank.

Ask: $1.5M seed round to expand to Tanzania and Uganda.`

const ACCEPTED_IMAGE_TYPES = "image/jpeg,image/png,image/webp,image/gif"
const MAX_IMAGE_MB = 5

export default function Document() {
    // ── Text mode state ──────────────────────────────────────
    const [text, setText] = useState("")

    // ── Image mode state ─────────────────────────────────────
    const [imageFile, setImageFile] = useState(null)
    const [imagePreview, setImagePreview] = useState(null)
    const [imageContext, setImageContext] = useState("")

    // ── Shared state ─────────────────────────────────────────
    const [mode, setMode] = useState("text")   // "text" | "image"
    const [result, setResult] = useState(null)
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState(null)

    const fileInputRef = useRef(null)
    const charCount = text.length
    const charLimit = 8000

    // ── Text submit ──────────────────────────────────────────
    async function handleTextSubmit(e) {
        e.preventDefault()
        if (text.trim().length < 50) return
        setLoading(true)
        setError(null)
        setResult(null)
        try {
            const data = await apiNovaDocument(text)
            setResult({ ...data, mode: "text" })
        } catch (err) {
            setError(err.message)
        } finally {
            setLoading(false)
        }
    }

    // ── Image submit ─────────────────────────────────────────
    async function handleImageSubmit(e) {
        e.preventDefault()
        if (!imageFile) return
        setLoading(true)
        setError(null)
        setResult(null)
        try {
            const data = await apiNovaAnalyzeImage(imageFile, imageContext || null)
            setResult({ ...data, mode: "image" })
        } catch (err) {
            setError(err.message)
        } finally {
            setLoading(false)
        }
    }

    // ── Image file selection ─────────────────────────────────
    function handleImageChange(e) {
        const file = e.target.files[0]
        if (!file) return

        if (file.size > MAX_IMAGE_MB * 1024 * 1024) {
            setError(`Image is too large (max ${MAX_IMAGE_MB} MB).`)
            return
        }
        setImageFile(file)
        setImagePreview(URL.createObjectURL(file))
        setResult(null)
        setError(null)
    }

    function clearImage() {
        setImageFile(null)
        setImagePreview(null)
        setImageContext("")
        setResult(null)
        setError(null)
        if (fileInputRef.current) fileInputRef.current.value = ""
    }

    function switchMode(m) {
        setMode(m)
        setResult(null)
        setError(null)
    }

    return (
        <div className="section document-page">

            {/* ── Header ── */}
            <div className="document-header">
                <div className="tag">PITCH DECK ANALYSIS</div>
                <h1>Document Analysis</h1>
                <p className="document-sub">
                    Paste your pitch deck text <em>or upload a slide image</em>.
                    Amazon Nova will evaluate it like a senior VC analyst — with a
                    clear <strong>Invest / Pass / Conditional</strong> verdict.
                </p>
            </div>

            {/* ── Mode tabs ── */}
            <div className="doc-mode-tabs">
                <button
                    className={`doc-tab ${mode === "text" ? "doc-tab-active" : ""}`}
                    onClick={() => switchMode("text")}
                    type="button"
                >
                    📄 Paste Text
                </button>
                <button
                    className={`doc-tab ${mode === "image" ? "doc-tab-active" : ""}`}
                    onClick={() => switchMode("image")}
                    type="button"
                >
                    🖼️ Upload Slide Image
                    <span className="doc-tab-badge">Multimodal</span>
                </button>
            </div>

            {/* ════════════════════════════════════════════════
                TEXT MODE
            ════════════════════════════════════════════════ */}
            {mode === "text" && (
                <>
                    <div className="doc-tips card">
                        <div className="tips-title">What to paste</div>
                        <div className="tips-grid">
                            {[
                                ["📋", "Pitch deck text", "Copy-paste the text content from your slides"],
                                ["📄", "Executive summary", "1–3 page overview of your business"],
                                ["💼", "Business plan section", "Problem, solution, market, traction, team, ask"],
                                ["🔗", "Any text outline", "Even rough notes — Nova adapts to what's there"],
                            ].map(([icon, title, desc]) => (
                                <div key={title} className="tip-item">
                                    <span className="tip-icon">{icon}</span>
                                    <div>
                                        <div className="tip-title">{title}</div>
                                        <div className="tip-desc">{desc}</div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>

                    <form className="document-form card" onSubmit={handleTextSubmit}>
                        <div className="doc-textarea-wrap">
                            <textarea
                                className="doc-textarea"
                                rows={16}
                                placeholder={PLACEHOLDER}
                                value={text}
                                onChange={e => setText(e.target.value)}
                                maxLength={charLimit}
                            />
                            <div className={`char-counter ${charCount > charLimit * 0.9 ? "char-warn" : ""}`}>
                                {charCount.toLocaleString()} / {charLimit.toLocaleString()} chars
                                {charCount > charLimit && " (will be trimmed)"}
                            </div>
                        </div>

                        <div className="form-actions">
                            <button
                                type="submit"
                                className="btn btn-primary"
                                disabled={loading || text.trim().length < 50}
                            >
                                {loading
                                    ? <><span className="spinner" /> Analyzing document…</>
                                    : "✦ Get Investment Analysis →"}
                            </button>
                            <button
                                type="button"
                                className="btn btn-outline"
                                onClick={() => { setText(""); setResult(null); setError(null) }}
                            >
                                Clear
                            </button>
                        </div>

                        {text.trim().length < 50 && text.length > 0 && (
                            <p className="doc-hint">Paste more content — minimum 50 characters needed.</p>
                        )}
                        {error && <div className="doc-error"><strong>Error:</strong> {error}</div>}
                    </form>
                </>
            )}

            {/* ════════════════════════════════════════════════
                IMAGE MODE — Multimodal (Nova Lite Vision)
            ════════════════════════════════════════════════ */}
            {mode === "image" && (
                <>
                    <div className="doc-tips card">
                        <div className="tips-title">Upload a pitch deck slide or screenshot</div>
                        <div className="tips-grid">
                            {[
                                ["📊", "Traction / metrics slide", "Nova reads charts, tables, and numbers directly"],
                                ["💰", "Financials slide", "Revenue projections, unit economics, burn rate"],
                                ["🗺️", "Market size diagram", "TAM/SAM/SOM diagrams and market maps"],
                                ["👥", "Team slide", "Headshots, bios, and advisor profiles"],
                            ].map(([icon, title, desc]) => (
                                <div key={title} className="tip-item">
                                    <span className="tip-icon">{icon}</span>
                                    <div>
                                        <div className="tip-title">{title}</div>
                                        <div className="tip-desc">{desc}</div>
                                    </div>
                                </div>
                            ))}
                        </div>
                        <p className="doc-hint" style={{ marginTop: "0.75rem" }}>
                            Powered by <strong>Amazon Nova Lite multimodal vision</strong> — reads text, charts, and diagrams directly from the image.
                        </p>
                    </div>

                    <form className="document-form card" onSubmit={handleImageSubmit}>
                        {/* Drop zone / file picker */}
                        {!imagePreview ? (
                            <div
                                className="doc-dropzone"
                                onClick={() => fileInputRef.current?.click()}
                                onDragOver={e => e.preventDefault()}
                                onDrop={e => {
                                    e.preventDefault()
                                    const file = e.dataTransfer.files[0]
                                    if (file) handleImageChange({ target: { files: [file] } })
                                }}
                            >
                                <span className="dropzone-icon">🖼️</span>
                                <span className="dropzone-label">Click or drag a slide image here</span>
                                <span className="dropzone-hint">JPEG, PNG, WebP — max {MAX_IMAGE_MB} MB</span>
                                <input
                                    ref={fileInputRef}
                                    type="file"
                                    accept={ACCEPTED_IMAGE_TYPES}
                                    style={{ display: "none" }}
                                    onChange={handleImageChange}
                                />
                            </div>
                        ) : (
                            <div className="doc-image-preview">
                                <img
                                    src={imagePreview}
                                    alt="Selected slide"
                                    className="preview-img"
                                />
                                <button
                                    type="button"
                                    className="preview-remove"
                                    onClick={clearImage}
                                    title="Remove image"
                                >
                                    ✕ Remove
                                </button>
                                <p className="preview-meta">
                                    {imageFile?.name} · {(imageFile?.size / 1024).toFixed(0)} KB
                                </p>
                            </div>
                        )}

                        {/* Optional context */}
                        <div className="form-group" style={{ marginTop: "1rem" }}>
                            <label>Add context (optional)</label>
                            <input
                                type="text"
                                placeholder='e.g. "This is our traction slide showing MoM customer growth"'
                                value={imageContext}
                                onChange={e => setImageContext(e.target.value)}
                            />
                        </div>

                        <div className="form-actions">
                            <button
                                type="submit"
                                className="btn btn-primary"
                                disabled={loading || !imageFile}
                            >
                                {loading
                                    ? <><span className="spinner" /> Analyzing image with Nova Vision…</>
                                    : "🖼️ Analyze Slide with Nova →"}
                            </button>
                            {imageFile && (
                                <button type="button" className="btn btn-outline" onClick={clearImage}>
                                    Clear
                                </button>
                            )}
                        </div>

                        {error && <div className="doc-error"><strong>Error:</strong> {error}</div>}
                    </form>
                </>
            )}

            {/* ── Shared result panel ── */}
            {result && (
                <div className="document-result fade-in">
                    <div className="doc-result-header">
                        <span>
                            {result.mode === "image" ? "🖼️ Image Analysis" : "Investment Analysis"}
                        </span>
                        <span className="doc-result-meta">
                            {result.mode === "image"
                                ? `${result.capability_used?.replace("_", " ")} · ${result.nova_model}`
                                : `${result.char_count?.toLocaleString()} chars analyzed`}
                        </span>
                    </div>
                    <NovaReport text={result.analysis} />
                </div>
            )}
        </div>
    )
}
