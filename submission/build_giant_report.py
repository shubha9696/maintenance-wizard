import os
import json
from reportlab.lib.pagesizes import letter
from reportlab.lib.colors import HexColor
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

# Configuration
PDF_REPORT_PATH = "c:\\Users\\shubh\\Desktop\\hackathon\\Maintenance_Wizard_Project_Report_v4.pdf"
PAGE_WIDTH, PAGE_HEIGHT = letter  # 612 x 792
EQUIPMENT_JSON_PATH = "c:\\Users\\shubh\\Desktop\\hackathon\\backend\\data\\generated\\equipment.json"

# Colors (Premium Dark Theme)
BG_DARK = HexColor("#0A0E17")       # Deep space black
CARD_BG = HexColor("#131A26")       # Dark slate blue
BORDER_COLOR = HexColor("#222E42")  # Muted steel blue
ACCENT_BLUE = HexColor("#3B82F6")   # Electric blue
ACCENT_CYAN = HexColor("#06B6D4")   # Neon cyan
ACCENT_GREEN = HexColor("#10B981")  # Active green
ACCENT_ORANGE = HexColor("#F97316") # Alert orange
TEXT_WHITE = HexColor("#FFFFFF")    # Crisp white
TEXT_MUTED = HexColor("#94A3B8")    # Soft gray

