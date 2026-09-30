# Car Dealer Assistant

An LLM-powered car dealer assistant built with Python and Streamlit.

Users can describe a vehicle in natural language, search the available inventory, receive relevant alternatives when an exact vehicle is unavailable, view dealer information, and simulate scheduling a dealer call.

The core design principle is:

> **AI for reasoning. Code for control. Inventory for truth.**

The LLM interprets user intent and ranks alternatives, while Python and the local inventory remain responsible for authoritative vehicle and dealer information.

---

## Features

- Natural-language vehicle search
- LLM-based intent extraction
- Exact inventory matching
- Semantic alternative recommendations
- Preference-based searches such as "electric SUV"
- Recommendations restricted to actual inventory
- Dealer details and contact information
- Simulated dealer call scheduling
- Local fallback when the LLM is unavailable
- Protection against overlapping requests
- Persistent Streamlit session state
- Automated tests for core behavior

---

## Tech Stack

| Area            | Technology    |
| --------------- | ------------- |
| Language        | Python 3.12   |
| UI              | Streamlit     |
| LLM             | Groq API      |
| Data Processing | Pandas        |
| Validation      | Pydantic      |
| Configuration   | python-dotenv |
| Storage         | CSV           |
| Testing         | Pytest        |

The core stack uses widely adopted open-source technologies. The assessment can be developed and demonstrated without dedicated paid infrastructure, using local CSV storage and the available free usage option for the LLM service.

---

## Architecture

User
  |
  v
Streamlit UI (app.py)
  |
  v
Search Orchestration (search.py)
  |
  +-------------------+
  |                   |
  v                   v
LLM Layer         Local Fallback
(llm.py)          Matching
  |                   |
  +---------+---------+
            |
            v
       Data Layer
       (data.py)
            |
      +-----+------+
      |            |
      v            v
   car.csv     dealer.csv
      |
      v
Validated Results
      |
      v
Dealer Details / Schedule Call

### Why this architecture?

The LLM is useful for understanding flexible requests.

However, the LLM is not treated as the inventory database.

The responsibilities are intentionally separated:

**LLM**

- Understand natural language
- Extract make/model/variant/preferences
- Rank relevant alternatives

**Python**

- Search inventory
- Validate recommendations
- Control workflow
- Handle failures
- Manage dealer interactions

**CSV inventory**

- Define which vehicles exist
- Store vehicle details and prices
- Maintain dealer relationships

This gives the application AI flexibility without sacrificing inventory integrity.

---

## Project Structure

car-dealer-chatbot/
├── data/
│   ├── car.csv
│   └── dealer.csv
├── src/
│   └── car_chatbot/
│       ├── __init__.py
│       ├── app.py
│       ├── config.py
│       ├── data.py
│       ├── llm.py
│       ├── models.py
│       └── search.py
├── tests/
│   ├── test_data.py
│   └── test_search.py
├── .env.example
├── .gitignore
├── pyproject.toml
└── README.md


The modules separate UI, search orchestration, LLM integration, data access, configuration, and structured models so each responsibility can be tested and changed independently.

---

## How It Works

### 1. Understand the request

The LLM converts natural-language input into structured information such as:

make: Toyota
model: Corolla
variant: optional
preferences: hybrid

Pydantic models validate the structured response.

### 2. Search inventory

For a specific make/model/variant, Python searches `car.csv` directly.

Exact inventory availability is therefore determined by application data, not by the LLM.

### 3. Recommend alternatives

If the requested vehicle is unavailable, the LLM ranks alternatives from the available inventory.

Instead of generating complete vehicles, the LLM returns existing `car_id` values.

Inventory -> LLM -> car_ids -> Python validation -> Results

Python validates every returned ID against `car.csv` before displaying it.

This prevents hallucinated vehicles, prices, variants, or dealer relationships.

### 4. Connect with the dealer

Each vehicle references a `dealer_id`. Once a vehicle is selected, the application retrieves the corresponding dealer from `dealer.csv`.

The user can view dealer details or select a preferred date/time for a simulated dealer call.

No real external booking is created.

---

## Data Design

The project uses two synthetic datasets created for the assessment.

### `car.csv`

Contains:

car_id, make, model, variant, year, price, dealer_id

### `dealer.csv`

Contains:

dealer_id, name, phone, email, city

`dealer_id` creates the relationship between vehicles and dealers.

CSV was intentionally chosen because the assessment uses a small inventory and does not require database infrastructure.

---

## Reliability and Fallback

The LLM is treated as an enhancement rather than a single point of failure.

If the LLM service is temporarily unavailable, the application can perform local inventory-aware matching for recognizable makes, models, and variants.

For semantic recommendations, the application does **not** return random vehicles when the LLM fails. Returning no recommendation is preferable to presenting unrelated inventory.

The application also handles:

- Missing inventory files
- Unavailable vehicles
- No suitable alternatives
- Unclear requests
- Missing dealer information
- LLM/API failures

Technical errors are logged while users receive readable feedback.

---

## Key Design Decisions & Trade-offs

### CSV instead of a database

**Why:** Lightweight, transparent, easy to review, and appropriate for the assessment-sized inventory.

**Evolution:** If inventory size or concurrency increases, `data.py` can be backed by PostgreSQL or a dealer inventory API without redesigning the search workflow.

### Streamlit instead of separate frontend/backend

**Why:** Provides an interactive end-to-end application with minimal frontend complexity and fast development.

**Evolution:** A production version could expose the backend through FastAPI and use a dedicated web/mobile frontend.

### LLM + deterministic search

