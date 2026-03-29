# Compliance Guardian

Automated video compliance screening powered by TwelveLabs Marengo 3.0 and Pegasus 1.2.

Built for the TwelveLabs Video Intelligence for Media & Entertainment Hackathon (March 28-29, 2026).

## Architecture

4-stage pipeline:

1. **Video Ingest** - Upload via URL or file, indexed by TwelveLabs (Marengo 3.0 + Pegasus 1.2)
2. **Rule Definition** - Natural language compliance rules with severity levels
3. **Analysis Engine** - Dual-model scan: Marengo semantic search + Pegasus reasoned analysis, merged and deduplicated
4. **Results Dashboard** - Timeline visualization, violation cards, JSON export for audit trail

## Setup

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your TwelveLabs API key
```

## Run

```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
# Open http://localhost:8000
```

## API Endpoints

| Method | Path                   | Description                                 |
| ------ | ---------------------- | ------------------------------------------- |
| GET    | /api/health            | Health check + TwelveLabs connection status |
| POST   | /api/ingest            | Upload video by URL or file                 |
| GET    | /api/rules             | Get current compliance rules                |
| POST   | /api/rules             | Set compliance rules                        |
| POST   | /api/analyze           | Run compliance scan against rules           |
| GET    | /api/results/{scan_id} | Retrieve scan results                       |

## Tech Stack

- Backend: Python 3.14+, FastAPI, Pydantic
- Frontend: HTML, Tailwind CSS, Vanilla JS
- AI: TwelveLabs Marengo 3.0 (Search/Embed), Pegasus 1.2 (Analyze)
- Infrastructure: AWS Bedrock (optional inference pathway)

## Author

Tony Gallo - Founder & Principal Architect, Industry Frequency LLC
