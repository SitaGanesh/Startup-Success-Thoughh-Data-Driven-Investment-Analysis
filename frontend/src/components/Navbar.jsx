import "./Navbar.css"

const ML_NAV = [
    { id: "home", label: "Home" },
    { id: "predict", label: "Predict" },
    { id: "compare", label: "Compare" },
    { id: "results", label: "Model Results" },
]

const NOVA_NAV = [
    { id: "analyze", label: "Analyze" },
    { id: "market", label: "Market" },
    { id: "document", label: "Docs" },
    { id: "chat", label: "AI Chat" },
]

export default function Navbar({ page, setPage }) {
    return (
        <nav className="navbar">
            <div className="navbar-inner">
                <button className="navbar-logo" onClick={() => setPage("home")}>
                    <span className="logo-bracket">[</span>
                    VERI<span className="logo-accent">TAS</span>
                    <span className="logo-bracket">]</span>
                </button>

                <div className="navbar-links">
                    {ML_NAV.map(n => (
                        <button
                            key={n.id}
                            className={`nav-link ${page === n.id ? "active" : ""}`}
                            onClick={() => setPage(n.id)}
                        >
                            {n.label}
                        </button>
                    ))}

                    <span className="nav-divider" />

                    {NOVA_NAV.map(n => (
                        <button
                            key={n.id}
                            className={`nav-link nav-link-nova ${page === n.id ? "active-nova" : ""}`}
                            onClick={() => setPage(n.id)}
                        >
                            {n.label}
                        </button>
                    ))}
                </div>

                <div className="navbar-status">
                    <span className="status-dot" />
                    <span>API LIVE</span>
                </div>
            </div>
        </nav>
    )
}