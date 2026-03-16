import { useState } from "react"
import { apiNovaMarket } from "../api"
import NovaReport from "../components/NovaReport"
import "./Market.css"

const POPULAR = [
    "fintech", "healthtech", "SaaS", "edtech", "e-commerce",
    "climate tech", "AI / ML", "biotech", "cybersecurity", "Web3",
    "proptech", "logistics", "foodtech", "HR tech", "gaming",
]

export default function Market() {
    const [market, setMarket] = useState("")
    const [context, setContext] = useState("")
    const [result, setResult] = useState(null)
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState(null)

    async function handleSubmit(e) {
        e?.preventDefault()
        if (!market.trim()) return
        setLoading(true)
        setError(null)
        setResult(null)
        try {
            const data = await apiNovaMarket(market.trim(), context.trim() || null)
            setResult(data)
        } catch (err) {
            setError(err.message)
        } finally {
            setLoading(false)
        }
    }

    function pickMarket(m) {
        setMarket(m)
        setResult(null)
        setError(null)
    }

    return (
        <div className="section market-page">

            {/* ── Header ── */}
            <div className="market-header">
                <div className="tag">MARKET INTELLIGENCE</div>
                <h1>Market Research</h1>
                <p className="market-sub">
                    Ask Amazon Nova Pro about any industry. Get a full market sizing,
                    competitive landscape, startup opportunities, and investment signals report.
                </p>
            </div>

            {/* ── Quick picks ── */}
            <div className="market-pills">
                <span className="pills-label">Popular:</span>
                <div className="pills-list">
                    {POPULAR.map(m => (
                        <button
                            key={m}
                            className={`pill ${market === m ? "pill-active" : ""}`}
                            onClick={() => pickMarket(m)}
                            type="button"
                        >
                            {m}
                        </button>
                    ))}
                </div>
            </div>

            {/* ── Form ── */}
            <form className="market-form card" onSubmit={handleSubmit}>
                <div className="form-group">
                    <label>Market / Industry *</label>
                    <input
                        type="text"
                        placeholder='e.g. "fintech", "healthtech", "B2B SaaS"'
                        value={market}
                        onChange={e => setMarket(e.target.value)}
                        required
                    />
                </div>

                <div className="form-group">
                    <label>Specific focus or question (optional)</label>
                    <textarea
                        rows={3}
                        placeholder='e.g. "Focus on AI-driven financial planning tools for SMBs in Southeast Asia"'
                        value={context}
                        onChange={e => setContext(e.target.value)}
                    />
                </div>

                <div className="form-actions">
                    <button type="submit" className="btn btn-primary" disabled={loading || !market.trim()}>
                        {loading
                            ? <><span className="spinner" /> Researching market…</>
                            : "Generate Market Report →"}
                    </button>
                    <button type="button" className="btn btn-outline"
                        onClick={() => { setMarket(""); setContext(""); setResult(null); setError(null) }}>
                        Clear
                    </button>
                </div>

                {error && (
                    <div className="market-error">
                        <strong>Error:</strong> {error}
                    </div>
                )}
            </form>

            {/* ── Report ── */}
            {result && (
                <div className="market-result fade-in">
                    <div className="market-result-title">
                        Market Report: <span className="glow">{result.market}</span>
                    </div>
                    <NovaReport text={result.report} />
                </div>
            )}
        </div>
    )
}
