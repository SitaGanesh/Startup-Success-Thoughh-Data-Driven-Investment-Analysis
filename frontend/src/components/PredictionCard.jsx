import "./PredictionCard.css"

function bandClass(band) {
    if (band.includes("HIGH CONFIDENCE SUCCESS")) return "band-HIGH"
    if (band.includes("LIKELY SUCCESS")) return "band-LIKELY_S"
    if (band.includes("UNCERTAIN")) return "band-UNCERTAIN"
    if (band.includes("LIKELY FAILURE")) return "band-LIKELY_F"
    return "band-FAIL"
}

function barColor(prob) {
    if (prob >= 0.75) return "#10b981"
    if (prob >= 0.55) return "#34d399"
    if (prob >= 0.45) return "#f59e0b"
    if (prob >= 0.25) return "#fb923c"
    return "#ef4444"
}

export default function PredictionCard({ result, label }) {
    const pct = Math.round(result.probability * 100)

    return (
        <div className="pred-card fade-in">
            {label && <div className="pred-label">{label}</div>}

            <div className="pred-score">
                <span className="pred-pct" style={{ color: barColor(result.probability) }}>
                    {pct}%
                </span>
                <span className="pred-verdict">
                    {result.success === 1 ? "SUCCESS" : "FAILURE"}
                </span>
            </div>

            <div className="prob-bar-track">
                <div
                    className="prob-bar-fill"
                    style={{
                        width: `${pct}%`,
                        background: barColor(result.probability),
                        boxShadow: `0 0 12px ${barColor(result.probability)}88`,
                    }}
                />
            </div>

            <div className={`pred-band ${bandClass(result.confidence_band)}`}>
                {result.confidence_band}
            </div>

            <div className="pred-model">
                MODEL: {result.best_model_name || result.model_used}
            </div>

            {result.interpretation && (
                <p className="pred-interp">{result.interpretation}</p>
            )}
        </div>
    )
}