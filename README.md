# ExpiryAware — Expiry-Aware Medicine Stock Redistribution Recommender

> **"Prevent expiry. Redistribute responsibly."**  
> *Responsible clinical inventory intelligence for temperature-sensitive specialty medicines.*

---

## 1. Project Overview & Problem Statement

Specialty clinics and hospital dispensaries routinely manage high-cost, short-dated, and temperature-sensitive pharmaceuticals (e.g. oncology biologics, insulins, immunology infusions). Due to volatile clinical demand, medicine batches frequently approach their expiration dates while held as local surplus at one facility, while a neighboring clinic faces impending stockouts of the exact same medication.

Traditional practice relies on isolated, single-clinic First-In-First-Out (**FIFO**) usage without dynamic inter-facility redistribution. As a result, millions of dollars worth of viable medicines are needlessly incinerated each year while patients experience treatment delays.

**ExpiryAware** is a production-grade clinical decision-support application that pairs an explainable, multi-factor rule engine with strict human-in-the-loop clinical governance to safely recommend inter-facility redistribution before medicines expire.

---

## 2. Key Objectives

1. **Reduce Clinical Waste**: Proactively identify medicine batches within $\le 30$ days of expiry where local consumption cannot absorb the stock.
2. **Match Verified Demand**: Ensure surplus stock is routed only to destination clinics with active projected patient demand, strictly adhering to capacity limits.
3. **Transparent Explainable AI (XAI)**: Replace opaque black-box models with deterministic, formulaic scoring that provides clinical staff with plain-English rationales and rule triggers.
4. **Human-in-the-Loop Safeguards (Rule 10)**: Ensure the system **never** autonomously dispatches medication. Pharmacist confirmation, explicit rejection, or structured reason capture for overrides is mandatory.
5. **Auditing & Traceability**: Persist every clinical action into an immutable SQLite audit log with timestamps, roles, and rationale notes.

---

## 3. Technology Stack

- **Backend**:
  - Python 3.11+ (verified with Python 3.14)
  - FastAPI (REST API framework with OpenAPI documentation)
  - Pydantic v2 (Strict request validation & data contract enforcement)
  - SQLAlchemy & SQLite (Embedded, zero-configuration persistent storage)
  - Pandas & NumPy (Data manipulation & empirical simulation)
  - Pytest & FastAPI TestClient (Automated test suite)
- **Frontend**:
  - React 18 & Vite 5 (Ultra-fast modern reactive web application)
  - Tailwind CSS (Custom healthcare design system with clinical palettes)
  - Recharts (Interactive SVG data visualizations: bar charts, donut charts)
  - Lucide React (Accessible healthcare iconography)
- **Zero Cloud / Zero API Dependencies**:
  - Operates 100% locally and offline after initial package installation.
  - No external tracking, no Docker requirements, and no third-party cloud API keys.

---

## 4. Complete Project Directory Structure

