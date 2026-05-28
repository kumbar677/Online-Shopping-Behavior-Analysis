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
        primary_color = colors.HexColor("#000000")   # Sleek Black
        text_muted = colors.HexColor("#64748B")      # Muted Slate Gray
        border_color = colors.HexColor("#E2E8F0")    # Soft border gray
        
        # --- HEADER ---
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(primary_color)
        self.drawString(54, 750, "RideX  |  System Implementation & Tech Specification")
        
        # Thin divider line below header
        self.setStrokeColor(border_color)
        self.setLineWidth(0.75)
        self.line(54, 742, 558, 742)
        
        # --- FOOTER ---
        # Thin divider line above footer
        self.line(54, 52, 558, 52)
        
        self.setFont("Helvetica", 8)
        self.setFillColor(text_muted)
        self.drawString(54, 38, "RideX Capstone  |  Full-Stack Ride Booking Application")
        
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.setFont("Helvetica-Bold", 8)
        self.drawRightString(558, 38, page_text)
        
        self.restoreState()

def create_callout(text, style, title="Feature Summary", bg_hex="#F8FAFC", border_hex="#0F172A"):
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

def generate_ridex_pdf(output_path=r"c:\Users\VERSH\OneDrive\Desktop\fullstack_proj\CAPSTONE\ridex_implemented_features.pdf"):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=72,
        bottomMargin=72
    )

    styles = getSampleStyleSheet()
    
    # Custom Palette - Sleek tech colors (inspired by modern ride-sharing apps: black, slate gray, green)
    c_primary = colors.HexColor("#0F172A")    # Midnight Dark Slate/Black
    c_secondary = colors.HexColor("#10B981")  # Active Green Accent
    c_charcoal = colors.HexColor("#1E293B")   # Readability Charcoal
    c_slate = colors.HexColor("#475569")      # Paths/Code slate grey
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
    story.append(Paragraph("RIDEX FULL-STACK CAPSTONE", subtitle_style))
    story.append(Spacer(1, 10))
    story.append(Paragraph("Implemented Features &amp;<br/>System Architecture Overview", title_style))
    story.append(Spacer(1, 5))
    
    # Decorative colored horizontal bar
    dec_bar = Table([[""]], colWidths=[200], rowHeights=[4])
    dec_bar.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), c_primary),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(dec_bar)
    story.append(Spacer(1, 30))
    
    story.append(Paragraph(
        "A comprehensive directory detailing all active modules, database models, backend controllers, "
        "socket-based real-time event flows, payment receipts, interactive maps, and frontend views currently "
        "deployed in the RideX ride-booking application.",
        ParagraphStyle('CoverDesc', parent=body_style, alignment=1, fontSize=10.5, leading=15, textColor=colors.HexColor("#475569"))
    ))
    
    story.append(Spacer(1, 150))
    
    # Metadata footer
    story.append(Paragraph("<b>Backend Architecture:</b> Node.js + Express (CommonJS)", meta_style))
    story.append(Paragraph("<b>Frontend Framework:</b> React + Vite + Redux Toolkit", meta_style))
    story.append(Paragraph("<b>Real-time Comm:</b> Socket.io Event Pipelines", meta_style))
    story.append(Paragraph("<b>Database Layer:</b> MongoDB (Mongoose schemas)", meta_style))
    story.append(Paragraph(f"<b>Documentation Compiled:</b> {datetime.now().strftime('%B %d, %Y')}", meta_style))
    story.append(PageBreak())

    # ==========================================
    #             PAGE 2: EXECUTIVE SUMMARY & TECH STACK
    # ==========================================
    story.append(Paragraph("1. Project Overview &amp; Architecture", h1_style))
    story.append(Paragraph(
        "<b>RideX</b> is a high-performance, full-stack ride-booking application designed to provide riders and drivers "
        "with a seamless real-time transportation experience. Similar to market-leading ride-sharing platforms, RideX "
        "facilitates registration, instant ride matchmaking, dynamic interactive maps with active driver simulations, "
        "secured transactions, automated receipts, and a dedicated admin interface to oversee driver approvals.",
        body_style
    ))
    
    # Tech Stack Callout
    tech_stack_desc = (
        "• <b>Backend Environment:</b> Node.js with Express framework, managing RESTful endpoints, token authentication, and background logic.<br/>"
        "• <b>Database Storage:</b> MongoDB (via Mongoose), utilizing geo-spatial indexing (2dsphere) for driver locating.<br/>"
        "• <b>Real-time Communication:</b> Socket.io integration establishing active TCP rooms for riders and drivers.<br/>"
        "• <b>State Management:</b> Redux Toolkit slices synchronizing auth contexts and booking states across the client.<br/>"
        "• <b>Frontend Build:</b> React (Vite) structured with clean modular layout folders and Tailwind styling.<br/>"
        "• <b>Email System:</b> Nodemailer SMTP transporter auto-dispatching ride payment invoices."
    )
    story.append(create_callout(tech_stack_desc, callout_body_style, "Operational Technology Stack", "#F0FDF4", "#10B981"))
    story.append(Spacer(1, 10))

    story.append(Paragraph("System Architecture Flow", h2_style))
    story.append(Paragraph(
        "Riders open dashboards to select destinations, drawing black solid routes on a custom Leaflet map. Drivers "
        "set their statuses online, receiving instant dispatch broadcasts. When a driver accepts a trip, a direct "
        "Socket channel coordinates coordinates, simulating a 7.5 seconds smooth arrival animation of the driver car "
        "to the rider's pin. Upon completion, a mock checkout processes payment and registers transaction histories.",
        body_style
    ))
    
    flow_diagram = (
        "<b>[Rider Client]</b> ← <i>(Socket.io / HTTP)</i> → <b>[Node.js Express Server]</b> ← <i>(Socket.io)</i> → <b>[Driver Client]</b><br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;↓&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;↓<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<b>[Mongoose Models]</b>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<b>[Nodemailer Transporter]</b><br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;↓&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;↓<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<b>[MongoDB Server]</b>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<b>[Rider Email Inboxes]</b>"
    )
    story.append(create_callout(flow_diagram, callout_body_style, "RideX End-to-End Event Architecture", "#F8FAFC", "#0F172A"))
    story.append(PageBreak())

    # ==========================================
    #             PAGE 3: DATABASE MODELS & REST APIs
    # ==========================================
    story.append(Paragraph("2. Mongoose Schemas &amp; Seeding", h1_style))
    story.append(Paragraph(
        "RideX leverages four primary database models to enforce type safety and structure relationships in MongoDB:",
        body_style
    ))
    
    models_desc = (
        "1. <b>User Schema (User.js):</b> Stores riders and admins. Includes fields: <code>name</code>, <code>email</code>, "
        "<code>password</code> (hashed with salt=10), <code>phone</code>, <code>role</code> (enum: ['rider', 'admin'], default: 'rider'), "
        "and <code>profileImage</code>.<br/><br/>"
        "2. <b>Driver Schema (Driver.js):</b> Tracks driver profiles. Includes: <code>driverName</code>, <code>email</code>, "
        "<code>password</code>, <code>phone</code>, <code>vehicleDetails</code> (make, model, year, licensePlate, color), "
        "<code>availabilityStatus</code> ('online' / 'offline'), <code>isApproved</code> (boolean, default false), "
        "and <code>currentLocation</code> (indexed as a <code>2dsphere</code> spatial coordinate [long, lat]).<br/><br/>"
        "3. <b>Ride Schema (Ride.js):</b> Coordinates booking data. Stores: <code>riderId</code> (ref: User), <code>driverId</code> "
        "(ref: Driver), <code>pickupLocation</code> &amp; <code>dropLocation</code> (address strings + [long, lat] coordinates), "
        "<code>distance</code> (in km), <code>fare</code>, <code>status</code> (enum: ['pending', 'accepted', 'arriving', 'started', "
        "'completed', 'cancelled']), and <code>paymentStatus</code> ('pending', 'completed', 'failed').<br/><br/>"
        "4. <b>Payment Schema (Payment.js):</b> Captures financial logs: <code>rideId</code>, <code>userId</code>, <code>amount</code>, "
        "<code>currency</code>, <code>status</code> ('pending', 'completed', 'failed', 'refunded'), <code>transactionId</code>, "
        "and <code>paymentMethod</code> (enum: ['card', 'cash', 'wallet'])."
    )
    story.append(create_callout(models_desc, callout_body_style, "MongoDB Schema Structures", "#FAF5FF", "#8B5CF6"))
    story.append(Spacer(1, 10))

    story.append(Paragraph("Database Seeding Subsystem", h2_style))
    story.append(Paragraph(
        "To facilitate rapid developer onboarding and demonstrations, the database connector automatically checks and "
        "seeds a default Admin User (<code>admin@ridex.com</code> / <code>password123</code>) and three premium mock drivers "
        "(Alexander Sterling driving a Tesla Model S Plaid, Seraphina Vance in a Mercedes-Benz EQS SUV, and Viktor Thorne "
        "in a Lucid Air Sapphire) if those collections are empty upon server boot.",
        body_style
    ))
    story.append(PageBreak())

    # ==========================================
    #             PAGE 4: SOCKETS & TRANSACTION PIPELINES
    # ==========================================
    story.append(Paragraph("3. Socket.io Event Pipelines &amp; Dispatching", h1_style))
    story.append(Paragraph(
        "Real-time event coordination bypasses classic REST constraints using dedicated Socket.io room handlers, "
        "acting as the system's matching coordinate brain:",
        body_style
    ))

    socket_desc = (
        "• <b>Connection Room Management:</b> On connecting, riders join their specific private room (<code>join-rider</code> → riderId). "
        "Drivers join both a private room (driverId) and a global broadcast channel (<code>join-driver</code> → 'drivers' room).<br/>"
        "• <b>Ride Dispatch Event (<code>request-ride</code>):</b> When a rider requests a cab, the system generates a unique ID, "
        "stores the status as 'searching' in an active Map, and broadcasts the ride details to all drivers in the 'drivers' room.<br/>"
        "• <b>Ride Acceptance Event (<code>accept-ride</code>):</b> A driver accepts a ride. Server matches driver credentials, "
        "notifies the specific rider room (emitting <code>ride-accepted</code> with vehicle specs), and withdraws the request from "
        "all other driver feeds (emitting <code>ride-withdrawn</code>).<br/>"
        "• <b>Trip Complete Event (<code>complete-ride</code>):</b> Triggers arrival and journey conclusions, freeing both user "
        "states and removing the ride from active server memory."
    )
    story.append(create_callout(socket_desc, callout_body_style, "Socket.io Core Events", "#F8FAFC", "#0F172A"))
    story.append(Spacer(1, 10))

    story.append(Paragraph("4. Checkout, Payments &amp; Receipts Transporter", h1_style))
    story.append(Paragraph(
        "RideX processes transactions via a secure controller that logs transactions to MongoDB and connects "
        "directly to an email transporter.",
        body_style
    ))

    payment_desc = (
        "• <b>Payment Ingestion (<code>POST /api/payments/process</code>):</b> Creates a completed payment record, generating "
        "a transaction ID (<code>mock_txn_&lt;timestamp&gt;</code>) and updating the ride payment status to 'completed'.<br/>"
        "• <b>Nodemailer Invoice Dispatcher:</b> Integrates with Nodemailer to email HTML payment receipts to riders, "
        "including details like payment amount, ride ID, and transaction hashes."
    )
    story.append(create_callout(payment_desc, callout_body_style, "Payment &amp; Mailing Flows", "#FFFBEB", "#D97706"))
    story.append(PageBreak())

    # ==========================================
    #             PAGE 5: INTERACTIVE MAP & FRONTEND PAGES
    # ==========================================
    story.append(Paragraph("5. Interactive Maps &amp; Animations", h1_style))
    story.append(Paragraph(
        "The frontend uses Leaflet mapping APIs in React to render mapping dashboards with dynamic visual animations:",
        body_style
    ))

    map_desc = (
        "• <b>Visual Street Maps:</b> Renders Voyager style street tile layers in <code>MapComponent.jsx</code>.<br/>"
        "• <b>Pulsing Driver Car Icons:</b> Generates custom pulsing HTML divIcons representing active cars nearby. "
        "Animate positions every 2.5 seconds to simulate city driving activity.<br/>"
        "• <b>Sleek Solid Black Routing Polyline:</b> Draws solid black polylines connecting green pickup pins and red dropoff pins, fitting bounds automatically.<br/>"
        "• <b>Smooth Arrival Drive Animation:</b> When a driver is matched, the car marker animates coordinates "
        "from its starting spot to the rider's pickup pin over 7.5 seconds using ease-out formulas."
    )
    story.append(create_callout(map_desc, callout_body_style, "Leaflet Graphics Capabilities", "#F0FDF4", "#10B981"))
    story.append(Spacer(1, 10))

    story.append(Paragraph("6. React Pages &amp; Redux State Management", h1_style))
    story.append(Paragraph(
        "The client-side interface contains six React pages styled with Tailwind CSS, utilizing Redux Toolkit slices "
        "for centralized state control:",
        body_style
    ))

    pages_desc = (
        "• <b>LandingPage.jsx:</b> Initial corporate splash page introducing RideX services.<br/>"
        "• <b>Login.jsx &amp; Register.jsx:</b> Interactive forms connecting to auth endpoints, with tabs separating riders and drivers.<br/>"
        "• <b>RiderDashboard.jsx:</b> Main rider portal. Features search panels for destination inputs, fare estimators, "
        "interactive Leaflet route lines, and checkout panels.<br/>"
        "• <b>DriverDashboard.jsx:</b> Portal for drivers. Features status toggles (online/offline) and incoming ride request banners.<br/>"
        "• <b>AdminDashboard.jsx:</b> Visual overview displaying KPI cards (Riders Count, Drivers Count, Total Rides, Gross Revenue) "
        "and tables for driver verification and approvals.<br/>"
        "• <b>Redux Slices:</b> Centralizes state management through <code>authSlice.js</code> (storing token validation and identity) "
        "and <code>rideSlice.js</code> (handling active booking events, match lists, and histories)."
    )
    story.append(create_callout(pages_desc, callout_body_style, "Client-Side Slices &amp; Pages", "#FAF5FF", "#8B5CF6"))
    story.append(PageBreak())

    # ==========================================
    #             PAGE 6: CODEBASE MAPPING & APIS
    # ==========================================
    story.append(Paragraph("7. RESTful API Endpoint Reference", h1_style))
    story.append(Paragraph(
        "Below is a list of backend REST endpoints routing JSON payloads inside RideX:",
        body_style
    ))

    # REST APIs Table
    # Columns: Endpoint (140pt), Method (50pt), Description (314pt)
    api_headers = [
        [
            Paragraph("<b>Endpoint URI</b>", table_header_style), 
            Paragraph("<b>Method</b>", table_header_style), 
            Paragraph("<b>API Endpoint Description</b>", table_header_style)
        ],
        [Paragraph("/api/auth/register/user", table_cell_code_style), Paragraph("POST", table_cell_style), Paragraph("Registers a new rider user, hashing passwords via bcrypt.", table_cell_style)],
        [Paragraph("/api/auth/register/driver", table_cell_code_style), Paragraph("POST", table_cell_style), Paragraph("Registers a new driver with vehicle specifications.", table_cell_style)],
        [Paragraph("/api/auth/login", table_cell_code_style), Paragraph("POST", table_cell_style), Paragraph("Authenticates credentials for both users and drivers, generating JWTs.", table_cell_style)],
        [Paragraph("/api/rides/book", table_cell_code_style), Paragraph("POST", table_cell_style), Paragraph("Saves a pending ride request with pickup, destination, distance, and fare.", table_cell_style)],
        [Paragraph("/api/rides/:id/accept", table_cell_code_style), Paragraph("PUT", table_cell_style), Paragraph("Enables a driver to accept a pending ride request.", table_cell_style)],
        [Paragraph("/api/rides/:id/status", table_cell_code_style), Paragraph("PUT", table_cell_style), Paragraph("Updates trip progress status ('arriving', 'started', 'completed').", table_cell_style)],
        [Paragraph("/api/rides/history", table_cell_code_style), Paragraph("GET", table_cell_style), Paragraph("Returns the booking history log filtered by user role.", table_cell_style)],
        [Paragraph("/api/payments/process", table_cell_code_style), Paragraph("POST", table_cell_style), Paragraph("Logs mock payment completion, updates ride status, and emails receipt.", table_cell_style)],
        [Paragraph("/api/admin/stats", table_cell_code_style), Paragraph("GET", table_cell_style), Paragraph("Calculates riders, drivers, total rides, and gross revenue sum.", table_cell_style)],
        [Paragraph("/api/admin/drivers/:id/approve", table_cell_code_style), Paragraph("PUT", table_cell_style), Paragraph("Approves driver registrations, enabling them to receive dispatch feeds.", table_cell_style)]
    ]

    t_api = Table(api_headers, colWidths=[140, 50, 314])
    t_api.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F8FAFC")]),
    ]))
    story.append(t_api)
    story.append(Spacer(1, 10))

    story.append(Paragraph("8. Core Codebase Directory Structure", h1_style))
    story.append(Paragraph(
        "Below is the file layout of the backend server and frontend src modules:",
        body_style
    ))

    # Directory layout table
    # Columns: Folder / File (140pt), Purpose (364pt)
    dir_headers = [
        [
            Paragraph("<b>File / Folder Path</b>", table_header_style), 
            Paragraph("<b>Implementation Details &amp; Purpose</b>", table_header_style)
        ],
        [Paragraph("backend/server.js", table_cell_code_style), Paragraph("Main server configuration. Boots Express middleware, initializes Socket.io handlers, connects to MongoDB, and registers routes.", table_cell_style)],
        [Paragraph("backend/sockets/socket.js", table_cell_code_style), Paragraph("Socket event pipelines managing ride dispatches, driver accepts, and passenger arrival anim triggers.", table_cell_style)],
        [Paragraph("backend/models/", table_cell_code_style), Paragraph("Contains Mongoose schemas: User, Driver, Ride, and Payment.", table_cell_style)],
        [Paragraph("backend/controllers/", table_cell_code_style), Paragraph("Controller functions mapping REST APIs: Admin, Auth, Payment, and Ride controllers.", table_cell_style)],
        [Paragraph("frontend/src/pages/", table_cell_code_style), Paragraph("React pages: RiderDashboard, DriverDashboard, AdminDashboard, Login, Register, and LandingPage.", table_cell_style)],
        [Paragraph("frontend/src/redux/", table_cell_code_style), Paragraph("Redux store and slices (authSlice, rideSlice) for front-end state management.", table_cell_style)],
        [Paragraph("frontend/src/components/", table_cell_code_style), Paragraph("Reusable components including MapComponent (Leaflet) and Form controls.", table_cell_style)]
    ]

    t_dir = Table(dir_headers, colWidths=[160, 344])
    t_dir.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F8FAFC")]),
    ]))
    story.append(t_dir)

    # Build the document
    doc.build(story, canvasmaker=NumberedCanvas)
    return output_path

if __name__ == '__main__':
    generate_ridex_pdf()
    print("Success: Generated RideX implemented features PDF.")
