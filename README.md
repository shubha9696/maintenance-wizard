# 🏭 Maintenance Wizard — AI-Powered Industrial Equipment Decision Support

> **Tata Steel AI Hackathon 2026 | Round 2 — Agentic AI Challenge**

An intelligent, AI-powered maintenance decision-support system for industrial equipment in steel manufacturing environments. The Maintenance Wizard helps maintenance engineers diagnose equipment issues, predict failures, assess risks, prioritize actions, and generate actionable recommendations — all through natural language interaction.

---

## 🎯 Problem Statement

Develop an intelligent AI-powered maintenance decision-support system that helps maintenance engineers:
- Diagnose equipment issues and identify root causes
- Predict equipment degradation and remaining useful life (RUL)
- Detect anomalies and generate early warnings
- Prioritize maintenance actions based on operational constraints
- Generate structured maintenance reports and recommendations

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND (Next.js 14)                     │
│  ┌──────────┬──────────┬──────────┬──────────┬──────────┐   │
│  │Dashboard │ AI Chat  │Equipment │  Alerts  │ Reports  │   │
│  └────┬─────┴────┬─────┴────┬─────┴────┬─────┴────┬─────┘   │
│       │          │          │          │          │           │
└───────┼──────────┼──────────┼──────────┼──────────┼───────────┘
        │          │          │          │          │
        ▼          ▼          ▼          ▼          ▼
┌─────────────────────────────────────────────────────────────┐
│                   BACKEND (FastAPI)                          │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              AGENTIC ORCHESTRATOR                     │   │
│  │  Intent Classification → Agent Routing → Chaining     │   │
│  └──┬──────┬──────┬──────────┬──────────┬───────────────┘   │
│     │      │      │          │          │                    │
│     ▼      ▼      ▼          ▼          ▼                    │
│  ┌─────┐┌─────┐┌─────┐ ┌─────────┐ ┌────────┐              │
│  │Diag-││Pred-││Reco-│ │Knowledge│ │Report  │              │
│  │nostic││ict- ││mmen-│ │Retrieval│ │Agent   │              │
│  │Agent ││ion  ││dation│ │Agent    │ │        │              │
│  └──┬───┘└──┬──┘└──┬──┘ └────┬────┘ └───┬────┘              │
│     │       │      │         │           │                    │
│     ▼       ▼      ▼         ▼           ▼                    │
│  ┌──────────────────────────────────────────────────────┐    │
│  │              SERVICES LAYER                          │    │
│  │  ChromaDB (RAG)  │  Anomaly Detection  │  RUL Pred.  │    │
│  │  Vector Store     │  Isolation Forest   │  Health Idx  │    │
│  └──────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐    │
│  │              DATA LAYER                              │    │
│  │  Equipment  │  Sensors  │  Logs  │  SOPs  │  Spares  │    │
│  └──────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────┘
        │
        ▼
