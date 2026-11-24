# NDT INTELLIGENCE — PHASE 1 CODEBASE & ARCHITECTURAL AUDIT REPORT

**Date:** 2026-11-24  
**Auditor:** Lead AI/Software Systems Engineer  
**Scope:** Full repository audit (`app.py`, `model/`, `data/`, `components/`, `utils/`, `requirements.txt`)  
**Status:** Completed (Phase 1 Gate — Awaiting Approval Before Phase 2)

---

## 1. Executive Summary

A comprehensive, line-by-line audit of the "NDT Intelligence" concrete strength assessment prototype was conducted. The application functions as an interactive Streamlit prototype predicting concrete compressive strength from Rebound Index, UPV, and Age using a 6-6-1 Artificial Neural Network. 

However, critical scientific, architectural, data provenance, and reliability vulnerabilities were identified that must be addressed before presenting this system to university faculty:
1. **Data Provenance Reality**: Only **5 of the 152 samples (3.3%)** are real experimental observations from the reference report (`C001`–`C005`). The remaining **147 samples (96.7%)** are synthetic, produced by `data/generate_dataset.py` using deterministic empirical curves with Gaussian noise ($\pm 2.5\%$). This synthetic generation explains the exceptionally high correlation ($R = 0.9966$) and represents an existential risk if presented to faculty as real-world experimental validation.
2. **False Certification Claims**: Multiple UI elements and PDF outputs claim "CONFIDENTIAL & CERTIFIED", "OFFICIAL STAMP / SEAL", and "VERIFIED", violating engineering ethics and Global Rule 6.
3. **Train/Test Leakage in Visual Analytics**: The parity plot and error distribution charts in `components/analytics.py` evaluate on both training and test data combined rather than held-out test data.
4. **Reliability & State Flaws**: Duplicate insertions occur on Streamlit reruns, file paths are hardcoded without a centralized config, and model caching does not leverage `@st.cache_resource`.

---

## 2. System Tree & Dependency Map

### 2.1 File Tree
```
c:\AI Concrete Assessment System\
├── app.py                      # Main entrypoint & UI layout
├── requirements.txt            # Dependency specifications
├── README.md                   # Project documentation
├── components/
│   ├── dashboard.py            # Executive KPI & sample overview
│   ├── predictor.py            # AI prediction interactive form
│   ├── database.py             # Experimental dataset table & filters
│   ├── analytics.py            # Plotly acoustic-mechanical charts
│   └── reports.py              # PDF report generation UI
├── data/
│   ├── concrete_samples.csv    # 152 sample rows (5 real + 147 synthetic)
│   ├── concrete_samples_evaluated.csv # Samples with model predictions
│   ├── generate_dataset.py     # Deterministic synthetic data generator
│   ├── assessment_history.db   # SQLite local database
│   └── assessment_history.csv  # Auto-synced CSV backup
├── model/
│   ├── train_model.py          # 6-6-1 ANN MLPRegressor pipeline
│   ├── predictor.py            # Inference engine, feature engineering & grading
│   └── trained_model.pkl       # Serialized joblib bundle
├── utils/
│   ├── storage.py              # SQLite & CSV persistence layer
│   └── pdf_generator.py        # ReportLab PDF compilation engine
└── docs/
    └── AUDIT_REPORT.md         # This audit document
```

### 2.2 Component Dependency Map
```
                   ┌──────────────┐
                   │    app.py    │
                   └──────┬───────┘
         ┌────────────┬───┴────────┬────────────┬─────────────┐
         ▼            ▼            ▼            ▼             ▼
   dashboard.py  predictor.py  database.py  analytics.py  reports.py
         │            │            │            │             │
         ├────────────┼────────────┴────────────┼─────────────┤
         │            │                         │             │
         ▼            ▼                         ▼             │
     storage.py   predictor.py (model)  predictor.py (bundle) │
         │            │                         │             │
         │            ▼                         │             │
         │       train_model.py                 │             │
         │            │                         │             │
         │            ▼                         │             │
         │     trained_model.pkl                │             │
         │                                      │             │
         └──────────────────────────────────────┴─────────────┘
                                │
                                ▼
                        pdf_generator.py
```

