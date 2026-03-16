"""
main.py  —  Veritas FastAPI Backend
─────────────────────────────────────────
Folder layout:
  root/
  ├── backend/main.py         ← this file
  ├── ml/
  │   ├── artifacts/model.pkl
  │   ├── artifacts/preprocessor.pkl
  │   ├── artifacts/model_results.csv
  │   └── src/pipeline/predict_pipeline.py

Run:
    python main.py
    # or: uvicorn main:app --port 8000

Endpoints:
  GET  /                         health check
  GET  /api/status               model status + metadata
  POST /api/predict              predict one startup
  GET  /api/demo/predict         demo prediction (no input needed)
  GET  /api/model/results        all 5 model scores table
  POST /api/train                retrain model (background)
  GET  /api/train/status         training progress
  POST /api/predict/batch        predict up to 50 startups
  POST /api/predict/compare      compare two startups side-by-side
"""

import os
import sys
import time
import traceback
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional, List

import pandas as pd
import numpy as np
import uvicorn
from dotenv import load_dotenv

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict, Field

# Load .env from repo root (AWS credentials, etc.)
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

# ── Path setup ────────────────────────────────────────────────
BACKEND_DIR = Path(__file__).resolve().parent
ROOT_DIR = BACKEND_DIR.parent
ML_DIR = ROOT_DIR / "ml"
NOVA_DIR = ROOT_DIR / "nova"
ARTIFACTS_DIR = ML_DIR / "artifacts"
MODEL_PKL = ARTIFACTS_DIR / "model.pkl"
RESULTS_CSV = ARTIFACTS_DIR / "model_results.csv"

# Add ml/ to sys.path so src.pipeline.predict_pipeline is importable
# Add root/ to sys.path so nova/ package is importable
sys.path.insert(0, str(ML_DIR))
sys.path.insert(0, str(ROOT_DIR))

# ── Lazy-load predict pipeline ────────────────────────────────
_pipeline = None
_model_loaded = False
_load_error = None


def get_pipeline():
    global _pipeline, _model_loaded, _load_error
    if _pipeline is not None:
        return _pipeline
    try:
        os.chdir(str(ML_DIR))   # artifacts/ paths are relative to ml/
        from src.pipeline.predict_pipeline import PredictPipeline
        _pipeline = PredictPipeline()
        _pipeline._load()
        _model_loaded = True
        _load_error = None
        print(f"✅  Model loaded from {MODEL_PKL}")
    except Exception as e:
        _model_loaded = False
        _load_error = str(e)
        print(f"❌  Model load failed: {e}")
    return _pipeline


# ── Lifespan (modern replacement for @on_event) ───────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀  Veritas backend starting …")
    if MODEL_PKL.exists():
        get_pipeline()
    else:
        print("⚠️   model.pkl not found — POST /api/train to train first")
    yield
    # Shutdown (nothing needed)
    print("👋  Veritas backend shutting down")


