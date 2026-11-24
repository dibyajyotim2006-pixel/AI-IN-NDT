# NDT INTELLIGENCE: AI-Powered Concrete Strength Assessment System

**NDT Intelligence** is a decision-support web application for civil engineers, structural auditors, and QA/QC inspectors. It predicts concrete compressive strength (in MPa) non-destructively using combined Rebound Hammer (ASTM C805 / IS 13311 Part 2) and Ultrasonic Pulse Velocity (UPV - ASTM C597 / IS 13311 Part 1) measurements alongside concrete curing maturity.

---

## 🏗️ 1. Project Overview & Methodology

Destructive testing of concrete cores is time-consuming, expensive, and structurally invasive. **NDT Intelligence** eliminates the requirement for destructive core extraction for every new test location by combining two complementary non-destructive methods (the **SonReb method**):

1. **Rebound Hammer Test (Schmidt Hammer)**:
   - Measures near-surface hardness and compaction.
   - Standard: **IS 13311 (Part 2) / ASTM C805 / BS 1881:202**.
2. **Ultrasonic Pulse Velocity (UPV)**:
   - Measures longitudinal acoustic pulse velocity ($V = L / T$).
   - Sensitive to internal concrete density, dynamic modulus of elasticity, and micro-porosity.
   - Standard: **IS 13311 (Part 1) / ASTM C597 / BS 1881:203**.
3. **Curing Age**:
   - Accounts for hydration kinetics and strength gain over time (1 to 90+ days).

---

## 🧠 2. Artificial Neural Network (ANN) Architecture

The application implements the exact documented neural network architecture:

- **Input Layer**: 6 Engineered Features
  1. $\text{Age}$ (Curing age in days)
  2. $\text{Rebound\_Index}$ (Hammer reading $R$)
  3. $\text{UPV}$ (Pulse velocity in m/s)
  4. $\text{UPV} / \text{Age}$ (Acoustic development rate)
  5. $\text{Rebound\_Index} / \text{Age}$ (Surface crystallization rate)
  6. $\text{UPV} \times \text{Rebound\_Index}$ (Combined non-linear SonReb interaction)
- **Hidden Layer**:
  - **6 Hidden Neurons**
  - **Sigmoid (Logistic) Activation Function**: $\sigma(z) = \frac{1}{1 + e^{-z}}$
- **Output Layer**:
  - **1 Linear Output Neuron**: Predicted Compressive Strength in $\text{MPa}$
- **Optimization**:
  - Supervised Backpropagation (L-BFGS quasi-Newton optimizer with feature and target scaling)

### Model Verification & Benchmark Comparison

| Metric | Project Report Target | NDT Intelligence Model |
| :--- | :---: | :---: |
| **Correlation Coefficient ($R$)** | **0.99486** (99.5%) | **0.9966** |
| **Coefficient of Determination ($R^2$)** | **0.9897** | **0.9930** |
| **Mean Squared Error (MSE)** | **0.53494** | **1.36 MPa²** |
| **Root Mean Squared Error (RMSE)** | ~1.4 MPa | **1.17 MPa** |
| **Mean Absolute Error (MAE)** | ~1.0 MPa | **0.88 MPa** |

---

## 📁 3. Project Directory Structure

```
NDT-INTELLIGENCE/
│
├── app.py                      # Main Streamlit application and navigation router
│
├── model/
│   ├── train_model.py          # ANN training pipeline (6-6-1 Sigmoid architecture)
│   ├── predictor.py            # Feature engineering, validation & prediction engine
│   └── trained_model.pkl       # Saved model pipeline bundle (weights, scaler, metrics)
│
├── data/
│   ├── concrete_samples.csv    # Experimental concrete testing dataset
│   ├── concrete_samples_evaluated.csv # Dataset with model predictions & residuals
│   ├── assessment_history.db   # Persistent SQLite storage for inspection records
│   └── assessment_history.csv  # Backup export of field assessment history
│
├── components/
│   ├── dashboard.py            # Module A: Executive KPI Dashboard & quality donut
│   ├── predictor.py            # Module B: Interactive AI Strength Predictor & calibration plot
│   ├── database.py             # Module C: Filterable & searchable experimental database
│   ├── analytics.py            # Module D: Engineering analytics & 5 Plotly visualizations
│   └── reports.py              # Module E: Certified PDF Assessment Report generator
│
├── utils/
│   ├── pdf_generator.py        # ReportLab PDF report builder with custom styling
│   └── storage.py              # SQLite & CSV persistence engine
│
└── requirements.txt            # Python dependencies
```

---

## 🚀 4. How to Run Locally

### Step 1: Install Requirements
Open PowerShell or your command prompt in the project root:
```powershell
pip install -r requirements.txt
```

### Step 2: (Optional) Re-train the Machine Learning Model
The repository already includes the pre-trained model bundle. If you wish to re-train the ANN from scratch:
```powershell
python model/train_model.py
```

### Step 3: Launch the Streamlit Web Application
```powershell
streamlit run app.py
```
Your default web browser will automatically open:
```
http://localhost:8501
```

---

## 🎯 5. Application Modules & Features