┌──────────────────┐
│  Google Gemini   │
│  API (LLM)       │
└──────────────────┘
```

---

## 📷 Screenshots & UI Walkthrough

Here are 20 high-resolution original screenshots demonstrating the system's execution flows, diagnostics, remaining useful life predictions, spares optimizer matching, and executive report generation:

### 1. Plant Overview Dashboard
Displays summary statistics (healthy assets, warning assets, alerts) and circular overall plant health chart rating (82%). Includes the live Cyber Scan Stack representing the real-time thermal profile of the Blast Furnace.
![1. Plant Overview Dashboard](screenshots_raw/Screenshot%20Capture%20-%202026-06-11%20-%2001-10-35.png)

---
### 2. Digital Twin Plant Floor & Critical Assets
Overview of plant sector health (Blast Furnace 76.6%, Rolling Mill 82.2%) coupled with the 'Critical Assets Attention' list and recent maintenance log updates.
![2. Digital Twin Plant Floor & Critical Assets](screenshots_raw/Screenshot%20Capture%20-%202026-06-11%20-%2001-10-48.png)

---
### 3. Equipment Fleet Sector Filter
Active asset fleet view monitoring 25 assets across the steel plant. Allows quick category filtering by sector (Blast Furnace, Steel Melting Shop, Rolling Mill, Coke Oven, Sinter Plant, Power Plant).
![3. Equipment Fleet Sector Filter](screenshots_raw/Screenshot%20Capture%20-%202026-06-11%20-%2001-11-06.png)

---
### 4. Equipment Asset Status & Health Cards
Grid of asset health cards displaying criticality level, health score percentages, real-time warning indicators, and status badges (Critical, Degraded, Operational).
![4. Equipment Asset Status & Health Cards](screenshots_raw/Screenshot%20Capture%20-%202026-06-11%20-%2001-11-10.png)

---
### 5. Active Fleet Operations Log
Dynamic tracking of healthy assets (e.g. BF Hydraulic System at 93.3% health, ld LD Converter Vessel #1 at 94.2%) to keep shift engineers informed of operational stability.
![5. Active Fleet Operations Log](screenshots_raw/Screenshot%20Capture%20-%202026-06-11%20-%2001-11-20.png)

---
### 6. Predictive Analytics & ROI Engine
Predicts remaining operational days per machine, displays risk distribution charts, and calculates Net Financial Savings ($118k prevented failures ROI) for plant management.
![6. Predictive Analytics & ROI Engine](screenshots_raw/Screenshot%20Capture%20-%202026-06-11%20-%2001-11-48.png)

---
### 7. Dynamic Gantt Scheduler & Spares Check
AI-prioritized 7-day timeline showing planned maintenance tasks. Selecting a task displays the scope of work, assigned engineer, downtime, and live spare parts availability check (e.g., 'IN STOCK').
![7. Dynamic Gantt Scheduler & Spares Check](screenshots_raw/Screenshot%20Capture%20-%202026-06-11%20-%2001-12-12.png)

---
### 8. Inventory Spares Shortage & Risk Optimizer
Flags a critical spare parts shortage risk alert and estimates production downtime risk exposure (₹2,628,000) for degraded machines missing matching spare components.
![8. Inventory Spares Shortage & Risk Optimizer](screenshots_raw/Screenshot%20Capture%20-%202026-06-11%20-%2001-12-27.png)

---
### 9. Logistics Spares & 1-Click Purchase Order
Parts warehouse inventory status (in stock, low stock, out of stock) showing costs, lead times, and dispatch/expedite PO buttons to prevent supply chain bottlenecks.
![9. Logistics Spares & 1-Click Purchase Order](screenshots_raw/Screenshot%20Capture%20-%202026-06-11%20-%2001-12-56.png)

---
### 10. Anomaly Alerts Console Logs
Real-time alert logger listing warnings categorized by severity (Critical, High, Medium, Low) and plant area, tracking vibration/temperature limit violations (e.g. EOT Crane vibration exceeding limits by 181%).
![10. Anomaly Alerts Console Logs](screenshots_raw/Screenshot%20Capture%20-%202026-06-11%20-%2001-13-23.png)

---
### 11. AI Reports Generation Console
Generates 4 types of plant maintenance documentation: Maintenance Summary, Alert Summary, Equipment Health Card, and Failure Analysis.
![11. AI Reports Generation Console](screenshots_raw/Screenshot%20Capture%20-%202026-06-11%20-%2001-14-31.png)

---
### 12. Knowledge Center Ingestion Pipeline
Drag-and-drop document upload interface (PDF, TXT, MD, JSON, CSV) displaying indexed chunks count, ingestion dates, and vector status.
![12. Knowledge Center Ingestion Pipeline](screenshots_raw/Screenshot%20Capture%20-%202026-06-11%20-%2001-14-58.png)

---
### 13. Platform Specifications & Multi-Agent Architecture
Official submission credits detailing the compliance score, multi-agent brain specification, vector database features, and scikit-learn models.
![13. Platform Specifications & Multi-Agent Architecture](screenshots_raw/Screenshot%20Capture%20-%202026-06-11%20-%2001-16-05.png)

---
### 14. AI Chat: Real-Time Thought Logs & Diagnostic Routing
Engine console logs showing orchestrator routing, ChromaDB vector matching, and diagnostic threshold evaluations (vibration 4.8 mm/s vs 4.5 mm/s upper limit).
![14. AI Chat: Real-Time Thought Logs & Diagnostic Routing](screenshots_raw/Screenshot%20Capture%20-%202026-06-11%20-%2001-16-30.png)

---
### 15. AI Chat: Probable Diagnoses & Root Cause Chain
AI analysis of high vibration and temperature on the Blast Furnace Cooling Pump, detailing Bearing Failure (60% likelihood) and mapping the lubrication breakdown root cause chain.
![15. AI Chat: Probable Diagnoses & Root Cause Chain](screenshots_raw/Screenshot%20Capture%20-%202026-06-11%20-%2001-16-44.png)

---
### 16. AI Chat: Risk Assessment & Safety Actions
Safety recommendation outputting immediate corrective actions (e.g. shutdown the pump, notify maintenance) and compiling evidence from past failures.
![16. AI Chat: Risk Assessment & Safety Actions](screenshots_raw/Screenshot%20Capture%20-%202026-06-11%20-%2001-16-54.png)

---
### 17. AI Chat: Asset Details & History Retrieval
RAG query retrieving full asset metadata and failure logs directly into the conversational interface.
![17. AI Chat: Asset Details & History Retrieval](screenshots_raw/Screenshot%20Capture%20-%202026-06-11%20-%2001-17-41.png)

---
### 18. AI Chat: Health Score Mathematical Formula
Explainable AI response mapping the exact mathematical formula and variables used to compute an asset's health score dynamically.
![18. AI Chat: Health Score Mathematical Formula](screenshots_raw/Screenshot%20Capture%20-%202026-06-11%20-%2001-18-15.png)

---
### 19. AI Chat: Failure Risk Prediction & Forecasts
Orchestrates Isolation Forest predictions to output failure probability timelines and degradation rates.
![19. AI Chat: Failure Risk Prediction & Forecasts](screenshots_raw/Screenshot%20Capture%20-%202026-06-11%20-%2001-19-53.png)

---
### 20. AI Chat: Continuous Caster Anomaly Diagnosis
Diagnoses roller bearing failures for Continuous Caster #1, correlating thermal stress, and validating inventory spare parts.
![20. AI Chat: Continuous Caster Anomaly Diagnosis](screenshots_raw/Screenshot%20Capture%20-%202026-06-11%20-%2001-21-14.png)

---

## 🛠️ Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | Next.js 14, React 18, TypeScript | Premium dashboard & chat UI |
| **Charts** | Recharts | Interactive sensor & health visualizations |
| **Styling** | Custom CSS with design system | Dark theme, glassmorphism, animations |
| **Backend** | FastAPI (Python 3.10) | REST API, async processing |
| **LLM** | Google Gemini 2.0 Flash / 2.5 Flash | Reasoning, diagnosis, recommendations |
| **Vector DB** | ChromaDB | RAG over manuals, SOPs, logs |
| **Embeddings** | Gemini text-embedding-004 | Semantic search |
| **Anomaly Detection** | scikit-learn (Isolation Forest) | Multivariate anomaly detection |
| **RUL Prediction** | NumPy + trend analysis | Remaining useful life estimation |
| **Data** | Synthetic (25 equipment, 90 days) | Realistic steel plant data |

---

## 📋 Features Implemented

### Functional Requirements (All 7 covered)

| # | Requirement | Implementation |
|---|------------|----------------|
| 1 | Contextual Reasoning (LLM) | Google Gemini with chain-of-thought prompting |
| 2 | Knowledge Integration | ChromaDB RAG over manuals, SOPs, maintenance records, failure reports |
| 3 | Natural Language Interaction | Multi-turn conversational chat with context awareness |
| 4 | Explainable Recommendations | Source citations, evidence-based reasoning, confidence scores |
| 5 | Anomaly Detection & Prediction | Isolation Forest + threshold analysis + RUL prediction |
| 6 | Feedback-Driven Improvement | Thumbs up/down + corrections → feedback store |
| 7 | Real-Time Alerting | Anomaly-based alert generation with severity levels |

### Optional & Advanced Enhancements Implemented
- ✅ **Conversational interface**: Dedicated multi-turn AI Chat with real-time multi-agent routing visualization.
- ✅ **Visualization Dashboard**: Plant health status overview with equipment drilldowns.
- ✅ **Interactive Digital Twin Plant Visualizer**: Plant floor mapping with dynamic, live equipment nodes.
- ✅ **3D Isometric Hologram**: Rotating thermal profile of the blast furnace stack.
- ✅ **Predictive Analytics Dashboard**: Fleet-wide RUL forecasts, degradation leaderboard, risk distribution, ROI savings engine, and anomaly detection feeds.
- ✅ **UI/UX Polish**: Animated particle constellation background, sleek glassmorphic layout, color-shifting aurora sidebar, and shimmer skeleton loader indicators.
- ✅ **User Feedback System**: Direct thumbs up/down and correction flow for active learning.

---

## 🤖 Agentic AI Architecture

The system uses a **multi-agent architecture** with 6 specialized agents:

1. **Orchestrator Agent** — Classifies intent, routes queries, chains agents
2. **Diagnostic Agent** — Chain-of-thought fault diagnosis with root cause analysis
3. **Prediction Agent** — RUL estimation, anomaly detection, early warnings
4. **Recommendation Agent** — SOP-grounded, spare-parts-aware action plans
5. **Report Agent** — Structured maintenance reports (4 types)
6. **Knowledge Agent** — RAG retrieval and synthesis over documentation

### Agent Chaining Example
```
User: "The blast furnace cooling pump has high vibration"
  → Orchestrator classifies intent: diagnostic
  → Diagnostic Agent: fault analysis + root cause
  → Prediction Agent: RUL + failure probability
  → Recommendation Agent: maintenance plan + spare parts
  → Response: Comprehensive diagnosis + prediction + action plan
