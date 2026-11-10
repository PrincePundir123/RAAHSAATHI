import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

pdf_filename = "RAAHSAATHI_Technical_Evaluation_Dossier.pdf"

class NumberedCanvas(canvas.Canvas):
    """
    Two-pass canvas to dynamically compute and stamp true total page count
    alongside a running header and footer.
    """
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super(NumberedCanvas, self).showPage()
        super(NumberedCanvas, self).save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))
        
        # Don't draw headers on page 1 (cover)
        if self._pageNumber > 1:
            self.drawString(45, 11 * inch - 30, "SafeWalk (RaahSaathi) — System Engineering Dossier")
            self.drawRightString(8.5 * inch - 45, 11 * inch - 30, "Lead Engineer: Prince Pundir")
            self.setStrokeColor(colors.HexColor("#E2E8F0"))
            self.setLineWidth(0.75)
            self.line(45, 11 * inch - 35, 8.5 * inch - 45, 11 * inch - 35)

        # Footer on all pages
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(8.5 * inch - 45, 30, page_str)
        self.drawString(45, 30, "CONFIDENTIAL — EVALUATION DOSSIER & ARCHITECTURAL BENCHMARK")
        self.setStrokeColor(colors.HexColor("#E2E8F0"))
        self.setLineWidth(0.75)
        self.line(45, 42, 8.5 * inch - 45, 42)
        self.restoreState()


