import { useEffect, useLayoutEffect, useRef, useState } from "react"
import { gsap } from "gsap"
import { ScrollTrigger } from "gsap/ScrollTrigger"
import { apiStatus, apiDemo } from "../api"
import PredictionCard from "../components/PredictionCard"
import "./Home.css"

const FEATURES = [
    { icon: "⚡", title: "5 ML Models", desc: "Random Forest, XGBoost, SVC, SVR, Logistic Regression trained on 49K+ startups." },
    { icon: "🎯", title: "AUC 0.94", desc: "XGBoost achieves 94% ROC-AUC — trained on real AngelList + startup data." },
    { icon: "🔍", title: "AngelList Data", desc: "Enriched with quality signals, employee counts, and funding stage data." },
    { icon: "🤖", title: "Amazon Nova AI", desc: "Strategic insights and market intelligence powered by Amazon Bedrock." },
]

export default function Home({ setPage }) {
    const rootRef = useRef(null)
    const [status, setStatus] = useState(null)
    const [demo, setDemo] = useState(null)
    const [loading, setLoading] = useState(false)

    useEffect(() => {
        apiStatus().then(setStatus).catch(() => { })
    }, [])

    useLayoutEffect(() => {
        gsap.registerPlugin(ScrollTrigger)
        if (!rootRef.current) return

        const ctx = gsap.context(() => {
            gsap.from(".hero-tag", {
                y: -18,
                opacity: 0,
                duration: 0.55,
                ease: "power3.out",
            })

            gsap.from(".hero-title-line", {
                y: 36,
                opacity: 0,
                duration: 0.75,
                stagger: 0.1,
                ease: "power4.out",
            })

            gsap.from(".hero-sub", {
                y: 20,
                opacity: 0,
                delay: 0.2,
                duration: 0.6,
                ease: "power3.out",
            })

            gsap.from(".hero-actions .btn", {
                y: 18,
                opacity: 0,
                delay: 0.3,
                duration: 0.55,
                stagger: 0.08,
                ease: "power3.out",
            })

            gsap.utils.toArray(".status-item").forEach((item) => {
                gsap.from(item, {
                    scrollTrigger: {
                        trigger: item,
                        start: "top 92%",
                    },
                    y: 24,
                    opacity: 0,
                    duration: 0.55,
                    ease: "power2.out",
                })
            })

            gsap.utils.toArray(".feature-card").forEach((card, i) => {
                gsap.from(card, {
                    scrollTrigger: {
                        trigger: card,
                        start: "top 90%",
                    },
                    y: 34,
                    opacity: 0,
                    duration: 0.65,
                    delay: i * 0.05,
                    ease: "power3.out",
                })
            })
        }, rootRef)

        return () => ctx.revert()
    }, [])

    async function handleDemo() {
        setLoading(true)
        try {
            const r = await apiDemo()
            setDemo(r)
        } catch (e) {
            alert(`Demo failed: ${e.message}\n\nMake sure the backend is running:\ncd ML && python -m src.pipeline.predict_pipeline\n\nThen start the backend:\ncd backend && python main.py`)
        } finally {
            setLoading(false)
        }
    }

    function handleCardMove(e) {
        const card = e.currentTarget
        const rect = card.getBoundingClientRect()
        const x = ((e.clientX - rect.left) / rect.width) * 2 - 1
        const y = ((e.clientY - rect.top) / rect.height) * 2 - 1
        card.style.setProperty("--mx", `${x.toFixed(3)}`)
        card.style.setProperty("--my", `${y.toFixed(3)}`)
    }

    function resetCardMove(e) {
        const card = e.currentTarget
        card.style.setProperty("--mx", "0")
        card.style.setProperty("--my", "0")
    }

    return (
        <div className="home" ref={rootRef}>

            {/* ── Hero ── */}
            <section className="hero">
                <div className="hero-tag tag">Veritas: Bridging the Gap Between Predictive Data and Strategic Reasoning.</div>
                <h1 className="hero-title">
                    <span className="hero-title-line">Will Your Startup</span><br />
                    <span className="glow hero-title-line">Succeed</span> <span className="hero-title-line">or Fail?</span>
                </h1>
                <p className="hero-sub">
                    Enter your startup details. Our ensemble of 5 ML models —
                    trained on 49,000+ real startups — predicts your success probability
                    in seconds.
                </p>
                <div className="hero-actions">
                    <button className="btn btn-primary" onClick={() => setPage("predict")}>
                        Predict My Startup →
                    </button>
                    <button className="btn btn-outline" onClick={handleDemo} disabled={loading}>
                        {loading ? <span className="spinner" /> : "Try a Demo"}
                    </button>
                </div>

                {demo && (
                    <div className="hero-demo">
                        <p className="demo-label">Sample: SF Software Startup, $5M raised, 2018</p>
                        <PredictionCard result={demo} />
                    </div>
                )}
            </section>

            {/* ── Status bar ── */}
            {status?.model_loaded && (
                <div className="status-bar">
                    <div className="status-item">
                        <span className="status-val glow">{status.best_model_name}</span>
                        <span className="status-key">Best Model</span>
                    </div>
                    <div className="status-divider" />
                    <div className="status-item">
                        <span className="status-val glow">{(status.best_roc_auc * 100).toFixed(1)}%</span>
                        <span className="status-key">ROC-AUC Score</span>
                    </div>
                    <div className="status-divider" />
                    <div className="status-item">
                        <span className="status-val glow">{status.feature_count}</span>
                        <span className="status-key">Features Used</span>
                    </div>
                    <div className="status-divider" />
                    <div className="status-item">
                        <span className="status-val glow">49K+</span>
                        <span className="status-key">Startups Trained On</span>
                    </div>
                </div>
            )}

            {/* ── Feature cards ── */}
            <section className="section features-section">
                <h2 className="section-title">How It Works</h2>
                <div className="features-grid">
                    {FEATURES.map((f, i) => (
                        <div
                            className="feature-card"
                            key={i}
                            onMouseMove={handleCardMove}
                            onMouseLeave={resetCardMove}
                        >
                            <div className="feature-icon">{f.icon}</div>
                            <h3 className="feature-title">{f.title}</h3>
                            <p className="feature-desc">{f.desc}</p>
                        </div>
                    ))}
                </div>
            </section>

            {/* ── CTA ── */}
            <section className="cta-section">
                <h2>Ready to Analyse Your Startup?</h2>
                <p>Get your success probability in under 10 seconds.</p>
                <div className="cta-actions">
                    <button className="btn btn-primary" onClick={() => setPage("predict")}>
                        Start Predicting →
                    </button>
                    <button className="btn btn-outline" onClick={() => setPage("compare")}>
                        Compare Two Startups
                    </button>
                </div>
            </section>

        </div>
    )
}