```
expiry-aware-recommender/
│
├── backend/
│   ├── app/
│   │   ├── __init__.py           # App package initialiser
│   │   ├── main.py               # FastAPI router, CORS, API endpoints, error handling
│   │   ├── database.py           # SQLite engine, sessionmaker, auto-seeding
│   │   ├── models.py             # SQLAlchemy models (InventoryBatch, Recommendation, AuditLog)
│   │   ├── schemas.py            # Pydantic validation schemas
│   │   ├── recommender.py        # Explainable scoring engine (Rules 1-10)
│   │   ├── validation.py         # Clinical data validation (VALID, WARNING, BLOCKED)
│   │   ├── explanation.py        # Narrative clinical rationale generator
│   │   ├── evaluation.py         # FIFO baseline vs ExpiryAware empirical simulation
│   │   └── seed_data.py          # Deterministic synthetic inventory generator (seed=42)
│   │
│   ├── tests/
│   │   ├── test_recommender.py   # Unit tests for scoring, capping, and priority bands
│   │   ├── test_validation.py    # Unit tests for 7 edge cases and safety blocks
│   │   └── test_api.py           # End-to-end FastAPI TestClient integration tests
│   │
│   ├── requirements.txt          # Python dependencies
│   └── run.py                    # Backend server entrypoint launcher (port 8000)
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Navbar.jsx        # Branding, connection badge, demo reset trigger
│   │   │   ├── Sidebar.jsx       # Clinical operations navigation tabs
│   │   │   ├── MetricCard.jsx    # Styled KPI summary card
│   │   │   ├── OverrideModal.jsx # Mandatory clinical override dialog
│   │   │   ├── BatchDetailDrawer.jsx # Slide-out inventory inspection panel
│   │   │   └── ResetDemoModal.jsx # Demo data re-seed confirmation dialog
│   │   ├── pages/
│   │   │   ├── DashboardPage.jsx # Executive KPI dashboard & interactive Recharts
│   │   │   ├── InventoryPage.jsx # Searchable, sortable, filterable inventory table
│   │   │   ├── RecommendationsPage.jsx # Transfer cards, explanations & human actions
│   │   │   ├── EvaluationPage.jsx # Empirical baseline vs proposed experiment table
│   │   │   ├── AuditLogPage.jsx  # Immutable clinical audit trail table
│   │   │   ├── DataQualityPage.jsx # Data integrity metrics & flagged records
│   │   │   └── ResponsibleAIPage.jsx # Ethical AI governance & transparency principles
│   │   ├── services/
│   │   │   └── api.js            # Centralized API service with offline fallbacks
│   │   ├── App.jsx               # Application root & tab state router
│   │   ├── main.jsx              # React DOM mounting
│   │   └── index.css             # Tailwind design system & healthcare badges
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   └── index.html
│
├── data/
│   ├── synthetic_inventory.csv   # 110+ deterministic synthetic batches
│   ├── edge_cases.csv            # 7 documented failure & boundary cases
│   └── stakeholder_feedback.csv  # Synthetic multi-role evaluation ratings
│
├── evaluation/
│   ├── generate_report.py        # Standalone CLI report generator
│   ├── evaluation_report.json    # Exported evaluation metrics (JSON)
│   └── evaluation_report.md      # Exported evaluation metrics (Markdown)
│
├── README.md                     # Comprehensive project documentation
└── .gitignore
```

---

## 5. Synthetic Dataset & Privacy Guarantees

> [!IMPORTANT]
> **Zero Protected Health Information (PHI)**: This system uses **only synthetic data**. Fictional medicine codes (`MED-A01` through `MED-J10`), generated batch codes (`BATCH-101+`), and synthetic clinic designations (`Clinic-A` through `Clinic-E`) are utilized throughout.

The dataset is generated deterministically (`random.seed(42)`) in `backend/app/seed_data.py`.

### Schema Attributes:
| Field | Type | Description |
| :--- | :--- | :--- |
| `batch_id` | String | Unique batch code (e.g. `BATCH-102`) |
| `medicine_code` | String | Fictional code (e.g. `MED-A01`, `MED-B02`) |
| `medicine_name` | String | Clinical formulation name |
| `medicine_category` | String | Oncology, Endocrine, Immunology, Anti-Infective |
| `source_location` | String | Origin facility (Clinics A–E) |
| `quantity` | Float | Units in dispensary |
| `unit_value` | Float | Unit acquisition cost ($) |
| `expiry_date` | Date | ISO YYYY-MM-DD format |
| `avg_daily_demand` | Float | Expected consumption rate at source |
| `destination_location`| String | Candidate recipient facility |
| `destination_daily_demand`| Float | Expected consumption rate at destination |
| `transfer_distance_km`| Float | Road transit distance (km) |
| `temperature_sensitive`| Boolean | Cold-chain required (2°C – 8°C) vs Ambient |
| `data_quality_score`| Float | Completeness score (0 – 100) |

---

## 6. Recommendation Methodology (Rules 1–10)

The scoring engine calculates a normalized **Risk Score ($0 - 100$)**:
$$\text{Risk Score} = 0.35 \times \text{Expiry} + 0.25 \times \text{Surplus} + 0.25 \times \text{Demand} + 0.10 \times \text{Location} + 0.05 \times \text{Data Quality}$$

