import { useLayoutEffect, useRef, useState } from "react"
import { gsap } from "gsap"
import Home from "./pages/Home"
import Predict from "./pages/Predict"
import Compare from "./pages/Compare"
import Results from "./pages/Results"
import Analyze from "./pages/Analyze"
import Market from "./pages/Market"
import Document from "./pages/Document"
import Chat from "./pages/Chat"
import Navbar from "./components/Navbar"
import "./App.css"

export default function App() {
  const [page, setPage] = useState("home")
  const pageRef = useRef(null)

  useLayoutEffect(() => {
    if (!pageRef.current) return

    const ctx = gsap.context(() => {
      gsap.fromTo(
        pageRef.current,
        { opacity: 0, y: 24, filter: "blur(8px)" },
        {
          opacity: 1,
          y: 0,
          filter: "blur(0px)",
          duration: 0.55,
          ease: "power3.out",
        }
      )
    }, pageRef)

    return () => ctx.revert()
  }, [page])

  return (
    <div className="app">
      <div className="app-ambient" aria-hidden="true">
        <span className="ambient-orb ambient-orb-a" />
        <span className="ambient-orb ambient-orb-b" />
        <span className="ambient-orb ambient-orb-c" />
      </div>
      <Navbar page={page} setPage={setPage} />
      <main>
        <div ref={pageRef} key={page} className="page-shell">
          {page === "home" && <Home setPage={setPage} />}
          {page === "predict" && <Predict />}
          {page === "compare" && <Compare />}
          {page === "results" && <Results />}
          {page === "analyze" && <Analyze />}
          {page === "market" && <Market />}
          {page === "document" && <Document />}
          {page === "chat" && <Chat />}
        </div>
      </main>
    </div>
  )
}