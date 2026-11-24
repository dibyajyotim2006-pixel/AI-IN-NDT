import os
import sys
from pathlib import Path

# Switch to control dev data vs local app data
# Set NDT_USE_DEV_DATA=1 in environment if a local ./dev_data/ directory is preferred during testing
USE_LOCAL_DEV_DATA = os.environ.get("NDT_USE_DEV_DATA", "0").lower() in ("1", "true")

def get_base_dir() -> str:
    """Returns the base directory of the application: sys._MEIPASS when frozen, else project root."""
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        return getattr(sys, '_MEIPASS')
    return os.path.dirname(os.path.abspath(__file__))

def resource_path(relative_path: str) -> str:
    """
    Get absolute path to read-only bundled resource.
    Works for dev and for PyInstaller onedir/onefile bundles.
    """
    base_path = get_base_dir()
    clean_rel = relative_path.replace("/", os.sep).replace("\\", os.sep).lstrip(os.sep)
    return os.path.normpath(os.path.join(base_path, clean_rel))

def user_data_dir() -> str:
    """
    Returns the persistent user data directory:
    Windows: %LOCALAPPDATA%\\NDT Intelligence\\
    Ensures db/, logs/, exports/, and reports/ subfolders exist.
    """
    if USE_LOCAL_DEV_DATA:
        base = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dev_data")
    else:
        local_app_data = os.environ.get("LOCALAPPDATA")
        if not local_app_data:
            local_app_data = os.path.expanduser("~")
        base = os.path.join(local_app_data, "NDT Intelligence")

    # Create directory structure
    for sub in ["db", "logs", "exports", "reports"]:
        os.makedirs(os.path.join(base, sub), exist_ok=True)

    return os.path.normpath(base)

def get_db_path() -> str:
    return os.path.join(user_data_dir(), "db", "assessment_history.db")

def get_csv_backup_path() -> str:
    return os.path.join(user_data_dir(), "db", "assessment_history.csv")

def get_log_path() -> str:
    return os.path.join(user_data_dir(), "logs", "app.log")

def get_exports_dir() -> str:
    return os.path.join(user_data_dir(), "exports")

def get_reports_dir() -> str:
    return os.path.join(user_data_dir(), "reports")

def get_model_path() -> str:
    return resource_path("model/trained_model.pkl")

def get_dataset_path() -> str:
    return resource_path("data/concrete_samples.csv")

def get_evaluated_dataset_path() -> str:
    return resource_path("data/concrete_samples_evaluated.csv")
