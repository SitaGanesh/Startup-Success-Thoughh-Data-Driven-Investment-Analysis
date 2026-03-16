import { useState } from "react"
import { apiNovaAnalyze, apiNovaAgent } from "../api"
import PredictionCard from "../components/PredictionCard"
import NovaReport from "../components/NovaReport"
import "./Analyze.css"

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

const STEPS = [
    { icon: "🤖", label: "ML Predicts" },
    { icon: "✦", label: "Nova Analyzes" },
    { icon: "📊", label: "Full Report" },
]

const AGENT_STEPS = [
    { icon: "🔍", label: "Profile Scout" },
    { icon: "📈", label: "Market Research" },
    { icon: "⚠️", label: "Risk Audit" },
    { icon: "💡", label: "Investment Thesis" },
]

export default function Analyze() {
    const [form, setForm] = useState(DEFAULTS)
    const [result, setResult] = useState(null)
    const [agentResult, setAgentResult] = useState(null)
    const [loading, setLoading] = useState(false)
    const [phase, setPhase] = useState("")
    const [error, setError] = useState(null)
    const [mode, setMode] = useState("standard")  // "standard" | "agent"

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
        setAgentResult(null)

        const startup = buildPayload()

        try {
            if (mode === "agent") {
                setPhase("Step 1/4 — Profile Scout running…")
                const data = await apiNovaAgent(startup)
                setAgentResult(data)
                setPhase("")
            } else {
                setPhase("Running ML prediction…")
                setPhase("Generating AI analysis with Amazon Nova…")
                const data = await apiNovaAnalyze(startup)
                setResult(data)
            }
        } catch (err) {
            setError(err.message)
        } finally {
            setLoading(false)
            setPhase("")
        }
    }

    function handleReset() {
        setForm(DEFAULTS)
        setResult(null)
        setAgentResult(null)
        setError(null)
    }

    const Toggle = ({ k, label }) => (
        <label className="toggle-wrap">
            <input
                type="checkbox"
                checked={form[k] === "1"}
                onChange={e => set(k, e.target.checked ? "1" : "0")}
            />
            <span className="toggle-slider" />
            <span className="toggle-label">{label}</span>
        </label>
    )

    return (
        <div className="section analyze-page">

            {/* ── Header ── */}
            <div className="analyze-header">
                <div className="tag">NOVA AI + ML</div>
                <h1>Deep Startup Analysis</h1>
                <p className="analyze-sub">
                    Enter startup details below. Choose <strong>Standard</strong> for a
                    fast ML + Nova report, or <strong>Agent Mode</strong> for a 4-step
                    agentic investment research chain.
                </p>

                {/* Mode switcher */}
                <div className="analyze-mode-tabs">
                    <button
                        type="button"
                        className={`analyze-tab ${mode === "standard" ? "analyze-tab-active" : ""}`}
                        onClick={() => { setMode("standard"); setResult(null); setAgentResult(null); setError(null) }}
                    >
                        ✦ Standard Analysis
                    </button>
                    <button
                        type="button"
                        className={`analyze-tab ${mode === "agent" ? "analyze-tab-active" : ""}`}
                        onClick={() => { setMode("agent"); setResult(null); setAgentResult(null); setError(null) }}
                    >
                        🤖 Agent Mode
                        <span className="analyze-tab-badge">Agentic AI</span>
                    </button>
                </div>

                <div className="analyze-pipeline">
                    {(mode === "agent" ? AGENT_STEPS : STEPS).map((s, i) => (
                        <div key={i} className="pipeline-step">
                            <div className="pipeline-icon">{s.icon}</div>
                            <span>{s.label}</span>
                            {i < (mode === "agent" ? AGENT_STEPS : STEPS).length - 1 && (
                                <div className="pipeline-arrow">→</div>
                            )}
                        </div>
                    ))}
                </div>
            </div>

            {/* ── Form ── */}
            <form className="analyze-form card" onSubmit={handleSubmit}>

                <div className="form-section-title">Startup Profile</div>
                <div className="form-row">
                    <div className="form-group">
                        <label>Market / Industry</label>
                        <select value={form.market} onChange={e => set("market", e.target.value)}>
                            <option value="">Select market…</option>
                            {MARKETS.map(m => <option key={m} value={m}>{m}</option>)}
                        </select>
                    </div>
                    <div className="form-group">
                        <label>Country</label>
                        <select value={form.country_code} onChange={e => set("country_code", e.target.value)}>
                            {COUNTRIES.map(([code, name]) => (
                                <option key={code} value={code}>{name}</option>
                            ))}
                        </select>
                    </div>
                    <div className="form-group">
                        <label>Founded Year</label>
                        <input
                            type="number" min="1990" max="2025" placeholder="e.g. 2019"
                            value={form.founded_year} onChange={e => set("founded_year", e.target.value)}
                        />
                    </div>
                </div>

                <div className="form-row">
                    <div className="form-group">
                        <label>City</label>
                        <input type="text" placeholder="San Francisco"
                            value={form.city} onChange={e => set("city", e.target.value)} />
                    </div>
                    <div className="form-group">
                        <label>Region</label>
                        <input type="text" placeholder="SF Bay Area"
                            value={form.region} onChange={e => set("region", e.target.value)} />
                    </div>
                    <div className="form-group">
                        <label>AngelList Signal (1–5)</label>
                        <input
                            type="number" min="1" max="5" step="0.1" placeholder="e.g. 3.5"
                            value={form.angellist_signal}
                            onChange={e => set("angellist_signal", e.target.value)}
                        />
                    </div>
                </div>

                <div className="form-section-title">Funding</div>
                <div className="form-row">
                    <div className="form-group">
                        <label>Total Funding (USD)</label>
                        <input
                            type="number" min="0" placeholder="e.g. 5000000"
                            value={form.funding_total_usd}
                            onChange={e => set("funding_total_usd", e.target.value)}
                        />
                    </div>
                    <div className="form-group">
                        <label>Funding Rounds</label>
                        <input
                            type="number" min="0" placeholder="e.g. 2"
                            value={form.funding_rounds}
                            onChange={e => set("funding_rounds", e.target.value)}
                        />
                    </div>
                    <div className="form-group">
                        <label>Employees</label>
                        <input
                            type="number" min="1" placeholder="e.g. 25"
                            value={form.employee_count}
                            onChange={e => set("employee_count", e.target.value)}
                        />
                    </div>
                </div>

                <div className="form-section-title">Funding Types Received</div>
                <div className="toggles-row">
                    <Toggle k="seed" label="Seed" />
                    <Toggle k="angel" label="Angel" />
                    <Toggle k="venture" label="Venture" />
                    <Toggle k="round_A" label="Series A" />
                    <Toggle k="round_B" label="Series B" />
                </div>

                <div className="form-actions">
                    <button type="submit" className="btn btn-primary" disabled={loading}>
                        {loading ? (
                            <><span className="spinner" /> {phase}</>
                        ) : (
                            "✦ Generate Analysis"
                        )}
                    </button>
                    <button type="button" className="btn btn-outline" onClick={handleReset}>
                        Reset
                    </button>
                </div>

                {error && (
                    <div className="analyze-error">
                        <strong>Error:</strong> {error}
                    </div>
                )}
            </form>

            {/* ── Results ── */}
            {result && (
                <div className="analyze-results fade-in">
                    <div className="results-split">
                        <div className="results-ml">
                            <div className="results-label">ML Prediction</div>
                            <PredictionCard result={result.prediction} />
                        </div>
                    </div>

                    <div className="results-nova">
                        <div className="results-label">Amazon Nova Analysis</div>
                        <NovaReport text={result.analysis} />
                    </div>
                </div>
            )}

            {/* ── Agent Mode Results ── */}
            {agentResult && (
                <div className="analyze-results fade-in">
                    {/* ML Prediction card */}
                    <div className="results-split">
                        <div className="results-ml">
                            <div className="results-label">ML Prediction</div>
                            <PredictionCard result={agentResult.prediction} />
                        </div>
                    </div>

                    {/* Agent verdict summary */}
                    {agentResult.agent?.verdicts && (
                        <div className="agent-verdict-card card">
                            <div className="agent-verdict-header">
                                <span className="agent-verdict-title">🤖 Agent Verdict</span>
                                <span className={`agent-verdict-badge ${agentResult.agent.verdicts.invest ? "verdict-invest" : "verdict-pass"}`}>
                                    {agentResult.agent.verdicts.recommendation || (agentResult.agent.verdicts.invest ? "Invest" : "Pass")}
                                </span>
                            </div>
                            <div className="agent-verdict-grid">
                                <div className="agent-verdict-item">
                                    <span className="verdict-label">Conviction Score</span>
                                    <span className="verdict-val glow">
                                        {Math.round((agentResult.agent.final_score || 0) * 100)}%
                                    </span>
                                </div>
                                <div className="agent-verdict-item">
                                    <span className="verdict-label">Ideal Stage</span>
                                    <span className="verdict-val">{agentResult.agent.verdicts.ideal_stage || "—"}</span>
                                </div>
                                <div className="agent-verdict-item">
                                    <span className="verdict-label">Valuation Range</span>
                                    <span className="verdict-val">{agentResult.agent.verdicts.target_valuation_range || "—"}</span>
                                </div>
                                <div className="agent-verdict-item">
                                    <span className="verdict-label">Agent Steps</span>
                                    <span className="verdict-val">{agentResult.agent_steps} steps · {(agentResult.agent.total_duration_ms / 1000).toFixed(1)}s</span>
                                </div>
                            </div>
                            {agentResult.agent.verdicts.key_conditions?.length > 0 && (
                                <div className="agent-conditions">
                                    <span className="verdict-label">Key Conditions</span>
                                    <ul>
                                        {agentResult.agent.verdicts.key_conditions.map((c, i) => (
                                            <li key={i}>{c}</li>
                                        ))}
                                    </ul>
                                </div>
                            )}
                        </div>
                    )}

                    {/* Agent step outputs */}
                    {agentResult.agent?.steps?.map((step, i) => (
                        <div key={i} className="agent-step-card">
                            <div className="agent-step-header">
                                <span className="agent-step-num">Step {i + 1}</span>
                                <span className="agent-step-name">{step.name}</span>
                                <span className="agent-step-timing">{step.duration_ms}ms</span>
                            </div>
                            <NovaReport text={step.output} />
                        </div>
                    ))}
                </div>
            )}
        </div>
    )
}
