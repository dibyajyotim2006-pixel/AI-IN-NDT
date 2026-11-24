import streamlit as st
import pandas as pd
import numpy as np
import os

def render_database():
    st.markdown("""
    <div style="margin-bottom: 25px;">
        <h1 style="margin: 0; color: #FFFFFF; font-size: 2.2rem; font-weight: 700; letter-spacing: -0.5px;">
            Experimental Sample Database
        </h1>
        <p style="margin: 5px 0 0 0; color: #94A3B8; font-size: 1rem;">
            Searchable experimental concrete testing repository with actual vs AI predicted compressive strengths
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Load evaluated or base samples
    evaluated_path = "data/concrete_samples_evaluated.csv"
    base_path = "data/concrete_samples.csv"
    
    if os.path.exists(evaluated_path):
        df = pd.read_csv(evaluated_path)
    elif os.path.exists(base_path):
        df = pd.read_csv(base_path)
        from model.predictor import get_model_bundle, engineer_features
        try:
            bundle = get_model_bundle()
            X = engineer_features(df)
            X_s = bundle["scaler_X"].transform(X)
            df["Predicted_Strength"] = np.round(bundle["pipeline"].predict(X_s), 2)
            df["Prediction_Error"] = np.round(df["Predicted_Strength"] - df["Actual_Strength"], 2)
        except Exception:
            pass
    else:
        st.error("No concrete samples dataset found.")
        return

    # Filter Sidebar / Controls
    st.markdown("""
    <div style="background-color: #1E293B; border-radius: 10px; border: 1px solid #334155; padding: 18px 20px 10px 20px; margin-bottom: 20px;">
        <div style="font-size: 1.1rem; font-weight: 600; color: #FFFFFF; margin-bottom: 4px;">
            Database Query & Multi-Parameter Filter Controls
        </div>
        <div style="font-size: 0.85rem; color: #94A3B8; margin-bottom: 14px;">
            Filter experimental concrete specimens by ID, curing maturity, surface hardness, and acoustic velocity
        </div>
    """, unsafe_allow_html=True)

    f_col1, f_col2, f_col3, f_col4 = st.columns([1.2, 1, 1.2, 1.2])

    with f_col1:
        search_id = st.text_input("🔍 Search Sample ID", placeholder="e.g. C001, C025, C100")

    with f_col2:
        all_ages = sorted(df['Age'].unique().tolist())
        selected_ages = st.multiselect("Curing Age (Days)", options=all_ages, default=all_ages)

    with f_col3:
        min_reb, max_reb = float(df['Rebound_Index'].min()), float(df['Rebound_Index'].max())
        reb_range = st.slider("Rebound Index (R)", min_value=min_reb, max_value=max_reb, value=(min_reb, max_reb), step=0.5)

    with f_col4:
        min_upv, max_upv = int(df['UPV'].min()), int(df['UPV'].max())
        upv_range = st.slider("UPV (m/s)", min_value=min_upv, max_value=max_upv, value=(min_upv, max_upv), step=25)

    st.markdown("</div>", unsafe_allow_html=True)

    # Filter Application
    filtered_df = df.copy()
    if search_id.strip():
        filtered_df = filtered_df[filtered_df['Sample_ID'].str.contains(search_id.strip(), case=False, na=False)]
    if selected_ages:
        filtered_df = filtered_df[filtered_df['Age'].isin(selected_ages)]
    filtered_df = filtered_df[
        (filtered_df['Rebound_Index'] >= reb_range[0]) & 
        (filtered_df['Rebound_Index'] <= reb_range[1]) &
        (filtered_df['UPV'] >= upv_range[0]) & 
        (filtered_df['UPV'] <= upv_range[1])
    ]

    # Metrics Summary Row
    kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
    with kpi1:
        st.metric("Filtered Records", f"{len(filtered_df)} / {len(df)}")
    with kpi2:
        avg_act = filtered_df['Actual_Strength'].mean() if not filtered_df.empty else 0
        st.metric("Mean Actual Strength", f"{avg_act:.2f} MPa")
    with kpi3:
        if 'Predicted_Strength' in filtered_df.columns and not filtered_df.empty:
            avg_pred = filtered_df['Predicted_Strength'].mean()
            st.metric("Mean AI Predicted", f"{avg_pred:.2f} MPa")
        else:
            st.metric("Mean AI Predicted", "N/A")
    with kpi4:
        if 'Prediction_Error' in filtered_df.columns and not filtered_df.empty:
            mae = filtered_df['Prediction_Error'].abs().mean()
            st.metric("Mean Abs Error (MAE)", f"{mae:.2f} MPa")
        else:
            st.metric("MAE", "N/A")
    with kpi5:
        avg_u = filtered_df['UPV'].mean() if not filtered_df.empty else 0
        st.metric("Average UPV", f"{avg_u:.0f} m/s")

    st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

    # Table Display
    display_df = filtered_df.copy()
    
    # Rename columns for clarity
    column_renames = {
        "Sample_ID": "Sample ID",
        "Age": "Age (Days)",
        "Rebound_Index": "Rebound Index (R)",
        "UPV": "UPV (m/s)",
        "Actual_Strength": "Actual Strength (MPa)",
        "Predicted_Strength": "AI Predicted (MPa)",
        "Prediction_Error": "Residual Error (MPa)"
    }
    display_df = display_df.rename(columns=column_renames)

    st.dataframe(
        display_df,
        hide_index=True,
        use_container_width=True,
        height=450
    )

    # Export CSV
    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    csv_bytes = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label=f"📥 Export {len(filtered_df)} Filtered Records to CSV",
        data=csv_bytes,
        file_name="concrete_samples_filtered.csv",
        mime="text/csv",
        type="secondary",
        use_container_width=True
    )