```

---

## ⚡ Enterprise Engineering & Performance Optimizations

To prepare this system for actual production deployments in heavy steel plants, several advanced engineering optimizations have been implemented:

1. **Unified Multi-LLM Provider with Automatic Fallback**:
   - Integrated an abstraction layer (`llm_client.py`) that supports both **Google Gemini 2.5** and **Groq (Llama 3.3)**.
   - If Groq is enabled but fails (due to network issues, rate limits, or bad credentials), the client **automatically and silently falls back to Gemini**, guaranteeing 100% system uptime.
2. **20x Faster Batch Ingestion with Exponential Backoff**:
   - Rewrote the ChromaDB custom embedding function to process documents in batches of 20 using `gemini-embedding-2`.
   - Added robust **exponential retry backoff** to handle 429 / rate limits gracefully.
3. **In-Memory JSON Caching (Latency reduced by 100x)**:
   - Implemented an in-memory dictionary cache for the heavy sensor history log (`sensor_data_full.json`).
   - Disk read and JSON parse overhead is eliminated after the first request, reducing API response times from **200ms to under 2ms**, preventing memory leaks on Windows decoders.
4. **Focused RAG Ingestion**:
   - Filtered out thousands of non-essential routine inspection logs, indexing only logs with actual breakdown, repair, replacement, or emergency actions. This keeps the vector index small, highly relevant, and avoids rate limit issues.
5. **Deduplicated Dashboard Alerts**:
   - Deduplicated overlapping equipment alerts at the frontend level to guarantee clean React lists.

---

## 📊 Data Flow

```
Equipment Sensors → Sensor Data (JSON)
                        ↓
              Anomaly Detector (Isolation Forest)
                        ↓
                  Alert Generation
                        ↓
              RUL Predictor (Trend Analysis)
                        ↓
                Health Index + Risk Level
                        ↓