---

## 3. Dataset Provenance Investigation

A forensic analysis of `data/concrete_samples.csv` revealed the exact origin of all 152 rows:

| Row Range | Sample IDs | Curing Ages | Strength Range | Classification | Provenance Evidence |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Row 1 – 5** | `C001` – `C005` | 1 Day | 7.74 – 9.08 MPa | **REAL** | Exact anchor rows documented in project report. Tested on Day 1. |
| **Row 6 – 152** | `C006` – `C152` | 1, 3, 7, 14, 28, 56, 90 Days | 5.50 – 71.17 MPa | **SYNTHETIC** | Generated by `data/generate_dataset.py` (`np.random.seed(101)`). Mix grades M15–M50, 7 ages, 3 reps per group ($7 \times 7 \times 3 = 147$ rows). |

### Mathematical Noise Model Used for Synthetic Rows
```python
# From data/generate_dataset.py:
fc = mix["fc28_mean"] * age_strength_ratio[age] * (1.0 + N(0, 0.025))
reb = mix["rebound_28"] * age_rebound_ratio[age] + N(0, 0.9)
upv = mix["upv_28"] * age_upv_ratio[age] + N(0, 30)
```
### Provenance Verdict:
- **Total Samples:** 152
- **Real Observed Samples:** 5 (3.29%)
- **Synthetic Samples:** 147 (96.71%)
- **Unverified Samples:** 0

> **Critical Implication:** The high correlation ($R = 0.9966$) is fundamentally a reflection of the neural network fitting the smooth synthetic generator function. When presenting to university faculty, the synthetic nature of these 147 rows must be explicitly labeled. We must provide separate evaluation metrics for real vs synthetic data.

---

## 4. Prioritized Vulnerabilities & Defects

### Severity 1: Critical (Must Fix Immediately)

1. **Unsubstantiated Certification / Safety Claims (Ethics & Safety Violation)**
   - **Locations:**
     - `utils/pdf_generator.py:127`: Header states `"CONFIDENTIAL & CERTIFIED"`.
     - `utils/pdf_generator.py:269`: State marked as `"Status: VERIFIED"`.
     - `utils/pdf_generator.py:268`: Block marked as `"OFFICIAL STAMP / SEAL"`.
     - `components/reports.py:15`: Label states `"Generate formal, certified civil engineering..."`.
   - **Impact:** Violates engineering standards and Global Rule 6. This is a university research decision-support prototype, not a legal certification tool.
   - **Fix:** Replace all certification claims with honest research prototype disclaimers.

2. **Absence of Real vs. Synthetic Separation in UI and Analytics**
   - **Locations:** `components/database.py`, `components/analytics.py`, `components/dashboard.py`.
   - **Impact:** Misleads users into believing all 152 samples are physical laboratory specimens.
   - **Fix:** Add a persistent `Data_Source` column (`REAL` vs `SYNTHETIC`) to the database, display badges on every row, and provide independent evaluation metric splits.

3. **Duplicate Database Inserts on Streamlit Reruns**
   - **Locations:** `components/predictor.py:148-169`, `utils/storage.py:60-89`.
   - **Impact:** Every time a user changes a filter, resizes the window, or interacts with a widget after predicting, `predict_clicked` logic or unmanaged state can re-insert the identical record into SQLite.
   - **Fix:** Introduce an explicit "Save Assessment" button with an idempotency session token / hash guard to prevent accidental duplicate inserts.

### Severity 2: High (Scientific & Architectural Issues)

4. **Evaluation Leakage in Visual Analytics**
   - **Location:** `model/train_model.py:137-140`, `components/analytics.py:94-156`.
   - **Impact:** The parity plot ($y = x$), $R^2$, and residual histograms display predictions generated on the full dataset (training + test combined). Generalization metrics are artificially inflated.
   - **Fix:** Split evaluation explicitly between train and test sets. Clearly indicate held-out test performance.