**Why:** LLMs are valuable for understanding flexible language, while deterministic Python filtering is more reliable for exact inventory lookup.

This provides semantic flexibility while keeping authoritative operations predictable.

### Inventory IDs instead of LLM-generated vehicles

**Why:** The LLM returns existing `car_id` values rather than generating complete vehicle records.

This prevents incorrect prices, variants, or dealer information from being introduced by model generation.

### Direct LLM ranking instead of vector search

**Why:** The current inventory is small enough to rank directly. Adding embeddings and a vector database would add unnecessary complexity.

**Evolution:** At larger scale, structured filtering or vector retrieval could first produce a candidate set before LLM re-ranking.

### Local fallback instead of LLM-only behavior

**Why:** Basic searches should remain usable during temporary LLM/API failures.

The fallback intentionally provides simpler matching and acts as graceful degradation.

---

## Cost-Conscious Design

The solution intentionally minimizes operational overhead.

The core application uses open-source technologies including Python, Streamlit, Pandas, Pydantic, python-dotenv, and Pytest.


The LLM integration can be demonstrated using the provider's available free usage option.

This follows the principle:

> **Use the simplest reliable component that satisfies the current requirement while keeping a clear path for future scale.**

---

## Setup

### Requirements

* Python 3.12
* Groq API key

### 1. Clone the repository

git clone (https://github.com/amnaosaba/car-dealer-chatbot)
cd car-dealer-chatbot

### 2. Create a virtual environment

### 3. Install dependencies

### 4. Configure the API key

Create `.env` using `.env.example`:

GROQ_API_KEY=your_api_key_here

Never commit the real `.env` file.

---

## Run the Application

### Windows CMD

set PYTHONPATH=src
python -m streamlit run src/car_chatbot/app.py

### PowerShell

$env:PYTHONPATH="src"
python -m streamlit run src/car_chatbot/app.py

### macOS/Linux

export PYTHONPATH=src
python -m streamlit run src/car_chatbot/app.py

The application is typically available at:

http://localhost:8501

## Run Tests

python -m pytest -v

Tests cover:

- Inventory loading
- Dealer lookup
- Exact vehicle search
- Request understanding
- Local fallback
- Alternative recommendations
- Recommendation limits
- Inventory ID validation
- Prevention of arbitrary fallback recommendations

LLM behavior is mocked where appropriate so automated tests remain repeatable and do not depend on live API availability or quota.

---

## Web App (React and FastAPI)

The same search also runs as a web app, so it can be deployed on Vercel. Streamlit needs a long running server, which Vercel does not give.

* `app.py` is the entry point Vercel looks for. It loads the FastAPI app from `src/car_chatbot/main.py`.
* `frontend/` is a React app built with Vite. Vercel builds it into `public/` and serves it as static files.
* The API reuses the existing search code. The Streamlit app still works as before.

### Run with Docker

docker compose up --build

Open http://localhost:5173 for the app. Port 8000 is the API only, so `/` there returns Not Found. The API docs are at http://localhost:8000/docs. The key is read from `.env`.

Python packages are installed once when the image is built. Run with `--build` again after changing `pyproject.toml`.

Run the tests in the container:

docker compose exec api python -m pytest

### Run without Docker

pip install -e ".[dev]"
uvicorn app:app --port 8000

In a second terminal:

cd frontend
npm install
npm run dev

Check the frontend with `npm run check` (format, lint, types, build).

### API

Base URL: `/api/v1`

| Method | Endpoint | Payload | Response |
| --- | --- | --- | --- |
| POST | `/cars/search` | `{"message": "Toyota Corolla hybrid"}` | `{"cars": [...], "notices": [...]}` |

* `message` is required, 1 to 500 characters. The frontend uses the same limit.
* Each car has its dealer and `priceInCents`. Prices are whole cents, never floats.
* Extra fields in the request are ignored.
* Errors: 422 invalid payload, 415 when the body is not JSON, 405 wrong method, 503 when the inventory cannot be loaded.

### Limitations

* No rate limiting yet. Every search can call the LLM, so a limit per IP should be added before real traffic. On Vercel it needs a shared store like Redis, because each function instance has its own memory.
* Call scheduling is a demo in the browser only. Nothing is sent to the dealer.

---

## Security

- API credentials are stored in environment variables.
- `.env` is excluded through `.gitignore`.
- `.env.example` documents required configuration without exposing secrets.
- LLM recommendations are validated against actual inventory.
- Generated model output is not treated as authoritative business data.

---

## Assumptions

- Vehicle and dealer data are synthetic and created for this assessment.
- `car.csv` represents currently available inventory.
- Only vehicles present in inventory can be displayed.
- Alternative recommendations must reference existing inventory.
- Call scheduling is simulated only.
- No external booking, CRM, or payment system is contacted.
- The inventory is intentionally small enough for direct local processing.

---

## Production Evolution

The current architecture is intentionally lightweight, but its modular structure allows individual components to evolve:

| Current            | Production Evolution           |
| ------------------ | ------------------------------ |
| CSV                | PostgreSQL / Inventory API     |
| Streamlit          | Web/Mobile UI + FastAPI        |
| Session state      | Redis / Persistent storage     |
| Direct LLM ranking | Retrieval + LLM re-ranking     |
| Local dealer data  | Dealer / CRM API               |
| Simulated calls    | Calendar / Booking API         |
| Local execution    | Containerized cloud deployment |

Additional capabilities such as authentication, caching, observability, rate limiting, CI/CD, and asynchronous processing can be introduced when real scale or business requirements justify them.

---

> **AI for reasoning. Code for control. Inventory for truth.**