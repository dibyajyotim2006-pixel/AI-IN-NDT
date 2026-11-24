# NDT Intelligence - Installation Guide

The **NDT Intelligence** system can be installed and executed in two modes:
1. **Standalone Portable Desktop Application** (Recommended for end-users, faculty demonstrations, and lab testing).
2. **Developer / Source Code Mode** (For modifying algorithms, retraining models, or inspecting source code).

---

## Mode A: Standalone Desktop Application (No Python Required)

### 1. Download
Extract `NDT_Intelligence_v1.0.0_win64.zip` to your preferred directory.

### 2. Execution
Run `NDT Intelligence.exe`.

### 3. Verification
- The application will initialize a local background analytics process and present a native Edge Chromium window.
- Test with sample preset **Anchor C001 (1d Early)** or enter custom Rebound Hammer and UPV values.
- Click **📄 Download Assessment Report (PDF)** to generate standardized engineering documentation.

---

## Mode B: Developer Mode (From Source)

### 1. Clone the Repository
```powershell
git clone https://github.com/dibyajyotim2006-pixel/AI-IN-NDT.git
cd AI-IN-NDT
```

### 2. Create and Activate Virtual Environment
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install Dependencies
```powershell
python -m pip install -r requirements.txt
python -m pip install -r requirements-build.txt
```

### 4. Run Automated Test Suite
```powershell
python -m pytest tests/ -v
```

### 5. Launch Application
- **In Browser Mode:**
  ```powershell
  streamlit run app.py
  ```
- **In Desktop App Mode:**
  ```powershell
  python launcher.py
  ```
