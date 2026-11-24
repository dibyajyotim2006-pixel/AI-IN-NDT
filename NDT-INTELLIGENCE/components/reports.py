import streamlit as st
import pandas as pd
import datetime
from utils.storage import get_all_assessments
from utils.pdf_generator import generate_pdf_report
from model.predictor import predict_concrete_strength, validate_inputs

def render_reports():
    st.markdown("""
    <div style="margin-bottom: 25px;">
        <h1 style="margin: 0; color: #FFFFFF; font-size: 2.2rem; font-weight: 700; letter-spacing: -0.5px;">
            PDF Assessment Report Generator
        </h1>
        <p style="margin: 5px 0 0 0; color: #94A3B8; font-size: 1rem;">
            Generate formal, certified civil engineering Non-Destructive Testing assessment reports
        </p>
    </div>
    """, unsafe_allow_html=True)

    df_history = get_all_assessments()

    # Mode selection: From History or Custom / Manual Entry
    report_source = st.radio(
        "Report Source Selection:",
        options=["Select from Logged Field Assessments", "Enter Manual Inspection Data"],
        horizontal=True
    )

    if report_source == "Select from Logged Field Assessments":
        if df_history.empty:
            st.warning("No field assessments found in database. Switch to 'Enter Manual Inspection Data' or run a prediction first.")
            return

        st.markdown("""
        <div style="background-color: #1E293B; border-radius: 10px; border: 1px solid #334155; padding: 18px 20px 10px 20px; margin-bottom: 20px;">
            <div style="font-size: 1.1rem; font-weight: 600; color: #FFFFFF; margin-bottom: 4px;">
                Select Assessment Record
            </div>
            <div style="font-size: 0.85rem; color: #94A3B8; margin-bottom: 12px;">
                Choose an evaluated concrete specimen from the local SQLite history
            </div>
        """, unsafe_allow_html=True)

        sample_options = [
            f"{row['sample_id']} - {row['timestamp']} | Age: {row['age']}d | UPV: {row['upv']:.0f} m/s | {row['predicted_strength']} MPa ({row['upv_grade']})"
            for _, row in df_history.iterrows()
        ]
        selected_option = st.selectbox("Inspection Records", sample_options)
        selected_index = sample_options.index(selected_option)
        rec = df_history.iloc[selected_index]

        st.markdown("</div>", unsafe_allow_html=True)

        # Allow project customization
        c1, c2, c3 = st.columns(3)
        with c1:
            project_name = st.text_input("Project Name", value=rec.get("project_name", "Metro Viaduct Audit"))
        with c2:
            inspector_name = st.text_input("Lead NDT Engineer", value=rec.get("inspector_name", "Er. Kiran N. (Civil QA/QC)"))
        with c3:
            location = st.text_input("Inspection Location", value=rec.get("location", "Sector 4 Pier Cap"))

        remarks = st.text_area(
            "Engineering Remarks & Technical Notes",
            value="Concrete demonstrates structural soundness compliant with IS 13311 acoustic criteria. No surface honeycombing detected in test area."
        )

        sample_id = rec["sample_id"]
        age = float(rec["age"])
        rebound = float(rec["rebound_index"])
        upv = float(rec["upv"])
        predicted_strength = float(rec["predicted_strength"])
        assessment = rec["assessment"]
        upv_grade = rec["upv_grade"]
        strength_class = rec.get("strength_class", "")

    else:
        # Manual data entry
        st.markdown("""
        <div style="background-color: #1E293B; border-radius: 10px; border: 1px solid #334155; padding: 18px 20px 10px 20px; margin-bottom: 20px;">
            <div style="font-size: 1.1rem; font-weight: 600; color: #FFFFFF; margin-bottom: 4px;">
                Manual Inspection Data Entry
            </div>
            <div style="font-size: 0.85rem; color: #94A3B8; margin-bottom: 12px;">
                Specify specimen measurements and project details for direct PDF generation
            </div>
        """, unsafe_allow_html=True)

        r_col1, r_col2, r_col3, r_col4 = st.columns(4)
        with r_col1:
            sample_id = st.text_input("Sample ID", value="C-FIELD-01")
        with r_col2:
            age = st.number_input("Curing Age (Days)", min_value=1.0, max_value=730.0, value=28.0, step=1.0)
        with r_col3:
            rebound = st.number_input("Rebound Index (R)", min_value=10.0, max_value=70.0, value=38.0, step=0.5)
        with r_col4:
            upv = st.number_input("UPV (m/s)", min_value=1500, max_value=5500, value=4450, step=25)

        c1, c2, c3 = st.columns(3)
        with c1:
            project_name = st.text_input("Project Name", value="Highway Flyover Quality Audit")
        with c2:
            inspector_name = st.text_input("Lead NDT Engineer", value="Er. Kiran N. (Chartered Engineer)")
        with c3:
            location = st.text_input("Location / Element", value="Pier Cap P-08, Grid A")

        remarks = st.text_area(
            "Engineering Remarks & Technical Notes",
            value="Combined Rebound Index and Ultrasonic Pulse Velocity indicate sound structural integrity with low internal porosity."
        )

        st.markdown("</div>", unsafe_allow_html=True)

        # Run AI prediction for this manual record
        pred = predict_concrete_strength(sample_id, age, rebound, upv)
        predicted_strength = pred["predicted_strength"]
        assessment = pred["assessment"]
        upv_grade = pred["upv_grade"]
        strength_class = pred["strength_class"]

    # Preview Card
    st.markdown("""
    <div style="background-color: #0F172A; border-radius: 10px; border: 1.5px solid #0284C7; padding: 22px 25px; margin-bottom: 25px;">
        <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #1E293B; padding-bottom: 10px; margin-bottom: 15px;">
            <div style="font-size: 1.2rem; font-weight: 700; color: #FFFFFF;">
                📄 Live Assessment Report Summary Preview
            </div>
            <div style="font-size: 0.8rem; background-color: #0369A1; color: white; padding: 4px 10px; border-radius: 4px; font-weight: 600;">
                READY FOR EXPORT
            </div>
        </div>
        
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 15px;">
            <div>
                <span style="color: #64748B; font-size: 0.85rem;">SAMPLE IDENTIFIER</span><br/>
                <strong style="color: #38BDF8; font-size: 1.1rem;">{sample_id}</strong>
            </div>
            <div>
                <span style="color: #64748B; font-size: 0.85rem;">CURING MATURITY</span><br/>
                <strong style="color: #E2E8F0; font-size: 1.1rem;">{age:.1f} Days</strong>
            </div>
            <div>
                <span style="color: #64748B; font-size: 0.85rem;">REBOUND HAMMER (R)</span><br/>
                <strong style="color: #E2E8F0; font-size: 1.1rem;">{rebound:.1f}</strong>
            </div>
            <div>
                <span style="color: #64748B; font-size: 0.85rem;">PULSE VELOCITY</span><br/>
                <strong style="color: #E2E8F0; font-size: 1.1rem;">{upv:.0f} m/s</strong>
            </div>
        </div>
        
        <div style="background-color: #1E293B; border-radius: 8px; padding: 15px; border-left: 4px solid #38BDF8;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <span style="color: #94A3B8; font-size: 0.85rem; font-weight: 600;">AI PREDICTED STRENGTH</span>
                    <div style="font-size: 2rem; font-weight: 800; color: #38BDF8;">
                        {strength:.2f} MPa
                    </div>
                </div>
                <div style="text-align: right;">
                    <span style="color: #94A3B8; font-size: 0.85rem; font-weight: 600;">QUALITY GRADE</span>
                    <div style="font-size: 1.2rem; font-weight: 700; color: #10B981;">
                        {upv_grade}
                    </div>
                    <div style="font-size: 0.85rem; color: #94A3B8;">{strength_class}</div>
                </div>
            </div>
        </div>
    </div>
    """.format(
        sample_id=sample_id,
        age=age,
        rebound=rebound,
        upv=upv,
        strength=predicted_strength,
        upv_grade=upv_grade,
        strength_class=strength_class
    ), unsafe_allow_html=True)

    # Generate PDF
    pdf_bytes = generate_pdf_report(
        sample_id=sample_id,
        age=age,
        rebound_index=rebound,
        upv=upv,
        predicted_strength=predicted_strength,
        assessment=assessment,
        upv_grade=upv_grade,
        strength_class=strength_class,
        project_name=project_name,
        inspector_name=inspector_name,
        location=location,
        notes=remarks
    )

    st.download_button(
        label=f"📥 Download Official PDF Report: NDT-{sample_id}.pdf",
        data=pdf_bytes,
        file_name=f"NDT_Assessment_Report_{sample_id}.pdf",
        mime="application/pdf",
        type="primary",
        use_container_width=True
    )
