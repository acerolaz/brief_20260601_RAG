# brief_20260601 — LangChain RAG Application

A production-ready **Hexagonal Architecture (Ports & Adapters)** LangChain application for Retrieval-Augmented Generation (RAG). Implements LCEL chains, semantic search, tool calling, and structured ingestion pipelines.

---

## 🏗️ Architecture

The project strictly follows **Hexagonal Architecture** principles:

```
┌─────────────────────────────────────────────────────────────────┐
│                        FastAPI HTTP Layer                       │
│                  (Driving Adapters)                             │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                   Application Core (Use Cases)                  │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────┐  │
│  │ IngestStructured │  │ IngestFreshness  │  │QueryAssistant│  │
│  └──────────────────┘  └──────────────────┘  └──────────────┘  │
│                                                                   │
│  Inbound Ports (Driving)  ────  Outbound Ports (Driven)         │
│  ┌─────────────────────┐  ┌──────────────────────┐             │
│  │ Use Case Contracts  │  │ Port Abstractions    │             │
│  └─────────────────────┘  ├──────────────────────┤             │
│                           │ VectorStorePort      │             │
│ Domain Entities           │ AIAssistantPort      │             │
│ ─────────────────         │ DocumentSplitterPort │             │
│ • Chunk                   │ SignalStorePort      │             │
│ • Signal                  │ ScraperPort          │             │
│ • Document                └──────────────────────┘             │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                Infrastructure Layer (Adapters)                  │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────┐  │
│  │PgVectorStore     │  │OpenAIAssistant   │  │HTTPxScraper  │  │
│  │(VectorStorePort) │  │(AIAssistantPort) │  │(ScraperPort) │  │
│  └──────────────────┘  └──────────────────┘  └──────────────┘  │
│                                                                   │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────┐  │
│  │TextSplitterAdapt │  │InMemorySignalStor│  │FastAPI       │  │
│  │(DocumentSplitter │  │(SignalStorePort) │  │Controllers   │  │
│  │Port)             │  │                  │  │              │  │
│  └──────────────────┘  └──────────────────┘  └──────────────┘  │
│                                                                   │
│  LangChain Utilities:                                            │
│  ├── LCEL Chains (RAG, Summarization)                          │
│  ├── ReAct Agent Factory                                        │
│  ├── Tool Builders                                              │
│  ├── Retrievers                                                 │
│  ├── Memory Buffers                                             │
│  └── Tracing Callbacks                                          │
└─────────────────────────────────────────────────────────────────┘
                              ↓
           External Systems (PostgreSQL, OpenAI, etc.)
```

---

## 🖥️ Console Interface (Driving Adapter)

The system includes a **console driving adapter** that provides an interactive shell with two modes:

### 1. Query Mode (Fast RAG)

Quick, deterministic question-answering using the RAG pipeline:

```bash
# Start interactive console
python -m src.infrastructure.cli.main

# Select "1" for Query Mode
❓ Question: What is LangChain?

💡 Answer:
LangChain is a framework for developing applications powered by language models...

📚 Sources: doc-001
```

### 2. Agent Mode (Multi-step Reasoning)

Complex reasoning with tool access via ReAct agent:

```
❓ Complex Question: Compare LangChain vs Llama Index for RAG systems

🤖 Agent is thinking...

🎯 Agent Response:
[Agent shows multi-step reasoning, document searches, and final answer]
```

### Usage

```bash
# Interactive console (both query + agent modes available)
python -m src.infrastructure.cli.main

# Direct query (non-interactive)
python -m src.infrastructure.cli.main "What is RAG?"

# Inside console
  1 → Query Mode (fast deterministic answers)
  2 → Agent Mode (complex multi-step reasoning with tools)
  h → Help
  q → Quit / Ctrl+C
```

---

## 📁 Project Structure

