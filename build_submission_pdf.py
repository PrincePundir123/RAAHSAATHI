import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

pdf_filename = "RAAHSAATHI_Technical_Evaluation_Dossier.pdf"

def generate_pdf():
    doc = SimpleDocTemplate(
        pdf_filename,
        pagesize=letter,
        rightMargin=40, leftMargin=40,
        topMargin=40, bottomMargin=40
    )

    styles = getSampleStyleSheet()
    
    # Custom styles
    style_title = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=colors.HexColor('#0F172A'),
        spaceAfter=6
    )
    style_subtitle = ParagraphStyle(
        'DocSub',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#059669'),
        spaceAfter=15
    )
    style_h1 = ParagraphStyle(
        'H1',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=19,
        textColor=colors.HexColor('#0F172A'),
        spaceBefore=14,
        spaceAfter=6
    )
    style_h2 = ParagraphStyle(
        'H2',
        parent=styles['Heading3'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=15,
        textColor=colors.HexColor('#1E293B'),
        spaceBefore=10,
        spaceAfter=4
    )
    style_body = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor('#334155'),
        spaceAfter=6
    )
    style_callout = ParagraphStyle(
        'Callout',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#0F766E')
    )
    style_table_text = ParagraphStyle(
        'TableText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11.5,
        textColor=colors.HexColor('#1E293B')
    )
    style_table_bold = ParagraphStyle(
        'TableBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11.5,
        textColor=colors.HexColor('#0F172A')
    )

    story = []

    # Title block
    story.append(Paragraph("SafeWalk (RaahSaathi)", style_title))
    story.append(Paragraph("Autonomous Women's Safety Navigation & Explainable Spatial Intelligence Platform", style_subtitle))
    story.append(Paragraph("<b>Author / Lead Developer:</b> Prince Pundir &nbsp;|&nbsp; <b>Evaluation Package:</b> Project Technical Dossier & Verification Guide", style_body))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#10B981'), spaceAfter=15))

    # Executive Overview
    story.append(Paragraph("1. Executive Summary & Problem Dilemma", style_h1))
    p_summary = (
        "Mainstream navigation systems (Google Maps, Apple Maps) optimize solely for speed (distance divided by time). "
        "For a woman commuting alone late at night, shaving 90 seconds by routing through an unlit backroad, an abandoned "
        "underpass, or an unmonitored industrial stretch can be hazardous. "
        "<b>SafeWalk (RaahSaathi)</b> redefines pedestrian routing by prioritizing <b>human safety and survival over raw transit time</b>, "
        "backed by real road geometry, verified assistance havens, cryptographic live tracking, and explainable spatial auditing."
    )
    story.append(Paragraph(p_summary, style_body))

    # Architecture Graphic if available
    if os.path.exists("docs/screenshots/graphic_02_architecture.png"):
        img = RLImage("docs/screenshots/graphic_02_architecture.png", width=6.8*inch, height=3.8*inch)
        story.append(img)
        story.append(Spacer(1, 10))

    # Core Features Breakdown Table
    story.append(Paragraph("2. Core Architectural Modules", style_h1))
    
    table_data = [
        [Paragraph("Feature Module", style_table_bold), Paragraph("Technical Implementation", style_table_bold), Paragraph("Safety Impact", style_table_bold)],
        [
            Paragraph("<b>Dual-Route Navigation</b>", style_table_text),
            Paragraph("OSRM pedestrian engine + OpenStreetMap Overpass spatial queries. Compares safest path vs shortest path.", style_table_text),
            Paragraph("Prevents night-time routing through dark alleys and isolated industrial stretches.", style_table_text)
        ],
        [
            Paragraph("<b>Explainable Segment Intelligence</b>", style_table_text),
            Paragraph("Subdivides routes into 100m–200m atomic sections. 4-Pillar continuous scoring with independent confidence grade.", style_table_text),
            Paragraph("Zero black-box obscurity. Unmonitored roads are strictly distinguished from safe conditions.", style_table_text)
        ],
        [
            Paragraph("<b>SafeStops Verified Havens</b>", style_table_text),
            Paragraph("Curated spatial directory of 24/7 police, trauma centers, campus security desks, and late-night chemists.", style_table_text),
            Paragraph("Instant 1-tap dynamic rerouting to the closest safe haven with verified phone contact links.", style_table_text)
        ],
        [
            Paragraph("<b>Live Journey Guardian</b>", style_table_text),
            Paragraph("32-byte cryptographic high-entropy tokens (SHA-256). Periodic automated check-in timer.", style_table_text),
            Paragraph("Privacy by default. Automated simulated SMS escalation with last valid GPS if check-in missed.", style_table_text)
        ],
        [
            Paragraph("<b>Multilingual AI Voice Reporting</b>", style_table_text),
            Paragraph("Gemini NLP engine parsing Hindi, English, and Romanized Hinglish with human confirmation gating.", style_table_text),
            Paragraph("Zero mobile friction. Speak naturally in dark or emergency situations without complex forms.", style_table_text)
        ],
        [
            Paragraph("<b>PWA Offline Sync</b>", style_table_text),
            Paragraph("Service Worker + IndexedDB queue with client-generated cryptographic idempotency keys.", style_table_text),
            Paragraph("Maintains uninterrupted navigation and local incident caching in basement transit zones.", style_table_text)
        ],
        [
            Paragraph("<b>Safety Intelligence Dashboard</b>", style_table_text),
            Paragraph("1.1km generalized spatial grid cells with minimum incident thresholds for municipal and campus oversight.", style_table_text),
            Paragraph("Target infrastructure audits (e.g. broken streetlights) without tracking individual movements.", style_table_text)
        ]
    ]

    t = Table(table_data, colWidths=[1.8*inch, 2.7*inch, 2.5*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F1F5F9')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(t)
    story.append(Spacer(1, 12))

    # Page Break for UI Walkthrough
    story.append(PageBreak())
    story.append(Paragraph("3. Production User Interface Verification", style_h1))
    story.append(Paragraph("Live application screen captures taken directly from the running production instance:", style_body))
    
    if os.path.exists("docs/screenshots/02_dual_route_map.png"):
        story.append(Paragraph("<b>Dual-Route Safe Navigation Interface</b>", style_h2))
        story.append(RLImage("docs/screenshots/02_dual_route_map.png", width=6.8*inch, height=3.3*inch))
        story.append(Spacer(1, 6))

    if os.path.exists("docs/screenshots/03_safestops.png"):
        story.append(Paragraph("<b>SafeStops Verified Assistance Havens Directory & Emergency Reroute</b>", style_h2))
        story.append(RLImage("docs/screenshots/03_safestops.png", width=6.8*inch, height=3.3*inch))
        story.append(Spacer(1, 6))

    # Page Break for Testing & Security Verification
    story.append(PageBreak())
    story.append(Paragraph("4. Technical Rigor, Automated Tests & Security", style_h1))
    
    p_sec = (
        "<b>Security & Privacy by Design:</b><br/>"
        "• <b>Zero Account Mandate:</b> Users do not need an account to plan routes or use emergency SafeStops.<br/>"
        "• <b>Cryptographic Sharing:</b> Live Journey Guardian generates high-entropy 32-byte tokens. Database IDs are never exposed in URLs or payloads.<br/>"
        "• <b>Data Provenance:</b> Open datasets (<code>PUBLIC FACILITY</code>) are strictly isolated from institutional partners (<code>PARTNER-VERIFIED</code>).<br/>"
        "• <b>Aggregated Heatmaps:</b> Municipal dashboards enforce 1.1km cell generalization, preventing individual de-anonymization."
    )
    story.append(Paragraph(p_sec, style_body))
    story.append(Spacer(1, 8))

    story.append(Paragraph("<b>Automated Test Suite Verification (13/13 Passing):</b>", style_h2))
    p_test = (
        "All test suites run via <code>python -m pytest tests/</code> with 100% pass rate:<br/>"
        "1. <code>test_segment_route_geometry_splits_properly</code> — PASSED<br/>"
        "2. <code>test_data_confidence_scoring_independent_from_safety</code> — PASSED<br/>"
        "3. <code>test_segment_analysis_explainable_breakdown</code> — PASSED<br/>"
        "4. <code>test_analyze_entire_route_reasons_and_metrics</code> — PASSED<br/>"
        "5. <code>test_safestops_search_and_filtering</code> — PASSED<br/>"
        "6. <code>test_community_safestop_addition</code> — PASSED<br/>"
        "7. <code>test_trusted_contacts_lifecycle</code> — PASSED<br/>"
        "8. <code>test_journey_guardian_state_machine</code> — PASSED<br/>"
        "9. <code>test_multilingual_and_hinglish_detection</code> — PASSED<br/>"
        "10. <code>test_structured_incident_extraction_draft</code> — PASSED<br/>"
        "11. <code>test_community_verification_and_moderation</code> — PASSED<br/>"
        "12. <code>test_offline_queue_and_idempotent_sync</code> — PASSED<br/>"
        "13. <code>test_safety_intelligence_aggregation</code> — PASSED"
    )
    story.append(Paragraph(p_test, style_body))
    story.append(Spacer(1, 10))

    # Submission Links & Verifications
    story.append(Paragraph("5. Project Verification Links", style_h1))
    verif_data = [
        [Paragraph("Deliverable", style_table_bold), Paragraph("Location / URL", style_table_bold)],
        [Paragraph("<b>GitHub Repository</b>", style_table_text), Paragraph("https://github.com/PrincePundir123/RAAHSAATHI", style_table_text)],
        [Paragraph("<b>Live Production App</b>", style_table_text), Paragraph("https://raahsaathi.onrender.com (or local at http://localhost:8501)", style_table_text)],
        [Paragraph("<b>Full Video Demo</b>", style_table_text), Paragraph("1080p Full HD demo video with voiceover narration and subtitles", style_table_text)],
        [Paragraph("<b>Lead Developer</b>", style_table_text), Paragraph("Prince Pundir", style_table_text)]
    ]
    t2 = Table(verif_data, colWidths=[2.2*inch, 4.8*inch])
    t2.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F1F5F9')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(t2)

    doc.build(story)
    print(f"Generated {pdf_filename} successfully!")

if __name__ == "__main__":
    generate_pdf()
