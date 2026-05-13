# StoreSignal — AI Readiness Intelligence for Shopify

## Problem
AI shopping agents (ChatGPT, Google AI Mode) now recommend products
directly. Merchants have zero visibility into how these agents
perceive their store — or why they get skipped.

## Solution
StoreSignal simulates AI buyer personas against your store data,
measures where agents fail, and generates optimised rewrites.

## What it does
- Runs 12 AI-simulated buyer questions across 4 personas
- Detects hallucinations and low-confidence answers
- Measures answer drift (same question, different phrasings)
- Scores store across 5 readiness dimensions
- Generates AI-optimised rewrites for every gap found

## Tech stack
- Backend: FastAPI + Python
- AI simulation: Groq (Llama 3.3 70B)
- Frontend: React + Recharts
- Data: Shopify Admin API (mock data for demo)

## Setup
```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# Frontend
cd frontend
npm install
npm start
```

## Team
- Person A — AI simulation engine, drift detection, scoring
- Person B — Data pipeline, FastAPI server, React dashboard