```
brief_20260601/
│
├── src/
│   ├── domain/                          ← CORE: Pure business logic (zero deps)
│   │   ├── entities.py                    Chunk, Document, Signal
│   │   └── exceptions.py                  Domain error types
│   │
│   ├── application/                     ← CORE: Use cases & ports only
│   │   ├── dtos.py                        Inbound/outbound data shapes
│   │   ├── ports/
│   │   │   ├── inbound.py                 Driving ports (use-case contracts)
│   │   │   └── outbound.py                Driven ports (adapter interfaces)
│   │   └── use_cases/
│   │       ├── ingest_structured.py       Split → embed → store documents
│   │       ├── ingest_freshness.py        Validate & persist signals (RSS/webhooks)
│   │       └── query_assistant.py         RAG: retrieve → context → generate
│   │
│   └── infrastructure/                  ← PERIPHERY: Frameworks & I/O
│       ├── adapters/                      Concrete port implementations
│       │   ├── pgvector_store.py            PostgreSQL + pgvector vector DB
│       │   ├── openai_assistant.py          OpenAI chat + LCEL chains
│       │   ├── httpx_scraper.py             URL fetching & parsing
│       │   └── in_memory_signal_store.py    Signal persistence (in-process)
│       │
│       ├── langchain/                      LangChain-specific utilities
│       │   ├── chains/                      LCEL chain builders
│       │   │   ├── rag_chain.py               Retriever → context → LLM
│       │   │   └── summary_chain.py           Text summarization chain
│       │   ├── agents/                       ReAct agent factory
│       │   ├── tools/                        Typed tool adapters
│       │   ├── retrievers/                   Vectorstore wrapper
│       │   ├── memory/                       Conversation buffer
│       │   ├── splitters/                    Text splitting adapter
│       │   └── callbacks/                    LangSmith tracing
│       │
│       ├── api/                             FastAPI HTTP layer
│       │   ├── schemas.py                    Pydantic HTTP models
│       │   ├── main.py                       FastAPI app & routers
│       │   └── controllers/                  Endpoint handlers
│       │       ├── structured_ingestion.py   POST /api/v1/ingest/structured/
│       │       └── freshness_ingestion.py    POST /api/v1/ingest/freshness/
│       │
│       ├── console/                          Console driving adapter
│       │   └── __init__.py                    Interactive shell with Query + Agent modes
│       │
│       ├── cli/                             Legacy console interface
│       │   └── main.py                       CLI entry point
│       │
│       └── config/                          Settings & DI
│           ├── settings.py                   Pydantic settings loader
│           ├── container.py                  Composition root (wiring)
│           └── init_db.py                    DB schema initialization
│
├── prompts/                                Canonical prompt templates
│   ├── loader.py                           Safe template loader
│   ├── rag_system.txt                       RAG system prompt
│   └── summary_system.txt                   Summarization prompt
│
├── tests/                                  Full test coverage
│   ├── conftest.py                         Global fixtures (mocks)
│   ├── unit/                                Isolated domain + app tests
│   │   ├── test_query_assistant.py
│   │   ├── test_ingest_structured.py
│   │   ├── test_ingest_freshness.py
│   │   ├── test_text_splitter.py
│   │   └── test_signal_store.py
│   └── acceptance/                          Black-box API contract tests
│       └── test_api_contracts.py
│
├── data/                                   Raw documents (ignored in git)
│
├── .env.example                            Environment template
├── .gitignore                              Git ignore rules
├── requirements.txt                        Python dependencies
├── pyproject.toml                          Build metadata
├── Dockerfile                              Multi-stage container build
├── docker-compose.yml                      Local stack orchestration
├── Makefile                                Automation tasks
└── README.md                               This file
```

---

## 🚀 Quick Start

### 1. Clone & Setup

```bash
# Create and activate venv
python -m venv .venv && source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy configuration
cp .env.example .env
```

### 2. Set Environment Variables

Edit `.env` and add:

```bash
OPENAI_API_KEY=sk-...your-key-here...
POSTGRES_SERVER=db                   # Using docker-compose
POSTGRES_USER=postgres
POSTGRES_PASSWORD=secure_dev_password_2026
```

### 3. Run with Docker Compose

```bash
# Build & start services (PostgreSQL + pgvector + API)
make build
make up

# Initialize database
make init-db

# Verify health
curl http://localhost:8000/health
```

### 4. Test Locally

```bash
# Run all tests (mocked, no API keys needed)
make test

# Or individually
make test-unit          # Fast unit tests only
make test-acceptance    # API contract tests
```

---

## 📋 API Endpoints

The system exposes three **driving adapters**:

### 1. HTTP/REST (FastAPI)

For integrations, web frontends, and microservices:

```bash
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is RAG?"}'
```

### 2. Console Interface (Interactive Shell)

For development, testing, and direct interaction:

```bash
python -m src.infrastructure.cli.main

# With modes: Query (fast RAG) and Agent (multi-step reasoning)
```

### 3. Programmatic (Python directly)

For embedded usage and scripting:

```python
from src.infrastructure.config.container import get_query_assistant_use_case
from src.application.dtos import QueryRequest
import asyncio

async def main():
    use_case = get_query_assistant_use_case()
    response = await use_case.execute(
        QueryRequest(question="What is LangChain?")
    )
    print(response.answer)

asyncio.run(main())
```

---

## 📋 REST Endpoints

### Ingest a Structured Document

```bash
POST /api/v1/ingest/structured/
Content-Type: application/json

{
  "document_id": "doc-001",
  "title": "LangChain Guide",
  "content": "LangChain is a framework...",
  "source_url": "https://docs.langchain.dev",
  "metadata": {"author": "Acme Corp"}
}

# Response: 201 CREATED
{
  "document_id": "doc-001",
  "chunks_stored": 5
}
```

### Ingest a Freshness Signal (Webhook / RSS)

```bash
POST /api/v1/ingest/freshness/
Content-Type: application/json

{
  "signal_id": "sig-001",
  "signal_type": "rss",
  "topic": "LangChain 0.3 release",
  "payload": {"url": "https://example.com/feed"}
}

# Response: 202 ACCEPTED
{
  "signal_id": "sig-001",
  "acknowledged": true
}
```

### Query the RAG Assistant

```bash
POST /api/v1/query
Content-Type: application/json

{
  "question": "What is LangChain?",
  "top_k": 4
}

# Response: 200 OK
{
  "answer": "LangChain is a framework for developing...",
  "source_ids": ["doc-001"]
}
```

