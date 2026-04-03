# 🚀 SupplyMind AI — Supply Chain Optimization Agent

AI-powered supply chain optimization using Prophet forecasting, LangChain ReAct agent, PostgreSQL, and Streamlit.

---

## Architecture

```
PostgreSQL DB
     ↓
FastAPI Backend
  ├── /inventory   → Stock levels, ROP, days-to-stockout
  ├── /forecast    → Prophet demand forecasting
  ├── /agent       → LangChain ReAct agent (tools: inventory, forecast, ROP/EOQ, RAG, PO)
  ├── /orders      → Purchase orders
  └── /weather     → OpenWeatherMap external signal
     ↓
Streamlit Frontend
  ├── Home         → KPI overview + weather signal + risk alerts
  ├── Dashboard    → Stock charts + sales trend
  ├── Inventory    → Product table + stock update
  ├── Forecast     → Prophet chart with confidence intervals
  ├── Agent Chat   → LangChain ReAct agent interface
  ├── PO Manager   → Purchase orders list
  └── Savings      → Monthly savings report
```

---

## Setup

### 1. PostgreSQL
Create the database:
```sql
CREATE DATABASE supplymind;
```
Update `backend/.env`:
```
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/supplymind
OPENWEATHER_API_KEY=your_key   # optional, works without it
OPENAI_API_KEY=your_key        # optional, falls back to rule-based agent
```

### 2. Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```
The database tables are created and seeded automatically on first startup.

### 3. Frontend
```bash
cd frontend
pip install -r requirements.txt
streamlit run app.py
```

---

## Features
- **Prophet Forecasting** — 365 days of seasonal sales data, 30-day rolling forecast with 80% CI
- **LangChain ReAct Agent** — autonomous tool use: check stock → forecast → ROP/EOQ → risk RAG → generate PO
- **RAG Risk Intelligence** — FAISS + sentence-transformers over supply chain incident corpus
- **ROP/EOQ Engine** — mathematically optimal reorder points and order quantities
- **PostgreSQL** — products, inventory, sales history, suppliers, purchase orders
- **OpenWeatherMap** — external demand signal integration
- **Streamlit Dashboard** — real-time alerts, Plotly charts, savings report