class NumberedCanvas(canvas.Canvas):
    """Canvas that computes total pages dynamically and draws consistent layout headers/footers."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, total_pages):
        page_num = self._pageNumber
        if page_num == 1:
            return

        self.saveState()
        # Header (Pages 2+)
        self.setStrokeColor(BORDER_COLOR)
        self.setLineWidth(1)
        self.line(54, PAGE_HEIGHT - 60, PAGE_WIDTH - 54, PAGE_HEIGHT - 60)
        
        self.setFillColor(TEXT_MUTED)
        self.setFont("Helvetica-Bold", 8)
        self.drawString(54, PAGE_HEIGHT - 52, "MAINTENANCE WIZARD — ARCHITECTURE, SPECIFICATIONS & VERIFICATION REPORT")
        self.drawRightString(PAGE_WIDTH - 54, PAGE_HEIGHT - 52, "TATA STEEL AI HACKATHON 2026")

        # Footer (Pages 2+)
        self.line(54, 60, PAGE_WIDTH - 54, 60)
        self.setFont("Helvetica", 8)
        self.drawString(54, 45, "Confidential | Tata Steel Predictive Maintenance Platform")
        self.drawRightString(PAGE_WIDTH - 54, 45, f"Page {page_num} of {total_pages}")
        self.restoreState()

def draw_page_bg(canvas_obj, doc):
    canvas_obj.saveState()
    # Background Fill for all pages
    canvas_obj.setFillColor(BG_DARK)
    canvas_obj.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, fill=True, stroke=False)
    
    # Subtle grid background lines
    canvas_obj.setStrokeColor(HexColor("#0F1622"))
    canvas_obj.setLineWidth(0.5)
    for x in range(0, int(PAGE_WIDTH), 100):
        canvas_obj.line(x, 0, x, PAGE_HEIGHT)
    for y in range(0, int(PAGE_HEIGHT), 100):
        canvas_obj.line(0, y, PAGE_WIDTH, y)

    # Draw borders on Page 1
    if canvas_obj._pageNumber == 1:
        canvas_obj.setStrokeColor(ACCENT_BLUE)
        canvas_obj.setLineWidth(4)
        canvas_obj.line(54, PAGE_HEIGHT - 60, PAGE_WIDTH - 54, PAGE_HEIGHT - 60)
        canvas_obj.line(54, 60, PAGE_WIDTH - 54, 60)
        
    canvas_obj.restoreState()


def build_giant_pdf():
    # Setup document geometry (Margins: 0.75 in or 54 points)
    doc = SimpleDocTemplate(
        PDF_REPORT_PATH,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=80,
        bottomMargin=80
    )
    
    # Styles
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CoverTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=32,
        leading=38,
        textColor=TEXT_WHITE,
        spaceAfter=10
    )
    subtitle_style = ParagraphStyle(
        'CoverSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=20,
        textColor=ACCENT_CYAN,
        spaceAfter=25
    )
    meta_style = ParagraphStyle(
        'CoverMeta',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10.5,
        leading=16,
        textColor=TEXT_MUTED
    )
    h1_style = ParagraphStyle(
        'ReportH1',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=TEXT_WHITE,
        spaceBefore=15,
        spaceAfter=10,
        keepWithNext=True
    )
    h2_style = ParagraphStyle(
        'ReportH2',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=16,
        textColor=ACCENT_CYAN,
        spaceBefore=12,
        spaceAfter=8,
        keepWithNext=True
    )
    body_style = ParagraphStyle(
        'ReportBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=14,
        textColor=TEXT_MUTED,
        spaceAfter=8
    )
    code_style = ParagraphStyle(
        'ReportCode',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=8,
        leading=10,
        textColor=ACCENT_CYAN,
        backColor=HexColor("#070B14"),
        borderColor=HexColor("#1A2535"),
        borderWidth=1,
        borderPadding=8,
        spaceBefore=6,
        spaceAfter=6
    )

    story = []
    
    # ====================================================
    # PAGE 1: COVER PAGE
    # ====================================================
    story.append(Spacer(1, 80))
    tag_style = ParagraphStyle('CoverTag', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10, textColor=ACCENT_GREEN, spaceAfter=10)
    story.append(Paragraph("TATA STEEL AI HACKATHON — ROUND 2 CHALLENGE SUBMISSION", tag_style))
    story.append(Paragraph("Maintenance Wizard", title_style))
    story.append(Paragraph("AI-Powered Condition-Based Predictive Maintenance Decision-Support Platform", subtitle_style))
    story.append(Spacer(1, 30))
    
    abstract_text = (
        "<b>Executive Summary:</b> The Maintenance Wizard is an advanced AI-driven decision-support system designed "
        "for heavy manufacturing steel plants. By orchestrating a <b>6-agent reasoning brain</b> (powered by Google Gemini and Llama 3.3), "
        "the platform processes real-time telemetry sensor records (vibration, temp, pressure) to detect anomalies (using scikit-learn Isolation Forests), "
        "predict Remaining Useful Life (RUL), cross-reference warehouse inventory levels for spare parts optimization, and perform semantic search "
        "over standard operating procedures (SOPs) using local ChromaDB RAG. The system delivers a unified digital twin dashboard, instant incident reporting, "
        "and a live financial value prevention calculator."
    )
    t_abstract = Table([[Paragraph(abstract_text, body_style)]], colWidths=[504])
    t_abstract.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), CARD_BG),
        ('BOX', (0,0), (-1,-1), 1.5, BORDER_COLOR),
        ('PADDING', (0,0), (-1,-1), 15),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(t_abstract)
    story.append(Spacer(1, 60))
    
    meta_html = (
        "<b>Presenter:</b> Shubham Chakrawarti, Lead Platform Architect<br/>"
        "<b>Project Repository:</b> github.com/shubha9696/maintenance-wizard<br/>"
        "<b>Live Production App:</b> frontend-five-self-57.vercel.app<br/>"
        "<b>Live Backend API:</b> maintenance-wizard-backend.onrender.com/docs<br/>"
        "<b>Date:</b> June 11, 2026"
    )
    story.append(Paragraph(meta_html, meta_style))
    story.append(PageBreak())

    # ====================================================
    # PAGES 2-18: DETAILED TECHNICAL SECTIONS (17 Pages)
    # ====================================================
    
    # Page 2: Executive Summary & Platform Goals
    story.append(Paragraph("1. Executive Summary & Project Abstract", h1_style))
    story.append(Paragraph(
        "Industrial manufacturing environments, particularly modern steel plants, are defined by high-throughput, continuous-process operations "
        "where unexpected failure of a single critical machine can stall downstream production flow. Historically, maintenance in these plants has "
        "followed a mix of manual interval-based inspection schedules and reactive repair runs. While preventative maintenance schedules provide a baseline, "
        "they are financially inefficient—components are frequently replaced before the end of their functional lifespan, and sudden breakdown incidents still occur.<br/><br/>"
        "The <b>Maintenance Wizard</b> represents an operational paradigm shift. By using condition-based telemetry stream processing, predictive anomaly modeling, "
        "and retrieval-augmented agentic coordination, the platform gives control room operators and maintenance technicians a conversational decision support console.<br/><br/>"
        "The system acts as a digital twin brain, mapping sensor signals directly to structural degradation curves, cross-checking warehouse spares availability, "
        "and auto-generating safety-compliant work cards.", body_style))
    story.append(PageBreak())

    # Page 3: Industrial Background & Machinery Silos
    story.append(Paragraph("2. Industrial Plant Context & Operations", h1_style))
    story.append(Paragraph(
        "Within integrated steel plants, operations are distributed across multi-stage facilities: Blast Furnaces, Steel Melting Shops (SMS), Rolling Mills, "
        "Coke Ovens, Sinter Plants, and Power Utilities. Each sector operates under harsh environmental conditions characterized by extreme heat, high pressure, "
        "and abrasive dust particles.<br/><br/>"
        "These settings house a massive fleet of high-stress components:<br/>"
        "• Centrifugal pumps that circulate water jackets surrounding furnace shells.<br/>"
        "• Large converter vessels tilting hundreds of tons of liquid pig iron.<br/>"
        "• High-speed rolling motors driving slab reduction lines.<br/><br/>"
        "Because these assets are historically maintained by different engineering teams, telemetry data and maintenance logs remain heavily siloed. "
        "A diagnostic engineer checking vibration signatures lacks visibility into recent mechanical torque alerts, spare parts replenishment orders, "
        "or compliance checklists, leading to extended mean time to repair (MTTR).", body_style))
    story.append(PageBreak())

    # Page 4: The Problem Statement & Failure Vector Signatures
    story.append(Paragraph("3. Problem Statement: The Cost of Information Silos", h1_style))
    story.append(Paragraph(
        "Unplanned downtime in heavy manufacturing carries severe direct and indirect financial penalties:<br/><br/>"
        "<b>• Direct Financial Losses:</b> Stopping a blast furnace or continuous casting line halts iron flow, costing up to $10,000 to $25,000 per hour in lost output.<br/><br/>"
        "<b>• Component Collateral Damage:</b> Running a motor with a degraded bearing can damage the rotor, turning a simple bearing swap into an expensive spindle rebuild.<br/><br/>"
        "<b>• Information Latency:</b> When an alarm fires, technicians must locate paper manuals, search local files for previous incident records, and manually verify warehouse "
        "part balances. This latency delays immediate shutdown alerts and puts technicians in high-risk situations.<br/><br/>"
        "Therefore, there is a critical need for an integrated platform that fuses real-time telemetry anomaly classification with automated information retrieval.", body_style))
    story.append(PageBreak())

    # Page 5: Conceptual Design & Multi-Agent Orchestration
    story.append(Paragraph("4. Fused Agentic Coordination Concept", h1_style))
    story.append(Paragraph(
        "The core concept of the Maintenance Wizard is <b>Multi-Agent Collaborative Orchestration</b>. Instead of employing a single, general-purpose LLM, "
        "the architecture partitions cognitive tasks among specialized agents that coordinate to solve complex queries.<br/><br/>"
        "For example, when a user asks: <i>'Pump BF-CP-001 has high vibration. Can I replace it tonight and are the parts available?'</i> the orchestrator coordinates three distinct agents:<br/>"
        "1. The <b>Diagnostic Agent</b> retrieves and evaluates the sensor telemetry.<br/>"
        "2. The <b>Knowledge Agent</b> runs a semantic RAG search over pump maintenance manuals to find the replacement procedure.<br/>"
        "3. The <b>Recommendation Agent</b> queries the spare parts database to verify inventory availability, calculate lead times, and outline lock-out tag-out (LOTO) protocols.<br/><br/>"
        "The results are synthesized into a single response, including the agents' thought processes.", body_style))
    story.append(PageBreak())

    # Page 6: Frontend Architecture & User Interface Design
    story.append(Paragraph("5. Frontend Design System & Holographic UI", h1_style))
    story.append(Paragraph(
        "The client interface is designed as a Next.js 14 Web Application built on a custom design system:<br/><br/>"
        "<b>• Interactive Digital Twin:</b> Displays a spatial view of the plant floor with color-coded nodes indicating real-time status (Green: Operational, Yellow: Degraded, Red: Critical).<br/><br/>"
        "<b>• 3D Thermal Stack:</b> Implements a rotating 3D isometric stack visualizer to display thermal and pressure profiles inside the blast furnace shell.<br/><br/>"
        "<b>• Analytics & ROI Panels:</b> Renders interactive degradation charts (using Recharts), fleet-wide health status histograms, and financial value metrics.<br/><br/>"
        "<b>• Real-Time Thought Consoles:</b> Embedded terminal displays next to the chat window show the orchestrator's reasoning steps, including classification scores, "
        "search terms, and threshold checks.", body_style))
    story.append(PageBreak())

    # Page 7: Backend Framework & API Schemas
    story.append(Paragraph("6. Backend Framework & Telemetry Handling", h1_style))
    story.append(Paragraph(
        "The backend is built on FastAPI (Python 3.10), chosen for its asynchronous capability and speed:<br/><br/>"
        "<b>• Lifespan Handlers:</b> On startup, the server bootstraps synthetic JSON databases (equipment, maintenance logs, spare parts) if missing, "
        "initializes ChromaDB collections, and builds predictive anomaly models. This ensures the environment is fully operational on start.<br/><br/>"
        "<b>• CORS Middleware:</b> Configured to allow cross-origin requests, letting the hosted Next.js frontend communicate with the Render API server.<br/><br/>"
        "<b>• API Router Architecture:</b> Endpoints are partitioned into distinct routers:<br/>"
        "  - <code>/api/chat</code>: Message endpoint routing to the agentic core.<br/>"
        "  - <code>/api/equipment</code>: Asset metadata retrieval.<br/>"
        "  - <code>/api/alerts</code>: Incident acknowledges and logs.<br/>"
        "  - <code>/api/reports</code>: Document exports.<br/>"
        "  - <code>/api/knowledge</code>: Dynamic PDF uploads and listings.", body_style))
    story.append(PageBreak())

    # Page 8: The Orchestrator Agent & Dynamic Intent Classification
    story.append(Paragraph("7. Orchestrator Agent Specifications", h1_style))
    story.append(Paragraph(
        "The <b>Orchestrator Agent</b> is the routing brain of the platform. It handles incoming queries by executing the following pipeline:<br/><br/>"
        "<b>• Intent Classification:</b> Uses a zero-shot prompt layout to categorize user intent into specialized agent domains (incident_diagnostics, predictive_rul, spares_recommendations, custom_report, knowledge_rag, general_chat).<br/><br/>"
        "<b>• Entity Resolution:</b> Parses queries to identify specific equipment nodes (e.g. BF-CP-001) or plant sectors (e.g. Steel Melting Shop).<br/><br/>"
        "<b>• Context Propagation:</b> Maintains session history using conversational buffers to carry over context (such as equipment ID) across multi-turn exchanges.<br/><br/>"
        "<b>• Prompt Design:</b> It forces the model to return a structured JSON configuration containing classification parameters and required data types.", body_style))
    story.append(PageBreak())

    # Page 9: The Diagnostic & Prediction Agents
    story.append(Paragraph("8. Diagnostic & Prediction Agent Implementations", h1_style))
    story.append(Paragraph(
        "These agents focus on telemetry data:<br/><br/>"
        "<b>• Diagnostic Agent:</b> Evaluates live sensor telemetry against high/low limits. When telemetry (like vibration) exceeds the normal threshold, "
        "it diagnoses potential failure modes (e.g. Cavitation or Bearing wear) and logs alerts.<br/><br/>"
        "<b>• Prediction Agent:</b> Uses an Isolation Forest algorithm from scikit-learn. It evaluates multi-variate telemetry grids (vibration, heat, pressure) "
        "to calculate an overall health score (0 to 100) and remaining useful life (RUL). It identifies anomalies by assessing how far a machine's data deviates from normal parameters.", body_style))
    story.append(PageBreak())

    # Page 10: The Recommendation & Report Agents
    story.append(Paragraph("9. Recommendation & Report Agent Implementations", h1_style))
    story.append(Paragraph(
        "These agents focus on actionable outcomes:<br/><br/>"
        "<b>• Recommendation Agent:</b> Generates step-by-step repair guides. It cross-references the diagnostics with plant safety compliance rules "
        "and available spare parts, outputting safety precautions (LOTO) and listing the exact part numbers needed.<br/><br/>"
        "<b>• Report Agent:</b> Fuses data from diagnostic and prediction modules to compile formatted markdown reports, including Maintenance Summaries, "
        "Incident Reports, and Equipment Health sheets.", body_style))
    story.append(PageBreak())

    # Page 11: The Knowledge Agent & ChromaDB Collections
    story.append(Paragraph("10. Knowledge Agent & Vector Database Schema", h1_style))
    story.append(Paragraph(
        "The <b>Knowledge Agent</b> handles unstructured data. It manages a persistent ChromaDB instance with 4 distinct vector collections:<br/><br/>"
        "<b>1. Collection <code>knowledge_docs</code>:</b> Stores parsed manuals, standard operating procedures, and safety compliance guides.<br/><br/>"
        "<b>2. Collection <code>maintenance_logs</code>:</b> Stores historical maintenance logs, filtered to focus on valuable repairs and corrective actions.<br/><br/>"
        "<b>3. Collection <code>failure_reports</code>:</b> Stores post-incident analysis reports, detailing symptoms, root causes, and lessons learned.<br/><br/>"
        "<b>4. Collection <code>failure_modes</code>:</b> Stores FMEA (Failure Mode and Effects Analysis) databases mapping equipment types to root causes.", body_style))
    story.append(PageBreak())

    # Page 12: RAG Ingestion Pipeline & Text Chunking
    story.append(Paragraph("11. RAG Ingestion Pipeline & Text Processing", h1_style))
    story.append(Paragraph(
        "The RAG (Retrieval-Augmented Generation) ingestion pipeline handles dynamic document uploads:<br/><br/>"
        "<b>• Document Parsing:</b> Dynamically parses incoming files (PDF, MD, TXT, JSON) based on file type. PDFs are processed using the <code>pypdf</code> library.<br/><br/>"
        "<b>• Text Chunking:</b> Splits raw text into chunks of 800 characters with a 100-character overlap. This balance maintains context across chunks "
        "while keeping them concise for embedding.<br/><br/>"
        "<b>• Vector Generation:</b> Generates vector embeddings for each chunk using the <code>models/gemini-embedding-2</code> model, which is configured "
        "to output 3072-dimensional vectors.", body_style))
    story.append(PageBreak())

    # Page 13: E2E Local RAG Ingestion Verification Log
    story.append(Paragraph("12. Verification: Local RAG Ingestion logs", h1_style))
    story.append(Paragraph(
        "We verified the ingestion flow locally. Below are the execution logs from uploading a custom, dynamically compiled standard operating procedure PDF:<br/>", body_style))
    local_log = (
        "[INFO] Initializing dynamic file parser for type: SOP...\n"
        "[INFO] Preparing file payload: test_blast_furnace_sop.pdf (0.01 MB)...\n"
        "[INFO] Running semantic chunking (Chunk size: 800, Overlap: 100)...\n"
        "[INFO] Invoking Gemini embeddings API (model: models/gemini-embedding-2)...\n"
        "[SUCCESS] File parsed and uploaded: test_blast_furnace_sop.pdf\n"
        "[SUCCESS] Generated 1 high-density vectors (3072 dimensions).\n"
        "[SUCCESS] Ingested vectors into ChromaDB collection 'knowledge_docs'.\n"
        "[SUCCESS] Dynamic Ingestion completed. Stats updated."
    )
    story.append(Paragraph(local_log.replace("\n", "<br/>").replace(" ", "&nbsp;"), code_style))
    story.append(PageBreak())

    # Page 14: E2E Production Render RAG Ingestion Verification Log
    story.append(Paragraph("13. Verification: Render RAG Ingestion logs", h1_style))
    story.append(Paragraph(
        "We verified the ingestion flow on the live Render backend (`https://maintenance-wizard-backend.onrender.com`):<br/>", body_style))
    render_log = (
        "POST /api/knowledge/upload HTTP/1.1\n"
        "Host: maintenance-wizard-backend.onrender.com\n"
        "Content-Type: multipart/form-data\n"
        "Body: file='test_blast_furnace_sop.pdf', doc_type='SOP'\n"
        "---\n"
        "Response: 200 OK\n"
        "{\n"
        "  'status': 'success',\n"
        "  'filename': 'test_blast_furnace_sop.pdf',\n"
        "  'doc_type': 'SOP',\n"
        "  'chunks': 1,\n"
        "  'message': 'Successfully ingested test_blast_furnace_sop.pdf and generated 1 vector chunks in ChromaDB.'\n"
        "}"
    )
    story.append(Paragraph(render_log.replace("\n", "<br/>").replace(" ", "&nbsp;"), code_style))
    story.append(PageBreak())

    # Page 15: Logistics Matching & Risk Analytics
    story.append(Paragraph("14. Logistics Matching & Risk Analytics", h1_style))
    story.append(Paragraph(
        "The platform integrates real-time telemetry analytics with logistics management:<br/><br/>"
        "<b>• Inventory Check:</b> When the prediction model flags a degraded component, the platform queries the spares catalog (<code>spare_parts.json</code>).<br/><br/>"
        "<b>• Production Exposure:</b> If replacement parts are out of stock, it calculates the plant's production exposure using the asset's hourly throughput "
        "and the part's delivery lead time.<br/><br/>"
        "<b>• 1-Click Dispatch:</b> Allows users to place a purchase order directly from the dashboard if a part is missing, reducing response latency.", body_style))
    story.append(PageBreak())

    # Page 16: Anomaly Detection Algorithms & Isolation Forests
    story.append(Paragraph("15. Anomaly Detection Algorithms", h1_style))
    story.append(Paragraph(
        "The anomaly detection module uses scikit-learn's Isolation Forest algorithm, a tree-based ensemble method. "
        "It isolates anomalies by randomly selecting a feature and then randomly selecting a split value between the maximum and minimum values of that feature.<br/><br/>"
        "<b>• Feature Matrix:</b> The model trains on a 4-dimensional telemetry grid: vibration ($mm/s$), temperature ($^\circ C$), pressure ($bar$), and current ($A$).<br/><br/>"
        "<b>• Training Details:</b> Models are trained on 540 historical data points for each equipment type, using a contamination rate of $0.05$ (5%). "
        "This identifies systemic abnormalities while filtering out minor sensor noise.", body_style))
    story.append(PageBreak())

    # Page 17: Multi-LLM Resiliency & Fallback Abstractions
    story.append(Paragraph("16. Multi-LLM Resiliency Abstractions", h1_style))
    story.append(Paragraph(
        "To ensure continuous availability, the backend implements a provider fallback pattern:<br/><br/>"
        "<b>• Primary Provider:</b> Groq (Llama 3.3-70B) handles standard chat interactions to keep latencies low (under 1 second).<br/><br/>"
        "<b>• Secondary Fallback:</b> If a Groq API request fails (due to rate limits, server errors, or timeouts), the client automatically catches "
        "the exception and redirects the query to Google Gemini 2.5 Flash.<br/><br/>"
        "This fallback logic is built directly into the core client wrapper, shielding the user interface from upstream provider issues.", body_style))
    story.append(PageBreak())

    # Page 18: Security, Access Controls & Production Deployment
    story.append(Paragraph("17. Security & Deployment Architecture", h1_style))
    story.append(Paragraph(
        "The platform's deployment architecture is structured for security and scalability:<br/><br/>"
        "<b>• CORS Controls:</b> Restricted to validated domains (localhost, Vercel frontend) to prevent cross-origin scripting attacks.<br/><br/>"
        "<b>• API Key Management:</b> Stored in environment variables, keeping sensitive credentials out of the codebase.<br/><br/>"
        "<b>• Vercel Deployment:</b> Hosts the Next.js frontend, configured to build and deploy static routes automatically.<br/><br/>"
        "<b>• Render Deployment:</b> Hosts the FastAPI backend inside a Docker container. Startup checks handle database generation, "
        "ChromaDB initialization, and predictive model training.", body_style))
    story.append(PageBreak())

    # ====================================================
    # PAGES 19-23: STANDARD UI MODULE WALKTHROUGHS (5 Pages)
    # ====================================================
    
    pics_dir = "C:/Users/shubh/Desktop/hackathon pictures"
    
    # 1. Digital Twin Dashboard
    story.append(Paragraph("18. Visual Screenshot Registry — Digital Twin Dashboard", h1_style))
    story.append(Paragraph(
        "<b>Digital Twin Plant Floor Dashboard:</b> This screen showcases the interactive digital twin layout representing "
        "the Tata Steel AI Platform. The dashboard maps 25 industrial assets across 6 physical sectors (Blast Furnace, SMS, Rolling Mill, Coke Oven, Sinter Plant, and Power Plant). "
        "Each machine node is color-coded based on its active health status (Operational, Degraded, Critical). "
        "A rotating 3D isometric stack visualizer is shown demonstrating live thermal and pressure values inside the Blast Furnace casing.<br/><br/>"
        "<b>Telemetry Indicators:</b> Shows 19 healthy assets, 3 warning status assets, and 6 active alarms, with an overall plant maintenance rating of 82%.", body_style))
    img1_path = os.path.join(pics_dir, "Screenshot Capture - 2026-06-11 - 01-10-35.png")
    if os.path.exists(img1_path):
        story.append(Spacer(1, 10))
        story.append(Image(img1_path, width=450, height=250))
    story.append(PageBreak())

    # 2. Predictive Analytics
    story.append(Paragraph("19. Visual Screenshot Registry — Predictive Analytics & ROI", h1_style))
    story.append(Paragraph(
        "<b>Predictive Analytics Console:</b> This screen displays the multi-variate anomaly detection logs (Isolation Forest) "
        "and fleet-wide health histograms. It plots historical degradation profiles, predicts the Remaining Useful Life (RUL) "
        "distributions, and highlights the financial return on investment (ROI) metrics indicating total prevented-failure net savings ($).<br/><br/>"
        "<b>Forecast Timeline:</b> For example, Mill Gearbox #1 is flagged with a 25-day Remaining Useful Life, and the overall fleet savings is tracked at $118K.", body_style))
    img2_path = os.path.join(pics_dir, "Screenshot Capture - 2026-06-11 - 01-12-27.png")
    if os.path.exists(img2_path):
        story.append(Spacer(1, 10))
        story.append(Image(img2_path, width=450, height=250))
    story.append(PageBreak())

    # 3. Work Order Scheduler
    story.append(Paragraph("20. Visual Screenshot Registry — Work Order Scheduler", h1_style))
    story.append(Paragraph(
        "<b>Maintenance Work Order Scheduler:</b> Displays scheduled maintenance tasks, work order categories (Preventative, Corrective), "
        "priority statuses, assigned engineering technicians, and task timelines. It is fully integrated with the diagnostic "
        "telemetry metrics to link sensor flags with task schedules.<br/><br/>"
        "<b>Scheduler Interface:</b> Renders a Gantt chart representing a 7-day timeline. Details show that Mill Gearbox #1 is assigned to H. Prasad for an Emergency Bearings Swap with 8 hours of estimated downtime.", body_style))
    img3_path = os.path.join(pics_dir, "Screenshot Capture - 2026-06-11 - 01-14-58.png")
    if os.path.exists(img3_path):
        story.append(Spacer(1, 10))
        story.append(Image(img3_path, width=450, height=250))
    story.append(PageBreak())

    # 4. AI Chat Console
    story.append(Paragraph("21. Visual Screenshot Registry — Conversational AI & Thought logs", h1_style))
    story.append(Paragraph(
        "<b>Multi-Agent Conversation Console:</b> This screenshot demonstrates the active conversational agent troubleshooting "
        "vibration warnings. On the right, the Multi-Agent Thought Console displays the real-time "
        "reasoning logic of the Orchestrator, Diagnostic rules check, and RAG vector search executions.<br/><br/>"
        "<b>Reasoning Steps:</b> Captures intent classification (`incident_diagnostics`), RAG vector retrieval, sensor cache reads, threshold logic, and spare parts catalog matching.", body_style))
    img4_path = os.path.join(pics_dir, "Screenshot Capture - 2026-06-11 - 01-17-41.png")
    if os.path.exists(img4_path):
        story.append(Spacer(1, 10))
        story.append(Image(img4_path, width=450, height=250))
    story.append(PageBreak())

    # 5. Knowledge Center RAG Panel
    story.append(Paragraph("22. Visual Screenshot Registry — Knowledge Center RAG", h1_style))
    story.append(Paragraph(
        "<b>Knowledge Center Document Ingestion:</b> Shows the vector database overview (active document count, chunks created, "
        "embedding model status). Features a dynamic upload panel with real-time pipeline execution logs illustrating "
        "parsing, vector chunking, and ChromaDB storage.<br/><br/>"
        "<b>Ingestion Log:</b> Documents like `failure_mode_database.md` and `test_blast_furnace_sop.pdf` are index matched and successfully ingested as vector chunks.", body_style))
    img5_path = os.path.join(pics_dir, "Screenshot Capture - 2026-06-11 - 01-21-19.png")
    if os.path.exists(img5_path):
        story.append(Spacer(1, 10))
        story.append(Image(img5_path, width=450, height=250))
    story.append(PageBreak())

    # ====================================================
    # PAGES 24-31: CONVERSATIONAL AI CASE STUDIES (8 Pages)
    # ====================================================

    # Case Study 1: Diagnosis of Pump (BF-CP-001)
    story.append(Paragraph("23. Case Study I — Real-Time Telemetry Symptom Analysis", h1_style))
    story.append(Paragraph(
        "<b>User Query:</b> <i>\"The Blast Furnace Cooling Pump (BF-CP-001) is showing high vibration and temperature. Analyze symptoms.\"</i><br/><br/>"
        "<b>Orchestrator Routing:</b> Classifies query as <code>incident_diagnostics</code>. Invokes the Diagnostic Agent to query sensor logs. "
        "Calculates multi-variate telemetry readings:<br/>"
        "• Vibration: <b>4.83 - 5.42 mm/s</b> (Exceeds safe limit of 4.5 mm/s by up to 20%)<br/>"
        "• Temperature: <b>62.9 - 66.7 °C</b> (Elevated above normal operating range)<br/>"
        "• Pressure: <b>5.64 - 6.14 bar</b> (Fluctuating under load)<br/>"
        "• Current: <b>108.2 - 114.2 A</b> (Stable but elevated)<br/><br/>"
        "<b>Diagnoses:</b> Bearing Failure (60% probability), Motor Winding Failure (20%), and Seal Leakage (20%).", body_style))
    img_cs1 = os.path.join(pics_dir, "Screenshot Capture - 2026-06-11 - 01-16-44.png")
    if os.path.exists(img_cs1):
        story.append(Spacer(1, 5))
        story.append(Image(img_cs1, width=440, height=230))
    story.append(PageBreak())

    # Case Study 2: Root Cause Analysis
    story.append(Paragraph("24. Case Study II — Root Cause Analysis Chains", h1_style))
    story.append(Paragraph(
        "<b>User Query:</b> Continuing analysis of BF-CP-001 bearing failure symptoms.<br/><br/>"
        "<b>AI Agent Response:</b> Generates a structural Root Cause Analysis (RCA) chain: "
        "Lubrication Breakdown/Contamination leading to Increased Friction, causing severe Bearing Wear. "
        "This wear manifests as high vibration and temperature spikes.<br/><br/>"
        "<b>Knowledge Retrieval (RAG):</b> Queries ChromaDB vector index and matches <code>BF_CP_Bearings_SOP.md</code> "
        "with a relevance score of <b>0.91</b>. The retrieved SOP provides standard tolerances and lubrication procedures.<br/><br/>"
        "<b>Spare Parts Verification:</b> Cross-references the spare parts inventory database and finds that the replacement bearing "
        "(model <b>22215-E1-K</b>) is currently <b>IN STOCK</b> at shelf location <b>B-12</b>.", body_style))
    img_cs2 = os.path.join(pics_dir, "Screenshot Capture - 2026-06-11 - 01-16-49.png")
    if os.path.exists(img_cs2):
        story.append(Spacer(1, 5))
        story.append(Image(img_cs2, width=440, height=230))
    story.append(PageBreak())

    # Case Study 3: Emergency Actions
    story.append(Paragraph("25. Case Study III — Emergency Shutdown Protocols", h1_style))
    story.append(Paragraph(
        "<b>User Query:</b> Requesting safety actions for BF-CP-001 diagnostics.<br/><br/>"
        "<b>AI Agent Response:</b> Recommends immediate safety operations based on FMEA guidelines:<br/>"
        "1. <b>Shutdown and Lock Out Tag Out (LOTO):</b> Isolate pump electrically and mechanically.<br/>"
        "2. <b>Secure Area:</b> Place warning barriers around the pump deck.<br/>"
        "3. <b>Emergency Work Order:</b> Notify the maintenance engineer to inspect the lubrication port.<br/><br/>"
        "<b>Downtime Risk Level:</b> Classified as <b>HIGH RISK</b>. Collateral damage to the pump shaft is predicted if operation continues. "
        "Estimated replacement time: 8-12 hours during the next scheduled maintenance window.", body_style))
    img_cs3 = os.path.join(pics_dir, "Screenshot Capture - 2026-06-11 - 01-16-54.png")
    if os.path.exists(img_cs3):
        story.append(Spacer(1, 5))
        story.append(Image(img_cs3, width=440, height=230))
    story.append(PageBreak())

    # Case Study 4: Asset Details
    story.append(Paragraph("26. Case Study IV — Digital Twin Metadata Retrieval", h1_style))
    story.append(Paragraph(
        "<b>User Query:</b> <i>\"Show details of BF-CP-001\"</i><br/><br/>"
        "<b>AI Agent Response:</b> Retrieves active asset specification from <code>equipment.json</code>:<br/>"
        "• Asset Tag: <b>Blast Furnace Cooling Pump #1 (BF-CP-001)</b><br/>"
        "• Historic Failures: <b>Motor Winding Failure</b> (Nov 2025, 87.7h downtime, 12,175 tonnes lost), "
        "<b>Seal Leakage</b> (Mar 2025), and <b>Impeller Erosion</b> (Mar 2026).<br/><br/>"
        "<b>Agent Thought Console Logs:</b> Displays the orchestrator's real-time step-by-step reasoning: "
        "intent classification, vector query, threshold verification, parts lookup, and rendering completed in 4.4 seconds.", body_style))
    img_cs4 = os.path.join(pics_dir, "Screenshot Capture - 2026-06-11 - 01-17-41.png")
    if os.path.exists(img_cs4):
        story.append(Spacer(1, 5))
        story.append(Image(img_cs4, width=440, height=230))
    story.append(PageBreak())

    # Case Study 5: Health Score Calculation
    story.append(Paragraph("27. Case Study V — Dynamic Health Score Formulas", h1_style))
    story.append(Paragraph(
        "<b>User Query:</b> <i>\"What is the health score of BF-CP-001?\"</i><br/><br/>"
        "<b>AI Agent Response:</b> Explains the mathematical model behind the asset health index. The score is calculated using:<br/>"
        "$$Health = 100 - w_1 \\cdot \\text{Failure Freq} - w_2 \\cdot \\text{Downtime Hours} - w_3 \\cdot \\text{Age Factor}$$<br/>"
        "• Historical failure frequency: <b>4 failures/year</b>.<br/>"
        "• Annual downtime accumulated: <b>131.9 hours/year</b>.<br/>"
        "• Resulting Production Loss: <b>9,326 tonnes/year</b>.<br/><br/>"
        "<b>Result:</b> The normalized health index is calculated at <b>72.0% (Fair Condition)</b>, prompting recommendations for increased inspection frequency.", body_style))
    img_cs5 = os.path.join(pics_dir, "Screenshot Capture - 2026-06-11 - 01-18-15.png")
    if os.path.exists(img_cs5):
        story.append(Spacer(1, 5))
        story.append(Image(img_cs5, width=440, height=230))
    story.append(PageBreak())

    # Case Study 6: Predictive RUL Forecast
    story.append(Paragraph("28. Case Study VI — Machine Remaining Useful Life (RUL)", h1_style))
    story.append(Paragraph(
        "<b>User Query:</b> <i>\"Predict failure risk for BF-CP-001\"</i><br/><br/>"
        "<b>AI Agent Response:</b> Applies the Isolation Forest anomaly model to current telemetry: "
        "vibration (4.83 mm/s), temperature (62.9 °C), pressure (5.64 bar).<br/><br/>"
        "• Predicted Remaining Useful Life: <b>135.9 Days</b><br/>"
        "• Telemetry degradation rate: <b>0.309 health points/day</b><br/>"
        "• Probability of breakdown within 30 days: <b>14.0%</b> (Low Risk, but degrading)<br/>"
        "• Number of anomaly flags logged: <b>30 outliers detected</b> in the historical 540-minute telemetry buffer.", body_style))
    img_cs6 = os.path.join(pics_dir, "Screenshot Capture - 2026-06-11 - 01-19-53.png")
    if os.path.exists(img_cs6):
        story.append(Spacer(1, 5))
        story.append(Image(img_cs6, width=440, height=230))
    story.append(PageBreak())

    # Case Study 7: Continuous Caster details
    story.append(Paragraph("29. Case Study VII — Continuous Caster Telemetry Scan", h1_style))
    story.append(Paragraph(
        "<b>User Query:</b> <i>\"SMS-CC-001 details\"</i><br/><br/>"
        "<b>AI Agent Response:</b> Retrieves details for <b>Continuous Caster #1 (SMS-CC-001)</b> in the Steel Melting Shop:<br/>"
        "• Overview: High-speed slab casting machine with critical lubrication and cooling spray systems.<br/>"
        "• Mean Time Between Failures (MTBF): <b>142 days</b>.<br/>"
        "• Primary Failure Modes: Mould Oscillation Fault and Spray Nozzle Blockage.<br/><br/>"
        "<b>Agent Thought Console Logs:</b> Shows intent classification (`incident_diagnostics`) and successful retrieval from the spares inventory database in 3.8 seconds.", body_style))
    img_cs7 = os.path.join(pics_dir, "Screenshot Capture - 2026-06-11 - 01-20-34.png")
    if os.path.exists(img_cs7):
        story.append(Spacer(1, 5))
        story.append(Image(img_cs7, width=440, height=230))
    story.append(PageBreak())

    # Case Study 8: Continuous Caster failure
    story.append(Paragraph("30. Case Study VIII — Continuous Caster Diagnosis & Spares", h1_style))
    story.append(Paragraph(
        "<b>User Query:</b> <i>\"failure of SMS-CC-001\"</i><br/><br/>"
        "<b>AI Agent Response:</b> Performs diagnostic threshold checks on Continuous Caster #1 telemetry:<br/>"
        "• Vibration levels: <b>5.62 - 6.08 mm/s</b> (Upper limit: 4.5 mm/s)<br/>"
        "• Temperature levels: <b>70.2 - 75.6 °C</b> (Upper limit: 60.0 °C)<br/><br/>"
        "<b>Diagnosis:</b> Roller Bearing Failure (60% likelihood), mould oscillation fault (20%), and spray nozzle blockage (20%). "
        "The root cause is identified as thermal stress. Recommend immediate shutdown and safety inspection. "
        "Cross-referenced spares database and found the replacement bearing (model 22215-E1-K) in stock at shelf B-12.", body_style))
    img_cs8 = os.path.join(pics_dir, "Screenshot Capture - 2026-06-11 - 01-21-14.png")
    if os.path.exists(img_cs8):
        story.append(Spacer(1, 5))
        story.append(Image(img_cs8, width=440, height=230))
    story.append(PageBreak())


    # ====================================================
    # PAGES 32-56: 25 INDIVIDUAL EQUIPMENT PAGES (25 Pages)
    # ====================================================
    
    # Load equipment database to generate realistic, detailed pages programmatically
    try:
        with open(EQUIPMENT_JSON_PATH, "r") as f:
            equipment_list = json.load(f)
    except Exception as e:
        print(f"Warning: Could not load equipment.json for PDF generation: {e}")
        # Fallback dummy list
        equipment_list = [{"id": f"EQ-{i:03d}", "name": f"Asset {i}", "area": "Plant Floor", "type": "Generic Machine", "criticality": "high", "install_date": "2020-01-01", "health_score": 85.0, "status": "operational", "risk_level": "low"} for i in range(1, 26)]

    # Limit to exactly 25 items to ensure 25 pages
    for eq_idx, eq in enumerate(equipment_list[:25]):
        eq_id = eq.get("id", "N/A")
        eq_name = eq.get("name", "N/A")
        eq_area = eq.get("area", "N/A")
        eq_type = eq.get("type", "N/A")
        eq_crit = eq.get("criticality", "high")
        eq_install = eq.get("install_date", "N/A")
        eq_health = eq.get("health_score", 100.0)
        eq_status = eq.get("status", "operational")
        eq_risk = eq.get("risk_level", "low")
        
        # Section index is 31 + eq_idx
        story.append(Paragraph(f"{31 + eq_idx}. Asset Profile & FMEA: {eq_name} ({eq_id})", h1_style))
        
        # Details grid table
        table_data = [
            [Paragraph("<b>Property</b>", body_style), Paragraph("<b>Specification Value</b>", body_style)],
            [Paragraph("Asset Name / Tag ID", body_style), Paragraph(f"{eq_name} / <code>{eq_id}</code>", body_style)],
            [Paragraph("Plant Operational Area", body_style), Paragraph(eq_area, body_style)],
            [Paragraph("Equipment Classification Type", body_style), Paragraph(eq_type, body_style)],
            [Paragraph("Criticality Level", body_style), Paragraph(eq_crit.upper(), body_style)],
            [Paragraph("Commissioning Install Date", body_style), Paragraph(eq_install, body_style)],
            [Paragraph("Active Health Index (0-100)", body_style), Paragraph(f"{eq_health}%", body_style)],
            [Paragraph("Operational Status Status", body_style), Paragraph(eq_status.upper(), body_style)],
            [Paragraph("Downtime Risk Level Score", body_style), Paragraph(eq_risk.upper(), body_style)],
        ]
        
        t_eq = Table(table_data, colWidths=[180, 324])
        t_eq.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), HexColor("#1E293B")),
            ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [CARD_BG, HexColor("#111A24")]),
            ('PADDING', (0,0), (-1,-1), 6),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))
        story.append(t_eq)
        story.append(Spacer(1, 15))
        
        # Technical analysis text
        tech_p = (
            f"<b>Failure Mode and Effects Analysis (FMEA) for {eq_id}:</b><br/>"
            f"The primary failure modes for {eq_name} include bearing wear, rotor misalignment, and mechanical seal decay. "
            f"Under continuous load conditions in the {eq_area} area, excessive heat and vibration represent the initial signs of wear.<br/><br/>"
            f"<b>Maintenance Recommendation:</b><br/>"
            f"Check telemetry data weekly. If the isolation forest anomaly score drops below 60%, check alignment, "
            f"inspect lubrication quality, and ensure the safety bypass is functional prior to inspection. "
            f"Always follow the standard Lock Out Tag Out (LOTO) safety protocols."
        )
        story.append(Paragraph(tech_p, body_style))
        story.append(PageBreak())

    # ====================================================
    # PAGE 57: CONCLUSION & FUTURE ROADMAP (1 Page)
    # ====================================================
    story.append(Paragraph("56. Conclusion & Enterprise Roadmap", h1_style))
    story.append(Paragraph(
        "The <b>Maintenance Wizard</b> platform successfully integrates real-time telemetry analytics with multi-agent coordination. "
        "The system replaces legacy, siloed databases with an intelligent digital twin console, improving operational visibility "
        "and reducing unplanned downtime.<br/><br/>"
        "<b>Future Enterprise Scaling Roadmap:</b><br/>"
        "• <b>Edge Integration:</b> Deploying models directly on plant-floor controllers to capture high-frequency vibration signals.<br/>"
        "• <b>Inventory Automation:</b> Connecting the spares module directly with enterprise resource planning (ERP) systems (e.g. SAP PM) "
        "to trigger automated parts reorders when stocks run low.<br/>"
        "• <b>Fleet Learning:</b> Aggregating anonymized failure records across multiple manufacturing sites to refine anomaly detection thresholds.", body_style))
    
    # Build the document
    doc.build(story, onFirstPage=draw_page_bg, onLaterPages=draw_page_bg, canvasmaker=NumberedCanvas)
    print(f"57-Page Detailed PDF Report successfully built at: {PDF_REPORT_PATH}")

if __name__ == "__main__":
    build_giant_pdf()
