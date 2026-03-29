# Compliance Guardian — Technical Architecture

## System Overview

Compliance Guardian is an automated video compliance screening system. It accepts video content, analyzes it against user-defined natural language rules using two complementary AI models, and produces a timestamped violation report with confidence scores, severity rankings, and model reasoning.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                        COMPLIANCE GUARDIAN                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────┐    ┌──────────┐    ┌──────────────┐    ┌──────────┐  │
│  │  VIDEO    │    │  RULE    │    │   ANALYSIS   │    │ RESULTS  │  │
│  │  INGEST   │───▶│  ENGINE  │───▶│    ENGINE    │───▶│DASHBOARD │  │
│  │          │    │          │    │              │    │          │  │
│  │ Upload   │    │ NL Rules │    │ Marengo 3.0  │    │ Timeline │  │
│  │ Index    │    │ Category │    │ Pegasus 1.2  │    │ Detail   │  │
│  │ Store    │    │ Toggle   │    │ Merger       │    │ Export   │  │
│  └──────────┘    └──────────┘    └──────────────┘    └──────────┘  │
│       │                               │                             │
│       ▼                               ▼                             │
│  ┌─────────────────────────────────────────────┐                   │
│  │          TWELVELABS API LAYER               │                   │
│  │                                             │                   │
│  │  ┌─────────────────┐  ┌─────────────────┐  │                   │
│  │  │  MARENGO 3.0    │  │  PEGASUS 1.2    │  │                   │
│  │  │  (Search/Embed) │  │  (Analyze)      │  │                   │
│  │  │                 │  │                 │  │                   │
│  │  │  Semantic clip  │  │  Reasoned JSON  │  │                   │
│  │  │  matching with  │  │  analysis with  │  │                   │
│  │  │  rank scoring   │  │  timestamps     │  │                   │
│  │  └─────────────────┘  └─────────────────┘  │                   │
│  └─────────────────────────────────────────────┘                   │
│                          │                                          │
│              ┌───────────┼───────────┐                             │
│              ▼           ▼           ▼                             │
│  ┌───────────────┐ ┌──────────┐ ┌──────────────┐                  │
│  │ TwelveLabs    │ │   AWS    │ │   NVIDIA     │                  │
│  │ SaaS API      │ │ Bedrock  │ │   NIMs       │                  │
│  │ (Prototype)   │ │ (Prod)   │ │ (Edge)       │                  │
│  └───────────────┘ └──────────┘ └──────────────┘                  │
└─────────────────────────────────────────────────────────────────────┘
```

## Data Flow

### Stage 1: Video Ingest
1. User uploads video via URL or local file through the web interface
2. Backend creates (or reuses) a dual-model index configured for both Marengo 3.0 and Pegasus 1.2
3. Video is uploaded to TwelveLabs via the Tasks API
4. Backend polls task status until indexing completes (status: "ready")
5. Returns `index_id` and `video_id` to the frontend
6. Video loads in the HTML5 player for reference during review

### Stage 2: Rule Definition
1. Default rules cover four categories: substance, violence, adult content, brand safety
2. Rules are plain English strings stored in memory (sufficient for prototype; production would use a database)
3. Users can add, edit, remove, and toggle rules via the UI
4. Each rule has: id, text, category, and enabled flag

### Stage 3: Analysis Engine (Dual-Model Architecture)

For each enabled rule, two parallel analysis passes execute:

**Pass 1: Marengo 3.0 Semantic Search**
- The rule text is used as a search query via `client.search.query()`
- Marengo returns ranked clips with timestamps
- Rank is converted to a confidence proxy: `confidence = 1.0 / rank` (capped at 1.0)
- Each clip becomes a candidate violation with source="search"

**Pass 2: Pegasus 1.2 Reasoned Analysis**
- The rule text is embedded in a compliance auditor prompt sent to `client.analyze()`
- Pegasus returns structured JSON with violations, timestamps, confidence, severity, and reasoning
- Each finding becomes a candidate violation with source="analyze"

**Pass 3: Merge and Deduplicate**
- Violations from both passes are compared for timestamp overlap (2-second tolerance)
- Overlapping violations for the same rule are merged:
  - Timestamp range expands to the union of both
  - Confidence takes the maximum of both
  - Severity escalates if either model flagged "critical"
  - Reasoning is concatenated with a [CORROBORATED] label
  - Source becomes "merged"
- Non-overlapping violations pass through unchanged
- Final list sorted by timestamp, then by confidence descending

### Stage 4: Results Dashboard
- Timeline visualization with color-coded severity markers (red=critical, amber=warning)
- Clicking a marker seeks the video player to that timestamp
- Detail panel shows: severity badge, timestamp range, source model, triggered rule, model reasoning, and confidence bar
- Stats bar: total violations, critical count, warning count, average confidence, scan time
- JSON export produces a complete audit trail

## Integration Approach: TwelveLabs + AWS Bedrock

### Prototype (Current)
The prototype uses TwelveLabs SaaS API directly via the Python SDK (v1.2.1):
- `client.tasks.create()` for video upload and indexing
- `client.search.query()` for Marengo semantic search
- `client.analyze()` for Pegasus reasoned analysis
- `client.indexes.create()` for dual-model index management

This provides the fastest development cycle with built-in index management.

### Production Pathway (AWS Bedrock)
Both TwelveLabs models are available in Amazon Bedrock. The production deployment would route through Bedrock for:
- **Guardrails:** Content filtering and safety controls enforced at the infrastructure level
- **Cost management:** Per-token billing visibility across all models in a single dashboard
- **Multi-model routing:** Same API surface for TwelveLabs, Claude, and other models
- **Enterprise compliance:** SOC2, HIPAA, and data residency requirements met by AWS infrastructure
- **Credential management:** IAM roles replace API keys; temporary session tokens for workshop/production

The service layer (`twelvelabs_service.py`) is designed so swapping to Bedrock requires only changing the client initialization and method calls, not the analysis engine logic.

### Additional Sponsor Integrations (Architecture-Ready)

| Sponsor | Role | Integration Point |
|---------|------|-------------------|
| **NVIDIA NIMs** | Edge pre-processing | Video Search & Summary NIM for real-time stream filtering before deep analysis |
| **LTX Studio** | Test content generation | Synthetic compliance test videos for QA validation of new rule sets |
| **Baseten** | Production model serving | Custom fine-tuned compliance models served with speed/cost/quality optimization |

## Performance Benchmarks

Measured on a 20-second LTX-generated festival scene with 4 compliance rules enabled.

| Metric | Value |
|--------|-------|
| Video upload + indexing | ~45 seconds |
| Marengo search per rule | ~1.5 seconds |
| Pegasus analysis per rule | ~2.5 seconds |
| Merge + dedup | < 100ms |
| Total scan (4 rules) | 14.6 seconds |
| Violations detected | 30 (1 critical, 29 warning) |
| End-to-end latency | ~60 seconds |

### Scalability Discussion
- Indexing is a one-time cost per video; subsequent scans against the same video are search/analyze only
- Rules execute sequentially in the prototype; production would parallelize across rules
- TwelveLabs API rate limits: 8 requests per reset window (observed from response headers)
- At production scale, Bedrock provides auto-scaling and burst capacity
- For real-time use cases, NVIDIA NIMs provide edge inference with sub-second latency on pre-filtered streams

## Production Readiness Considerations

- **Error handling:** All API calls wrapped in try/except with meaningful error messages surfaced to the UI
- **Edge cases:** Empty rule sets rejected with 400; failed indexing returns status to user; malformed video files return TwelveLabs API error
- **Audit trail:** Every violation includes timestamp, confidence, severity, rule reference, model reasoning, and source model — exportable as JSON
- **Security:** API keys loaded from .env, never hardcoded; CORS restricted to known origins
- **Observability:** Server logs indexing status polls, search/analyze errors with query context

## Architectural Decisions and Tradeoffs

| Decision | Rationale |
|----------|-----------|
| TwelveLabs SaaS over Bedrock for prototype | Faster development, built-in index management, no vector DB needed |
| Dual-model (search + analyze) over single model | Cross-validation reduces false positives; corroborated violations are higher confidence |
| Sequential rule execution over parallel | Simpler error handling for prototype; parallel is a production optimization |
| In-memory results store over database | Sufficient for demo; production would use PostgreSQL or DynamoDB |
| Single HTML file over React/Next.js | Zero build step, instant iteration, no framework overhead for a dashboard UI |
| Rank-to-confidence conversion (1/rank) | Marengo 3.0 deprecated score/confidence fields; rank is the only relevance signal |
| 2-second overlap tolerance for merge | Balances catching true corroborations vs. false merges from adjacent but distinct events |