### Rules Enforced:
1. **Rule 1 (Expiry Urgency)**: If `days_to_expiry` $\le 30$ days, expiry score increases to $\ge 85$.
2. **Rule 2 (Surplus Detection)**: If source quantity exceeds projected local consumption ($\text{qty} > \text{days} \times \text{local\_demand}$), source is marked as surplus.
3. **Rule 3 (Destination Eligibility)**: Candidate clinic must have active daily demand $> 0$.
4. **Rule 4 (Logistics Feasibility)**: Transfer distance $\le 100$ km earns high feasibility score ($85 - 100$). Long haul transit for cold-chain medicines incurs penalties.
5. **Rule 5 (Safety Block - Missing Expiry)**: If expiry date is unavailable, recommendation is **BLOCKED**.
6. **Rule 6 (Safety Block - Non-Positive Qty)**: If quantity $\le 0$, recommendation is **BLOCKED**.
7. **Rule 7 (Uncertainty Warning)**: If destination demand is missing, confidence is reduced by $25\%$ and a `WARNING` status is emitted.
8. **Rule 8 (Quantity Capping)**: Never recommend transferring more than destination demand can consume:
   $$\text{Transfer Qty} = \min(\text{Surplus Qty}, \text{Destination Capacity}, \text{Available Stock})$$
9. **Rule 9 (Safety Block - Expired Batch)**: Already-expired medicines are strictly **BLOCKED** from redistribution.
10. **Rule 10 (Mandatory Human Confirmation)**: System **never** auto-executes. Pharmacist review is required.

### Priority Bands:
- **80 – 100**: `HIGH PRIORITY` (Immediate pharmacist dispatch review)
- **60 – 79**: `MEDIUM PRIORITY` (Active transfer candidate)
- **40 – 59**: `LOW PRIORITY` (Monitor local consumption)
- **Below 40**: `NO ACTION` (Surplus absorbed locally or no eligible demand)

---

## 7. Installation & Quick Start

### Prerequisites
- **Python 3.11+** installed
- **Node.js 18+** installed

### Step 1: Backend Setup
```bash
cd expiry-aware-recommender/backend

# Optional: create virtual environment
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run backend (auto-initializes and auto-seeds SQLite database)
python run.py
```
The FastAPI backend will start on **`http://localhost:8000`**.  
Interactive API Docs: **`http://localhost:8000/docs`**.

### Step 2: Frontend Setup
In a new terminal:
```bash
cd expiry-aware-recommender/frontend

# Install dependencies
npm install

# Start Vite development server
npm run dev
```
Open **`http://localhost:5173`** in your browser.

---

## 8. Running Automated Tests

Run the complete Pytest suite from the `backend/` directory:
```bash
cd expiry-aware-recommender/backend
python -m pytest tests/ -v
```
All **25 tests** cover:
- Edge Cases 1–7 (Missing dates, negative quantity, expired stock, capping, long distances).
- Multi-factor mathematical scoring and priority band thresholds.
- REST API integration: health, dashboard KPIs, inventory filtering, human approvals, overrides, audit trail, and database re-seeding.

To verify frontend production build:
```bash
cd expiry-aware-recommender/frontend
npm run build
```

---

## 9. Evaluation Methodology: Baseline vs Proposed

To measure real clinical efficacy, ExpiryAware runs an empirical simulation comparing two operating models over the synthetic inventory:

1. **Baseline Model (FIFO Local Only)**:
   - Each clinic operates as an isolated silo.
   - Stock is consumed locally until expiry: $\text{Consumed} = \min(\text{Quantity}, \text{Days} \times \text{Source Demand})$.
   - Surplus stock that cannot be absorbed locally expires and is discarded as financial waste.
2. **Proposed Model (ExpiryAware Redistribution)**:
   - Identifies surplus stock before expiration.
   - Routes eligible surplus to regional partner clinics with verified demand.
   - Preserves viable stock from being discarded.

