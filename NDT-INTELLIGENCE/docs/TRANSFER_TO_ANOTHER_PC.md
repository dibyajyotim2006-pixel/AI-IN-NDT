# Transferring NDT Intelligence to Another PC

This guide describes how to deploy the packaged **NDT Intelligence** desktop application to any target Windows 10 or Windows 11 PC **without installing Python, pip, or running terminal commands**.

---

## 1. System Requirements

| Requirement | Target Specification |
| :--- | :--- |
| **Operating System** | Windows 10 (64-bit build 1809+) or Windows 11 (64-bit) |
| **Architecture** | x86_64 / AMD64 |
| **RAM** | 4 GB minimum (8 GB recommended) |
| **Disk Space** | ~400 MB free disk space |
| **Dependencies** | Microsoft Edge WebView2 (Pre-installed out-of-the-box on Windows 11 and modern Windows 10) |
| **Network** | **Fully Offline** (No internet connection or external API calls required) |

---

## 2. Transfer Steps (USB Flash Drive / Network Share)

### Step 1: Obtain the Distribution Package
Copy `NDT_Intelligence_v1.0.0_win64.zip` to a USB drive or shared network folder.

### Step 2: Copy to Target PC
Paste the zip file onto the target PC (e.g., in `C:\Program Files\`, `C:\NDT Intelligence\`, or on the user's `Desktop`).

### Step 3: Extract the Archive
Right-click `NDT_Intelligence_v1.0.0_win64.zip` and select **Extract All...**.

### Step 4: Launch the Application
1. Open the extracted folder: `NDT Intelligence/`.
2. Locate and double-click `NDT Intelligence.exe` (identified with the blue acoustic sensor icon).
3. The native desktop application will initialize and open automatically.

> [!TIP]
> **Optional Desktop Shortcut:** Right-click `NDT Intelligence.exe` → **Send to** → **Desktop (create shortcut)** for one-click access.

---

## 3. Persistent Data Storage & History Backups

The application separates read-only binaries from user-generated field data:
- **Application Binaries & Model:** Located in the extracted folder (`dist/NDT Intelligence/`).
- **User Data & SQLite Database:** Located in `%LOCALAPPDATA%\NDT Intelligence\`:
  - `db/assessment_history.db`: SQLite database storing all logged concrete field evaluations.
  - `db/assessment_history.csv`: Automated flat-file backup of all records.
  - `logs/app.log`: Application runtime and diagnostic logs.
  - `exports/`: Saved CSV/Excel inspection batches.

### Migrating History Between PCs:
To transfer previous inspection records to another computer:
1. Open File Explorer and paste `%LOCALAPPDATA%\NDT Intelligence` in the address bar.
2. Copy the `db\` folder to the same location on the new machine.

---

## 4. Troubleshooting & FAQ

#### Q1: Does the target PC need Python installed?
**No.** All Python runtimes, C-extensions, Scikit-learn models, and UI dependencies are bundled in the distribution folder.

#### Q2: Windows Defender or SmartScreen shows "Unrecognized App"?
Because this is a bespoke university / research build without a purchased commercial EV code-signing certificate, Windows SmartScreen may display an advisory prompt:
1. Click **More info**.
2. Click **Run anyway**.

#### Q3: What happens if port 8501 is already in use by another app?
The desktop launcher dynamically detects and binds to any free ephemeral port on `127.0.0.1` (localhost), ensuring there are no port collision failures.