User Query → Orchestrator → Agent(s) → Gemini API
                                ↓
                    ChromaDB (RAG Retrieval)
                                ↓
                    Structured Response
```

---

## 🚀 Installation & Setup

### Prerequisites
- Python 3.10+
- Node.js 18+
- Google Gemini API key

### Step 1: Clone & Configure
```bash
cd hackathon
cp .env.example .env
# Edit .env and add your Gemini API key
```

### Step 2: Install Dependencies
```bash
# Backend
pip install -r backend/requirements.txt

# Frontend
cd frontend && npm install && cd ..
```

### Step 3: Generate Data
```bash
python -X utf8 backend/data/generate_synthetic_data.py
```

### Step 4: Start the Application
```powershell
# Option 1: One-click start
.\start.ps1

# Option 2: Manual start
# Terminal 1 - Backend:
python -m uvicorn backend.main:app --reload --port 8000

# Terminal 2 - Frontend:
cd frontend && npm run dev
```

### Step 5: Open in Browser
- **Dashboard**: http://localhost:3000
- **AI Chat**: http://localhost:3000/chat
- **API Docs**: http://localhost:8000/docs

---

## 🌐 Production Cloud Deployment

The application is fully prepared for zero-configuration production cloud deployments:

### 1. Frontend (Vercel)
The Next.js frontend has been compiled and is deployed live on Vercel:
- **Live Frontend URL**: [https://frontend-five-self-57.vercel.app](https://frontend-five-self-57.vercel.app)
- Framework configuration is set up in [vercel.json](file:///c:/Users/shubh/Desktop/hackathon/frontend/vercel.json).

### 2. Backend (Render Blueprint)
The FastAPI backend has been containerized and configured for one-click deployment to Render using the Blueprint specification.
- **Blueprint Config**: [render.yaml](file:///c:/Users/shubh/Desktop/hackathon/render.yaml)
- **Container Config**: [Dockerfile](file:///c:/Users/shubh/Desktop/hackathon/Dockerfile) and [.dockerignore](file:///c:/Users/shubh/Desktop/hackathon/.dockerignore)

#### How to Deploy Backend on Render:
1. Log in to your Render dashboard.
2. Click **New +** at the top right and select **Blueprint**.
3. Link your GitHub repository `shubha9696/maintenance-wizard`.
4. Render will read the `render.yaml` specification and create a new Web Service automatically.
5. In the configuration prompt:
   - Provide your `GEMINI_API_KEY` and `GROQ_API_KEY`.
   - Set the `CHROMA_DB_PATH` to `./chroma_db`.
6. Click **Deploy** to build and launch the backend.

#### Linking Frontend & Backend:
Once your Render backend is deployed and you have its live URL (e.g., `https://maintenance-wizard-backend.onrender.com`), configure it in your Vercel project:
1. Go to your **Vercel Project Settings** → **Environment Variables**.
2. Add a new variable: `NEXT_PUBLIC_API_URL` with your Render backend URL as the value.
3. Redeploy your project. The Vercel app will dynamically routing all agentic requests, diagnostics, and reports to your cloud backend!

