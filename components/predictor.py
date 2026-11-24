import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from model.predictor import predict_concrete_strength, validate_inputs
from utils.storage import save_assessment, get_all_assessments
from utils.pdf_generator import generate_pdf_report

def render_predictor():
    st.markdown("""
    <div style="margin-bottom: 25px;">
        <h1 style="margin: 0; color: #FFFFFF; font-size: 2.2rem; font-weight: 700; letter-spacing: -0.5px;">
            AI Compressive Strength Predictor
        </h1>
        <p style="margin: 5px 0 0 0; color: #94A3B8; font-size: 1rem;">
            Artificial Neural Network estimation based on combined SonReb Non-Destructive Testing
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Preset selector for fast faculty/demonstration tests
    st.markdown("""
    <div style="background-color: #1E293B; border-radius: 8px; border: 1px solid #334155; padding: 12px 18px; margin-bottom: 20px;">
        <div style="font-size: 0.9rem; font-weight: 600; color: #38BDF8; margin-bottom: 8px;">
            QUICK LOAD EXPERIMENTAL PRESETS
        </div>
    </div>
    """, unsafe_allow_html=True)

    p_col1, p_col2, p_col3, p_col4 = st.columns(4)
    with p_col1:
        if st.button("Anchor C001 (1d Early)", use_container_width=True):
            st.session_state["p_sample_id"] = "C001"
            st.session_state["p_age"] = 1.0
            st.session_state["p_rebound"] = 21.3
            st.session_state["p_upv"] = 3649
    with p_col2:
        if st.button("Anchor C003 (1d Early)", use_container_width=True):
            st.session_state["p_sample_id"] = "C003"
            st.session_state["p_age"] = 1.0
            st.session_state["p_rebound"] = 23.9
            st.session_state["p_upv"] = 3592
    with p_col3:
        if st.button("Standard M30 (28d)", use_container_width=True):
            st.session_state["p_sample_id"] = "C-M30"
            st.session_state["p_age"] = 28.0
            st.session_state["p_rebound"] = 38.5
            st.session_state["p_upv"] = 4510
    with p_col4:
        if st.button("High-Performance (56d)", use_container_width=True):
            st.session_state["p_sample_id"] = "C-HPC56"
            st.session_state["p_age"] = 56.0
            st.session_state["p_rebound"] = 48.0
            st.session_state["p_upv"] = 4850

    # Default values from session state or fallbacks
    init_sample_id = st.session_state.get("p_sample_id", "C001")
    init_age = float(st.session_state.get("p_age", 1.0))
    init_rebound = float(st.session_state.get("p_rebound", 21.3))
    init_upv = int(st.session_state.get("p_upv", 3649))

    # Form layout
    col_form, col_meta = st.columns([1.5, 1])

    with col_form:
        st.markdown("""
        <div style="background-color: #1E293B; border-radius: 10px; border: 1px solid #334155; padding: 20px 22px 10px 22px; margin-bottom: 20px;">
            <div style="font-size: 1.15rem; font-weight: 600; color: #FFFFFF; margin-bottom: 4px;">
                Non-Destructive Test Input Parameters
            </div>
            <div style="font-size: 0.85rem; color: #94A3B8; margin-bottom: 18px;">
                Enter verified field measurements according to ASTM C805 and IS 13311 protocols
            </div>
        """, unsafe_allow_html=True)

        sample_id_input = st.text_input("Sample Identifier / Specimen Code", value=init_sample_id, help="Unique sample identifier (e.g. C001, C015, PIER-4A)")

        row_c1, row_c2 = st.columns(2)
        with row_c1:
            age_input = st.number_input(
                "Concrete Curing Age (Days)",
                min_value=0.5,
                max_value=730.0,
                value=init_age,
                step=1.0,
                format="%.1f",
                help="Age since casting in standard curing conditions"
            )
        with row_c2:
            rebound_input = st.number_input(
                "Rebound Hammer Index (R)",
                min_value=10.0,
                max_value=70.0,
                value=init_rebound,
                step=0.1,
                format="%.1f",
                help="Average rebound hammer reading (ASTM C805 / IS 13311 Part 2)"
            )

        upv_input = st.number_input(
            "Ultrasonic Pulse Velocity - UPV (m/s)",
            min_value=1500,
            max_value=5500,
            value=init_upv,
            step=10,
            help="Direct acoustic transmission velocity in meters per second (IS 13311 Part 1)"
        )

        st.markdown("</div>", unsafe_allow_html=True)

    with col_meta:
        st.markdown("""
        <div style="background-color: #1E293B; border-radius: 10px; border: 1px solid #334155; padding: 20px 22px 10px 22px; margin-bottom: 20px;">
            <div style="font-size: 1.15rem; font-weight: 600; color: #FFFFFF; margin-bottom: 4px;">
                Project Inspection Metadata
            </div>
            <div style="font-size: 0.85rem; color: #94A3B8; margin-bottom: 18px;">
                Included in the official engineering assessment report
            </div>
        """, unsafe_allow_html=True)

        project_name_input = st.text_input("Project / Structure Name", value="Metro Infrastructure Viaduct Audit")
        inspector_name_input = st.text_input("Lead NDT Testing Engineer", value="Er. Kiran N. (Civil QA/QC)")
        location_input = st.text_input("Inspection Location / Element", value="Pier Cap P-14 / Sector 5")

        st.markdown("</div>", unsafe_allow_html=True)

    # Predict Button
    predict_clicked = st.button("⚡ Run AI Strength Prediction", use_container_width=True, type="primary")

    # If predicted or already in session state
    if predict_clicked or "last_prediction" in st.session_state:
        # If user clicked, perform new prediction
        if predict_clicked:
            is_valid, err_msg = validate_inputs(age_input, rebound_input, upv_input)
            if not is_valid:
                st.error(f"❌ Input Validation Error: {err_msg}")
                return

            try:
                pred_result = predict_concrete_strength(
                    sample_id=sample_id_input,
                    age=age_input,
                    rebound_index=rebound_input,
                    upv=upv_input
                )
                
                # Save to persistent history database
                save_assessment(
                    sample_id=pred_result["sample_id"],
                    age=pred_result["age"],
                    rebound_index=pred_result["rebound_index"],
                    upv=pred_result["upv"],
                    predicted_strength=pred_result["predicted_strength"],
                    assessment=pred_result["assessment"],
                    upv_grade=pred_result["upv_grade"],
                    strength_class=pred_result["strength_class"],
                    project_name=project_name_input,
                    inspector_name=inspector_name_input,
                    location=location_input
                )
                st.session_state["last_prediction"] = pred_result
                st.session_state["last_meta"] = {
                    "project_name": project_name_input,
                    "inspector_name": inspector_name_input,
                    "location": location_input
                }
                st.toast(f"✅ Prediction complete for {sample_id_input}: {pred_result['predicted_strength']} MPa", icon="🎉")
            except Exception as e:
                st.error(f"Prediction Error: {str(e)}")
                return
        else:
            pred_result = st.session_state["last_prediction"]

        meta_info = st.session_state.get("last_meta", {
            "project_name": project_name_input,
            "inspector_name": inspector_name_input,
            "location": location_input
        })

        st.markdown("<div style='height: 25px;'></div>", unsafe_allow_html=True)

        # 1. Prediction Hero Section
        st.markdown("""
        <div style="background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%); border-radius: 12px; border: 2px solid #38BDF8; padding: 25px 30px; margin-bottom: 25px; box-shadow: 0 10px 25px -5px rgba(2, 132, 199, 0.2);">
            <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #334155; padding-bottom: 12px; margin-bottom: 18px;">
                <div>
                    <span style="font-size: 0.85rem; letter-spacing: 1.5px; color: #38BDF8; font-weight: 700; text-transform: uppercase;">AI PREDICTION RESULT</span>
                    <h2 style="margin: 4px 0 0 0; color: #FFFFFF; font-size: 1.8rem; font-weight: 700;">SAMPLE: {sample_id}</h2>
                </div>
                <div style="text-align: right;">
                    <span style="background-color: #064E3B; color: #34D399; font-size: 0.85rem; font-weight: 600; padding: 5px 12px; border-radius: 20px; border: 1px solid #059669;">
                        ● Status: {status}
                    </span>
                </div>
            </div>
            
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 20px; align-items: center;">
                <div style="background-color: rgba(15, 23, 42, 0.7); border-radius: 10px; border: 1px solid #1E3A8A; padding: 20px; text-align: center;">
                    <div style="font-size: 0.9rem; color: #94A3B8; font-weight: 600; margin-bottom: 6px;">PREDICTED COMPRESSIVE STRENGTH</div>
                    <div style="font-size: 3.2rem; font-weight: 800; color: #38BDF8; line-height: 1.1;">
                        {strength:.2f} <span style="font-size: 1.5rem; color: #93C5FD; font-weight: 600;">MPa</span>
                    </div>
                    <div style="font-size: 0.85rem; color: #64748B; margin-top: 8px;">6-6-1 Sigmoid Artificial Neural Network</div>
                </div>
                
                <div style="background-color: rgba(15, 23, 42, 0.7); border-radius: 10px; border: 1px solid #334155; padding: 20px;">
                    <div style="font-size: 0.85rem; color: #94A3B8; font-weight: 600; margin-bottom: 6px;">INDICATIVE ASSESSMENT</div>
                    <div style="font-size: 1.3rem; font-weight: 700; color: {badge_color}; margin-bottom: 8px;">
                        {assessment}
                    </div>
                    <div style="font-size: 0.9rem; color: #E2E8F0; line-height: 1.4;">
                        <strong>Pulse Velocity:</strong> {upv:.0f} m/s ({upv_grade})<br/>
                        <strong>Rebound Index:</strong> {rebound:.1f}<br/>
                        <strong>Concrete Maturity:</strong> {age:.1f} Days Curing
                    </div>
                </div>
            </div>
        </div>
        """.format(
            sample_id=pred_result["sample_id"],
            status=pred_result["status"],
            strength=pred_result["predicted_strength"],
            badge_color=pred_result["upv_color"],
            assessment=pred_result["assessment"],
            upv=pred_result["upv"],
            upv_grade=pred_result["upv_grade"],
            rebound=pred_result["rebound_index"],
            age=pred_result["age"]
        ), unsafe_allow_html=True)

        # 2. Feature Engineering Technical Breakdown
        with st.expander("🔬 View Engineered ANN Features (6 Inputs Breakdown)", expanded=True):
            f_dict = pred_result["features"]
            feat_df = pd.DataFrame([
                {"#": "1", "Feature Name": "Specimen Age", "Symbol": "Age", "Engineered Value": f"{f_dict['Age']:.2f}", "Unit": "Days", "Engineering Significance": "Hydration maturity timeline"},
                {"#": "2", "Feature Name": "Rebound Hammer Index", "Symbol": "R", "Engineered Value": f"{f_dict['Rebound_Index']:.2f}", "Unit": "Dimensionless", "Engineering Significance": "Near-surface hardness & compaction"},
                {"#": "3", "Feature Name": "Ultrasonic Pulse Velocity", "Symbol": "UPV", "Engineered Value": f"{f_dict['UPV']:.1f}", "Unit": "m/s", "Engineering Significance": "Elastic modulus & internal acoustic density"},
                {"#": "4", "Feature Name": "Acoustic Development Rate", "Symbol": "UPV / Age", "Engineered Value": f"{f_dict['UPV_over_Age']:.2f}", "Unit": "m/(s·d)", "Engineering Significance": "Initial acoustic velocity progression"},
                {"#": "5", "Feature Name": "Surface Hardening Rate", "Symbol": "R / Age", "Engineered Value": f"{f_dict['Rebound_over_Age']:.2f}", "Unit": "1/d", "Engineering Significance": "Rate of matrix crystallization at surface"},
                {"#": "6", "Feature Name": "Combined SonReb Cross-Term", "Symbol": "UPV × R", "Engineered Value": f"{f_dict['UPV_x_Rebound']:,.1f}", "Unit": "m·R/s", "Engineering Significance": "Non-linear interaction between core & surface"}
            ])
            st.dataframe(feat_df, hide_index=True, use_container_width=True)

        # 3. Visual Comparison With Historical Samples
        st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
        st.markdown("""
        <div style="background-color: #1E293B; border-radius: 10px; border: 1px solid #334155; padding: 18px 20px 10px 20px; margin-bottom: 15px;">
            <div style="font-size: 1.1rem; font-weight: 600; color: #FFFFFF; margin-bottom: 4px;">
                Visual Calibration Against Experimental Concrete Dataset
            </div>
            <div style="font-size: 0.85rem; color: #94A3B8;">
                Real-time positioning of sample <strong>{sample_id}</strong> relative to experimental concrete curing curves
            </div>
        </div>
        """.format(sample_id=pred_result["sample_id"]), unsafe_allow_html=True)

        try:
            df_samples = pd.read_csv("data/concrete_samples.csv")
            
            comp_fig = go.Figure()
            # Historical samples scatter
            comp_fig.add_trace(go.Scatter(
                x=df_samples['Age'],
                y=df_samples['Actual_Strength'],
                mode='markers',
                name='Experimental Database',
                marker=dict(
                    size=8,
                    color=df_samples['Rebound_Index'],
                    colorscale='Blues',
                    showscale=True,
                    colorbar=dict(title=dict(text="Rebound Index (R)", font=dict(color="#94A3B8"))),
                    opacity=0.7
                ),
                text=[f"Sample: {s}<br>Age: {a}d<br>Strength: {fc} MPa<br>UPV: {u} m/s" 
                      for s, a, fc, u in zip(df_samples['Sample_ID'], df_samples['Age'], df_samples['Actual_Strength'], df_samples['UPV'])],
                hoverinfo='text'
            ))

            # Current sample prediction marker
            comp_fig.add_trace(go.Scatter(
                x=[pred_result["age"]],
                y=[pred_result["predicted_strength"]],
                mode='markers+text',
                name=f'Predicted: {pred_result["sample_id"]}',
                text=[f"  ★ {pred_result['sample_id']} ({pred_result['predicted_strength']} MPa)"],
                textposition="top right",
                textfont=dict(color="#00F2FE", size=13, family="Segoe UI, sans-serif"),
                marker=dict(
                    symbol='star',
                    size=18,
                    color='#00F2FE',
                    line=dict(width=2, color='#FFFFFF')
                ),
                hoverinfo='text'
            ))

            comp_fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(15, 23, 42, 0.6)",
                font=dict(color="#E2E8F0", family="Segoe UI, sans-serif"),
                margin=dict(l=40, r=20, t=20, b=40),
                height=380,
                xaxis=dict(
                    title=dict(text="Concrete Curing Age (Days)", font=dict(size=12, color="#94A3B8")),
                    gridcolor="#334155",
                    tickfont=dict(color="#94A3B8")
                ),
                yaxis=dict(
                    title=dict(text="Compressive Strength (MPa)", font=dict(size=12, color="#94A3B8")),
                    gridcolor="#334155",
                    tickfont=dict(color="#94A3B8")
                ),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1,
                    font=dict(color="#E2E8F0")
                )
            )
            st.plotly_chart(comp_fig, use_container_width=True)
        except Exception as e:
            st.warning(f"Comparison plot unavailable: {e}")

        # 4. Instant Download PDF Report Action
        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
        pdf_bytes = generate_pdf_report(
            sample_id=pred_result["sample_id"],
            age=pred_result["age"],
            rebound_index=pred_result["rebound_index"],
            upv=pred_result["upv"],
            predicted_strength=pred_result["predicted_strength"],
            assessment=pred_result["assessment"],
            upv_grade=pred_result["upv_grade"],
            strength_class=pred_result["strength_class"],
            features=pred_result["features"],
            project_name=meta_info.get("project_name", "Metro Viaduct Audit"),
            inspector_name=meta_info.get("inspector_name", "Er. Kiran N."),
            location=meta_info.get("location", "Sector 5")
        )

        st.download_button(
            label=f"📄 Download Assessment Report for {pred_result['sample_id']} (PDF)",
            data=pdf_bytes,
            file_name=f"NDT_Assessment_Report_{pred_result['sample_id']}.pdf",
            mime="application/pdf",
            use_container_width=True,
            type="secondary"
        )
