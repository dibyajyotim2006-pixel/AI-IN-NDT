import os
import sqlite3
import datetime
import shutil
import pandas as pd
from paths import get_db_path, get_csv_backup_path, resource_path

# SQLite configuration:
# Rollback journal mode (DELETE) with a 30-second busy timeout is deliberately chosen over WAL mode.
# Rationale: On Windows desktop installations, WAL mode creates memory-mapped `-shm` and `-wal` files
# that often cause file-locking issues, process crash recovery failures, and antivirus inspection locks.
# Rollback journal guarantees clean, single-file ACID transactions without dangling lock files.
BUSY_TIMEOUT_SECONDS = 30.0

def get_connection():
    db_file = get_db_path()
    os.makedirs(os.path.dirname(db_file), exist_ok=True)
    
    try:
        conn = sqlite3.connect(db_file, timeout=BUSY_TIMEOUT_SECONDS, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=DELETE;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        return conn
    except (sqlite3.DatabaseError, sqlite3.OperationalError) as e:
        # Graceful handling of corrupt or locked database
        if "corrupt" in str(e).lower() or "malformed" in str(e).lower():
            recover_corrupt_database(db_file)
            conn = sqlite3.connect(db_file, timeout=BUSY_TIMEOUT_SECONDS, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            return conn
        raise

def recover_corrupt_database(db_file: str):
    """
    Safely preserves corrupt DB by renaming with timestamp before initializing a fresh DB.
    Never deletes user data.
    """
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    corrupt_backup = f"{db_file}.corrupt-{ts}"
    try:
        if os.path.exists(db_file):
            shutil.move(db_file, corrupt_backup)
            print(f"[RECOVERY] Corrupt database preserved at: {corrupt_backup}")
    except Exception as err:
        print(f"[RECOVERY ERROR] Could not rename corrupt DB: {err}")

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS assessment_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sample_id TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            age REAL NOT NULL,
            rebound_index REAL NOT NULL,
            upv REAL NOT NULL,
            predicted_strength REAL NOT NULL,
            assessment TEXT NOT NULL,
            upv_grade TEXT NOT NULL,
            strength_class TEXT,
            project_name TEXT DEFAULT 'Standard Inspection',
            inspector_name TEXT DEFAULT 'NDT Engineer',
            location TEXT DEFAULT 'Site Area'
        )
    """)
    conn.commit()
    
    # Check if empty, seed initial inspection history if so
    cursor.execute("SELECT COUNT(*) FROM assessment_history")
    count = cursor.fetchone()[0]
    if count == 0:
        seed_initial_records(conn)
    conn.close()

def seed_initial_records(conn):
    sample_data = [
        ("C001", "2026-11-20 09:30:00", 1.0, 21.3, 3649.0, 7.41, "Medium / Satisfactory Quality (Early-Age Curing Concrete)", "Medium / Satisfactory", "Early-Age Curing (< 15 MPa)", "Pier Pier-04 Quality Audit", "Er. K. Sharma", "Metro Corridor Block B"),
        ("C012", "2026-11-21 11:15:00", 7.0, 28.5, 4120.0, 21.80, "Good Quality (Moderate Strength Concrete (15 - 25 MPa))", "Good", "Moderate Strength Concrete (15 - 25 MPa)", "Bridge Deck Cast Test", "Er. K. Sharma", "Flyover Pier Cap"),
        ("C028", "2026-11-22 14:00:00", 28.0, 38.5, 4520.0, 39.40, "Excellent Quality (High-Strength Structural Concrete)", "Excellent", "High-Strength Structural Concrete (35 - 50 MPa)", "Commercial Tower Slab C3", "Er. R. Verma", "Sector 62 Commercial Hub"),
        ("C035", "2026-11-23 16:45:00", 28.0, 44.2, 4750.0, 48.90, "Excellent Quality (High-Strength Structural Concrete)", "Excellent", "High-Strength Structural Concrete (35 - 50 MPa)", "Prestressed Girder G-12", "Er. D. Sen", "Precast Yard 2"),
        ("C042", "2026-11-24 10:20:00", 14.0, 34.0, 4310.0, 29.50, "Good Quality (Standard Structural Concrete (25 - 35 MPa))", "Good", "Standard Structural Concrete (25 - 35 MPa)", "Basement Retaining Wall", "Er. D. Sen", "Tower B Substructure")
    ]
    cursor = conn.cursor()
    cursor.executemany("""
        INSERT INTO assessment_history 
        (sample_id, timestamp, age, rebound_index, upv, predicted_strength, assessment, upv_grade, strength_class, project_name, inspector_name, location)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, sample_data)
    conn.commit()

def save_assessment(sample_id, age, rebound_index, upv, predicted_strength, assessment, upv_grade, strength_class=None, project_name=None, inspector_name=None, location=None):
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    project = project_name.strip() if project_name and project_name.strip() else "Structural Field Assessment"
    inspector = inspector_name.strip() if inspector_name and inspector_name.strip() else "Lead NDT Inspector"
    loc = location.strip() if location and location.strip() else "Main Construction Sector"
    
    cursor.execute("""
        INSERT INTO assessment_history 
        (sample_id, timestamp, age, rebound_index, upv, predicted_strength, assessment, upv_grade, strength_class, project_name, inspector_name, location)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        str(sample_id),
        timestamp,
        float(age),
        float(rebound_index),
        float(upv),
        float(predicted_strength),
        str(assessment),
        str(upv_grade),
        str(strength_class or ""),
        project,
        inspector,
        loc
    ))
    conn.commit()
    conn.close()
    
    # Sync backup copy to user data dir
    sync_csv_backup()

def get_all_assessments():
    init_db()
    conn = get_connection()
    try:
        df = pd.read_sql_query("SELECT * FROM assessment_history ORDER BY id DESC", conn)
    finally:
        conn.close()
    return df

def delete_assessment(assessment_id):
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM assessment_history WHERE id = ?", (assessment_id,))
    conn.commit()
    conn.close()
    sync_csv_backup()

def sync_csv_backup():
    try:
        conn = get_connection()
        df = pd.read_sql_query("SELECT * FROM assessment_history ORDER BY id DESC", conn)
        conn.close()
        csv_file = get_csv_backup_path()
        os.makedirs(os.path.dirname(csv_file), exist_ok=True)
        df.to_csv(csv_file, index=False)
    except Exception as e:
        print("[STORAGE WARNING] CSV backup sync error:", e)
