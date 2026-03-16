import "./NovaReport.css"

/**
 * Renders Amazon Nova's markdown-style output into styled HTML.
 * Handles: ## headings, - bullets, **bold**, and plain paragraphs.
 */
export default function NovaReport({ text, title = "AI Analysis" }) {
    if (!text) return null

    const blocks = parseBlocks(text)

    return (
        <div className="nova-report fade-in">
            <div className="nova-report-header">
                <span className="nova-badge">NOVA AI</span>
                <span className="nova-model">{title}</span>
                <span className="nova-model">amazon.nova-pro-v1:0</span>
            </div>

            <div className="nova-report-body">
                {blocks.map((block, i) => {
                    if (block.type === "heading") {
                        return (
                            <h3 key={i} className="nova-heading">
                                {block.content}
                            </h3>
                        )
                    }
                    if (block.type === "list") {
                        return (
                            <ul key={i} className="nova-list">
                                {block.items.map((item, j) => (
                                    <li key={j} dangerouslySetInnerHTML={{ __html: boldify(item) }} />
                                ))}
                            </ul>
                        )
                    }
                    if (block.type === "para" && block.content.trim()) {
                        return (
                            <p key={i} className="nova-para"
                                dangerouslySetInnerHTML={{ __html: boldify(block.content) }} />
                        )
                    }
                    return null
                })}
            </div>
        </div>
    )
}

// ── Helpers ───────────────────────────────────────────────────

function parseBlocks(text) {
    const lines = text.split("\n")
    const blocks = []
    let currentList = null

    for (const raw of lines) {
        const line = raw.trimEnd()

        if (line.startsWith("## ")) {
            if (currentList) { blocks.push(currentList); currentList = null }
            blocks.push({ type: "heading", content: line.slice(3).trim() })
            continue
        }

        if (line.startsWith("- ") || line.startsWith("* ")) {
            const item = line.slice(2).trim()
            if (!currentList) currentList = { type: "list", items: [] }
            currentList.items.push(item)
            continue
        }

        if (currentList) { blocks.push(currentList); currentList = null }

        if (line.trim() === "") {
            blocks.push({ type: "blank" })
        } else {
            blocks.push({ type: "para", content: line })
        }
    }

    if (currentList) blocks.push(currentList)
    return blocks
}

/** Convert **bold** markers to <strong> tags (no XSS risk since Nova output is trusted) */
function boldify(text) {
    return text.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
}
