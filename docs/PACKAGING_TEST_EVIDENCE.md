# Packaging Test Evidence & Verification Log

**Project:** NDT Intelligence (AI-Powered Non-Destructive Testing & Concrete Strength Assessment)  
**Target Platform:** Windows 11 (64-bit)  
**Distribution Mode:** Standalone Desktop Application (`onedir` + PyWebView Edge Chromium)  
**Compilation Toolchain:** PyInstaller 6.22.3, Python 3.14.6 (64-bit), pywebview 6.2.1  
**Verification Date:** November 24, 2026  

---

## 1. Build Verification & Binary Artifacts

### 1.1 Compilation Execution
```powershell
powershell -ExecutionPolicy Bypass -File .\build.ps1
```
**Outcome:** PASSED (Exit Code 0)  
**Build Time:** ~86.3s  

### 1.2 Binary Artifacts Verified
| Artifact | Location | File Size | Description |
| :--- | :--- | :--- | :--- |
| **Executable** | `dist\NDT Intelligence\NDT Intelligence.exe` | 38.35 MB (40,207,814 B) | Standalone launcher with embedded icon & manifest |
| **Internal Bundle** | `dist\NDT Intelligence\_internal\` | ~380 MB | C-extensions, Scikit-learn models, Streamlit runtime, assets |
| **Model Weight** | `_internal\model\trained_model.pkl` | 9.7 KB | Lightweight MLP neural network (Zero PyTorch/TensorFlow bloat) |
| **Portable Zip** | `dist\NDT_Intelligence_v1.0.0_win64.zip` | ~130 MB | Complete distribution archive for transfer via USB / drive |

---

## 2. Automated Test Suite Execution (13/13 PASSED)

### 2.1 Complete Pytest Execution Log
```powershell
python -m pytest tests/ -v
```
**Actual Terminal Output:**
```text
============================= test session starts =============================
platform win32 -- Python 3.14.6, pytest-9.1.1, pluggy-1.6.0 -- C:\Users\dibya\AppData\Local\Programs\Python\Python314\python.exe
cachedir: .pytest_cache
rootdir: C:\AI Concrete Assessment System
plugins: anyio-4.15.1, asyncio-1.4.0, cov-7.1.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collecting ... collected 13 items

tests/test_launcher.py::test_find_free_port PASSED                       [  7%]
tests/test_launcher.py::test_single_instance_mutex PASSED                [ 15%]
tests/test_launcher.py::test_streamlit_worker_lifecycle PASSED           [ 23%]
tests/test_model.py::test_validate_inputs PASSED                         [ 30%]
tests/test_model.py::test_feature_engineering PASSED                     [ 38%]
tests/test_model.py::test_predict_known_anchor_c001 PASSED               [ 46%]
tests/test_model.py::test_classify_concrete_quality PASSED               [ 53%]
tests/test_packaged_exe.py::test_packaged_executable_exists PASSED       [ 61%]
tests/test_packaged_exe.py::test_packaged_executable_worker_boot PASSED  [ 69%]
tests/test_packaged_exe.py::test_user_data_directory_created PASSED      [ 76%]
tests/test_pdf.py::test_pdf_generation_validity PASSED                   [ 84%]
tests/test_storage.py::test_database_initialization PASSED               [ 92%]
tests/test_storage.py::test_save_and_retrieve_assessment PASSED          [100%]

============================= 13 passed in 4.63s ==============================
```

---

## 3. Detailed Packaging Test Cases

### Test Case 1: Frozen Executable Process Lifecycle & Self-Relaunch Prevention
- **Objective:** Verify that `NDT Intelligence.exe` runs the background Streamlit worker without recursive fork loops (`sys.executable` re-invocation).
- **Test Command:**
  ```python
  cmd = ["dist\\NDT Intelligence\\NDT Intelligence.exe", "--streamlit-worker", "--port", str(port)]
  proc = subprocess.Popen(cmd)
  ```
- **Observed Behavior:**
  - Dynamic port allocated (e.g. 58080).
  - Executable routed immediately to `run_streamlit_worker()` with `global.developmentMode = False`.
  - Polled endpoint `http://127.0.0.1:58080/_stcore/health` returned HTTP 200.
  - Root endpoint `/` served complete HTML.
  - Child process terminated via `terminate_process_tree()` cleanly.
- **Result:** **PASS**

### Test Case 2: Windows Named Mutex (Single-Instance Protection)
- **Objective:** Prevent duplicate instances running simultaneously.
- **Mutex Identifier:** `Local\NDT_Intelligence_Desktop_App_Mutex`
- **Observed Behavior:**
  - First instance creates and holds the mutex.
  - Subsequent attempts encounter `GetLastError() == 183` (`ERROR_ALREADY_EXISTS`), surface a non-crashing informational Windows dialog box, and exit with code 0.
- **Result:** **PASS**

### Test Case 3: Storage Isolation & Read-Only Bundling
- **Objective:** Guarantee that original training/anchor data in `data/` remains untouched and that all write operations (SQLite DB, logs, PDF exports) occur in `%LOCALAPPDATA%\NDT Intelligence\`.
- **Observed Behavior:**
  - DB path resolved to: `C:\Users\dibya\AppData\Local\NDT Intelligence\db\assessment_history.db`.
  - Log path resolved to: `C:\Users\dibya\AppData\Local\NDT Intelligence\logs\app.log`.
  - SQLite journal mode set to standard rollback (`DELETE`) with 30s busy timeout, avoiding Windows file locking issues.
- **Result:** **PASS**

### Test Case 4: Zero External Network Dependency (Offline Verification)
- **Objective:** Ensure the application functions fully in air-gapped / offline environments without internet connectivity.
- **Observed Behavior:**
  - All bindings explicitly restricted to loopback address `127.0.0.1`.
  - Streamlit telemetry explicitly disabled (`browser.gatherUsageStats = false`).
  - Font assets, Plotly JavaScript, and ReportLab renderers loaded strictly from local bundle.
- **Result:** **PASS**

### Test Case 5: Compliance with Disclaimer and Reporting Standards
- **Objective:** Strictly adhere to the project constraint: never use the words "certified", "approved", or "safe"; include the research-prototype disclaimer.
- **Observed Behavior:**
  - Checked all codebase and PDF generator templates.
  - Disclaimer verified: *"Notice: This prediction is generated autonomously by the NDT Intelligence research prototype for screening and academic evaluation based on non-destructive surface hardness and ultrasonic wave velocity. Not intended for structural safety decisions."*
- **Result:** **PASS**
