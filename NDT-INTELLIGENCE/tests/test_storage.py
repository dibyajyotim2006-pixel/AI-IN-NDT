import pytest
import os
import sqlite3
import pandas as pd
from utils.storage import init_db, save_assessment, get_all_assessments, get_connection

def test_database_initialization():
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='assessment_history'")
    table = cursor.fetchone()
    conn.close()
    assert table is not None

def test_save_and_retrieve_assessment():
    init_db()
    test_id = "TEST-SPECIMEN-99"
    save_assessment(
        sample_id=test_id,
        age=28.0,
        rebound_index=36.0,
        upv=4350.0,
        predicted_strength=32.50,
        assessment="Good Quality (Standard Structural Concrete)",
        upv_grade="Good",
        strength_class="Standard Structural Concrete",
        project_name="Unit Test Project",
        inspector_name="Tester",
        location="Lab Testing Rack"
    )
    df = get_all_assessments()
    assert not df.empty
    matched = df[df["sample_id"] == test_id]
    assert len(matched) >= 1
    assert matched.iloc[0]["predicted_strength"] == pytest.approx(32.50)