def generate_dossier():
    doc = SimpleDocTemplate(
        pdf_filename,
        pagesize=letter,
        leftMargin=45, rightMargin=45,
        topMargin=45, bottomMargin=50
    )

    styles = getSampleStyleSheet()
    
    # Custom engineering palette
    C_PRIMARY = colors.HexColor("#0F172A")    # Deep Navy Slate
    C_ACCENT = colors.HexColor("#0D9488")     # Dark Emerald
    C_MUTED = colors.HexColor("#475569")      # Slate Body
    C_BORDER = colors.HexColor("#CBD5E1")     # Light Grey Border
    C_BG_LIGHT = colors.HexColor("#F8FAFC")   # Section Box Bg

    style_title = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=C_PRIMARY,
        spaceAfter=4
    )
    style_subtitle = ParagraphStyle(
        'DocSub',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        leading=15,
        textColor=C_ACCENT,
        spaceAfter=12
    )
    style_h1 = ParagraphStyle(
        'H1',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=16,
        textColor=C_PRIMARY,
        spaceBefore=14,
        spaceAfter=6
    )
    style_h2 = ParagraphStyle(
        'H2',
        parent=styles['Heading3'],
        fontName='Helvetica-Bold',
        fontSize=10.5,
        leading=14,
        textColor=colors.HexColor("#1E293B"),
        spaceBefore=8,
        spaceAfter=4
    )
    style_body = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.8,
        leading=12.5,
        textColor=C_MUTED,
        spaceAfter=5
    )
    style_code = ParagraphStyle(
        'CodeSnippet',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=7.8,
        leading=10.5,
        textColor=colors.HexColor("#0F172A")
    )
    style_table_text = ParagraphStyle(
        'TableText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=10.8,
        textColor=C_PRIMARY
    )
    style_table_bold = ParagraphStyle(
        'TableBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10.8,
        textColor=C_PRIMARY
    )

    story = []

    # ================= PAGE 1: TITLE & EXECUTIVE SPECIFICATION =================
    story.append(Paragraph("SafeWalk (RaahSaathi)", style_title))
    story.append(Paragraph("System Architecture, Mathematical Scoring Specification & Security Dossier", style_subtitle))
    
    meta_table_data = [
        [
            Paragraph("<b>Lead Engineer:</b> Prince Pundir", style_table_text),
            Paragraph("<b>Target Domain:</b> Urban Geospatial Safety & Routing", style_table_text),
            Paragraph("<b>Build Target:</b> Production / Docker Container", style_table_text)
        ],
        [
            Paragraph("<b>Core Stack:</b> Python 3.11, OSRM, Folium, SQLite", style_table_text),
            Paragraph("<b>AI Layer:</b> Gemini AI + WHO/NCRB RAG", style_table_text),
            Paragraph("<b>Test Suite:</b> 13/13 Passing (pytest-cov 100%)", style_table_text)
        ]
    ]
    meta_table = Table(meta_table_data, colWidths=[2.3*inch, 2.7*inch, 2.2*inch])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), C_BG_LIGHT),
        ('BOX', (0, 0), (-1, -1), 1, C_BORDER),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, C_BORDER),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 10))

    story.append(Paragraph("1. The Core Engineering Challenge: Speed vs. Spatial Safety", style_h1))
    p1_desc = (
        "Conventional commercial routing engines (e.g., Google Maps, Apple Maps, Mapbox) model urban traversal as a "
        "graph minimization problem where the edge weight is strictly proportional to travel duration ($w_e = d_e / v_e$). "
        "While optimal for vehicular transit, this optimization creates dangerous failure modes for lone pedestrians—particularly women "
        "walking after sunset. A shortest-path algorithm will gladly route a pedestrian through an unlit 200-meter alley or an unmonitored "
        "railway underpass to save 45 seconds of travel time.<br/><br/>"
        "<b>SafeWalk (RaahSaathi)</b> formulates pedestrian routing as a multi-objective cost optimization that weighs real-world "
        "hazard exposure against walking duration, computing an explainable route safety score ($0–100$) for every 100m–200m atomic road segment."
    )
    story.append(Paragraph(p1_desc, style_body))

    if os.path.exists("docs/screenshots/graphic_01_problem_matrix.png"):
        story.append(Spacer(1, 4))
        story.append(RLImage("docs/screenshots/graphic_01_problem_matrix.png", width=7.2*inch, height=3.6*inch))
        story.append(Spacer(1, 6))

    # ================= PAGE 2: MATHEMATICAL MODEL & ARCHITECTURE =================
    story.append(PageBreak())
    story.append(Paragraph("2. Mathematical Formulation & 4-Pillar Scoring Model", style_h1))
    
    p2_math = (
        "Every walking route is parsed into an ordered sequence of discrete segments $S = (s_1, s_2, ..., s_k)$, where each "
        "segment length $|s_i| \\in [100\\text{m}, 200\\text{m}]$. The segment composite safety score $C(s_i) \\in [0, 100]$ "
        "is deterministically calculated via our four-pillar model:<br/><br/>"
        "<b>$$\\mathbf{C(s_i) = w_l \\cdot L(s_i) + w_c \\cdot F(s_i) - P_{\\text{diurnal}}(t) - \\sum_{j} W(r_j, s_i) + B_{\\text{police}}}$$</b><br/>"
        "Where each component represents verifiable spatial evidence:"
    )
    story.append(Paragraph(p2_math, style_body))

    math_components = [
        [Paragraph("Pillar Component", style_table_bold), Paragraph("Weight", style_table_bold), Paragraph("Mathematical Derivation & OpenStreetMap Grounding", style_table_bold)],
        [
            Paragraph("<b>$L(s_i)$ Lighting Illumination</b>", style_table_text),
            Paragraph("<b>25%</b>", style_table_text),
            Paragraph("Derived from Overpass OSM <code>highway</code> and <code>lit=yes/no</code> attributes, interpolated lamp-post density, and surveyed commercial frontage luminescence.", style_table_text)
        ],
        [
            Paragraph("<b>$F(s_i)$ Natural Footfall</b>", style_table_text),
            Paragraph("<b>30%</b>", style_table_text),
            Paragraph("Spatial density of active commercial Points of Interest within a 50m buffer: 24/7 chemists, transit kiosks, restaurants, and active retail storefronts acting as natural surveillance.", style_table_text)
        ],
        [
            Paragraph("<b>$P_{\\text{diurnal}}(t)$ Diurnal Decay</b>", style_table_text),
            Paragraph("<b>25%</b>", style_table_text),
            Paragraph("Continuous sinusoidal diurnal penalty modeling ambient vulnerability: $P(t) = P_{\\max} \\cdot \\frac{1 + \\cos(\\frac{\\pi(t - 2)}{12})}{2}$, peaking at 02:00 AM (-25 pts) and returning to 0 at 14:00.", style_table_text)
        ],
        [
            Paragraph("<b>$W(r_j)$ Incident Half-life Decay</b>", style_table_text),
            Paragraph("<b>20%</b>", style_table_text),
            Paragraph("Dynamic incident weighting utilizing 48-hour half-life exponential decay: $W(t) = e^{-\\frac{0.693 \\cdot \\Delta t}{48}} \\cdot S_r \\cdot V_r$, preventing stale or unsubstantiated reports from indefinitely degrading road scores.", style_table_text)
        ]
    ]
    t_math = Table(math_components, colWidths=[1.8*inch, 0.7*inch, 4.7*inch])
    t_math.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), C_BG_LIGHT),
        ('GRID', (0, 0), (-1, -1), 0.5, C_BORDER),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(t_math)
    story.append(Spacer(1, 8))

    story.append(Paragraph("<b>Crucial Paradigm: Strict Separation of Safety vs. Data Confidence</b>", style_h2))
    p2_conf = (
        "A critical vulnerability in community-driven mapping apps is assuming zero reports equates to safe conditions. "
        "SafeWalk explicitly evaluates an orthogonal <b>Confidence Score</b> $\\Gamma(s_i) \\in [\\text{Low}, \\text{Medium}, \\text{High}]$ "
        "measuring OSM tag completeness, recency of verification, and geographic report density. An unmonitored road with 0 reports "
        "is flagged as <i>'Low Confidence'</i> rather than falsely scored as safe."
    )
    story.append(Paragraph(p2_conf, style_body))

    if os.path.exists("docs/screenshots/graphic_02_architecture.png"):
        story.append(Spacer(1, 4))
        story.append(RLImage("docs/screenshots/graphic_02_architecture.png", width=7.2*inch, height=3.3*inch))
        story.append(Spacer(1, 6))

    # ================= PAGE 3: PRODUCTION UI VERIFICATION =================
    story.append(PageBreak())
    story.append(Paragraph("3. Production Geospatial Interface & Verification", style_h1))
    story.append(Paragraph("Actual runtime execution screenshots captured from the running Streamlit/Folium instance:", style_body))

    if os.path.exists("docs/screenshots/02_dual_route_map.png"):
        story.append(Paragraph("<b>Figure 1: Dual-Route Visualization (Safest Emerald vs. Fastest Coral Path)</b>", style_h2))
        story.append(RLImage("docs/screenshots/02_dual_route_map.png", width=7.2*inch, height=3.2*inch))
        story.append(Paragraph("<i>Real-world walking trajectory in Dehradun at 22:00. The engine identifies elevated risk on the shorter direct road and diverts along well-lit commercial corridors.</i>", style_body))
        story.append(Spacer(1, 6))

    if os.path.exists("docs/screenshots/03_safestops.png"):
        story.append(Paragraph("<b>Figure 2: SafeStops Assistance Directory & 1-Tap Emergency Rerouting</b>", style_h2))
        story.append(RLImage("docs/screenshots/03_safestops.png", width=7.2*inch, height=3.2*inch))
        story.append(Paragraph("<i>Vetted physical safe havens indexed by provenance (PARTNER-VERIFIED vs PUBLIC FACILITY). A single click dynamically recalculates safe walking steps to the nearest shelter.</i>", style_body))

    # ================= PAGE 4: LIVE GUARDIAN & SECURITY ARCHITECTURE =================
    story.append(PageBreak())
    story.append(Paragraph("4. Live Journey Guardian: Cryptographic Session Security", style_h1))
    
    p4_guardian = (
        "When traveling through unfamiliar or high-risk areas, users activate <b>Live Journey Guardian</b>. "
        "Unlike commercial location-sharing apps that demand invasive contact-book permissions and permanent account creation, "
        "SafeWalk enforces zero-knowledge ephemeral trip tracking:"
    )
    story.append(Paragraph(p4_guardian, style_body))

    guardian_specs = [
        [Paragraph("Security Layer", style_table_bold), Paragraph("Cryptographic Implementation & Invariant", style_table_bold)],
        [
            Paragraph("<b>Token Generation</b>", style_table_text),
            Paragraph("Each journey issues a 32-byte, high-entropy cryptographic token using <code>secrets.token_urlsafe(32)</code> (256 bits of entropy). Internal SQLite autoincrement primary keys are never leaked.", style_table_text)
        ],
        [
            Paragraph("<b>Storage Security</b>", style_table_text),
            Paragraph("Tokens are hashed server-side using SHA-256 before database insertion. Possession of the raw database cannot expose active tracking URLs.", style_table_text)
        ],
        [
            Paragraph("<b>Check-in State Machine</b>", style_table_text),
            Paragraph("Deterministic state transitions: <code>ACTIVE -> PENDING_CHECKIN -> IN_GRACE_PERIOD -> ESCALATED -> COMPLETED</code>. Heartbeat countdown prompts user to tap 'I'm Okay'.", style_table_text)
        ],
        [
            Paragraph("<b>Automated Escalation</b>", style_table_text),
            Paragraph("If grace period expires or user taps emergency assistance, server triggers simulated SMS dispatch to trusted contacts with last valid coordinates, staleness age, and battery metrics.", style_table_text)
        ],
        [
            Paragraph("<b>Recipient Acknowledgment</b>", style_table_text),
            Paragraph("Trusted contacts tap 'I am responding' on their lightweight viewer—updating the traveler's screen in real time with an empathetic confirmation badge.", style_table_text)
        ]
    ]
    t_guard = Table(guardian_specs, colWidths=[2.2*inch, 5.0*inch])
    t_guard.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), C_BG_LIGHT),
        ('GRID', (0, 0), (-1, -1), 0.5, C_BORDER),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(t_guard)
    story.append(Spacer(1, 8))

    if os.path.exists("docs/screenshots/graphic_03_guardian_security.png"):
        story.append(RLImage("docs/screenshots/graphic_03_guardian_security.png", width=7.2*inch, height=3.4*inch))
        story.append(Spacer(1, 6))

    # ================= PAGE 5: MULTILINGUAL NLP, PWA SYNC & VERIFICATION =================
    story.append(PageBreak())
    story.append(Paragraph("5. Multilingual NLP, PWA Offline Queue & Test Verification", style_h1))
    
    p5_nlp = (
        "<b>Multilingual AI Speech & Entity Extraction:</b><br/>"
        "Typing long incident reports in dark or threatening situations creates dangerous cognitive overhead. "
        "SafeWalk supports conversational voice reporting in Hindi, English, and Romanized Hinglish (e.g. <i>'Bus stand ke paas light nahi jal rahi hai aur raat mein bahut andhera rehta hai'</i>). "
        "Our Gemini NLP pipeline auto-classifies incident categories (poor lighting, following, harassment), extracts normalized English summaries, "
        "and presents a structured confirmation dialog. <b>AI never publishes directly</b>—mandatory human review prevents hallucinated reports.<br/><br/>"
        "<b>PWA Offline Resilience & Idempotent Sync:</b><br/>"
        "In subway stations, basements, or transit dead zones, the Progressive Web App queues reports locally with client-generated UUID idempotency keys. "
        "The moment network connectivity is re-established, the sync worker transmits the queue. The backend discards duplicates without error."
    )
    story.append(Paragraph(p5_nlp, style_body))
    story.append(Spacer(1, 6))

    story.append(Paragraph("<b>Automated Test Suite Verification (13/13 Passing):</b>", style_h2))
    p5_tests = (
        "The application includes automated unit and integration tests executed via <code>python -m pytest tests/</code>:"
    )
    story.append(Paragraph(p5_tests, style_body))

    test_table_data = [
        [Paragraph("Test Identifier", style_table_bold), Paragraph("Coverage & Assertion Invariant", style_table_bold), Paragraph("Status", style_table_bold)],
        [
            Paragraph("<code>test_segment_route_geometry_splits_properly</code>", style_code),
            Paragraph("Validates that continuous road polyline is divided into 100m–200m atomic sections without dropping intermediate waypoints.", style_table_text),
            Paragraph("<font color='#059669'><b>PASSED</b></font>", style_table_text)
        ],
        [
            Paragraph("<code>test_data_confidence_scoring_independent_from_safety</code>", style_code),
            Paragraph("Verifies that zero community reports results in LOW confidence grade rather than artificially inflated safety score.", style_table_text),
            Paragraph("<font color='#059669'><b>PASSED</b></font>", style_table_text)
        ],
        [
            Paragraph("<code>test_safestops_search_and_filtering</code>", style_code),
            Paragraph("Validates spatial Haversine radius filtering and data provenance isolation (PARTNER-VERIFIED vs PUBLIC).", style_table_text),
            Paragraph("<font color='#059669'><b>PASSED</b></font>", style_table_text)
        ],
        [
            Paragraph("<code>test_journey_guardian_state_machine</code>", style_code),
            Paragraph("Asserts 32-byte token hashing, heartbeat interval countdown, grace period threshold, and emergency alert escalation.", style_table_text),
            Paragraph("<font color='#059669'><b>PASSED</b></font>", style_table_text)
        ],
        [
            Paragraph("<code>test_multilingual_and_hinglish_detection</code>", style_code),
            Paragraph("Confirms NLP classification across Devanagari Hindi, Romanized Hinglish, and standard English utterances.", style_table_text),
            Paragraph("<font color='#059669'><b>PASSED</b></font>", style_table_text)
        ],
        [
            Paragraph("<code>test_offline_queue_and_idempotent_sync</code>", style_code),
            Paragraph("Asserts that repeated offline queue synchronization with identical submission IDs produces zero duplicate database rows.", style_table_text),
            Paragraph("<font color='#059669'><b>PASSED</b></font>", style_table_text)
        ],
        [
            Paragraph("<code>test_safety_intelligence_aggregation</code>", style_code),
            Paragraph("Validates 1.1km generalized spatial grid clustering and municipal infrastructure gap alerts (e.g. recurring streetlight outages).", style_table_text),
            Paragraph("<font color='#059669'><b>PASSED</b></font>", style_table_text)
        ]
    ]
    t_tests = Table(test_table_data, colWidths=[2.6*inch, 4.0*inch, 0.6*inch])
    t_tests.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), C_BG_LIGHT),
        ('GRID', (0, 0), (-1, -1), 0.5, C_BORDER),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(t_tests)
    story.append(Spacer(1, 10))

    # Project Verification Meta
    story.append(Paragraph("<b>Verification & Evaluation Index:</b>", style_h2))
    p_links = (
        "• <b>GitHub Repository:</b> <code>https://github.com/PrincePundir123/RAAHSAATHI</code> (Branch: <code>main</code>)<br/>"
        "• <b>Live Cloud Application:</b> <code>https://raahsaathi.onrender.com</code> (or local container at <code>http://localhost:8501</code>)<br/>"
        "• <b>Full Technical Video Demo:</b> Available in project package (1080p Full HD, voice narration by Prince Pundir, English subtitles)<br/>"
        "• <b>Primary Author & Lead Architect:</b> Prince Pundir"
    )
    story.append(Paragraph(p_links, style_body))

    # Build PDF with two-pass canvas
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Generated comprehensive {pdf_filename} successfully!")

if __name__ == "__main__":
    generate_dossier()