### Empirical Results (Deterministic Seed 42):
- **Baseline Expired Waste**: **$1,131,978.20**
- **Proposed Expired Waste**: **$290,300.55**
- **Net Waste Avoided (Protected Value)**: **$841,677.65** (**74.4% reduction in loss**)
- **Recommendation Coverage**: **87.3%** of eligible surplus batches routed
- **Recommendation Precision**: **47.0%** strictly valid transfer proposals (excluding safety-blocked batches)
- **Human Override Rate**: **33.3%** clinical exception capture

Run the evaluation CLI report anytime:
```bash
cd expiry-aware-recommender
python evaluation/generate_report.py
```

---

## 10. 3-Minute Live Demonstration Script

Follow this step-by-step script for an impactful demonstration to clinical stakeholders or evaluators:

### Minute 1: Executive Dashboard & Waste Avoided
1. Open `http://localhost:5173`.
2. Notice the top banner: **$841,677 Projected Waste Prevented (74.4% reduction)**.
3. Review the **Stock Value & Near-Expiry Risk by Clinic** chart showing Clinic-A and Clinic-B holding elevated near-expiry batches.
4. Point out the **API Connected** live status indicator in the top navbar.

### Minute 2: Explainable Recommendations & Clinical Override
1. Click **Recommendations** in the sidebar.
2. Highlight a **HIGH PRIORITY** card (e.g. `BATCH-102` or `BATCH-103`).
3. Click **"Show Evidence & Scoring Breakdown"**:
   - Show the 5 transparent scoring factors: Expiry Urgency (35%), Source Surplus (25%), Destination Demand (25%), Location Logistics (10%), Data Quality (5%).
   - Read the human-readable narrative explanation generated for the pharmacist.
4. Click **[Approve]**: Notice the status immediately changes to `APPROVED` with a toast notification.
5. On another batch, click **[Override]**:
   - Show the mandatory reason dropdown (`Demand changed`, `Stock already allocated`, `Temperature concern`, etc.).
   - Type clinical notes: *"5 units held for urgent pediatric outpatient infusion."*
   - Submit override: Status updates immediately to `OVERRIDDEN`.

### Minute 3: Audit Governance, Evaluation & Demo Reset
1. Click **Audit Log** in the sidebar:
   - Point out the newly recorded `APPROVED` and `OVERRIDDEN` events with exact UTC timestamps and staff roles.
2. Click **Evaluation & Baseline**:
   - Review the empirical comparison table showing Baseline FIFO vs Proposed ExpiryAware.
   - Scroll to **Error Analysis** showing safety-blocked cases (e.g. missing dates, negative stock).
3. Click **Reset Demo Data** in the top navbar:
   - Confirm reset. The database instantly re-seeds to the deterministic baseline, ready for the next demo run.

---

## 11. Edge Cases & Safety Constraints Handled

| Case # | Description | Engine Behavior | UI Status |
| :---: | :--- | :--- | :--- |
| **Case 1** | Missing expiry date | Safety blocked: cannot calculate urgency | `BLOCKED` |
| **Case 2** | Negative quantity | Safety blocked: physical impossibility | `BLOCKED` |
| **Case 3** | Missing destination demand | Confidence reduced by 25%; warning emitted | `WARNING` |
| **Case 4** | Already expired batch | Safety blocked: expired medicine cannot be dispatched | `BLOCKED` |
| **Case 5** | Destination demand < Surplus | Transfer quantity clamped to destination demand | Capped `Transfer Qty` |
| **Case 6** | Transfer distance > 150 km | Location score penalty; cold-chain risk flag | `CHALLENGING` transit |
| **Case 7** | Near-expiry but 0 destination demand | No transfer recommended; local clinical review | `NO ACTION` |

---

## 12. Future Improvements

- **Multi-Hop Inter-Clinic Routing**: Optimizing transfers across multi-tier hospital networks with central fulfillment hubs.
- **Direct EHR / Dispensing Machine Integration**: HL7 / FHIR connector to pull real-time inventory from automated dispensing cabinets (e.g. Pyxis, Omnicell).
- **IoT Cold-Chain Telemetry**: Live temperature sensor data streaming via MQTT to dynamically adjust transit feasibility scores during transit.