# ── App ───────────────────────────────────────────────────────
app = FastAPI(
    title="Veritas API",
    description="AI-powered startup success prediction — ML + Amazon Nova",
    version="1.0.0",
    docs_url="/docs",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─────────────────────────────────────────────────────────────
# Pydantic schemas  (Pydantic V2 style — no warnings)
# ─────────────────────────────────────────────────────────────

class StartupInput(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    # ── Core fields (from start_up_data.csv) ──────────────────
    market:            Optional[str] = Field(
        None, json_schema_extra={"example": "software"})
    funding_total_usd: Optional[float] = Field(
        None, json_schema_extra={"example": 5000000})
    funding_rounds:    Optional[int] = Field(
        None, json_schema_extra={"example": 2})
    country_code:      Optional[str] = Field(
        None, json_schema_extra={"example": "US"})
    region:            Optional[str] = Field(
        None, json_schema_extra={"example": "SF Bay Area"})
    city:              Optional[str] = Field(
        None, json_schema_extra={"example": "San Francisco"})
    founded_year:      Optional[int] = Field(
        None, json_schema_extra={"example": 2018})
    seed:    Optional[int] = Field(
        None, description="1 = seed funded, 0 = not")
    venture: Optional[int] = Field(
        None, description="1 = venture funded, 0 = not")
    angel:   Optional[int] = Field(None)
    round_A: Optional[int] = Field(None)
    round_B: Optional[int] = Field(None)
    round_C: Optional[int] = Field(None)

    # ── AngelList extras ───────────────────────────────────────
    angellist_signal: Optional[float] = Field(
        None, description="1-5 quality score from AngelList")
    employee_count:   Optional[float] = Field(None)
    latitude:         Optional[float] = Field(None)
    longitude:        Optional[float] = Field(None)


class PredictionResponse(BaseModel):
    success:          int
    probability:      float
    confidence_band:  str
    best_model_name:  str
    interpretation:   str
    input_summary:    dict


class CompareRequest(BaseModel):
    startup_a: StartupInput
    startup_b: StartupInput


# ─────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────

def _build_interpretation(prob: float, band: str, data: dict) -> str:
    pct = round(prob * 100, 1)
    lines = [f"This startup has a {pct}% probability of success ({band})."]

    if data.get("venture"):
        lines.append("Venture capital backing is a strong positive signal.")
    if data.get("seed"):
        lines.append("Seed funding shows early investor confidence.")
    fr = data.get("funding_rounds")
    if fr and int(fr) >= 3:
        lines.append(
            f"{fr} funding rounds indicate sustained investor interest.")
    sig = data.get("angellist_signal")
    if sig and float(sig) >= 4:
        lines.append(f"AngelList signal {sig}/5 suggests a high-quality team.")
    mkt = data.get("market")
    if mkt:
        lines.append(f"Operating in the '{mkt}' market.")

    if prob < 0.45:
        lines.append(
            "Recommendation: Consider improving funding strategy, "
            "team experience, or market positioning before scaling.")
    elif prob >= 0.75:
        lines.append(
            "Recommendation: Strong fundamentals detected. "
            "Focus on scaling and expanding market reach.")
    else:
        lines.append(
            "Recommendation: Moderate outlook. "
            "Strengthening traction and funding metrics could improve prospects.")

    return " ".join(lines)


def _safe_predict(data: dict) -> dict:
    pipeline = get_pipeline()
    if pipeline is None or not _model_loaded:
        raise HTTPException(
            status_code=503,
            detail=f"Model not loaded. {_load_error or 'Run POST /api/train first.'}"
        )
    try:
        return pipeline.predict(data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {e}")


def _get_best_auc() -> float:
    try:
        if RESULTS_CSV.exists():
            return float(pd.read_csv(RESULTS_CSV).iloc[0]["ROC_AUC"])
    except Exception:
        pass
    return 0.0


def _extract_bullets(text: str, limit: int = 3) -> list[str]:
    """Extract up to `limit` bullet-like lines from model text."""
    if not text:
        return []

    items: list[str] = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue

        if line.startswith(("- ", "* ", "• ")):
            cleaned = line[2:].strip()
        elif line[:2].isdigit() and line[2:3] in {".", ")"}:
            cleaned = line[3:].strip()
        else:
            continue

        if cleaned:
            items.append(cleaned)
        if len(items) >= limit:
            break

    return items


# ─────────────────────────────────────────────────────────────
# Routes


# ─────────────────────────────────────────────────────────────

@app.get("/", tags=["Health"])
async def root():
    return {
        "service": "Veritas API",
        "status":  "running",
        "docs":    "/docs",
        "version": "1.0.0",
    }


# ── Model status ──────────────────────────────────────────────
@app.get("/api/status", tags=["Model"])
async def get_status():
    """Return model metadata and load status."""
    if not MODEL_PKL.exists():
        return {
            "model_loaded":    False,
            "artifacts_exist": False,
            "message":         "No trained model found. POST /api/train to train.",
        }

    pipeline = get_pipeline()
    if not _model_loaded:
        return {
            "model_loaded":    False,
            "artifacts_exist": True,
            "error":           _load_error,
        }

    pkg = pipeline._pkg
    preprocessor = pkg["preprocessor"]
    return {
        "model_loaded":    True,
        "artifacts_exist": True,
        "best_model_name": pkg["best_model_name"],
        "best_roc_auc":    _get_best_auc(),
        "decision_threshold": float(pkg.get("decision_threshold", 0.5)),
        "threshold_metrics": pkg.get("threshold_metrics", {}),
        "feature_count":   len(preprocessor["X_columns"]),
        "model_path":      str(MODEL_PKL),
    }


# ── Single prediction ─────────────────────────────────────────
@app.post("/api/predict", response_model=PredictionResponse, tags=["Prediction"])
async def predict(startup: StartupInput):
    """
    Predict startup success probability.

    Send a JSON body with any combination of startup fields.
    All fields are optional — missing ones are handled automatically.

    **Example request body:**
    ```json
    {
      "market": "software",
      "funding_total_usd": 5000000,
      "funding_rounds": 2,
      "country_code": "US",
      "founded_year": 2018,
      "seed": 1,
      "venture": 1
    }
    ```
    """
    data = {k: v for k, v in startup.model_dump().items() if v is not None}
    result = _safe_predict(data)

    return PredictionResponse(
        success=result["success"],
        probability=result["probability"],
        confidence_band=result["confidence_band"],
        best_model_name=result["best_model_name"],
        interpretation=_build_interpretation(
            result["probability"], result["confidence_band"], data),
        input_summary={
            "fields_provided": len(data),
            "market":          data.get("market", "Not provided"),
            "country":         data.get("country_code", "Not provided"),
            "funding_usd":     data.get("funding_total_usd", "Not provided"),
            "founded_year":    data.get("founded_year", "Not provided"),
        }
    )


# ── Demo prediction ───────────────────────────────────────────
@app.get("/api/demo/predict", response_model=PredictionResponse, tags=["Prediction"])
async def demo_predict():
    """
    Try the API with a pre-built sample startup.
    No input required — just hit this endpoint.
    """
    return await predict(StartupInput(
        market="software",
        funding_total_usd=5_000_000,
        funding_rounds=2,
        country_code="US",
        region="SF Bay Area",
        city="San Francisco",
        founded_year=2018,
        seed=1,
        venture=1,
    ))


# ── Model results table ───────────────────────────────────────
@app.get("/api/model/results", tags=["Model"])
async def get_model_results():
    """All 5 model scores from the last training run."""
    if not RESULTS_CSV.exists():
        raise HTTPException(
            status_code=404,
            detail="No results found. Run POST /api/train first."
        )
    df = pd.read_csv(RESULTS_CSV)
    for col in [
        "Accuracy", "Precision", "Recall", "F1", "ROC_AUC",
        "Balanced_Accuracy", "Macro_F1", "Failure_Recall"
    ]:
        if col in df.columns:
            df[col] = df[col].round(4)

    best_row = df.iloc[0]
    return {
        "models":       df.to_dict(orient="records"),
        "best_model":   best_row["Model"],
        "best_roc_auc": float(best_row["ROC_AUC"]),
        "best_balanced_accuracy": float(best_row.get("Balanced_Accuracy", 0.0)),
        "best_macro_f1": float(best_row.get("Macro_F1", 0.0)),
        "best_failure_recall": float(best_row.get("Failure_Recall", 0.0)),
        "total_models": len(df),
    }


# ── Batch prediction ──────────────────────────────────────────
@app.post("/api/predict/batch", tags=["Prediction"])
async def predict_batch(startups: List[StartupInput]):
    """
    Predict success for up to 50 startups at once.

    Send a JSON array of startup objects.
    """
    if len(startups) > 50:
        raise HTTPException(status_code=400, detail="Max 50 per batch.")

    results = []
    for i, s in enumerate(startups):
        data = {k: v for k, v in s.model_dump().items() if v is not None}
        try:
            r = _safe_predict(data)
            results.append({
                "index":           i,
                "success":         r["success"],
                "probability":     r["probability"],
                "confidence_band": r["confidence_band"],
            })
        except Exception as e:
            results.append({"index": i, "error": str(e)})

    return {"total": len(results), "results": results}


# ── Compare two startups ──────────────────────────────────────
@app.post("/api/predict/compare", tags=["Prediction"])
async def compare_startups(req: CompareRequest):
    """
    Compare two startups side by side.

    Returns both predictions + a winner.
    """
    data_a = {k: v for k, v in req.startup_a.model_dump().items()
              if v is not None}
    data_b = {k: v for k, v in req.startup_b.model_dump().items()
              if v is not None}

    r_a = _safe_predict(data_a)
    r_b = _safe_predict(data_b)

    winner = "A" if r_a["probability"] >= r_b["probability"] else "B"
    delta = abs(r_a["probability"] - r_b["probability"])

    return {
        "startup_a":  r_a,
        "startup_b":  r_b,
        "winner":     f"Startup {winner}",
        "prob_delta": round(delta, 4),
        "model_used": r_a["best_model_name"],
    }


# ── Training ──────────────────────────────────────────────────
_training_status: dict = {
    "running":     False,
    "last_run":    None,
    "last_result": None,
    "error":       None,
}


def _run_training():
    global _pipeline, _model_loaded, _load_error, _training_status
    _training_status["running"] = True
    _training_status["error"] = None
    original_cwd = os.getcwd()

    try:
        os.chdir(str(ML_DIR))
        from src.pipeline.train_pipeline import TrainPipeline
        result = TrainPipeline().run()

        _training_status["last_result"] = {
            "best_model_name": result["best_model_name"],
            "best_roc_auc":    float(result["best_roc_auc"]),
            "train_rows":      result["train_shape"][0],
            "features":        result["train_shape"][1],
        }

        # Reload pipeline with newly trained model
        _pipeline = None
        _model_loaded = False
        get_pipeline()

    except Exception as e:
        _training_status["error"] = str(e)
        traceback.print_exc()
    finally:
        _training_status["running"] = False
        _training_status["last_run"] = time.strftime("%Y-%m-%d %H:%M:%S")
        os.chdir(original_cwd)


@app.post("/api/train", tags=["Model"])
async def train_model(background_tasks: BackgroundTasks):
    """
    Start full model retraining in the background.

    Takes ~30-40 minutes. Poll GET /api/train/status to check progress.
    """
    if _training_status["running"]:
        return {"message": "Training already running.", "status": _training_status}
    background_tasks.add_task(_run_training)
    return {
        "message": "Training started in background.",
        "note":    "Poll GET /api/train/status. Takes ~30-40 mins."
    }


@app.get("/api/train/status", tags=["Model"])
async def get_training_status():
    """Check if training is running and see the last result."""
    return _training_status


# ─────────────────────────────────────────────────────────────
# Nova AI — Pydantic schemas
# ─────────────────────────────────────────────────────────────

class NovaAnalyzeRequest(BaseModel):
    startup: StartupInput
    prediction: Optional[dict] = Field(
        None,
        description="Pre-computed ML result. If omitted the endpoint will call /api/predict first."
    )


class NovaChatMessage(BaseModel):
    role:    str   # "user" or "assistant"
    content: str


class NovaChatRequest(BaseModel):
    messages: List[NovaChatMessage]


class NovaMarketRequest(BaseModel):
    market:  str
    context: Optional[str] = None


class NovaDocumentRequest(BaseModel):
    document_text: str


class NovaImageRequest(BaseModel):
    image_b64:        str
    image_media_type: Optional[str] = Field(
        "image/jpeg",
        description="MIME type: image/jpeg, image/png, image/gif, image/webp"
    )
    extra_context:    Optional[str] = None


class NovaAgentRequest(BaseModel):
    startup: StartupInput
    prediction: Optional[dict] = Field(
        None,
        description="Pre-computed ML result. If omitted the endpoint runs /api/predict first."
    )


# ─────────────────────────────────────────────────────────────
# Nova AI — Routes
# ─────────────────────────────────────────────────────────────

def _nova_unavailable(e: Exception):
    """Raise a clean 503 for any Nova / boto3 failure."""
    raise HTTPException(status_code=503, detail=str(e))


async def _run_blocking(func, *args, **kwargs):
    """Run blocking SDK/model calls off the event loop."""
    return await run_in_threadpool(lambda: func(*args, **kwargs))


@app.post("/api/nova/analyze", tags=["Nova AI"])
async def nova_analyze(req: NovaAnalyzeRequest):
    """
    Run ML prediction then generate a full Amazon Nova analysis report.

    If you already have an ML result pass it in `prediction` to skip that step.
    Returns both the raw ML prediction and the Nova analysis text.
    """
    data = {k: v for k, v in req.startup.model_dump().items() if v is not None}

    # Get (or reuse) ML prediction
    if req.prediction:
        ml_result = req.prediction
    else:
        ml_result = _safe_predict(data)

    try:
        from nova.analyzer import analyze_startup
        analysis = await _run_blocking(analyze_startup, data, ml_result)
    except Exception as e:
        _nova_unavailable(e)

    return {
        "prediction":  ml_result,
        "analysis":    analysis,
        "nova_model":  "amazon.nova-pro-v1:0",
    }


@app.post("/api/nova/chat", tags=["Nova AI"])
async def nova_chat(req: NovaChatRequest):
    """
    Chat with the Veritas AI advisor.

    Send the full conversation history; the endpoint returns the next reply.
    """
    if not req.messages:
        raise HTTPException(status_code=400, detail="No messages provided.")

    messages = [{"role": m.role, "content": m.content} for m in req.messages]

    try:
        from nova.chat import chat
        response = await _run_blocking(chat, messages)
    except Exception as e:
        _nova_unavailable(e)

    return {"response": response, "nova_model": "amazon.nova-lite-v1:0"}


@app.post("/api/nova/market", tags=["Nova AI"])
async def nova_market(req: NovaMarketRequest):
    """
    Generate a market intelligence report for any industry or market sector.
    """
    if not req.market or len(req.market.strip()) < 2:
        raise HTTPException(
            status_code=400, detail="market field is required.")

    try:
        from nova.market import market_intelligence
        report = await _run_blocking(market_intelligence, req.market.strip(), req.context)
    except Exception as e:
        _nova_unavailable(e)

    return {
        "market":     req.market,
        "report":     report,
        "nova_model": "amazon.nova-pro-v1:0",
    }


@app.post("/api/nova/document", tags=["Nova AI"])
async def nova_document(req: NovaDocumentRequest):
    """
    Analyze a startup pitch deck or business plan pasted as plain text.

    Returns a structured investment analysis with a clear Invest/Pass verdict.
    """
    if not req.document_text or len(req.document_text.strip()) < 50:
        raise HTTPException(
            status_code=400,
            detail="document_text too short (minimum 50 characters)."
        )

    try:
        from nova.market import analyze_document
        analysis = await _run_blocking(analyze_document, req.document_text)
    except Exception as e:
        _nova_unavailable(e)

    return {
        "analysis":   analysis,
        "char_count": len(req.document_text),
        "nova_model": "amazon.nova-pro-v1:0",
    }


# ── Multimodal pitch-deck image analysis (Nova Lite Vision) ──
@app.post("/api/nova/analyze/image", tags=["Nova AI"])
async def nova_analyze_image(req: NovaImageRequest):
    """
    Analyse a pitch deck slide or any startup-related image using
    Amazon Nova Lite's **multimodal vision** capability.

    Send a base-64 encoded image (JPEG / PNG / WebP) and receive a
    structured VC-style analysis of the visual content.

    This endpoint demonstrates the **Multimodal Understanding** category:
    Nova reads text, charts, product screenshots, and diagrams directly
    from the image.

    **Request body:**
    ```json
    {
      "image_b64": "<base64-encoded-image>",
      "image_media_type": "image/jpeg",
      "extra_context": "This is our traction slide showing MoM growth"
    }
    ```
    """
    if not req.image_b64 or len(req.image_b64) < 100:
        raise HTTPException(
            status_code=400,
            detail="image_b64 is required (base-64 encoded image data)."
        )

    allowed_types = {"image/jpeg", "image/png", "image/gif", "image/webp"}
    media_type = (req.image_media_type or "image/jpeg").lower()
    if media_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported image_media_type '{media_type}'. "
            f"Allowed: {sorted(allowed_types)}"
        )

    try:
        from nova.market import analyze_document_image
        analysis = await _run_blocking(
            analyze_document_image,
            image_b64=req.image_b64,
            image_media_type=media_type,
            extra_context=req.extra_context,
        )
    except Exception as e:
        _nova_unavailable(e)

    return {
        "analysis":        analysis,
        "image_type":      media_type,
        "nova_model":      "amazon.nova-lite-v1:0",
        "capability_used": "multimodal_vision",
    }


# ── Agentic investment research (4-step Nova reasoning chain) ─
@app.post("/api/nova/agent", tags=["Nova AI"])
async def nova_agent(req: NovaAgentRequest):
    """
    Run the **Agentic Investment Research Agent** — a 4-step reasoning
    chain powered entirely by Amazon Nova Pro.

    The agent autonomously:
    1. **Profile Scout** — extracts key signals from startup data + ML result
    2. **Market Researcher** — deep-dives the target market & competitive landscape
    3. **Risk Auditor** — stress-tests business model assumptions
    4. **Investment Strategist** — synthesises all steps into a final thesis

    Each step sees all previous outputs, building a true chain-of-thought.
    Returns a structured `AgentResult` with per-step outputs, timing,
    conviction score, and JSON investment verdict.

    This endpoint demonstrates the **Agentic AI** category.
    """
    data = {k: v for k, v in req.startup.model_dump().items() if v is not None}

    # Get (or reuse) ML prediction
    if req.prediction:
        ml_result = req.prediction
    else:
        ml_result = _safe_predict(data)

    try:
        from nova.agent import run_investment_agent
        agent_result = await _run_blocking(run_investment_agent, data, ml_result)
    except Exception as e:
        _nova_unavailable(e)

    return {
        "prediction":  ml_result,
        "agent":       agent_result.to_dict(),
        "nova_model":  "amazon.nova-pro-v1:0",
        "agent_steps": len(agent_result.steps),
    }


@app.post("/api/nova/investor-brief", tags=["Nova AI"])
async def nova_investor_brief(req: NovaAgentRequest):
    """
    Generate a one-call investor brief for demos and executive reviews.

    The endpoint bundles:
    - ML prediction
    - Agentic verdict and confidence
    - Top 3 risks and opportunities
    - 30-second executive summary
    """
    data = {k: v for k, v in req.startup.model_dump().items() if v is not None}

    # Get (or reuse) ML prediction
    if req.prediction:
        ml_result = req.prediction
    else:
        ml_result = _safe_predict(data)

    try:
        from nova.agent import run_investment_agent
        agent_result = await _run_blocking(run_investment_agent, data, ml_result)
    except Exception as e:
        _nova_unavailable(e)

    opportunities = _extract_bullets(agent_result.market_research, limit=3)
    risks = _extract_bullets(agent_result.risk_audit, limit=3)

    prob_pct = round(float(ml_result.get("probability", 0.0)) * 100, 1)
    model_name = ml_result.get("best_model_name", "ML model")
    decision = agent_result.verdicts.get("invest")
    decision_text = "Invest" if decision is True else "Pass" if decision is False else "Conditional"
    stage = agent_result.verdicts.get("stage", "N/A")

    executive_summary = (
        f"{model_name} predicts {prob_pct}% success probability. "
        f"Agent verdict: {decision_text} (stage: {stage}) with confidence score "
        f"{round(agent_result.final_score, 2)}."
    )

    return {
        "prediction": ml_result,
        "verdict": agent_result.verdicts,
        "agent_confidence": agent_result.final_score,
        "top_opportunities": opportunities,
        "top_risks": risks,
        "executive_summary_30s": executive_summary,
        "investment_thesis": agent_result.investment_thesis,
        "nova_model": "amazon.nova-pro-v1:0",
        "agent_steps": len(agent_result.steps),
    }


# ─────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 50)
    print("  Veritas Backend")
    print("  http://localhost:8000")
    print("  Docs: http://localhost:8000/docs")
    print("=" * 50)
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
