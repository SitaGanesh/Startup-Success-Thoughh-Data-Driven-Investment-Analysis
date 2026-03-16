import { useState, useRef, useEffect } from "react"
import { apiNovaChat } from "../api"
import "./Chat.css"

const STARTERS = [
    "What funding stage should a pre-revenue startup aim for?",
    "What's the #1 mistake founders make when pitching investors?",
    "How does a startup's market size affect its fundability?",
    "What makes an AngelList profile stand out to investors?",
    "What's the difference between Series A and Series B criteria?",
    "How do I know if my startup idea is venture-scalable?",
]

function Message({ role, content }) {
    return (
        <div className={`chat-msg chat-msg-${role}`}>
            <div className="msg-avatar">
                {role === "user" ? "YOU" : "AI"}
            </div>
            <div className="msg-bubble">
                {content.split("\n").map((line, i) => (
                    line.trim()
                        ? <p key={i}>{line}</p>
                        : <br key={i} />
                ))}
            </div>
        </div>
    )
}

export default function Chat() {
    const [messages, setMessages] = useState([])
    const [input, setInput] = useState("")
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState(null)
    const bottomRef = useRef(null)
    const textareaRef = useRef(null)

    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: "smooth" })
    }, [messages, loading])

    async function send(text) {
        const userMsg = text || input.trim()
        if (!userMsg || loading) return

        const next = [...messages, { role: "user", content: userMsg }]
        setMessages(next)
        setInput("")
        setLoading(true)
        setError(null)

        try {
            const data = await apiNovaChat(next)
            setMessages(prev => [...prev, { role: "assistant", content: data.response }])
        } catch (err) {
            setError(err.message)
            // Remove the failed user message so they can retry
            setMessages(messages)
        } finally {
            setLoading(false)
        }
    }

    function handleKeyDown(e) {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault()
            send()
        }
    }

    function clearChat() {
        setMessages([])
        setError(null)
        setInput("")
    }

    const isEmpty = messages.length === 0

    return (
        <div className="chat-page">

            {/* ── Header ── */}
            <div className="chat-header">
                <div className="tag">AI ADVISOR</div>
                <h1>Veritas AI Chat</h1>
                <p className="chat-sub">
                    Ask anything about startups, fundraising, market strategy,
                    or investment analysis. Powered by Amazon Nova Lite.
                </p>
            </div>

            {/* ── Chat window ── */}
            <div className="chat-window card">

                {isEmpty && !loading && (
                    <div className="chat-empty">
                        <div className="chat-empty-icon">✦</div>
                        <div className="chat-empty-title">Veritas AI</div>
                        <p className="chat-empty-sub">
                            Ask me anything about startups, fundraising, or investment strategy.
                        </p>
                        <div className="starters-grid">
                            {STARTERS.map(s => (
                                <button
                                    key={s}
                                    className="starter-btn"
                                    onClick={() => send(s)}
                                    type="button"
                                >
                                    {s}
                                </button>
                            ))}
                        </div>
                    </div>
                )}

                {!isEmpty && (
                    <div className="messages-list">
                        {messages.map((m, i) => (
                            <Message key={i} role={m.role} content={m.content} />
                        ))}

                        {loading && (
                            <div className="chat-msg chat-msg-assistant">
                                <div className="msg-avatar">AI</div>
                                <div className="msg-bubble typing">
                                    <span /><span /><span />
                                </div>
                            </div>
                        )}

                        <div ref={bottomRef} />
                    </div>
                )}
            </div>

            {/* ── Error ── */}
            {error && (
                <div className="chat-error">
                    <strong>Error:</strong> {error}
                </div>
            )}

            {/* ── Input bar ── */}
            <div className="chat-input-bar card">
                <textarea
                    ref={textareaRef}
                    className="chat-input"
                    rows={2}
                    placeholder="Ask about startups, fundraising, markets… (Enter to send, Shift+Enter for newline)"
                    value={input}
                    onChange={e => setInput(e.target.value)}
                    onKeyDown={handleKeyDown}
                    disabled={loading}
                />
                <div className="chat-input-actions">
                    <button
                        className="btn btn-outline"
                        onClick={clearChat}
                        disabled={isEmpty}
                        type="button"
                    >
                        Clear chat
                    </button>
                    <button
                        className="btn btn-primary"
                        onClick={() => send()}
                        disabled={loading || !input.trim()}
                        type="button"
                    >
                        {loading
                            ? <><span className="spinner" /> Thinking…</>
                            : "Send →"}
                    </button>
                </div>
            </div>
        </div>
    )
}
