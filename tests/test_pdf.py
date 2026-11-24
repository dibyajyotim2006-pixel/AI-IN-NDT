import pytest
from utils.pdf_generator import generate_pdf_report

def test_pdf_generation_validity():
    pdf_bytes = generate_pdf_report(
        sample_id="TEST-C001",
        age=28.0,
        rebound_index=35.0,
        upv=4250.0,
        predicted_strength=34.20,
        assessment="Good Quality (Standard Structural Concrete)",
        upv_grade="Good",
        strength_class="Standard Structural Concrete",
        project_name="Automated Test Project",
        inspector_name="QA Specialist",
        location="Lab"
    )
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 2000
    # Must start with standard PDF header
    assert pdf_bytes.startswith(b"%PDF-")