---

## 🔧 Development

### Run Linter & Formatter

```bash
make format    # Auto-format with Ruff
make lint      # Check with Ruff
```

### Full Quality Pipeline

```bash
make check     # format + lint + test all in one
```

### Troubleshooting

**Port already in use:**
```bash
# Kill existing containers
make down
# Restart
make up
```

**Database not initializing:**
```bash
# Manually run init
make init-db
```

**Tests failing with import errors:**
```bash
# Ensure .env is copied
cp .env.example .env
# Reinstall deps
pip install -r requirements.txt
```

---

## 🎯 Design Principles

### 1. Hexagonal Architecture

- **Domain layer** (pure): `Chunk`, `Signal`, `Document` entities + exceptions
- **Application layer**: Three use-case interactors + dry ports
- **Infrastructure layer**: Concrete adapters + FastAPI HTTP + LangChain utilities

**Rule**: The application core never imports from infrastructure. Data flows inward via inbound ports, outward via outbound ports.

### 2. Composition Root (`container.py`)

All concrete adapters are instantiated **only** in the composition root. This is the single place where the dependency graph is wired:

```python
def get_query_assistant_use_case() -> QueryAssistantInteractor:
    return QueryAssistantInteractor(
        vector_store=_vector_store(),      # PgVectorStoreAdapter
        ai_assistant=_ai_assistant(),      # OpenAIAssistantAdapter
    )
```

### 3. Prompts as Canonical Files

Prompts are stored as `.txt` files under `prompts/` and loaded via `load_prompt()`. This keeps prompt logic decoupled from Python code and enables versioning via CHANGELOG.

### 4. LCEL Chains for Determinism

LCEL (LangChain Expression Language) composes components declaratively:

```python
chain = {
    "context": retriever | RunnableLambda(_format_docs),
    "question": RunnablePassthrough(),
} | prompt | llm | StrOutputParser()
```

Use chains for RAG, summarization, and other deterministic workflows. Use **agents** only when dynamic tool selection is needed.

### 5. Async by Default

All I/O (database, LLM, HTTP) is async to prevent blocking the event loop:

```python
async def execute(self, request: QueryRequest) -> QueryResponse:
    chunks = await self._vector_store.similarity_search(...)
    answer = await self._ai_assistant.answer(...)
```

### 6. Stateless by Design

Memory is opt-in and stored externally. The `ConversationBuffer` is in-process but marked as test-only; replace with PostgreSQL for production.

### 7. Tracing & Observability

LangSmith integration is automatic via environment variables:

```bash
LANGCHAIN_TRACING_V2=true
LANGSMITH_API_KEY=ls__...
```

Custom latency metrics are provided via `LatencyLoggerCallback`.

---

## 📦 Dependencies

| Category | Package | Purpose |
|---|---|---|
| **LangChain** | `langchain`, `langchain-core`, `langchain-openai`, `langchain-postgres`, `langchain-text-splitters` | RAG framework, LLM integrations, vector DB |
| **API** | `fastapi`, `uvicorn` | HTTP server & routing |
| **Database** | `asyncpg`, `pgvector`, `sqlalchemy[asyncio]` | PostgreSQL async driver + vector ops |
| **Scraping** | `httpx`, `beautifulsoup4` | URL fetching & HTML parsing |
| **Config** | `pydantic`, `pydantic-settings`, `python-dotenv` | Settings & validation |
| **Testing** | `pytest`, `pytest-asyncio`, `pytest-mock` | Unit + acceptance tests |

---

## 🔐 Environment Variables

```env
# App
APP_ENV=development
DEBUG=true
PROJECT_NAME=Tech Watch RAG Agent
API_V1_STR=/api/v1
LOG_LEVEL=INFO

# PostgreSQL + pgvector
POSTGRES_SERVER=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=secure_dev_password_2026
POSTGRES_DB=tech_watch_rag

# OpenAI
OPENAI_API_KEY=sk-...
EMBEDDING_MODEL=text-embedding-3-small
LLM_MODEL=gpt-4o

# LangSmith (optional)
LANGCHAIN_TRACING_V2=false
LANGSMITH_API_KEY=
LANGSMITH_PROJECT=tech_watch_rag

# Scraper
SCRAPER_TIMEOUT_SECONDS=15
```

---

## 🧪 Testing

All tests are **mocked** — no API keys or database required:

```bash
# Unit tests (fast, isolated)
pytest tests/unit/ -v

# Acceptance tests (API contracts)
pytest tests/acceptance/ -v

# Coverage report
pytest --cov=src --cov-report=term-missing
```

---

## 📚 References

- [LangChain Docs](https://python.langchain.com/)
- [LCEL Guide](https://python.langchain.com/docs/expression_language/)
- [Hexagonal Architecture](https://en.wikipedia.org/wiki/Hexagonal_architecture_(software))
- [pgvector](https://github.com/pgvector/pgvector-python)
- [Semantic Chunking](https://python.langchain.com/docs/modules/data_connection/document_loaders/split_chain_markdown/)

---

## 📝 License

MIT — See LICENSE file


