# FIRE — Freedom Intelligent Routing Engine

> AI-powered customer support ticket routing for financial institutions. Classifies, scores, geocodes, and routes tickets to the optimal manager using a local LLM, deterministic business rules, and geographic proximity — with a natural-language analytics assistant backed by a 120B-parameter model.

---

## Contents

- [System Architecture](#system-architecture)
- [NLP Pipeline](#nlp-pipeline)
- [Priority Scoring](#priority-scoring)
- [Language Detection](#language-detection)
- [Geocoding](#geocoding)
- [Routing Engine](#routing-engine)
- [AI Analytics Assistant](#ai-analytics-assistant)
- [FastMCP Integration](#fastmcp-integration)
- [Data Model](#data-model)
- [Configuration](#configuration)
- [Development](#development)

---

## System Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│  CSV Upload                                                       │
│                                                                   │
│  parse_csv()                                                      │
│      │                                                            │
│      ├─ NLP enrichment  ──── Ollama Gemma 3 (4b/1b)             │
│      │   asyncio.gather()    request_type · sentiment            │
│      │   concurrency=N       summary · next_actions · language    │
│      │                                                            │
│      ├─ Priority scoring ─── Deterministic rule engine           │
│      │                        BASE + SENTIMENT_ADJ + SEGMENT_BONUS│
│      │                                                            │
│      ├─ Geocoding ─────────── 2GIS Catalog API (async, cached)   │
│      │                        lat/lon per ticket address          │
│      │                                                            │
│      └─ Routing ───────────── Haversine → nearest office          │
│                                Competency filter (rule-based)     │
│                                Round-robin load balancing         │
│                                                                   │
└────────────────────────────────┬─────────────────────────────────┘
                                 │
                    PostgreSQL on Render
                    tickets_final_enriched
                                 │
           ┌─────────────────────┼──────────────────────┐
           │                     │                      │
      REST API              Analytics            /api/agent/query/stream
      FastAPI               endpoints            LangGraph ReAct
                                                 openai/gpt-oss-120b
                                                        │
                                                 FastMCP SSE /mcp
                                                 (external MCP clients)
           │
    React + Vite + Tailwind
    Dashboard · Ticket table · AI chat
```

**Stack**

| | |
|---|---|
| Backend | FastAPI, Uvicorn, SQLAlchemy 2.0, psycopg2 |
| Frontend | React 18, Vite, TypeScript, Tailwind CSS |
| Local LLM | Ollama — Gemma 3 4b / 1b |
| Language detection | lingua-language-detector |
| Geocoding | 2GIS Catalog API v3 |
| AI assistant | LangGraph, LangChain, openai/gpt-oss-120b via HuggingFace Router |
| MCP | FastMCP (SSE transport) |
| Database | PostgreSQL (Render) |

---

## NLP Pipeline

Each ticket description is passed to a locally-running **Gemma 3** model via Ollama's OpenAI-compatible API. The LLM produces four fields; priority is intentionally excluded from the prompt and computed separately.

**LLM outputs**

| Field | Domain |
|---|---|
| `request_type` | Жалоба · Смена данных · Консультация · Претензия · Неработоспособность приложения · Мошеннические действия · Спам |
| `sentiment` | Положительная · Нейтральная · Негативная |
| `language` | RU · KZ · ENG |
| `summary` | 1–2 sentence Russian summary |
| `next_actions` | Recommended manager actions (Russian) |

### Parallelism

Requests are dispatched concurrently via `asyncio.gather` behind an `asyncio.Semaphore`. Concurrency is tuned to match Ollama's `OLLAMA_NUM_PARALLEL`:

| `CONCURRENCY` | Target environment |
|---|---|
| 1 | Debug / constrained RAM |
| 2 | 1b model, 8 GB RAM |
| 4 | 4b model, 16 GB RAM |
| 6 | 4b model, 24 GB+ (default) |
| 8 | High-memory workstation |

Both model ID and concurrency are hot-swappable at runtime via `POST /api/settings` without restarting the server.

---

## Priority Scoring

Priority is a deterministic integer in **[1, 10]** derived from three inputs — the two LLM classifications and the segment from the source CSV. No LLM inference is involved.

```
priority = clamp(
    BASE_SCORE[request_type] + SENTIMENT_ADJ[sentiment] + SEGMENT_BONUS[segment],
    1, 10
)
```

**Lookup tables**

| Request type | Base | | Sentiment | Adj | | Segment | Bonus |
|---|---|---|---|---|---|---|---|
| Мошеннические действия | 9 | | Негативная | +2 | | VIP | +2 |
| Неработоспособность приложения | 7 | | Нейтральная | 0 | | Priority | +1 |
| Жалоба | 6 | | Положительная | −1 | | Mass | 0 |
| Смена данных | 5 | | | | | | |
| Претензия | 4 | | | | | | |
| Консультация | 4 | | | | | | |
| Спам | — | | | | | | |

**Hard rules** (applied after clamping)

- `Спам` → `1`, ticket is never assigned to a manager
- `Мошеннические действия` → floor `9`

---

## Language Detection

Built on **lingua-language-detector**, which uses quadrigram/trigram statistics and substantially outperforms `langdetect` on short Cyrillic texts.

**Supported languages:** `RU` · `KZ` · `ENG`

Detection runs in two passes:

1. **Kazakh fast-path** — scans for Kazakh-exclusive Unicode codepoints (`ә ғ қ ң ө ұ ү һ і`) and high-frequency function words. Short-circuits to `KZ` on sufficient signal.
2. **Lingua scoring** — evaluates confidence for Russian and English with asymmetric thresholds: English requires ≥ 0.90 (guarded against Cyrillic text with Latin loanwords); Russian requires ≥ 0.40. Falls back to `RU` if neither threshold is met.

Input is preprocessed: URLs, email prefixes, and extraneous whitespace are stripped before scoring.

---

## Geocoding

Each ticket's structured address (`city`, `street`, `building`) is resolved to `(lat, lon)` via the **2GIS Catalog API v3** (`catalog.api.2gis.com/3.0/items/geocode`).

- **Transport** — `httpx.AsyncClient`, non-blocking
- **Concurrency** — `asyncio.Semaphore(5)`, 20 s timeout per request
- **Caching** — per-session in-memory cache on normalised query strings and city names, eliminating redundant calls for repeated addresses
- **Country resolution** — defaults to `Казахстан` when the country field is absent or ambiguous
- **Locale** — `ru_KZ`

Coordinates feed directly into the haversine routing stage.

---

## Routing Engine

Assignment is a two-stage pipeline executed per ticket after geocoding.

### Stage 1 — Geographic resolution

`geo_filter.resolve_office_by_distance` selects the nearest office using the **Haversine formula**:

```
d = 2R · arcsin( √( sin²(Δφ/2) + cos φ₁ · cos φ₂ · sin²(Δλ/2) ) )   R = 6 371 km
```

If no geocoordinates are available, falls back to city-name matching. If the resolved office yields no eligible managers, `sorted_offices_by_distance` returns all other offices sorted by distance; each is tried in order until a candidate pool is found.

### Stage 2 — Competency filter

`competency_filter.filter_eligible_managers` applies cascading hard rules to the office's manager pool:

| # | Condition | Requirement |
|---|---|---|
| 1 | Segment ∈ {VIP, Priority} **or** priority ≥ 8 | Manager holds `VIP` skill |
| 2 | `request_type = DataChange` | Manager is `ChiefSpecialist` |
| 3 | `language = KZ` | Prefer `KZ`-skilled managers; retain full pool if none qualify (soft fallback) |
| 4 | `language = ENG` | Prefer `ENG`-skilled managers; soft fallback identical to rule 3 |

Rules are applied sequentially; each narrows the candidate set produced by the previous rule.

### Load balancing

```python
candidates.sort(key=lambda m: (m["workload"], m["manager_id"]))
top2   = candidates[:2]
chosen = top2[rr.next_index(office_id) % len(top2)]
chosen["workload"] += 1
```

`RoundRobinState` maintains a per-office binary toggle, alternating between the two lowest-workload candidates on successive calls. This prevents workload collapse onto a single manager under equal-workload conditions.

---

## AI Analytics Assistant

A streaming ReAct agent that answers natural-language questions about the live dataset, backed by **openai/gpt-oss-120b** routed through the HuggingFace Inference Router.

### Tool surface

| Tool | Description |
|---|---|
| `get_stats` | Aggregated counts and distributions (segment, request type, sentiment, language, city, manager, office) |
| `get_tickets(limit)` | Paginated ticket rows — all fields except raw description |
| `filter_tickets(field, value)` | Equality filter on city, country, region, segment, request type, sentiment, language, gender, manager, office |
| `get_priority_breakdown` | Count per priority level 1–10 |
| `get_manager_workloads` | Per-manager ticket count, level, and assigned office |

### Streaming

The `/api/agent/query/stream` endpoint emits **Server-Sent Events** as the agent reasons:

```
{"type": "tool_start",  "name": "get_stats", "args": {}}
{"type": "tool_result", "name": "get_stats", "preview": "312 tickets · avg priority 6.2 · top segment: Mass"}
{"type": "done",        "answer": "...",      "html_artifact": "<html>...</html>" | null}
```

The frontend renders tool calls as a collapsible trace above the final Markdown answer. When the agent determines a chart adds value, it emits a self-contained **Chart.js HTML artifact** rendered in a sandboxed `<iframe>`.

**Model configuration**

| | |
|---|---|
| Model | `openai/gpt-oss-120b` |
| Endpoint | `https://router.huggingface.co/v1` |
| Temperature | `0` |
| Framework | LangGraph `create_react_agent` |

---

## FastMCP Integration

A **FastMCP** server is mounted directly inside the FastAPI process and exposes the same PostgreSQL tool surface to external MCP clients over SSE.

```
GET /mcp/sse
```

Compatible with Claude Desktop, Cursor, and any MCP-compliant client. All five tools listed above are available. Queries execute against `tickets_final_enriched` via SQLAlchemy; no session state is required.

---

## Data Model

### `tickets_final_enriched`

| Column | Type | Source |
|---|---|---|
| `customer_guid` | uuid | CSV |
| `gender` | text | CSV |
| `date_of_birth` | text | CSV |
| `description` | text | CSV |
| `attachments` | text | CSV |
| `client_segment` | text | CSV — VIP / Priority / Mass |
| `country` · `region` · `city` | text | CSV |
| `street` · `building` | text | CSV |
| `lat` · `lon` | float | 2GIS geocoding |
| `request_type` | text | Gemma 3 classification |
| `sentiment` | text | Gemma 3 classification |
| `priority` | int | Deterministic scoring |
| `language` | text | Lingua detection |
| `summary` | text | Gemma 3 generation |
| `next_actions` | text | Gemma 3 generation |
| `assigned_manager_name` | text | Routing engine |
| `assigned_manager_level` | text | Routing engine |
| `assigned_office` | text | Routing engine |
| `assigned_office_address` | text | Routing engine |

---

## Configuration

```env
# backend/.env
DATABASE_URL=postgresql://user:pass@host:5432/db
HF_TOKEN=hf_...
TWOGIIS_API_KEY=...
FRONTEND_ORIGIN=http://localhost:5173
```

---

## Development

**Prerequisites:** Python 3.12+, Node 20+, [Ollama](https://ollama.com)

```bash
# Pull model
ollama pull gemma3:4b

# Start Ollama with parallelism matching CONCURRENCY setting
OLLAMA_NUM_PARALLEL=6 ollama serve
```

```bash
# Backend
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

```bash
# Frontend
cd frontend
npm install
npm run dev
```

Runtime NLP settings:

```bash
curl -X POST http://localhost:8000/api/settings \
  -H "Content-Type: application/json" \
  -d '{"model_id": "gemma3:1b", "concurrency": 2}'
```
