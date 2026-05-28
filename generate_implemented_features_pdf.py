import os
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
)
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    """
    A canvas that enables multi-pass page numbering ("Page X of Y")
    and renders consistent headers/footers on all pages except the cover page.
    """
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
            self.draw_page_elements(num_pages)
            super().showPage()
        super().save()

    def draw_page_elements(self, page_count):
        # Do not draw headers or footers on the cover page (Page 1)
        if self._pageNumber == 1:
            return
            
        self.saveState()
        
        # Primary branding colors
        primary_color = colors.HexColor("#1E3B8A")   # Deep Corporate Blue
        text_muted = colors.HexColor("#64748B")      # Muted Slate Gray
        border_color = colors.HexColor("#E2E8F0")    # Soft border gray
        
        # --- HEADER ---
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(primary_color)
        self.drawString(54, 750, "DataSense.AI  |  Platform Implementation & Feature Catalog")
        
        # Thin divider line below header
        self.setStrokeColor(border_color)
        self.setLineWidth(0.75)
        self.line(54, 742, 558, 742)
        
        # --- FOOTER ---
        # Thin divider line above footer
        self.line(54, 52, 558, 52)
        
        self.setFont("Helvetica", 8)
        self.setFillColor(text_muted)
        self.drawString(54, 38, "DataSense.AI  |  SaaS Platform Capabilities Documentation")
        
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.setFont("Helvetica-Bold", 8)
        self.drawRightString(558, 38, page_text)
        
        self.restoreState()

def create_callout(text, style, title="Feature Summary", bg_hex="#F8FAFC", border_hex="#3B82F6"):
    """
    Creates a styled callout box with a colored left-accent border and light background.
    """
    callout_content = f"<b><font color='{border_hex}'>{title}</font></b><br/><br/>{text}"
    p = Paragraph(callout_content, style)
    
    t = Table([[p]], colWidths=[504])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor(bg_hex)),
        ('LINELEFT', (0,0), (0,-1), 4, colors.HexColor(border_hex)),
        ('TOPPADDING', (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        ('LEFTPADDING', (0,0), (-1,-1), 14),
        ('RIGHTPADDING', (0,0), (-1,-1), 14),
    ]))
    return t

