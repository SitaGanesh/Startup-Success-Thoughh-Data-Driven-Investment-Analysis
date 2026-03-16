import { useState } from "react"
import { apiPredict } from "../api"
import PredictionCard from "../components/PredictionCard"
import "./Predict.css"

const MARKETS = [
    "software", "mobile", "enterprise", "health", "finance", "education",
    "e-commerce", "analytics", "social", "gaming", "hardware", "biotech",
    "clean technology", "security", "advertising", "travel", "food", "real estate", "other"
]

const COUNTRIES = [
    ["US", "United States"], ["IN", "India"], ["GB", "United Kingdom"],
    ["DE", "Germany"], ["CA", "Canada"], ["FR", "France"], ["SG", "Singapore"],
    ["AU", "Australia"], ["IL", "Israel"], ["BR", "Brazil"], ["CN", "China"],
    ["NL", "Netherlands"], ["SE", "Sweden"], ["JP", "Japan"], ["KR", "South Korea"],
]

const DEFAULTS = {
    market: "", funding_total_usd: "", funding_rounds: "",
    country_code: "US", region: "", city: "", founded_year: "",
    seed: "0", venture: "0", angel: "0", round_A: "0", round_B: "0",
    angellist_signal: "", employee_count: "",
}

export default function Predict() {
    const [form, setForm] = useState(DEFAULTS)
    const [result, setResult] = useState(null)
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState(null)

    function set(k, v) { setForm(f => ({ ...f, [k]: v })) }

    function buildPayload() {
        const p = {}
        if (form.market) p.market = form.market
        if (form.funding_total_usd) p.funding_total_usd = parseFloat(form.funding_total_usd)
        if (form.funding_rounds) p.funding_rounds = parseInt(form.funding_rounds)
        if (form.country_code) p.country_code = form.country_code
        if (form.region) p.region = form.region
        if (form.city) p.city = form.city
        if (form.founded_year) p.founded_year = parseInt(form.founded_year)
        p.seed = parseInt(form.seed)
        p.venture = parseInt(form.venture)
        p.angel = parseInt(form.angel)
        p.round_A = parseInt(form.round_A)
        p.round_B = parseInt(form.round_B)
        if (form.angellist_signal) p.angellist_signal = parseFloat(form.angellist_signal)
        if (form.employee_count) p.employee_count = parseFloat(form.employee_count)
        return p
    }

    async function handleSubmit(e) {
        e.preventDefault()
        setLoading(true)
        setError(null)
        setResult(null)
        try {
            const data = buildPayload()
            const r = await apiPredict(data)
            setResult(r)
        } catch (err) {
            setError(err.message)
        } finally {
            setLoading(false)
        }
    }

    function handleReset() {
        setForm(DEFAULTS)
        setResult(null)
        setError(null)
    }

    return (
        <div className="section predict-page">

            <div className="predict-header">
                <h1>Predict Success</h1>
                <p className="predict-sub">
                    Fill in what you know. Every field is optional — the model handles missing data.
                </p>
            </div>

            <div className="predict-layout">

                {/* ── Form ── */}
                <form className="predict-form card" onSubmit={handleSubmit}>

                    <div className="form-section-title">Core Details</div>

                    <div className="form-row">
                        <div className="form-field">
                            <label>Market / Industry</label>
                            <select value={form.market} onChange={e => set("market", e.target.value)}>
                                <option value="">— Select —</option>
                                {MARKETS.map(m => <option key={m} value={m}>{m}</option>)}
                            </select>
                        </div>
                        <div className="form-field">
                            <label>Country</label>
                            <select value={form.country_code} onChange={e => set("country_code", e.target.value)}>
                                {COUNTRIES.map(([c, n]) => <option key={c} value={c}>{n}</option>)}
                            </select>
                        </div>
                    </div>

                    <div className="form-row">
                        <div className="form-field">
                            <label>City</label>
                            <input
                                type="text" placeholder="e.g. San Francisco"
                                value={form.city} onChange={e => set("city", e.target.value)}
                            />
                        </div>
                        <div className="form-field">
                            <label>Region / State</label>
                            <input
                                type="text" placeholder="e.g. SF Bay Area"
                                value={form.region} onChange={e => set("region", e.target.value)}
                            />
                        </div>
                    </div>

                    <div className="form-row">
                        <div className="form-field">
                            <label>Total Funding (USD)</label>
                            <input
                                type="number" placeholder="e.g. 5000000" min="0"
                                value={form.funding_total_usd}
                                onChange={e => set("funding_total_usd", e.target.value)}
                            />
                        </div>
                        <div className="form-field">
                            <label>Funding Rounds</label>
                            <input
                                type="number" placeholder="e.g. 2" min="0" max="20"
                                value={form.funding_rounds}
                                onChange={e => set("funding_rounds", e.target.value)}
                            />
                        </div>
                        <div className="form-field">
                            <label>Founded Year</label>
                            <input
                                type="number" placeholder="e.g. 2020" min="1990" max="2026"
                                value={form.founded_year}
                                onChange={e => set("founded_year", e.target.value)}
                            />
                        </div>
                    </div>

                    <div className="form-section-title">Funding Type</div>
                    <div className="form-row toggle-row">
                        {[
                            ["seed", "Seed"],
                            ["venture", "Venture"],
                            ["angel", "Angel"],
                            ["round_A", "Series A"],
                            ["round_B", "Series B"],
                        ].map(([k, label]) => (
                            <button
                                type="button"
                                key={k}
                                className={`toggle-btn ${form[k] === "1" ? "on" : ""}`}
                                onClick={() => set(k, form[k] === "1" ? "0" : "1")}
                            >
                                {label}
                            </button>
                        ))}
                    </div>

                    <div className="form-section-title">Optional Signals</div>
                    <div className="form-row">
                        <div className="form-field">
                            <label>AngelList Signal (1–5)</label>
                            <input
                                type="number" placeholder="e.g. 4" min="1" max="5" step="0.1"
                                value={form.angellist_signal}
                                onChange={e => set("angellist_signal", e.target.value)}
                            />
                        </div>
                        <div className="form-field">
                            <label>Employee Count</label>
                            <input
                                type="number" placeholder="e.g. 25" min="1"
                                value={form.employee_count}
                                onChange={e => set("employee_count", e.target.value)}
                            />
                        </div>
                    </div>

                    <div className="form-actions">
                        <button
                            type="submit"
                            className="btn btn-primary"
                            disabled={loading}
                        >
                            {loading ? <><span className="spinner" /> Predicting…</> : "Predict →"}
                        </button>
                        <button type="button" className="btn btn-outline" onClick={handleReset}>
                            Reset
                        </button>
                    </div>

                    {error && <div className="form-error">⚠ {error}</div>}
                </form>

                {/* ── Result ── */}
                <div className="predict-result">
                    {result ? (
                        <PredictionCard result={result} label="Prediction Result" />
                    ) : (
                        <div className="result-placeholder card">
                            <div className="placeholder-icon">🔮</div>
                            <p>Fill in your startup details and click <strong>Predict</strong> to see your success probability.</p>
                            <ul className="placeholder-tips">
                                <li>All fields are optional</li>
                                <li>More data = more accurate prediction</li>
                                <li>Based on 49,000+ real startups</li>
                            </ul>
                        </div>
                    )}
                </div>

            </div>
        </div>
    )
}