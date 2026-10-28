# pdf-semantic-api

A small API that ingests PDFs, chunks and embeds their text with a local
Ollama model, stores the result in Postgres/pgvector, and answers natural
language queries over the ingested documents with a retrieval-augmented
answer.

This is a coding-challenge submission: a proof of concept, not a
production-grade service. It is scoped to demonstrate the ingest/embed/store/
retrieve pipeline end to end, not to survive production traffic. The
"Design decisions" section below is deliberate about where corners were cut
and what the production version of each corner would look like.

## Stack

- FastAPI (`fastapi[standard]`, so `uvicorn` ships with it)
- SQLAlchemy 2.0 against Postgres via `psycopg[binary]`
- pgvector for the embedding column and similarity search
- A local Ollama instance for both embeddings and chat completion
- Python 3.14, managed with `uv`

## Prerequisites

- Docker and Docker Compose
- `uv`
- Python >= 3.14 (pinned in `pyproject.toml`)
- A running Ollama instance with an embedding model and a chat model pulled,
  e.g. `qwen3-embedding:0.6b` and `qwen3.5:4b`

## Setup

### 1. Start the database

```
docker compose up -d --wait
```

This brings up a `pgvector/pgvector:pg18` container (service `db`) and waits
for its healthcheck. The database is published on host port `55432`, not the
usual `5432` — deliberately, so it doesn't collide with a local Postgres
install (see the comment in `compose.yaml`).

Credentials and database name are `pdf` / `pdf` / `pdf_semantic`.

To tear everything down, including the volume:

```
docker compose down -v
```

### 2. Configure the app

Copy `.env.example` to `.env` and fill it in:

```
cp .env.example .env
```

```
DATABASE_URL='postgresql+psycopg://pdf:pdf@localhost:55432/pdf_semantic'
```

A few things worth knowing before you fill the rest in:

- `OLLAMA_CHAT_MODEL` is required and has no default. Both model keys ship
  commented out in `.env.example`; uncomment and set the chat model, or the
  app fails at import with a pydantic validation error.
- `OLLAMA_EMBED_MODEL` has a default (`qwen3-embedding:0.6b`) and may stay
  commented out.
- An empty value is not the same as an unset one: `OLLAMA_EMBED_MODEL=` sets
  the empty string and overrides the default. Both fields declare
  `min_length=1`, so an empty value fails at startup rather than at the first
  Ollama call.
- `HOST` and `PORT` exist in `.env.example` and in `Settings`, but nothing in
  the app currently reads them. `uvicorn` takes host and port on the command
  line instead. Don't expect setting them in `.env` to do anything.
- `EMBED_BATCH_SIZE` controls how many chunks go into one `/api/embed`
  request. It defaults to `32` and ships commented out in `.env.example`,
  since the default is usable as-is. Lower it if the Ollama host is slow or
  memory-tight.

`EMBEDDING_DIMENSIONS` must match the embedding model's output — it's `1024`,
which matches `qwen3-embedding:0.6b`. Change the model without changing this
value and `embed_text` raises a `ValueError` rather than silently storing the
wrong shape.

### 3. Install dependencies and create the schema

```
uv sync
uv run init-db
```

`init-db` is a console script (see `[project.scripts]` in `pyproject.toml`)
that runs `CREATE EXTENSION IF NOT EXISTS vector` and then
`Base.metadata.create_all`. It works from any directory because the project
installs as a package via the hatchling build backend. `python -m app.init_db`
also works, from the repo root.

### 4. Run the API

```
uv run uvicorn app.main:app --reload
```

Interactive docs: `/docs`. ReDoc: `/redoc`. Raw schema: `/openapi.json`.

## Endpoints

Both are mounted with no URL prefix, via `app/api/router.py`.

### `POST /ingest_pdf`

Multipart upload. The form field name is `u_file`.

Extracts text per page, splits it into overlapping chunks, embeds each chunk
with the configured Ollama embedding model, and persists the document and its
chunks (with their embeddings) to Postgres.

Returns an `IngestResponse`:

| field          | type     | notes                                  |
|----------------|----------|-----------------------------------------|
| `document_id`  | UUID     |                                          |
| `file_name`    | string   |                                          |
| `page_count`   | int      | pages in the PDF, including any the text extractor found nothing on |
| `chunk_count`  | int      | number of chunks the document was split into |
| `created_at`   | datetime |                                          |

On a scanned or image-only document, `chunk_count` can be small relative to
`page_count` — those pages are counted but contribute no chunks.

On failure, returns an `ErrorResponse` (`{"detail": "..."}`) with status
400, 422, or 500.

### `POST /search_pdf`

JSON body, a `SearchRequest`:

| field              | type         | notes                                  |
|--------------------|--------------|------------------------------------------|
| `query`            | string       | required, 1-4000 characters              |
| `document_id`      | UUID or null | optional, restricts the search to one document |
| `top_k`            | int          | default 5, 1-25                          |
| `generate_answer`  | bool         | default true                             |
| `temperature`      | float or null | optional, 0-1; omit to use the configured `TEMPERATURE` setting (default `0.1`) |

Runs a similarity search over the stored chunk embeddings (filtered to
`document_id` if given), and, if `generate_answer` is true, feeds the
retrieved chunks to the Ollama chat model to produce an answer.

Returns a `SearchResponse`:

| field     | type               | notes                                    |
|-----------|--------------------|---------------------------------------------|
| `matches` | list of `SearchMatch` |                                           |
| `answer`  | string or null     | present only when `generate_answer` is true |