def generate_features_pdf(output_path="datasense_ai_implemented_features.pdf"):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=72,
        bottomMargin=72
    )

    styles = getSampleStyleSheet()
    
    # Custom Palette
    c_primary = colors.HexColor("#1E3A8A")    # Dark Deep Blue
    c_secondary = colors.HexColor("#7C3AED")  # Accent Royal Purple
    c_charcoal = colors.HexColor("#1E293B")   # Off-black charcoal for readability
    c_slate = colors.HexColor("#475569")      # Dark slate grey for code/paths
    c_border = colors.HexColor("#CBD5E1")
    
    # Custom Paragraph Styles
    title_style = ParagraphStyle(
        'CoverTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=26,
        leading=32,
        textColor=c_primary,
        alignment=1, # Center
        spaceAfter=15
    )
    
    subtitle_style = ParagraphStyle(
        'CoverSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=16,
        textColor=c_secondary,
        alignment=1, # Center
        spaceAfter=40
    )
    
    meta_style = ParagraphStyle(
        'CoverMeta',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=14,
        textColor=colors.HexColor("#64748B"),
        alignment=1, # Center
        spaceAfter=5
    )
    
    h1_style = ParagraphStyle(
        'MainHeading',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=16,
        leading=20,
        textColor=c_primary,
        spaceBefore=16,
        spaceAfter=10,
        keepWithNext=True
    )
    
    h2_style = ParagraphStyle(
        'SubHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=14,
        textColor=c_secondary,
        spaceBefore=12,
        spaceAfter=6,
        keepWithNext=True
    )
    
    body_style = ParagraphStyle(
        'BodyTextCustom',
        parent=styles['BodyText'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=14,
        textColor=c_charcoal,
        spaceAfter=10
    )
    
    callout_body_style = ParagraphStyle(
        'CalloutText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.0,
        leading=13.0,
        textColor=c_charcoal
    )
    
    code_style = ParagraphStyle(
        'CodeCellText',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=8.0,
        leading=11.0,
        textColor=c_slate
    )

    table_header_style = ParagraphStyle(
        'TableHeaderText',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9.0,
        textColor=colors.white,
        alignment=1
    )

    table_cell_style = ParagraphStyle(
        'TableCellText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11.0,
        textColor=c_charcoal
    )

    table_cell_code_style = ParagraphStyle(
        'TableCellCodeText',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=8.0,
        leading=10.0,
        textColor=c_slate
    )

    story = []

    # ==========================================
    #             PAGE 1: COVER PAGE
    # ==========================================
    story.append(Spacer(1, 120))
    story.append(Paragraph("DATASENSE.AI PLATFORM GUIDE", subtitle_style))
    story.append(Spacer(1, 10))
    story.append(Paragraph("Implemented Features &amp;<br/>System Architecture Overview", title_style))
    story.append(Spacer(1, 5))
    
    # Decorative colored horizontal bar
    dec_bar = Table([[""]], colWidths=[200], rowHeights=[4])
    dec_bar.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), c_secondary),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(dec_bar)
    story.append(Spacer(1, 30))
    
    story.append(Paragraph(
        "A comprehensive directory detailing all active modules, mathematical structures, database schemas, "
        "background services, and analytical capabilities currently deployed within the DataSense.AI online "
        "shopping behaviour analysis system.",
        ParagraphStyle('CoverDesc', parent=body_style, alignment=1, fontSize=10.5, leading=15, textColor=colors.HexColor("#475569"))
    ))
    
    story.append(Spacer(1, 150))
    
    # Metadata footer
    story.append(Paragraph("<b>System Architecture:</b> Multi-Tenant Python-Flask SaaS Application", meta_style))
    story.append(Paragraph("<b>Database Layer:</b> MongoDB (pymongo connection pool)", meta_style))
    story.append(Paragraph("<b>Asynchronous Workers:</b> Celery + Redis + Gevent", meta_style))
    story.append(Paragraph(f"<b>Documentation Compiled:</b> {datetime.now().strftime('%B %d, %Y')}", meta_style))
    story.append(PageBreak())

    # ==========================================
    #             PAGE 2: EXECUTIVE SUMMARY & TECH STACK
    # ==========================================
    story.append(Paragraph("1. Executive Summary &amp; Core Architecture", h1_style))
    story.append(Paragraph(
        "<b>DataSense.AI</b> is a highly-integrated, multi-tenant Software-as-a-Service (SaaS) analytics platform "
        "engineered to translate raw transaction streams into actionable retail strategies. Instead of generating "
        "flat, static dashboard aggregations, the system builds an operational metrics layer leveraging advanced linear "
        "algebra projections, market-basket frequent pattern mining, and temporal retention models to optimize business "
        "margins, inventory flow, and customer lifetime value (LTV).",
        body_style
    ))
    
    # Tech Stack Callout
    tech_stack_desc = (
        "• <b>Backend Framework:</b> Python Flask with Flask-Login context handling and Flask-Mail SMTP integrations.<br/>"
        "• <b>Database Storage:</b> MongoDB (via <code>pymongo</code>) providing high-throughput bulk inserts and aggregations.<br/>"
        "• <b>Distributed Queue:</b> Celery cluster using Redis as a broker and Gevent pools for asynchronous CSV parsing.<br/>"
        "• <b>Analytics Engines:</b> Scikit-Learn, NumPy, Pandas, SciPy, and Mlxtend (Apriori frequent itemsets).<br/>"
        "• <b>Strategic Reporting:</b> Dual PDF compilation layers powered by <code>fpdf2</code> and <code>reportlab</code>."
    )
    story.append(create_callout(tech_stack_desc, callout_body_style, "Operational Technology Stack", "#F0FDF4", "#10B981"))
    story.append(Spacer(1, 10))

    story.append(Paragraph("System Architecture Flow", h2_style))
    story.append(Paragraph(
        "Businesses access a isolated analytics sandbox where they register accounts, upload user datasets, "
        "define custom mapping schemas, and execute models. Multi-tenancy is strictly enforced across all database "
        "collections via a partitioned <code>business_id</code> field indexing strategy, ensuring that data queries, "
        "segmentations, and report downloads are locked to the currently authenticated corporate context.",
        body_style
    ))
    
    # Simple ASCII diagram or graphic text in a callout
    flow_diagram = (
        "<b>[Business Client]</b> → (Flask Web GUI / Uploads API)<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;↓<br/>"
        "<b>[Celery Background Workers]</b> ← <i>(Redis Broker)</i> → <b>[MongoDB Datasets]</b><br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;↓<br/>"
        "<b>[Analytics Suite]</b> (Pandas Aggs / NumPy Cosine / SVD / Apriori Rules)<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;↓<br/>"
        "<b>[Strategic Actions]</b> (Re-Engagement Emails / Restocking Tables / PDF Compilers)"
    )
    story.append(create_callout(flow_diagram, callout_body_style, "DataSense.AI Processing Pipeline", "#F8FAFC", "#3B82F6"))
    story.append(PageBreak())

    # ==========================================
    #             PAGE 3: AUTH & INGESTION PIPELINE
    # ==========================================
    story.append(Paragraph("2. Authentication &amp; Multi-Tenant Sandbox", h1_style))
    story.append(Paragraph(
        "DataSense.AI enforces isolated multi-tenant workspaces to ensure complete data boundary protection. "
        "The security modules are built around standard web encryption protocols, email verification steps, "
        "and session control layers.",
        body_style
    ))
    
    auth_features = (
        "• <b>Business Registration &amp; Welcoming:</b> Registers companies, hashes passwords with SHA-256 (via Werkzeug), "
        "and automatically dispatches an HTML welcome newsletter using <code>Flask-Mail</code> templates.<br/>"
        "• <b>Forgot Password &amp; 6-Digit OTP:</b> Provides self-service secure resets. Generates a random 6-digit passcode "
        "with a strict 10-minute database-enforced TTL (stored in <code>password_resets</code> collection).<br/>"
        "• <b>Corporate Customization:</b> Allows uploading custom corporate logos (up to 2MB) stored in organized "
        "directories, rendering custom headers dynamically across the UI and PDF exports."
    )
    story.append(create_callout(auth_features, callout_body_style, "Core Authentication Subsystems", "#FAF5FF", "#8B5CF6"))
    story.append(Spacer(1, 10))

    story.append(Paragraph("3. Asynchronous Data Ingestion Pipeline", h1_style))
    story.append(Paragraph(
        "To process massive transaction archives without compromising web server responsiveness, DataSense.AI "
        "implements an asynchronous file processing architecture powered by Celery workers.",
        body_style
    ))

    ingestion_features = (
        "• <b>Multi-File Upload UI:</b> Accepts three simultaneous CSV uploads: <code>users.csv</code>, <code>products.csv</code>, "
        "and <code>orders.csv</code>. Incorporates a smart CSV columns mapping parser, enabling users to bind arbitrary "
        "header names to standard database columns.<br/>"
        "• <b>Asynchronous Task Delegation:</b> Stores raw files temporarily in <code>/uploads</code> and offloads "
        "parsing to Celery. Uses a Gevent worker pool to insert documents in chunks of 10,000 for high performance.<br/>"
        "• <b>Real-time Ingestion Tracking:</b> Web clients poll <code>/api/dataset/&lt;id&gt;/status</code> to receive progress "
        "percentages, inserted rows, and queue positions.<br/>"
        "• <b>Error Reporting Layer:</b> Validates fields (date formats, numeric bounds). Captures row-level ingestion errors "
        "in the <code>upload_errors</code> collection, allowing administrators to download a detailed CSV error log.<br/>"
        "• <b>Soft-Delete History Management:</b> Historic datasets are managed under <code>/data-history</code> where users "
        "can view record counts, soft-delete datasets to exclude them from calculations, or restore them from trash."
    )
    story.append(create_callout(ingestion_features, callout_body_style, "Bulk Data Pipeline Features", "#FFFBEB", "#D97706"))
    story.append(PageBreak())

    # ==========================================
    #             PAGE 4: KPI DASHBOARD & DATA MINING
    # ==========================================
    story.append(Paragraph("4. Interactive KPI Dashboard &amp; Analytics", h1_style))
    story.append(Paragraph(
        "The web dashboard serves as the central hub for operational visibility. It translates raw MongoDB "
        "collections into high-level business indicators using a variety of aggregations, filters, and charts.",
        body_style
    ))

    dashboard_features = (
        "• <b>Core Business KPIs:</b> Real-time tracking of Gross Consolidated Revenue, Total Completed Orders, "
        "Unique Active Clients, and Average Order Value (AOV).<br/>"
        "• <b>Dynamic Global Filtering:</b> Instant filtering of charts by Date Ranges, Countries, Genders, "
        "Product Categories, Payment Methods, and Order Value Ranges.<br/>"
        "• <b>Visual Charts Suite:</b> Interactive trends built with Chart.js, covering Monthly Revenues, "
        "Category Revenue Contributions, Payment Channels, Country Distributions, and Age Demographics.<br/>"
        "• <b>Direct Data Exports:</b> Allows exporting current filtered transactional views as a standardized CSV file."
    )
    story.append(create_callout(dashboard_features, callout_body_style, "Dashboard &amp; Visual Analytics Capabilities", "#F0FDF4", "#10B981"))
    story.append(Spacer(1, 10))

    story.append(Paragraph("5. Advanced Data Mining &amp; Vector Mathematics", h1_style))
    story.append(Paragraph(
        "To deliver advanced intelligence, the system maps transaction matrices to multi-dimensional vector spaces "
        "and executes mathematical models implemented in <code>analysis.py</code>.",
        body_style
    ))

    math_features = (
        "• <b>L2-Normalized Cosine Similarity Matrix:</b> Normalizes user product purchase vectors to unit lengths. "
        "Computes pairwise cosine similarity using optimized NumPy matrix multiplication (dot product), yielding a "
        "scale-invariant customer similarity matrix for look-alike buyer groups.<br/>"
        "• <b>Singular Value Decomposition (SVD):</b> Centers user-product interaction matrices and projects "
        "sparse customer coordinates into low-dimensional latent spaces. Automatically isolates the first three "
        "principal dimensions (Customer Personas) and identifies their high-weight signature products.<br/>"
        "• <b>Apriori Association Rule Mining:</b> Groups transactions into binary purchase baskets and uses the "
        "Apriori paradigm (from <code>mlxtend</code>) to mine frequent itemsets. Calculates Support, Confidence, "
        "and Lift metrics to uncover cross-sell rules. Resolves the list of specific buyers for co-purchased items."
    )
    story.append(create_callout(math_features, callout_body_style, "Deployed Mathematical Engines", "#FAF5FF", "#8B5CF6"))
    story.append(PageBreak())

    # ==========================================
    #             PAGE 5: CLIENT RETENTION & INVENTORY ADVISORY
    # ==========================================
    story.append(Paragraph("6. Customer Retention &amp; Automated Campaigns", h1_style))
    story.append(Paragraph(
        "DataSense.AI features an automated re-engagement campaigner designed to combat customer churn "
        "using temporal decay timelines and targeted incentive matching.",
        body_style
    ))

    retention_features = (
        "• <b>Lifecycle Churn Classification:</b> Segments inactive customers into specific risk phases based on days "
        "elapsed since their last purchase: At Risk (30–60 days), Dormant (60–90 days), and Churned (&gt;90 days).<br/>"
        "• <b>Targeted Product Recommendations:</b> Identifies a churned customer's most recent purchase and "
        "uses association rules (Apriori co-purchases) or category affinity matrices to find the best product to recommend.<br/>"
        "• <b>Automated Incentives:</b> Assigns discount coupons dynamically based on risk severity (e.g. 15% for "
        "At Risk, 20% for Dormant, 40% for Churned), complete with generated coupon codes (COMEBACK15, etc.).<br/>"
        "• <b>One-Click &amp; Bulk Campaigner:</b> Integrates with Flask-Mail to outbox styled HTML re-engagement newsletters "
        "to targeted segments, with mock backups for testing when SMTP credentials are omitted."
    )
    story.append(create_callout(retention_features, callout_body_style, "Lifecycle Campaigning Module", "#FFFBEB", "#D97706"))
    story.append(Spacer(1, 10))

    story.append(Paragraph("7. Profitability &amp; Inventory Advisory", h1_style))
    story.append(Paragraph(
        "The inventory advisory system matches sales velocity metrics with wholesale procurement cost data, "
        "enabling businesses to identify stockouts that threaten profit margins.",
        body_style
    ))

    inventory_features = (
        "• <b>Product Profitability Pipeline:</b> Computes total revenues, cost of goods sold, total margins, "
        "and exact margin percentages for each catalog item.<br/>"
        "• <b>Stock Status Scanner:</b> Monitors database stock levels, flagging items that are running low (stock &lt; 35).<br/>"
        "• <b>Critical Restocking Orders:</b> Recommends specific restocking quantities based on sales history, "
        "calculating estimated restock costs, estimated profit gains, and assigning priority tiers (CRITICAL, HIGH, MEDIUM).<br/>"
        "• <b>Seasonal Trend Detection:</b> Ranks products by season (Winter, Spring, Summer, Autumn) using transactional date logs.<br/>"
        "• <b>AI Sales Growth Advisor:</b> Categorizes inventory into action classes (e.g., 'Critical Growth' - restock immediately, "
        "'Promote &amp; Accelerate' - increase marketing, 'High Margin/Low Vol' - push promotions) with clear reasoning."
    )
    story.append(create_callout(inventory_features, callout_body_style, "Operational Inventory &amp; Stock Advisory Modules", "#F0FDF4", "#10B981"))
    story.append(PageBreak())

    # ==========================================
    #             PAGE 6: PDF COMPILING & FILE INVENTORY
    # ==========================================
    story.append(Paragraph("8. Corporate Reporting &amp; Handbooks", h1_style))
    story.append(Paragraph(
        "To facilitate offline analysis and corporate presentations, DataSense.AI implements two independent "
        "PDF compiling engines generating beautifully formatted reports.",
        body_style
    ))

    pdf_features = (
        "• <b>Executive PDF Report Generator:</b> Compiles multi-page corporate reports summarizing business metrics, "
        "KPIs, monthly sales trend charts (generated on-the-fly using Matplotlib), RFM loyalty matrices, SVD personas, "
        "re-engagement campaigns, and restocking schedules. Styled with a professional deep-blue banner.<br/>"
        "• <b>Mathematical &amp; AI Foundations Handbook:</b> A pedagogical guide outlining the vector equations, "
        "L2-normalization formulas, SVD matrix equations, and Apriori lift formulations used in the system, complete "
        "with code snippets and multi-pass page numbering ('Page X of Y')."
    )
    story.append(create_callout(pdf_features, callout_body_style, "Strategic Reporting Subsystem", "#FAF5FF", "#8B5CF6"))
    story.append(Spacer(1, 10))

    story.append(Paragraph("9. Core Codebase Directory Structure", h1_style))
    story.append(Paragraph(
        "The following table maps the primary files in the workspace and their structural role in the platform:",
        body_style
    ))

    # Codebase mapping table
    # Columns: File Name (120pt), Role in Platform (384pt)
    table_data = [
        [
            Paragraph("<b>File Name</b>", table_header_style), 
            Paragraph("<b>Implementation Role &amp; Technical Capabilities</b>", table_header_style)
        ],
        [
            Paragraph("app.py", table_cell_code_style), 
            Paragraph("Main application entry. Configures Flask-Login, Flask-Mail, database connections, and routes all JSON APIs for dashboard visual metrics, csv uploads, campaign triggers, settings, and PDF downloads.", table_cell_style)
        ],
        [
            Paragraph("analysis.py", table_cell_code_style), 
            Paragraph("Analytics core. Formulates SQL-like aggregations on MongoDB data, computes L2 unit norms, pairwise Cosine Similarity, Singular Value Decomposition (SVD) customer personas, Apriori association rules, RFM loyalty scores, churn risks, restock triggers, and sales growth advisory.", table_cell_style)
        ],
        [
            Paragraph("data_import.py", table_cell_code_style), 
            Paragraph("Handles multi-file CSV ingestion, header normalization, custom column mapping, data cleaning, and row-level parsing validation. Tracks ingestion errors to MongoDB and logs progress for Celery tasks.", table_cell_style)
        ],
        [
            Paragraph("celery_worker.py", table_cell_code_style), 
            Paragraph("Configures the Celery background worker, binding tasks to Redis queue, launching data_import bulk insertion routines asynchronously to isolate heavy IO operations from web workers.", table_cell_style)
        ],
        [
            Paragraph("database.py", table_cell_code_style), 
            Paragraph("Sets up connection pools to the MongoDB database server, testing connectivity and providing helper wrappers to fetch cursors directly into Pandas DataFrames.", table_cell_style)
        ],
        [
            Paragraph("report_generator.py", table_cell_code_style), 
            Paragraph("Executes corporate executive PDF creation using FPDF, formatting KPI panels, drawing monthly sales trends (via Matplotlib), and drawing tabular summaries of CRM segments.", table_cell_style)
        ],
        [
            Paragraph("generate_math_pedagogy_pdf.py", table_cell_code_style), 
            Paragraph("Compiles the mathematical foundations guide using ReportLab, detailing vector representations, dot products, SVD equations, and Apriori lift stats, complete with custom styles and dynamic canvas pagination.", table_cell_style)
        ]
    ]

    t = Table(table_data, colWidths=[150, 354])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F8FAFC")]),
    ]))
    story.append(t)

    # Build the document
    doc.build(story, canvasmaker=NumberedCanvas)
    return output_path

if __name__ == '__main__':
    generate_features_pdf("datasense_ai_implemented_features.pdf")
    print("Success: Generated datasense_ai_implemented_features.pdf")
