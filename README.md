# Compliance Guardian

**Automated Video Compliance Screening powered by TwelveLabs Marengo 3.0 + Pegasus 1.2**

Built by Tony Gallo, Industry Frequency LLC | TwelveLabs Video Intelligence for M&E Hackathon | March 28-29, 2026

## What It Does

Compliance Guardian scans video content against user-defined compliance rules and produces a timestamped, confidence-ranked violation report with full audit trail. Upload a video, define rules in plain English, get results in under 2 minutes.

**Demo video:** [3-minute walkthrough](YOUR_RECORDING_URL_HERE)

## Quick Start (< 5 minutes)

### Prerequisites
- Python 3.11+
- TwelveLabs API key ([get one here](https://playground.twelvelabs.io))

### Setup

```bash
git clone https://github.com/industryfrequency/compliance-guardian.git
cd compliance-guardian/backend

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# Edit .env and add your TWELVELABS_API_KEY

uvicorn main:app --reload
```

Open `http://localhost:8000` in your browser.

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `TWELVELABS_API_KEY` | Yes | Your TwelveLabs API key |
| `AWS_ACCESS_KEY_ID` | No | For Bedrock production pathway |
| `AWS_SECRET_ACCESS_KEY` | No | For Bedrock production pathway |
| `AWS_REGION` | No | Default: us-west-2 |

## Architecture

See [ARCHITECTURE.md](ARCHITECTURE.md) for the full technical document with diagrams.

### 4-Stage Pipeline

1. **Video Ingest** — Upload via URL or file. Indexes video with dual models (Marengo 3.0 for search, Pegasus 1.2 for analysis).
2. **Rule Definition** — Natural language compliance rules, category-tagged, toggleable. No code required.
3. **Analysis Engine** — Marengo semantic search finds candidate moments. Pegasus analyzes and reasons about each. Custom merger deduplicates overlapping timestamps and labels corroborated violations (flagged by both models).
4. **Results Dashboard** — Timeline visualization with clickable markers, severity ranking, confidence scores, model reasoning, and JSON export for audit trail.

### Tech Stack

- **Backend:** Python 3.14, FastAPI, Pydantic, uvicorn
- **Frontend:** HTML5, Tailwind CSS, vanilla JavaScript, Lucide Icons
- **AI Models:** TwelveLabs Marengo 3.0 (Search/Embed), Pegasus 1.2 (Analyze)
- **Infrastructure:** TwelveLabs SaaS API (prototype), AWS Bedrock (production pathway)
- **Test Content:** LTX Studio 2.3 (synthetic compliance test video generation)

### Integration Approach: TwelveLabs + AWS Bedrock

The prototype uses TwelveLabs SaaS API directly for rapid development. Both Marengo and Pegasus models are also available via AWS Bedrock `invoke_model()`, which provides:
- Centralized guardrails and content filtering
- Cost management across multiple models
- Enterprise security and compliance (SOC2, HIPAA)
- Multi-model routing (switch between Claude, Marengo, Pegasus via single API)

In production, the Bedrock pathway replaces direct SaaS calls with zero code changes to the analysis engine — only the service layer swaps.

## Performance Benchmarks

| Metric | Value | Notes |
|--------|-------|-------|
| Ingest + Index (20s video) | ~45 seconds | Includes upload, dual-model indexing |
| Compliance Scan (4 rules) | ~14.6 seconds | Marengo search + Pegasus analysis per rule |
| Total violations detected | 30 | LTX-generated festival scene, all 4 rules |
| End-to-end (ingest + scan) | ~60 seconds | For a 20-second video |
| Projected: 10-min video | ~2 minutes scan | Based on API latency scaling |

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/ingest` | Upload video by URL or file |
| GET | `/api/rules` | Get current compliance rules |
| POST | `/api/rules` | Update compliance rules |
| POST | `/api/analyze` | Run compliance scan |
| GET | `/api/results/{scan_id}` | Retrieve scan results |
| GET | `/api/health` | System health check |

## Compliance Rules (Default Set)

| Category | Rule |
|----------|------|
| Substance | Flag any frame containing visible alcohol branding or consumption |
| Violence | Flag physical violence, aggressive contact, or dangerous crowd behavior |
| Adult | Flag nudity, sexually suggestive content, or inappropriate exposure |
| Brand Safety | Flag visible brand logos appearing within 3 seconds of dangerous or illegal activity |

Rules are fully customizable via the UI. Add, remove, edit, or toggle any rule without code changes.

## Project Structure

```
compliance-guardian/
├── backend/
│   ├── main.py              # FastAPI app, CORS, static files
│   ├── config.py            # Pydantic settings, env loading
│   ├── models.py            # All Pydantic schemas
│   ├── requirements.txt     # Python dependencies
│   ├── routes/
│   │   ├── ingest.py        # Video upload + indexing
│   │   ├── rules.py         # CRUD for compliance rules
│   │   ├── analyze.py       # Run compliance scan
│   │   └── results.py       # Retrieve scan results
│   └── services/
│       ├── twelvelabs_service.py  # TwelveLabs SDK wrapper
│       ├── analysis_engine.py     # Dual-model orchestration
│       └── result_merger.py       # Dedup + corroboration logic
├── frontend/
│   └── index.html           # Single-file dashboard (Tailwind + vanilla JS)
├── ARCHITECTURE.md
└── README.md
```

## Author

**Tony Gallo** — Founder & Principal Architect, Industry Frequency LLC
11+ years enterprise live entertainment production (Live Nation, AEG, Grammy Awards, Super Bowl)
