import os
import sqlite3
import datetime
import pandas as pd

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "assessment_history.db")
CSV_BACKUP_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "assessment_history.csv")

def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

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
    
    # Also sync to CSV backup
    sync_csv_backup()

def get_all_assessments():
    init_db()
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM assessment_history ORDER BY id DESC", conn)
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
        df.to_csv(CSV_BACKUP_PATH, index=False)
    except Exception as e:
        print("CSV backup sync warning:", e)
