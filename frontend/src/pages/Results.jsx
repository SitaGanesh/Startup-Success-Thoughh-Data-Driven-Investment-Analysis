import { useState, useEffect } from "react"
import { apiModelResults } from "../api"
import "./Results.css"

const DEFAULT_METRICS = ["ROC_AUC", "Balanced_Accuracy", "Macro_F1", "Failure_Recall", "Accuracy", "Precision", "Recall", "F1"]

function getMetrics(data) {
    if (!data?.models?.length) return DEFAULT_METRICS
    const first = data.models[0]
    return DEFAULT_METRICS.filter(metric => Object.prototype.hasOwnProperty.call(first, metric))
}

function MetricBar({ value }) {
    const pct = Math.round((value || 0) * 100)
    const color = pct >= 90 ? "#10b981" : pct >= 80 ? "#34d399" : pct >= 70 ? "#f59e0b" : "#ef4444"
    return (
        <div className="metric-bar-wrap">
            <span className="metric-val" style={{ color }}>{pct}%</span>
            <div className="prob-bar-track" style={{ flex: 1 }}>
                <div
                    className="prob-bar-fill"
                    style={{ width: `${pct}%`, background: color, boxShadow: `0 0 8px ${color}66` }}
                />
            </div>
        </div>
    )
}

export default function Results() {
    const [data, setData] = useState(null)
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState(null)
    const metrics = getMetrics(data)

    useEffect(() => {
        apiModelResults()
            .then(setData)
            .catch(e => setError(e.message))
            .finally(() => setLoading(false))
    }, [])

    return (
        <div className="section results-page">

            <div className="results-header">
                <h1>Model Results</h1>
                <p className="results-sub">
                    Performance breakdown of all 5 models trained on 49,000+ real startups.
                </p>
            </div>

            {loading && (
                <div className="results-loading">
                    <span className="spinner" /> Loading model scores…
                </div>
            )}

            {error && (
                <div className="results-error">
                    ⚠ {error} — Make sure the backend is running at localhost:8000
                </div>
            )}

            {data && (
                <div className="fade-in">

                    {/* ── Best model hero ── */}
                    <div className="best-model-card card">
                        <div className="best-tag tag">Best Model</div>
                        <div className="best-name glow">{data.best_model}</div>
                        <div className="best-auc">
                            ROC-AUC: <strong>{(data.best_roc_auc * 100).toFixed(2)}%</strong>
                        </div>
                        <p className="best-desc">
                            Trained on a combination of Crunchbase startup data and AngelList signals.
                            Models are ranked by balanced performance (including failure detection), not only ROC-AUC.
                        </p>
                    </div>

                    {/* ── Results table ── */}
                    <div className="results-table card">
                        <div className="table-header">
                            <span>Model</span>
                            {metrics.map(m => <span key={m}>{m.replaceAll("_", "-")}</span>)}
                        </div>

                        {data.models.map((m, i) => (
                            <div
                                className={`table-row ${m.Model === data.best_model ? "best-row" : ""}`}
                                key={i}
                            >
                                <div className="model-name-cell">
                                    {m.Model === data.best_model && <span className="crown">👑</span>}
                                    {m.Model}
                                </div>
                                {metrics.map(metric => (
                                    <div className="metric-cell" key={metric}>
                                        <MetricBar value={m[metric]} />
                                    </div>
                                ))}
                            </div>
                        ))}
                    </div>

                    {/* ── Info cards ── */}
                    <div className="info-grid">
                        <div className="card info-card">
                            <div className="info-icon">📊</div>
                            <h3>Training Data</h3>
                            <p>49,000+ startups from Crunchbase + 257 high-quality AngelList records with team signals and funding stages.</p>
                        </div>
                        <div className="card info-card">
                            <div className="info-icon">🔧</div>
                            <h3>Feature Engineering</h3>
                            <p>42 features including startup age, funding velocity, rounds per year, category encoding, and geographic signals.</p>
                        </div>
                        <div className="card info-card">
                            <div className="info-icon">🎯</div>
                            <h3>Target Variable</h3>
                            <p>Binary classification on realized outcomes: acquired/IPO = success (1), closed = failure (0). Ambiguous operating records are excluded.</p>
                        </div>
                    </div>

                </div>
            )}
        </div>
    )
}