Each `SearchMatch`:

| field          | type         | notes                                  |
|----------------|--------------|------------------------------------------|
| `document_id`  | UUID         |                                          |
| `file_name`    | string       |                                          |
| `page`         | int or null  | 1-based                                 |
| `chunk_index`  | int          |                                          |
| `text`         | string       |                                          |
| `score`        | float        | -1 to 1 (cosine similarity; 1 is identical) |

## Trying it out

These are POSIX-shell `curl` commands. They work as written in bash/zsh, and
also in PowerShell 7, where `curl` resolves to a real `curl.exe`. In the older
Windows PowerShell 5.1, `curl` is an alias for `Invoke-WebRequest`, and `-H`
won't bind there — use the native equivalent instead:

```
$r = Invoke-RestMethod -Uri http://localhost:8000/search_pdf -Method Post `
  -ContentType 'application/json' `
  -Body '{"query": "What does the warranty cover?", "generate_answer": false}'
$r.matches.Count
```

or skip the shell entirely and drive the endpoints from `/docs`.

Ingest a PDF. `test_data/` is gitignored, so drop your own PDF there first:

```
curl -X POST http://localhost:8000/ingest_pdf -F "u_file=@test_data/example.pdf"
```

The `document_id` in the response is what the search examples below reuse.

Search with a generated answer (the default):

```
curl -X POST http://localhost:8000/search_pdf -H "Content-Type: application/json" -d '{"query": "What does the warranty cover?", "top_k": 5}'
```

Retrieval only, no generation — faster, and useful for inspecting what
retrieval actually returned:

```
curl -X POST http://localhost:8000/search_pdf -H "Content-Type: application/json" -d '{"query": "What does the warranty cover?", "generate_answer": false}'
```

Scoped to one document, using the `document_id` from the ingest response:

```
curl -X POST http://localhost:8000/search_pdf -H "Content-Type: application/json" -d '{"query": "What does the warranty cover?", "document_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6"}'
```

Replace that UUID with the `document_id` from your own ingest response. Left
as-is, it matches no document, so the request succeeds with an empty
`matches` list rather than an error.

Overriding the temperature for one request — omit the field to use the
configured `TEMPERATURE` setting instead:

```
curl -X POST http://localhost:8000/search_pdf -H "Content-Type: application/json" -d '{"query": "What does the warranty cover?", "temperature": 0.7}'
```

See the field tables under "Endpoints" above for the full request and
response shapes.

## Project layout

```
app/
  api/          routers — ingest_pdf, search_pdf
  client/       Ollama HTTP client (embed, chat, async variants)
  models/       SQLAlchemy models — Document, Chunk
  processing/   PDF text extraction, chunking, embedding
  schemas/      Pydantic request/response models
  config.py     pydantic-settings configuration, loaded from .env
  db.py         engine, session factory, session_scope
  init_db.py    schema creation (console script: init-db)
  main.py       FastAPI app factory
```

## Design decisions

This is the part a reviewer should read closely — each choice below trades
something for simplicity, and the tradeoff is named rather than hidden.

- **`Base.metadata.create_all` instead of migrations.** For production I
  would use Alembic to manage schema changes. `create_all` is fine for a
  PoC where the schema is created once and never evolved in place.

- **No health or metrics endpoints, no error-handling middleware.** A
  production-ready app would have both; this one doesn't, to keep the
  surface area small.

- **pgvector rather than a dedicated vector store** (Qdrant, Weaviate,
  Pinecone). One datastore handles both relational metadata and embeddings,
  so there's no second system to run and keep in sync. The tradeoff is less
  specialised indexing than a purpose-built vector store offers.

- **Local Ollama rather than a hosted embedding/chat API.** No API keys, no
  per-token cost, and documents never leave the machine. The tradeoff is
  throughput, and the model being whatever the machine can run.

- **A single cached `OllamaClient`**, built with `@lru_cache` and injected
  via FastAPI's `Depends`. `OllamaClient.__init__` opens `httpx` connection
  pools (sync and async), so creating a new instance per request would leak
  sockets.

- **Chunking at 1000 characters with 200 characters of overlap**, both
  configurable via `.env`. The overlap exists so an answer spanning a chunk
  boundary is still retrievable from at least one chunk.

- **Synchronous embedding calls, batched at `EMBED_BATCH_SIZE` chunks per
  request.** This keeps one large document from turning into one unbounded
  `/api/embed` call, but there's still no retry or backoff. `OllamaClient`
  has async variants (`async_embed`, `async_chat`) that remain unused by the
  current routes. Production would still want retries with backoff and
  per-call timeouts.

- **No authentication, no rate limiting, no request-size cap on uploads.**

- **The non-default compose port, `55432`.** Chosen so the container never
  collides with a local Postgres install on the usual `5432`.

One detail for anyone editing `compose.yaml`: the `pgvector/pgvector:pg18`
image's volume mounts at `/var/lib/postgresql`, not
`/var/lib/postgresql/data` — Postgres 18 changed the data directory layout
from earlier images.

## What's not here

No test suite, no CI, no Alembic migrations, no health or metrics endpoints.

Tests would be necessary for any production-grade system. This is scoped to
demonstrate the concept and the ingestion/retrieval flow on a local machine,
where a suite would be overkill. The same goes for the rest of the list —
these are the production gaps named above, not oversights discovered later.