### A. Executive Dashboard
- **Top Metrics**: Total specimens, average compressive strength, maximum recorded strength, recent field assessments, and ANN correlation coefficient ($R = 0.9966$).
- **Distribution Histogram**: Real distribution of concrete compressive strength across experimental samples.
- **IS 13311 Quality Donut**: Visual classification of ultrasonic transmission quality (Excellent, Good, Medium, Doubtful).
- **Descriptive Statistics Table**: Mean, standard deviation, min, and max for all NDT parameters.
- **Recent Assessments**: Live audit log of recent inspections.

### B. AI Strength Predictor
- Interactive input form with sliders and number inputs:
  - Specimen ID
  - Concrete Curing Age (Days)
  - Rebound Hammer Index ($R$)
  - Ultrasonic Pulse Velocity (m/s)
- **Quick-Load Presets**: Instant 1-click test cases for faculty demonstrations:
  - *Anchor C001 (1d Early)*: Age 1, Reb 21.3, UPV 3649 $\rightarrow$ Predicts **7.41 MPa** (Medium / Early-Age)
  - *Anchor C003 (1d Early)*: Age 1, Reb 23.9, UPV 3592 $\rightarrow$ Predicts **8.86 MPa**
  - *Standard M30 (28d)*: Age 28, Reb 38.5, UPV 4510 $\rightarrow$ Predicts **38.90 MPa** (Good / Structural)
  - *High-Performance (56d)*: Age 56, Reb 48.0, UPV 4850 $\rightarrow$ Predicts **58.20 MPa** (Excellent / HPC)
- **Input Validation**: Rejects unphysical or out-of-range inputs with clear guidance.
- **Dynamic Feature Breakdown**: Displays all 6 engineered features and their physical engineering significance.
- **Instant Result Card**: Large compressive strength readout in MPa, IS 13311 quality rating badge, and concrete grade recommendation.
- **Visual Calibration Scatter Plot**: Places the predicted sample as a pulsing cyan star directly on the historical curing curve.
- **One-Click PDF Report**: Download button right beneath the prediction card.

### C. Experimental Sample Database
- Full tabular view of all 152 concrete specimens.
- Multi-parameter filtering:
  - Search by Sample ID
  - Age multi-select (1, 3, 7, 14, 28, 56, 90 days)
  - Rebound Index slider
  - UPV range slider
- Side-by-side comparison of **Actual Experimental Strength** vs **AI Predicted Strength** with residual error.
- One-click CSV export of filtered data.

### D. Analytics & Visualizations
Interactive Plotly charts designed with a dark navy industrial engineering palette:
1. **Actual vs Predicted Strength (Parity Plot)**: 1:1 diagonal verification plot demonstrating $R = 0.9966$.
2. **Strength vs Curing Age**: Logarithmic hydration maturation curve.
3. **UPV vs Compressive Strength**: Acoustic pulse transmission curve with shaded IS 13311 quality zones.
4. **Rebound Index vs Compressive Strength**: Surface hardness calibration curve.
5. **Residual Error Distribution**: Histogram of $(y - \hat{y})$ confirming zero-centered Gaussian error.
6. **Model Metrics Banner**: Displays $R$, $R^2$, MSE, RMSE, and MAE.

### E. PDF Assessment Report Generator
- Produces downloadable PDF engineering reports using ReportLab.
- Report includes:
  - Official header banner and report reference code.
  - Project information (Project Name, Inspector, Testing Date, Structure/Element Location).
  - Raw NDT test measurements (Age, Rebound Index, UPV).
  - Neural Network 6-Feature pipeline breakdown table.
  - Callout box with Predicted Compressive Strength (MPa) and IS 13311 rating.
  - Engineering remarks and formal signature / QA approval block.
- Downloadable directly into the browser.

---

## 📋 6. Faculty Demonstration Quick Reference

To impress your evaluators during your demonstration:
1. **Show the Dashboard**: Highlight the industrial theme, real 152-sample dataset, and live SQLite assessment history.
2. **Click AI Strength Predictor**: Click the **"Anchor C001 (1d Early)"** preset button and click **"Run AI Strength Prediction"**:
   - Point out that C001 was tested at 1 day ($R=21.3, UPV=3649\text{ m/s}$), producing an actual strength of $8.00\text{ MPa}$.
   - The AI accurately predicts **~7.41 MPa** ($\Delta < 0.6\text{ MPa}$), classifying it as *Early-Age Curing Concrete*.
   - Show the 6 engineered features in the expander ($\text{Age}, R, \text{UPV}, \text{UPV}/\text{Age}, R/\text{Age}, \text{UPV}\times R$).
   - Point to the visual calibration scatter plot showing the exact marker on the historical curve.
   - Click **"Download Assessment Report (PDF)"** and open the clean PDF report.
3. **Open Analytics**:
   - Walk through the **Actual vs Predicted Parity Plot** highlighting the $R = 0.9966$ correlation matching the project report.
   - Show the **IS 13311 Ultrasonic Velocity Zones** overlay on the UPV vs Strength graph.
4. **Open Sample Database**:
   - Filter by age (e.g. 28 days) to show standard structural concrete specimens (M25 to M50).
