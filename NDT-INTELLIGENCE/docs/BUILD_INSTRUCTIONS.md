# NDT Intelligence - Build Instructions

Instructions for compiling the standalone Windows 11 executable distribution from source using PyInstaller.

---

## 1. Build Environment Requirements
- **Host OS:** Windows 10 / 11 (64-bit)
- **Python:** 3.10 - 3.14 (64-bit)
- **Key Build Tools:** `pyinstaller>=6.0.0`, `pywebview>=5.0.0`, `psutil>=5.9.0`, `pillow>=10.0.0`

---

## 2. Automated One-Command Build
Run the included PowerShell build script:
```powershell
powershell -ExecutionPolicy Bypass -File .\build.ps1
```

This script:
1. Removes previous `build/` and `dist/NDT Intelligence/` artifacts.
2. Invokes `assets/make_icon.py` to regenerate the multi-resolution `.ico` icon file.
3. Compiles the application via PyInstaller using `NDT_Intelligence.spec`.

---

## 3. Build Configuration Specification (`NDT_Intelligence.spec`)
- **Distribution Mode:** `onedir` (Standalone folder with all necessary DLLs, runtimes, and models).
- **Console Setting:** `console=False` (Prevents terminal window from appearing).
- **Process Isolation:** The launcher process coordinates with `multiprocessing.freeze_support()` and executes Streamlit via direct `bootstrap.run()`, eliminating frozen process fork loops.
- **Bundled Assets:**
  - `data/`: Read-only anchor samples and calibration datasets.
  - `model/`: Scikit-learn MLP artificial neural network model (`trained_model.pkl`).
  - `components/`: UI view modules.
  - `utils/`: SQLite storage and ReportLab PDF generators.
  - `assets/`: Icons and brand graphics.

---

## 4. Packaging as a Distribution Zip
To create the portable archive for distribution:
```powershell
Compress-Archive -Path "dist\NDT Intelligence\*" -DestinationPath "dist\NDT_Intelligence_v1.0.0_win64.zip" -Force
```
