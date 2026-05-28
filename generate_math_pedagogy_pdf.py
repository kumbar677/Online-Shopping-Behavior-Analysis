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
        primary_color = colors.HexColor("#1E3A8A")   # Deep Corporate Blue
        text_muted = colors.HexColor("#64748B")      # Muted Slate Gray
        border_color = colors.HexColor("#E2E8F0")    # Soft border gray
        
        # --- HEADER ---
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(primary_color)
        self.drawString(54, 750, "DataSense.AI  |  Mathematical & AI Foundations Handbook")
        
        # Thin divider line below header
        self.setStrokeColor(border_color)
        self.setLineWidth(0.75)
        self.line(54, 742, 558, 742)
        
        # --- FOOTER ---
        # Thin divider line above footer
        self.line(54, 52, 558, 52)
        
        self.setFont("Helvetica", 8)
        self.setFillColor(text_muted)
        self.drawString(54, 38, "Confidential - Prepared exclusively for DataSense.AI Workspace")
        
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.setFont("Helvetica-Bold", 8)
        self.drawRightString(558, 38, page_text)
        
        self.restoreState()

def create_callout(text, style, title="Mathematical Formulation", bg_hex="#F8FAFC", border_hex="#3B82F6"):
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

def generate_math_pedagogy_pdf(output_path=None, company_name="DataSense.AI"):
    """
    Compiles a comprehensive, beautiful pedagogical guide to the mathematics
    powering the DataSense.AI behavior analytics suite.
    """
    import io
    if output_path is None:
        buf = io.BytesIO()
        doc_path = buf
    else:
        doc_path = output_path

    # 54 points = 0.75 inch margins
    # topMargin = 72 (1 inch) and bottomMargin = 72 (1 inch) to avoid overlap with header/footer
    doc = SimpleDocTemplate(
        doc_path,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=72,
        bottomMargin=72
    )

    styles = getSampleStyleSheet()
    
    # Custom Palette Definitions
    c_primary = colors.HexColor("#1E3A8A")    # Dark Deep Blue
    c_secondary = colors.HexColor("#7C3AED")  # Accent Royal Purple
    c_charcoal = colors.HexColor("#1E293B")   # Off-black charcoal for readability
    c_emerald = colors.HexColor("#059669")    # Deep emerald green
    c_slate = colors.HexColor("#475569")      # Dark slate grey for code
    
    # Custom Paragraph Styles
    title_style = ParagraphStyle(
        'CoverTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=28,
        leading=34,
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
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#64748B"),
        alignment=1, # Center
        spaceAfter=5
    )
    
    h1_style = ParagraphStyle(
        'MainHeading',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=c_primary,
        spaceBefore=18,
        spaceAfter=10,
        keepWithNext=True
    )
    
    h2_style = ParagraphStyle(
        'SubHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=15,
        textColor=c_secondary,
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True
    )
    
    body_style = ParagraphStyle(
        'BodyTextCustom',
        parent=styles['BodyText'],
        fontName='Helvetica',
        fontSize=10,
        leading=14.5,
        textColor=c_charcoal,
        spaceAfter=10
    )
    
    callout_body_style = ParagraphStyle(
        'CalloutText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=c_charcoal
    )
    
    code_style = ParagraphStyle(
        'CodeCellText',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=8.5,
        leading=11.5,
        textColor=c_slate
    )

    story = []

    # ==========================================
    #             PAGE 1: COVER PAGE
    # ==========================================
    story.append(Spacer(1, 100))
    story.append(Paragraph(f"MATHEMATICAL &amp; AI FOUNDATIONS", subtitle_style))
    story.append(Spacer(1, 10))
    story.append(Paragraph("DataSense.AI Behavior Analytics", title_style))
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
    
    story.append(Paragraph("A Technical Handbook on Linear Algebra, Vector Spaces, Matrix Multiplications, Singular Value Decomposition (SVD), Association Pattern Mining, and Customer Lifecycle Statistics.", ParagraphStyle('CoverDesc', parent=body_style, alignment=1, fontSize=11, leading=16, textColor=colors.HexColor("#475569"))))
    
    story.append(Spacer(1, 160))
    
    # Metadata footer
    story.append(Paragraph(f"<b>Platform Instance:</b> {company_name} Workspace", meta_style))
    story.append(Paragraph("<b>Version:</b> 4.2 (Secure Release)", meta_style))
    story.append(Paragraph(f"<b>Generated:</b> {datetime.now().strftime('%B %Y')}", meta_style))
    story.append(Paragraph("<b>Authoring Team:</b> DataSense.AI Core AI &amp; Research Group", meta_style))
    story.append(PageBreak())

    # ==========================================
    #             PAGE 2: INTRODUCTION & VECTORS
    # ==========================================
    story.append(Paragraph("Introduction to DataSense.AI Engine", h1_style))
    story.append(Paragraph(
        "Modern consumer applications generate vast streams of transaction logs. While basic business dashboards "
        "merely aggregate sum totals and average transaction counts, <b>DataSense.AI</b> transforms raw data tables into a "
        "coherent, multi-dimensional geometric representation. By modeling customer purchasing decisions as vectors "
        "lying in high-dimensional vector spaces, the system uncovers latent associations, maps granular customer matches, "
        "and projects future lifecycle trajectories using rigorous, proven algebraic frameworks.",
        body_style
    ))
    
    story.append(Paragraph("1. The Vector Space &amp; Matrix representation", h1_style))
    story.append(Paragraph(
        "Let the catalog of unique products belonging to a business be denoted as a set "
        "<i>P = {p<sub>1</sub>, p<sub>2</sub>, ..., p<sub>N</sub>}</i>, representing <i>N</i> orthogonal dimensions. "
        "Each customer <i>c</i> in the customer base <i>C</i> is mapped as a vector <b>v</b><sub>c</sub> residing "
        "in the real vector space <b>R</b><sup>N</sup>, where each dimension represents the purchasing volume of that specific product.",
        body_style
    ))
    
    v_def = (
        "<b>v</b><sub>c</sub> = [ q<sub>c, 1</sub>, &nbsp; q<sub>c, 2</sub>, &nbsp; ..., &nbsp; q<sub>c, N</sub> ] &nbsp; &isin; &nbsp; <b>R</b><sup>N</sup>"
        "<br/><br/>"
        "Where:<br/>"
        "&bull; <i>q<sub>c, j</sub> &ge; 0</i> represents the total quantity of product <i>p<sub>j</sub></i> purchased by customer <i>c</i>."
    )
    story.append(create_callout(v_def, callout_body_style, "Vector Space Mapping", "#F8FAFC", "#3B82F6"))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph(
        "By stacking the row vectors of all <i>M</i> customers, we construct the fundamental <b>User-Item Interaction Matrix</b> "
        "<i>A &isin; <b>R</b><sup>M &times; N</sup></i>. In typical retail contexts, <i>A</i> is highly <b>sparse</b> (often "
        "&gt;99% of entries are zero) because a single customer only purchases a tiny subset of the global catalog. "
        "Handling this sparsity is the primary challenge addressed by the matrix normalization and dimensionality reduction "
        "pipelines in <code>analysis.py</code>.",
        body_style
    ))
    
    matrix_def = (
        "<i>A = [ <b>v</b><sub>1</sub><sup>T</sup>, &nbsp; <b>v</b><sub>2</sub><sup>T</sup>, &nbsp; ..., &nbsp; <b>v</b><sub>M</sub><sup>T</sup> ]<sup>T</sup> &nbsp; &isin; &nbsp; <b>R</b><sup>M &times; N</sup></i>"
        "<br/><br/>"
        "Where each cell index <i>A<sub>i, j</sub></i> corresponds to the amount of product <i>j</i> purchased by customer <i>i</i>."
    )
    story.append(create_callout(matrix_def, callout_body_style, "User-Item Interaction Matrix", "#F8FAFC", "#3B82F6"))
    story.append(PageBreak())

    # ==========================================
    #             PAGE 3: COSINE SIMILARITY
    # ==========================================
    story.append(Paragraph("2. Vector Similarity &amp; Metric Spaces", h1_style))
    story.append(Paragraph(
        "To determine how similar two customers are (for targeted cross-selling and look-alike marketing), we model them "
        "as vectors and calculate the cosine of the angle between them in the <i>N</i>-dimensional space. "
        "Unlike standard Euclidean distance (which is sensitive to absolute volume and would separate a heavy buyer "
        "from a light buyer even if they bought identical proportions of products), <b>Cosine Similarity</b> focuses purely "
        "on the directional orientation of vectors, making it scale-invariant.",
        body_style
    ))
    
    story.append(Paragraph(
        "Before similarity computation, the scale effect is neutralized by normalizing each customer vector to unit length (L2 Normalization). "
        "The Euclidean ($L_2$) norm of vector <b>u</b> is defined as:",
        body_style
    ))
    
    norm_def = (
        "||<b>u</b>||<sub>2</sub> = &radic;( &sum;<sub>j=1</sub><sup>N</sup> u<sub>j</sub><sup>2</sup> )"
        "<br/><br/>"
        "Each vector is then converted to its corresponding unit vector:<br/>"
        "<b>&ucirc;</b> = <b>u</b> / ||<b>u</b>||<sub>2</sub> &nbsp; such that &nbsp; ||<b>&ucirc;</b>||<sub>2</sub> = 1"
    )
    story.append(create_callout(norm_def, callout_body_style, "L2 Vector Norm &amp; Normalization", "#F0FDF4", "#10B981"))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph(
        "The cosine similarity metric between two normalized vectors <b>u</b> and <b>v</b> corresponds exactly to their algebraic dot product. "
        "This returns a value bounded in the interval <i>[0, 1]</i> (since quantities are strictly non-negative):",
        body_style
    ))
    
    sim_def = (
        "Similarity(<b>u</b>, &nbsp; <b>v</b>) = cos(&theta;) = (<b>u</b> &bull; <b>v</b>) / (||<b>u</b>||<sub>2</sub> ||<b>v</b>||<sub>2</sub>) "
        "= &sum;<sub>j=1</sub><sup>N</sup> u<sub>j</sub> v<sub>j</sub> / [ &radic;( &sum; u<sub>j</sub><sup>2</sup> ) &times; &radic;( &sum; v<sub>j</sub><sup>2</sup> ) ]"
    )
    story.append(create_callout(sim_def, callout_body_style, "Cosine Similarity Definition", "#F0FDF4", "#10B981"))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph(
        "<b>Code Mapping:</b> In `analysis.py` (lines 264-277), this vector algebra is calculated highly efficiently "
        "using optimized NumPy matrix broadcasts, bypassing nested loops entirely:",
        body_style
    ))
    
    code_block = (
        "matrix = user_item_matrix.values<br/>"
        "norms = np.linalg.norm(matrix, axis=1, keepdims=True)<br/>"
        "norms[norms == 0] = 1 # Avoid division-by-zero singularities<br/>"
        "normalized_matrix = matrix / norms<br/>"
        "similarity_matrix = np.dot(normalized_matrix, normalized_matrix.T)"
    )
    
    ct = Table([[Paragraph(code_block, code_style)]], colWidths=[504])
    ct.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F1F5F9")),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('LEFTPADDING', (0,0), (-1,-1), 12),
        ('RIGHTPADDING', (0,0), (-1,-1), 12),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(ct)
    story.append(PageBreak())

    # ==========================================
    #             PAGE 4: SVD (PERSONAS)
    # ==========================================
    story.append(Paragraph("3. Latent Dimensions &amp; Singular Value Decomposition (SVD)", h1_style))
    story.append(Paragraph(
        "While direct similarity operates on the raw product space, it suffers from the <i>Curse of Dimensionality</i> "
        "and cannot capture structural relationships (e.g., a customer buying 'Shockproof Phone Case' and a customer buying "
        "'Tempered Glass Protector' might have 0% direct similarity, yet they both belong to the latent concept of 'Phone Accessory Buyers'). "
        "To capture this hidden layer, <b>DataSense.AI</b> uses <b>Singular Value Decomposition (SVD)</b>.",
        body_style
    ))
    
    story.append(Paragraph(
        "Before performing SVD, the raw interaction matrix <i>A</i> is centered by subtracting the mean purchasing "
        "quantity for each product columns-wise, creating the centered matrix <i>A<sub>centered</sub></i>. This centers the coordinates "
        "about the global purchasing centroid:",
        body_style
    ))
    
    svd_center = (
        "<i>A<sub>centered</sub> = A - <b>&mu;</b></i> &nbsp; where &nbsp; <i>&mu;<sub>j</sub></i> is the mean quantity of product <i>j</i>."
    )
    story.append(create_callout(svd_center, callout_body_style, "Matrix Mean Centering", "#FAF5FF", "#8B5CF6"))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph(
        "The SVD factorizes this centered matrix into three distinct mathematical linear transformation components:",
        body_style
    ))
    
    svd_eq = (
        "<i>A<sub>centered</sub> = U &Sigma; V<sup>T</sup></i>"
        "<br/><br/>"
        "Where:<br/>"
        "&bull; <b>U</b> &isin; <b>R</b><sup>M &times; k</sup> is a column-orthonormal matrix (<i>U<sup>T</sup>U = I</i>). "
        "It maps users to the latent 'concept' space (User-Concept Coordinate Matrix).<br/>"
        "&bull; <b>&Sigma;</b> &isin; <b>R</b><sup>k &times; k</sup> is a diagonal matrix containing sorted positive singular values "
        "(<i>s<sub>1</sub> &ge; s<sub>2</sub> &ge; ... &ge; s<sub>k</sub></i>). These represent the mathematical strength/importance "
        "of each latent persona.<br/>"
        "&bull; <b>V<sup>T</sup></b> &isin; <b>R</b><sup>k &times; N</sup> is a row-orthonormal matrix (<i>V<sup>T</sup>V = I</i>). "
        "Its rows represent the coordinates of the product categories in the latent concept space (Product-Concept Component Loading Matrix)."
    )
    story.append(create_callout(svd_eq, callout_body_style, "Singular Value Decomposition Formulation", "#FAF5FF", "#8B5CF6"))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph(
        "<b>Latent Persona Extraction:</b> In our SVD module (`analysis.py` lines 438-495), the system extracts the first "
        "three singular components (Personas). The strength of each persona <i>i</i> is computed as the percentage of captured variance:<br/>"
        "<i>Strength % = (s<sub>i</sub> / &sum; s<sub>j</sub>) &times; 100</i>. "
        "The associated signature products are retrieved by inspecting the loading vector <i>V<sup>T</sup>[i, :]</i> "
        "and identifying the dimensions (products) with the highest absolute positive projection values.",
        body_style
    ))
    story.append(PageBreak())

    # ==========================================
    #             PAGE 5: ASSOCIATION RULES
    # ==========================================
    story.append(Paragraph("4. Market Basket Analysis (Frequent Pattern Mining)", h1_style))
    story.append(Paragraph(
        "Linear algebra reveals continuous similarities and latent concepts, but to discover crisp, actionable rules "
        "governing purchase order structures (e.g., 'If a customer adds organic athletic socks to their cart, "
        "they are highly likely to purchase comfortable running shoes'), the system deploys <b>Association Rule Mining</b> "
        "under the probability-based <b>Apriori Paradigm</b>.",
        body_style
    ))
    
    story.append(Paragraph(
        "An association rule is represented as an implication of the form <i>X &rArr; Y</i>, where <i>X</i> is the "
        "<b>antecedent</b> itemset and <i>Y</i> is the <b>consequent</b> itemset. Three foundational statistical metrics "
        "determine the strength, validity, and independence of each rule:",
        body_style
    ))
    
    rules_defs = (
        "<b>1. Support:</b> The absolute probability that a transaction contains both itemsets.<br/>"
        "&nbsp; &nbsp; &nbsp; <i>Support(X &rArr; Y) = P(X &cup; Y) = Count(X &cup; Y) / Total Transactions</i><br/><br/>"
        "<b>2. Confidence:</b> The conditional probability that a customer purchases <i>Y</i> given that they bought <i>X</i>.<br/>"
        "&nbsp; &nbsp; &nbsp; <i>Confidence(X &rArr; Y) = P(Y | X) = Support(X &cup; Y) / Support(X)</i><br/><br/>"
        "<b>3. Lift:</b> The ratio of the observed joint probability to the expected probability if <i>X</i> and <i>Y</i> were completely independent. "
        "This measures rule strength.<br/>"
        "&nbsp; &nbsp; &nbsp; <i>Lift(X &rArr; Y) = P(X &cup; Y) / [ P(X) &times; P(Y) ] = Confidence(X &rArr; Y) / Support(Y)</i>"
    )
    story.append(create_callout(rules_defs, callout_body_style, "Association Rule Statistics", "#FFFBEB", "#D97706"))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph(
        "<b>Interpretation of Lift:</b><br/>"
        "&bull; <b>Lift &gt; 1:</b> <i>Positive correlation.</i> The purchase of the antecedent highly boosts the likelihood of purchasing the consequent. "
        "This is an ideal candidate for product bundle recommendations.<br/>"
        "&bull; <b>Lift = 1:</b> <i>Independence.</i> The two products are co-purchased purely by random chance; there is no structural behavior correlation.<br/>"
        "&bull; <b>Lift &lt; 1:</b> <i>Negative correlation.</i> The items act as substitutes or are mutually exclusive; buying one reduces the likelihood of buying the other.",
        body_style
    ))
    
    story.append(Paragraph(
        "<b>Computational Implementation:</b> In `analysis.py` (lines 279-381), the algorithm groups the transactional database "
        "into binary basket columns, passes them to the Apriori pattern algorithm to filter out sparse items using a "
        "minimum support threshold, and finally filters the valid rules using a minimum confidence threshold. "
        "A robust custom fallback generator simulates co-purchasing probability vectors if data size is sparse, "
        "ensuring the system is stable under cold-start database uploads.",
        body_style
    ))
    story.append(PageBreak())

    # ==========================================
    #             PAGE 6: RFM & CHURN
    # ==========================================
    story.append(Paragraph("5. Customer Loyalty Segmentation (RFM quartiles)", h1_style))
    story.append(Paragraph(
        "While predictive matching analyzes product-level interactions, high-level business planning requires dividing "
        "the customer base into structural tiers based on purchase volume and frequency. To accomplish this, DataSense.AI "
        "deploys an <b>RFM Model</b>, representing each customer as a three-dimensional behavioral coordinate:",
        body_style
    ))
    
    rfm_defs = (
        "&bull; <b>Recency (R):</b> The time elapsed since the customer's last order. "
        "<i>R<sub>c</sub> = t<sub>max</sub> - t<sub>c, last</sub></i> (measured in days). Lower values indicate highly active engagement.<br/>"
        "&bull; <b>Frequency (F):</b> The count of orders. "
        "<i>F<sub>c</sub> = &sum; 1</i> over all transactions made by customer <i>c</i>.<br/>"
        "&bull; <b>Monetary (M):</b> The sum of revenue generated. "
        "<i>M<sub>c</sub> = &sum; Amount<sub>c, i</sub></i> across all orders made by customer <i>c</i>."
    )
    story.append(create_callout(rfm_defs, callout_body_style, "RFM Coordinate Elements", "#FAF5FF", "#7C3AED"))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph(
        "<b>Quantile Scoring:</b> To convert absolute metrics (days, counts, dollars) into standardized profiles, "
        "the distribution of each metric is partitioned into four equal intervals (quartiles). "
        "A customer is assigned a score from 1 to 4 for each category, forming a 3-digit vector (e.g. 444, 214). "
        "In `analysis.py` (lines 383-436), this partitioning is computed using pandas quantile binning: "
        "<code>pd.qcut()</code>. The highest score, <b>444</b>, represents a hyper-loyal VIP customer who bought "
        "recently, buys often, and spends heavily.",
        body_style
    ))
    
    story.append(Paragraph("6. Customer Churn &amp; Temporal Retention Models", h1_style))
    story.append(Paragraph(
        "To prevent customer churn before it occurs, the system monitors the temporal decay of engagement. "
        "For each customer <i>c</i>, a <i>Days Absent</i> metric is calculated: <i>&Delta;t = t<sub>today</sub> - t<sub>last</sub></i>. "
        "Customers with <i>&Delta;t &gt; 30</i> days are isolated, and a discrete piecewise lifecycle classification function is applied:",
        body_style
    ))
    
    churn_func = (
        "<b>Status(&Delta;t) &amp; Marketing Actions:</b><br/>"
        "&bull; <b>At Risk:</b> &nbsp; 30 days &lt; &Delta;t &le; 60 days &nbsp; &rArr; &nbsp; <i>Action: Send Reminder Email</i><br/>"
        "&bull; <b>Dormant:</b> &nbsp; 60 days &lt; &Delta;t &le; 90 days &nbsp; &rArr; &nbsp; <i>Action: Offer 20% Discount</i><br/>"
        "&bull; <b>Churned:</b> &nbsp; &Delta;t &gt; 90 days &nbsp; &rArr; &nbsp; &nbsp; &nbsp; <i>Action: Offer 40% Win-Back Discount</i>"
    )
    story.append(create_callout(churn_func, callout_body_style, "Engagement Lifecycle Function", "#FEF2F2", "#EF4444"))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph(
        "This dynamic decay model enables marketing managers to automate highly targeted win-back campaigns "
        "based on exact behavioral timelines. The full list of risk-exposed customers is sorted by their cumulative lifetime spent (Monetary value), "
        "allowing teams to prioritize win-back efforts on the most valuable customers first.",
        body_style
    ))

    # Build the document
    doc.build(story, canvasmaker=NumberedCanvas)
    if output_path is None:
        return buf.getvalue()
    else:
        return output_path

if __name__ == '__main__':
    generate_math_pedagogy_pdf("mathematical_foundations_guide.pdf")
    print("Success: Compiled mathematical_foundations_guide.pdf")