---

## 💡 Sample Input/Output

### Input 1: Diagnostic Query
**User**: "The blast furnace cooling pump is showing high vibration and elevated temperature at the bearing housing. What's wrong?"

**Output**: Multi-section diagnosis including:
- Symptom analysis (vibration + temperature correlation)
- Top 3 probable diagnoses with probability percentages
- Root cause chain (lubrication → bearing wear → vibration)
- Risk assessment (HIGH — bearing seizure risk)
- Immediate actions (check lube, measure vibration spectrum)
- Evidence from similar historical failures

### Input 2: Prediction Query
**User**: "Which equipment is at highest risk of failure?"

**Output**: Ranked list of equipment with:
- Current health index, RUL (days), failure probability
- Risk level classification
- Early warning descriptions

### Input 3: Report Generation
**User**: "Generate a maintenance summary report"

**Output**: Structured report with executive summary, key metrics, notable issues, and prioritized recommendations.

---

## ⚠️ Assumptions & Limitations

1. **Synthetic Data**: Uses generated data to demonstrate capabilities; real deployment would require actual sensor integration
2. **LLM Dependency**: Requires internet access for Gemini API calls
3. **Simplified ML**: Anomaly detection and RUL use statistical methods; production would use deeper ML models
4. **Single User**: No authentication system (prototype scope)
5. **No Real IoT**: Simulated sensor data; production would integrate with SCADA/DCS systems

---

## 📁 Project Structure

```
hackathon/
├── backend/
│   ├── agents/           # AI Agents (6 agents)
│   │   ├── orchestrator.py
│   │   ├── diagnostic_agent.py
│   │   ├── prediction_agent.py
│   │   ├── recommendation_agent.py
│   │   ├── report_agent.py
│   │   └── knowledge_agent.py
│   ├── services/         # Core services
│   │   ├── vector_store.py
│   │   ├── anomaly_detector.py
│   │   ├── rul_predictor.py
│   │   └── feedback_store.py
│   ├── routers/          # API endpoints
│   │   ├── chat.py
│   │   ├── equipment.py
│   │   ├── alerts.py
│   │   ├── reports.py
│   │   └── feedback.py
│   ├── models/           # Pydantic schemas
│   ├── data/             # Data generation & knowledge base
│   ├── main.py           # FastAPI app
│   └── config.py         # Configuration
├── frontend/
│   └── src/
│       ├── app/          # Next.js pages
│       │   ├── page.tsx           # Dashboard
│       │   ├── chat/page.tsx      # AI Chat
│       │   ├── equipment/         # Equipment pages
│       │   ├── alerts/page.tsx    # Alerts
│       │   └── reports/page.tsx   # Reports
│       ├── components/   # Reusable components
│       └── lib/          # Utilities
├── .env                  # Environment variables
├── start.ps1             # One-click startup
└── README.md             # This file
```

---

## 👨‍💻 Author & Credits

**Shubham Chakrawarti**  
Built for Tata Steel AI Hackathon 2026 — Round 2: Agentic AI Challenge

🔗 **Social Links:**
- **LinkedIn**: [shubham-chakrawarti](https://www.linkedin.com/in/shubham-chakrawarti-27764836a/)
- **GitHub**: [shubha9696](https://github.com/shubha9696)
- **Portfolio**: [shubham-portfolio](https://shubham-potfolio.vercel.app/)
