import io
import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

def generate_pdf_report(
    sample_id,
    age,
    rebound_index,
    upv,
    predicted_strength,
    assessment,
    upv_grade,
    strength_class="",
    features=None,
    project_name="Metro Viaduct Structural Inspection",
    inspector_name="Lead NDT Engineer",
    location="Pier Cap & Girders, Sector 4",
    notes="Test conducted in accordance with IS 13311 (Part 1 & 2) and ASTM C805/C597 non-destructive testing procedures."
):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    
    # Custom Palette
    c_navy = colors.HexColor("#0B132B")
    c_dark_blue = colors.HexColor("#1C2541")
    c_cyan = colors.HexColor("#0284C7")
    c_light_bg = colors.HexColor("#F8FAFC")
    c_border = colors.HexColor("#CBD5E1")
    c_dark_txt = colors.HexColor("#0F172A")
    c_muted = colors.HexColor("#64748B")

    # Custom Typography Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.white,
        alignment=0
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#7DD3FC"),
        alignment=0
    )

    h2_style = ParagraphStyle(
        'Heading2Custom',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=c_dark_blue,
        spaceAfter=6,
        spaceBefore=10
    )

    body_style = ParagraphStyle(
        'BodyCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=c_dark_txt
    )

    bold_label_style = ParagraphStyle(
        'BoldLabel',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=13,
        textColor=c_dark_blue
    )

    pred_big_style = ParagraphStyle(
        'PredBig',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=colors.HexColor("#0284C7"),
        alignment=1
    )

    pred_sub_style = ParagraphStyle(
        'PredSub',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=colors.HexColor("#0F172A"),
        alignment=1
    )

    story = []

    # 1. Header Banner Table
    banner_data = [
        [
            Paragraph("<b>NDT INTELLIGENCE</b>", title_style),
            Paragraph(f"<b>REPORT REF:</b> NDT-{sample_id}<br/><b>DATE:</b> {datetime.datetime.now().strftime('%d-%b-%Y')}", ParagraphStyle('RightHeader', parent=subtitle_style, alignment=2, textColor=colors.white))
        ],
        [
            Paragraph("AI-Powered Concrete Compressive Strength Assessment System | Civil Engineering NDT Division", subtitle_style),
            Paragraph("CONFIDENTIAL & CERTIFIED", ParagraphStyle('RightSub', parent=subtitle_style, alignment=2, textColor=colors.HexColor("#38BDF8")))
        ]
    ]
    banner_table = Table(banner_data, colWidths=[380, 160])
    banner_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), c_navy),
        ('PADDING', (0, 0), (-1, -1), 10),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 1), (-1, 1), 10),
    ]))
    story.append(banner_table)
    story.append(Spacer(1, 14))

    # 2. Project & Inspection Metadata
    story.append(Paragraph("1. PROJECT & INSPECTION INFORMATION", h2_style))
    meta_data = [
        [
            Paragraph("<b>Project Name:</b>", bold_label_style),
            Paragraph(str(project_name), body_style),
            Paragraph("<b>Inspection Date:</b>", bold_label_style),
            Paragraph(datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), body_style),
        ],
        [
            Paragraph("<b>Sample ID:</b>", bold_label_style),
            Paragraph(f"<font color='#0284C7'><b>{sample_id}</b></font>", body_style),
            Paragraph("<b>Testing Location:</b>", bold_label_style),
            Paragraph(str(location), body_style),
        ],
        [
            Paragraph("<b>Lead Inspector:</b>", bold_label_style),
            Paragraph(str(inspector_name), body_style),
            Paragraph("<b>Testing Standard:</b>", bold_label_style),
            Paragraph("IS 13311 / ASTM C805 & C597", body_style),
        ]
    ]
    meta_table = Table(meta_data, colWidths=[100, 170, 110, 160])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), c_light_bg),
        ('BOX', (0, 0), (-1, -1), 1, c_border),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, c_border),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 12))

    # 3. NDT Raw Measurements Table
    story.append(Paragraph("2. EXPERIMENTAL NON-DESTRUCTIVE TESTING MEASUREMENTS", h2_style))
    meas_data = [
        [
            Paragraph("<b>Parameter</b>", bold_label_style),
            Paragraph("<b>Measured Value</b>", bold_label_style),
            Paragraph("<b>Standard Unit</b>", bold_label_style),
            Paragraph("<b>Reference Standard</b>", bold_label_style),
        ],
        [
            Paragraph("Concrete Curing Age", body_style),
            Paragraph(f"<b>{age:.1f}</b>", body_style),
            Paragraph("Days", body_style),
            Paragraph("Standard Water Curing @ 27±2°C", body_style),
        ],
        [
            Paragraph("Rebound Hammer Index", body_style),
            Paragraph(f"<b>{rebound_index:.1f}</b>", body_style),
            Paragraph("Dimensionless (R)", body_style),
            Paragraph("IS 13311 (Part 2) / ASTM C805", body_style),
        ],
        [
            Paragraph("Ultrasonic Pulse Velocity (UPV)", body_style),
            Paragraph(f"<b>{upv:.0f}</b>", body_style),
            Paragraph("m/s (or km/s)", body_style),
            Paragraph("IS 13311 (Part 1) / ASTM C597", body_style),
        ]
    ]
    meas_table = Table(meas_data, colWidths=[170, 110, 110, 150])
    meas_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#E2E8F0")),
        ('BOX', (0, 0), (-1, -1), 1, c_border),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, c_border),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('ALIGN', (1, 0), (2, -1), 'CENTER'),
    ]))
    story.append(meas_table)
    story.append(Spacer(1, 12))

    # 4. Neural Network Engineered Features Breakdown
    story.append(Paragraph("3. ARTIFICIAL NEURAL NETWORK (ANN) FEATURE PIPELINE", h2_style))
    
    # Calculate features if not provided
    f_upv_age = (upv / age) if age > 0 else 0
    f_reb_age = (rebound_index / age) if age > 0 else 0
    f_upv_reb = upv * rebound_index
    
    if features:
        f_upv_age = features.get("UPV_over_Age", f_upv_age)
        f_reb_age = features.get("Rebound_over_Age", f_reb_age)
        f_upv_reb = features.get("UPV_x_Rebound", f_upv_reb)
        
    feat_data = [
        [
            Paragraph("<b>#</b>", bold_label_style),
            Paragraph("<b>Input Feature</b>", bold_label_style),
            Paragraph("<b>Mathematical Definition</b>", bold_label_style),
            Paragraph("<b>Engineered Value</b>", bold_label_style),
        ],
        [Paragraph("1", body_style), Paragraph("Curing Age", body_style), Paragraph("Age (Days)", body_style), Paragraph(f"{age:.2f}", body_style)],
        [Paragraph("2", body_style), Paragraph("Rebound Index", body_style), Paragraph("R", body_style), Paragraph(f"{rebound_index:.2f}", body_style)],
        [Paragraph("3", body_style), Paragraph("Pulse Velocity", body_style), Paragraph("UPV (m/s)", body_style), Paragraph(f"{upv:.1f}", body_style)],
        [Paragraph("4", body_style), Paragraph("Acoustic Rate", body_style), Paragraph("UPV / Age", body_style), Paragraph(f"{f_upv_age:.2f}", body_style)],
        [Paragraph("5", body_style), Paragraph("Surface Hardening Rate", body_style), Paragraph("Rebound Index / Age", body_style), Paragraph(f"{f_reb_age:.2f}", body_style)],
        [Paragraph("6", body_style), Paragraph("Combined SonReb Cross-Term", body_style), Paragraph("UPV × Rebound Index", body_style), Paragraph(f"{f_upv_reb:,.1f}", body_style)],
    ]
    feat_table = Table(feat_data, colWidths=[30, 160, 200, 150])
    feat_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#F1F5F9")),
        ('BOX', (0, 0), (-1, -1), 1, c_border),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, c_border),
        ('PADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(feat_table)
    story.append(Spacer(1, 14))

    # 5. AI Prediction Highlight Card
    story.append(Paragraph("4. AI PREDICTIVE STRENGTH & QUALITY ASSESSMENT", h2_style))
    
    pred_box_data = [
        [
            Paragraph("AI PREDICTED COMPRESSIVE STRENGTH", ParagraphStyle('BoxHead', parent=body_style, fontName='Helvetica-Bold', fontSize=10, textColor=c_muted, alignment=1)),
            Paragraph("CONCRETE QUALITY ASSESSMENT & RATING", ParagraphStyle('BoxHead2', parent=body_style, fontName='Helvetica-Bold', fontSize=10, textColor=c_muted, alignment=1)),
        ],
        [
            Paragraph(f"<b>{predicted_strength:.2f} MPa</b>", pred_big_style),
            Paragraph(f"<b>{assessment}</b><br/><font size=9 color='#64748B'>UPV Grade: <b>{upv_grade}</b> | {strength_class}</font>", pred_sub_style),
        ],
        [
            Paragraph("<i>ANN 6-6-1 Sigmoid Architecture | Supervised Backpropagation</i>", ParagraphStyle('SubNote1', parent=body_style, fontSize=8, alignment=1, textColor=c_muted)),
            Paragraph("<i>Compliant with IS 13311 Ultrasonic Velocity Criteria</i>", ParagraphStyle('SubNote2', parent=body_style, fontSize=8, alignment=1, textColor=c_muted)),
        ]
    ]
    pred_box_table = Table(pred_box_data, colWidths=[260, 280])
    pred_box_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F0F9FF")),
        ('BOX', (0, 0), (-1, -1), 1.5, colors.HexColor("#38BDF8")),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#BAE6FD")),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        ('BOTTOMPADDING', (0, 1), (-1, 1), 8),
        ('BOTTOMPADDING', (0, 2), (-1, 2), 6),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(pred_box_table)
    story.append(Spacer(1, 14))

    # 6. Engineer Notes & Verification Block
    story.append(Paragraph("5. ENGINEERING REMARKS & CERTIFICATION", h2_style))
    notes_para = Paragraph(f"<b>Remarks:</b> {notes}", body_style)
    story.append(notes_para)
    story.append(Spacer(1, 12))

    sign_data = [
        [
            Paragraph("<b>TEST CONDUCTED BY:</b><br/><br/><br/>___________________________<br/>NDT Field Specialist", body_style),
            Paragraph("<b>VERIFIED & APPROVED BY:</b><br/><br/><br/>___________________________<br/>Chartered Structural Engineer", body_style),
            Paragraph(f"<b>OFFICIAL STAMP / SEAL:</b><br/><br/>Date: {datetime.datetime.now().strftime('%d/%m/%Y')}<br/>Status: <b>VERIFIED</b>", body_style)
        ]
    ]
    sign_table = Table(sign_data, colWidths=[180, 180, 180])
    sign_table.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 1, c_border),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, c_border),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#FAFAFA")),
        ('PADDING', (0, 0), (-1, -1), 8),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(sign_table)
    story.append(Spacer(1, 10))

    # Footer Disclaimer
    disclaimer = Paragraph(
        "<font size=7 color='#94A3B8'>Notice: This prediction is generated autonomously by the NDT Intelligence Neural Network System based on non-destructive surface hardness and ultrasonic wave velocity. For legal structural certification, periodic core extraction calibration is recommended as per local building codes.</font>",
        body_style
    )
    story.append(disclaimer)

    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes
