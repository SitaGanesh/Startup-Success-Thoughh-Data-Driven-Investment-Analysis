import { useState } from "react"
import { apiCompare } from "../api"
import PredictionCard from "../components/PredictionCard"
import "./Compare.css"

const MARKETS = [
    "software", "mobile", "enterprise", "health", "finance", "education",
    "e-commerce", "analytics", "social", "gaming", "hardware", "biotech",
    "clean technology", "security", "advertising", "travel", "food", "real estate", "other"
]

function StartupForm({ label, form, onChange }) {
    function set(k, v) { onChange({ ...form, [k]: v }) }

    return (
        <div className="compare-form card">
            <div className="compare-form-label">{label}</div>

            <div className="form-field">
                <label>Market</label>
                <select value={form.market} onChange={e => set("market", e.target.value)}>
                    <option value="">— Select —</option>
                    {MARKETS.map(m => <option key={m} value={m}>{m}</option>)}
                </select>
            </div>

            <div className="form-row-2">
                <div className="form-field">
                    <label>Total Funding (USD)</label>
                    <input
                        type="number" placeholder="e.g. 1000000"
                        value={form.funding_total_usd}
                        onChange={e => set("funding_total_usd", e.target.value)}
                    />
                </div>
                <div className="form-field">
                    <label>Rounds</label>
                    <input
                        type="number" placeholder="e.g. 2"
                        value={form.funding_rounds}
                        onChange={e => set("funding_rounds", e.target.value)}
                    />
                </div>
            </div>

            <div className="form-row-2">
                <div className="form-field">
                    <label>Country</label>
                    <input
                        type="text" placeholder="e.g. US"
                        value={form.country_code}
                        onChange={e => set("country_code", e.target.value)}
                    />
                </div>
                <div className="form-field">
                    <label>Founded Year</label>
                    <input
                        type="number" placeholder="e.g. 2019"
                        value={form.founded_year}
                        onChange={e => set("founded_year", e.target.value)}
                    />
                </div>
            </div>

            <div className="form-field">
                <label>City</label>
                <input
                    type="text" placeholder="e.g. New York"
                    value={form.city}
                    onChange={e => set("city", e.target.value)}
                />
            </div>

            <div className="toggle-section">
                <label>Funding Type</label>
                <div className="toggle-row">
                    {[["seed", "Seed"], ["venture", "Venture"], ["angel", "Angel"]].map(([k, lbl]) => (
                        <button
                            key={k} type="button"
                            className={`toggle-btn ${form[k] === "1" ? "on" : ""}`}
                            onClick={() => set(k, form[k] === "1" ? "0" : "1")}
                        >
                            {lbl}
                        </button>
                    ))}
                </div>
            </div>
        </div>
    )
}

const EMPTY = {
    market: "", funding_total_usd: "", funding_rounds: "",
    country_code: "", city: "", founded_year: "",
    seed: "0", venture: "0", angel: "0",
}

function toPayload(f) {
    const p = {}
    if (f.market) p.market = f.market
    if (f.funding_total_usd) p.funding_total_usd = parseFloat(f.funding_total_usd)
    if (f.funding_rounds) p.funding_rounds = parseInt(f.funding_rounds)
    if (f.country_code) p.country_code = f.country_code
    if (f.city) p.city = f.city
    if (f.founded_year) p.founded_year = parseInt(f.founded_year)
    p.seed = parseInt(f.seed)
    p.venture = parseInt(f.venture)
    p.angel = parseInt(f.angel)
    return p
}

export default function Compare() {
    const [formA, setFormA] = useState({ ...EMPTY, market: "software", country_code: "US", founded_year: "2019", venture: "1" })
    const [formB, setFormB] = useState({ ...EMPTY, market: "health", country_code: "US", founded_year: "2021", seed: "1" })
    const [result, setResult] = useState(null)
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState(null)

    async function handleCompare() {
        setLoading(true)
        setError(null)
        setResult(null)
        try {
            const r = await apiCompare(toPayload(formA), toPayload(formB))
            setResult(r)
        } catch (err) {
            setError(err.message)
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="section compare-page">

            <div className="compare-header">
                <h1>Compare Two Startups</h1>
                <p className="compare-sub">
                    Enter details for two startups — see which has a higher success probability.
                </p>
            </div>

            <div className="compare-forms">
                <StartupForm label="Startup A" form={formA} onChange={setFormA} />
                <div className="compare-vs">VS</div>
                <StartupForm label="Startup B" form={formB} onChange={setFormB} />
            </div>

            <div className="compare-actions">
                <button className="btn btn-primary" onClick={handleCompare} disabled={loading}>
                    {loading ? <><span className="spinner" /> Comparing…</> : "Compare →"}
                </button>
            </div>

            {error && <div className="compare-error">⚠ {error}</div>}

            {result && (
                <div className="compare-results fade-in">
                    <div className="winner-banner">
                        🏆 <span className="glow">{result.winner}</span> wins
                        &nbsp;—&nbsp;
                        {(result.prob_delta * 100).toFixed(1)}% higher probability
                    </div>

                    <div className="compare-cards">
                        <div className={`compare-col ${result.winner === "Startup A" ? "winner-col" : ""}`}>
                            <PredictionCard result={result.startup_a} label="Startup A" />
                        </div>
                        <div className={`compare-col ${result.winner === "Startup B" ? "winner-col" : ""}`}>
                            <PredictionCard result={result.startup_b} label="Startup B" />
                        </div>
                    </div>
                </div>
            )}
        </div>
    )
}