5. **Potential Division by Zero in Feature Engineering**
   - **Locations:**
     - `model/train_model.py:27, 30`: `X['UPV'] / X['Age']`, `X['Rebound_Index'] / X['Age']`.
     - `model/predictor.py:120, 121`: `upv / age`, `rebound_index / age`.
   - **Impact:** While input validation currently checks `age <= 0`, batch predictions or programmatic calls with $Age = 0$ will crash or yield `inf`.
   - **Fix:** Add numerical epsilon guard: `max(float(age), 0.1)`.

6. **Hardcoded File Paths & Lack of Central Configuration**
   - **Locations:** Throughout `app.py`, `model/predictor.py`, `components/*.py`, `utils/*.py`.
   - **Impact:** Relative paths like `"data/concrete_samples.csv"` fail if Streamlit or tests run from an alternative working directory.
   - **Fix:** Create a central `paths.py` that computes all absolute paths dynamically relative to project root.

7. **Missing Out-of-Distribution (OOD) Detection**
   - **Location:** `model/predictor.py:20-43`.
   - **Impact:** The model extrapolates blindly if an engineer enters $Age = 365$, $R = 65$, or $UPV = 5200$, presenting point estimates with no indicator that inputs are outside the training domain.
   - **Fix:** Implement domain boundary checking against training set min/max, displaying an honest out-of-distribution notice.

### Severity 3: Medium (Performance & Standards Compliance)

8. **Missing Streamlit Caching for Datasets and Models**
   - **Locations:** `components/dashboard.py:23`, `components/analytics.py:22`, `components/database.py:20`.
   - **Impact:** Repeated disk reads of CSV files on every Streamlit rerun.
   - **Fix:** Wrap CSV loading with `@st.cache_data` and model loading with `@st.cache_resource`.

9. **Deprecated Streamlit Parameters**
   - **Locations:** `use_container_width=True` used across dataframes and buttons.
   - **Impact:** Emits console deprecation warnings in Streamlit 1.67+.
   - **Fix:** Migrate to current Streamlit layout guidelines where applicable.

10. **Duplicate Tree in Subdirectory**
    - **Location:** `c:\AI Concrete Assessment System\NDT-INTELLIGENCE\`.
    - **Impact:** Two identical copies of code exist, creating maintenance drift.
    - **Fix:** Consolidate into the root workspace or establish clean single-source structure.

---

## 5. Proposed Phase 2–4 Action Plan

| Phase | Core Objective | Key Deliverables |
| :--- | :--- | :--- |
| **Phase 2: Scientific & ML Validation** | Retrain and benchmark with strict real/synthetic separation; OOD detection; unit consistency. | `docs/ML_VALIDATION.md`, updated `train_model.py`, separate metrics for real vs synthetic data, OOD bounds checker. |
| **Phase 3: Architecture & Reliability** | Implement `paths.py`, SQLite idempotency, error logging (`logs/app.log`), input sanitization. | `paths.py`, updated `storage.py`, `logs/app.log`, unit test harness in `tests/`. |
| **Phase 4: UI/UX & Disclaimers** | Remove false certification claims, add REAL/SYNTHETIC badges, separate lab vs user stats, clean up PDF report. | Updated `app.py`, `components/`, and `utils/pdf_generator.py` with research prototype disclaimers. |
| **Phase 5: Process Cleanup** | Audit running Streamlit and Python processes using exact PowerShell scripts. | Process report, clean port state. |
| **Phase 6: Standalone Packaging** | Evaluate PyInstaller, pywebview, Tauri for offline distribution. | `docs/PACKAGING_STRATEGY.md`. |
| **Phase 7: Comprehensive Testing** | Execute full pytest suite and write evidence log. | `docs/TEST_EVIDENCE.md` with passing test runs. |
| **Phase 8: Final Deliverables** | Updated README, demonstration guide, faculty FAQ. | Final deliverable package. |

---

**AUDIT CONCLUSION:** Phase 1 audit is complete. No code modifications have been made. Awaiting your approval before proceeding to Phase 2.
