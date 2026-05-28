import os
import uuid
from datetime import datetime
from fpdf import FPDF
import analysis
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

class ExecutivePDF(FPDF):
    def __init__(self, company_name="DataSense.AI", logo_url=None):
        super().__init__()
        self.company_name = company_name
        self.logo_url = logo_url

    def header(self):
        # Header banner
        if self.logo_url:
            local_path = self.logo_url.lstrip('/')
            if os.path.exists(local_path):
                try:
                    self.image(local_path, x=10, y=8, h=12)
                except:
                    pass
                    
        self.set_font('Arial', 'B', 16)
        self.set_text_color(30, 58, 138)  # Deep corporate blue
        self.cell(0, 10, f'{self.company_name} Executive Analytics Workspace', 0, 1, 'R')
        
        self.set_font('Arial', 'I', 9)
        self.set_text_color(100, 100, 100)
        self.cell(0, 4, f'Data Mining & Strategic Business Report | Generated: {datetime.now().strftime("%B %d, %Y")}', 0, 1, 'R')
        self.set_draw_color(226, 232, 240)
        self.set_line_width(0.5)
        self.line(10, 26, 200, 26)
        self.ln(8)
        
    def footer(self):
        self.set_y(-15)
        self.set_draw_color(226, 232, 240)
        self.set_line_width(0.5)
        self.line(10, self.get_y() - 2, 200, self.get_y() - 2)
        
        self.set_font('Arial', 'I', 8)
        self.set_text_color(148, 163, 184)
        self.cell(0, 10, f'Page {self.page_no()} | CONFIDENTIAL | DataSense.AI Intelligence Engine', 0, 0, 'C')
        
    def chapter_title(self, num, title, color=(30, 58, 138)):
        self.set_font('Arial', 'B', 12)
        self.set_fill_color(*color)
        self.set_text_color(255, 255, 255)
        self.cell(0, 8, f"  SECTION {num}: {title.upper()}", 0, 1, 'L', fill=True)
        self.ln(4)

def table_header(pdf, headers, widths):
    pdf.set_fill_color(30, 58, 138)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font('Arial', 'B', 9)
    for i, header in enumerate(headers):
        pdf.cell(widths[i], 7, header, 1, 0, 'C', fill=True)
    pdf.ln()

def table_row(pdf, data, widths, fill_color=False):
    if fill_color:
        pdf.set_fill_color(248, 250, 252)
    else:
        pdf.set_fill_color(255, 255, 255)
    pdf.set_text_color(15, 23, 42)
    pdf.set_font('Arial', '', 8.5)
    for i, item in enumerate(data):
        pdf.cell(widths[i], 7, str(item)[:45], 1, 0, 'L', fill=True)
    pdf.ln()

def add_paragraph(pdf, text):
    pdf.set_font('Arial', '', 9.5)
    pdf.set_text_color(51, 65, 85)
    pdf.multi_cell(0, 5, text)
    pdf.ln(3)

def generate_pdf_report(output_path=None, company_name="DataSense.AI", logo_url=None, **kwargs):
    pdf = ExecutivePDF(company_name, logo_url)
    pdf.set_auto_page_break(True, margin=20)
    pdf.add_page()
    
    # -------------------------------------------------------------
    # SECTION 1: EXECUTIVE SUMMARY
    # -------------------------------------------------------------
    pdf.chapter_title("1", "Executive Summary")
    
    # Metrics Widget Block
    kpis = analysis.get_kpis(**kwargs)
    pdf.set_fill_color(240, 246, 255) # light corporate blue highlight
    pdf.set_draw_color(191, 219, 254)
    pdf.rect(10, pdf.get_y(), 190, 20, 'DF')
    
    pdf.set_y(pdf.get_y() + 3)
    pdf.set_font('Arial', 'B', 9)
    pdf.set_text_color(30, 58, 138)
    pdf.cell(47, 5, 'GROSS REVENUE', 0, 0, 'C')
    pdf.cell(47, 5, 'TOTAL ORDERS', 0, 0, 'C')
    pdf.cell(47, 5, 'UNIQUE CLIENTS', 0, 0, 'C')
    pdf.cell(47, 5, 'AVERAGE ORDER VALUE', 0, 1, 'C')
    
    pdf.set_font('Arial', 'B', 12)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(47, 7, f"${kpis['revenue']:,.2f}", 0, 0, 'C')
    pdf.cell(47, 7, f"{kpis['orders']:,}", 0, 0, 'C')
    pdf.cell(47, 7, f"{kpis['customers']:,}", 0, 0, 'C')
    pdf.cell(47, 7, f"${kpis['avg_order']:,.2f}", 0, 1, 'C')
    pdf.ln(6)
    
    # Executive text analysis
    rev_eval = "stable market footing" if kpis['revenue'] > 5000 else "emerging startup volumes"
    summary_text = (
        f"This strategic business intelligence assessment evaluates the operational health, consumer purchase dynamics, "
        f"and inventory flow at {company_name}. Based on our automated ingestion pipelines, the workspace records "
        f"a total of {kpis['orders']:,} completed transactions yielding a gross consolidated revenue of ${kpis['revenue']:,.2f} "
        f"across {kpis['customers']:,} unique customers. The average order value (AOV) stands at ${kpis['avg_order']:,.2f}, indicating {rev_eval}.\n\n"
        f"Key observations show distinct consumer interest clusters, potential profit leakage from inventory shortages, "
        f"and specific risk metrics pointing to churn threats. Immediate deployment of targeted lifecycle campaigns "
        f"and margin-optimized inventory adjustments are recommended to scale operations and customer lifetime value (LTV)."
    )
    add_paragraph(pdf, summary_text)
    pdf.ln(5)

    # -------------------------------------------------------------
    # SECTION 2: CUSTOMER BEHAVIOR ANALYSIS
    # -------------------------------------------------------------
    pdf.chapter_title("2", "Customer Behavior Analysis")
    
    behavior_intro = (
        "Analyzing customer transaction patterns reveals when and what users buy. Below is the historical monthly trend "
        "of order revenue. This allows us to track seasonal shopping surges and calculate operational growth trajectory."
    )
    add_paragraph(pdf, behavior_intro)
    
    # Insert Trend Chart
    df_trend = analysis.get_monthly_sales_trend(**kwargs)
    if not df_trend.empty:
        fig, ax = plt.subplots(figsize=(7, 2.8))
        if len(df_trend) <= 2:
            ax.bar(df_trend['month'].astype(str), df_trend['total_revenue'], color='#1E3A8A', width=0.35)
        else:
            ax.plot(df_trend['month'].astype(str), df_trend['total_revenue'], marker='o', color='#2563EB', linewidth=2.5)
        ax.set_ylabel('Revenue ($)', fontsize=9)
        ax.set_title('Monthly Revenue Trend', fontsize=10, fontweight='bold', color='#1E293B')
        ax.grid(axis='y', linestyle='--', alpha=0.5)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        plt.xticks(rotation=15, fontsize=8)
        plt.yticks(fontsize=8)
        fig.tight_layout()
        
        trend_img = f"trend_{uuid.uuid4().hex[:8]}.png"
        fig.savefig(trend_img, dpi=120)
        plt.close(fig)
        pdf.image(trend_img, w=150, x=30)
        pdf.ln(4)
        if os.path.exists(trend_img):
            try: os.remove(trend_img)
            except: pass
    
    # Demographics and purchase behaviors
    age_prod_data = analysis.get_age_product_analysis(**kwargs)
    if age_prod_data:
        add_paragraph(pdf, "The matrix below displays specific purchase preferences categorized by age range, helping target marketing groups:")
        table_header(pdf, ['Age Group', 'Product Preferred', 'Total Quantity Bought'], [50, 90, 50])
        fill = False
        for age_grp, items in age_prod_data.items():
            if not items:
                table_row(pdf, [age_grp, "No purchases recorded", "0"], [50, 90, 50], fill)
                fill = not fill
            else:
                for item in items[:2]: # Show top 2 per age group
                    table_row(pdf, [age_grp, item['product_name'], str(item['total_quantity'])], [50, 90, 50], fill)
                    fill = not fill
        pdf.ln(5)

    # -------------------------------------------------------------
    # SECTION 3: DATA MINING & SEGMENTATION INSIGHTS
    # -------------------------------------------------------------
    pdf.add_page()
    pdf.chapter_title("3", "Data Mining & Segmentation Insights")
    
    mining_intro = (
        "Using unsupervised Data Mining models, we segmented the customer base via RFM (Recency, Frequency, "
        "Monetary) metrics to pinpoint loyalty groups. Furthermore, Apriori association rule mining was executed "
        "to discover frequently co-purchased items, detailing the specific buyers associated with these transaction sets."
    )
    add_paragraph(pdf, mining_intro)
    
    # VIP RFM Table
    pdf.set_font('Arial', 'B', 10)
    pdf.set_text_color(30, 58, 138)
    pdf.cell(0, 6, "Key Loyalty Clusters (Top VIP Customer Segment):", ln=1)
    rfm = analysis.get_rfm_analysis(limit=4, **kwargs)
    if rfm:
        table_header(pdf, ['Customer Name', 'Recency (Days)', 'Order Count', 'Total Monetary Spend ($)'], [60, 40, 40, 50])
        fill = False
        for r in rfm:
            table_row(pdf, [r['name'], str(r['recency']), str(r['frequency']), f"${r['monetary']:,.2f}"], [60, 40, 40, 50], fill)
            fill = not fill
    else:
        add_paragraph(pdf, "No RFM segments computed. Insufficient user data.")
    pdf.ln(4)
    
    # Association Rules Table
    pdf.set_font('Arial', 'B', 10)
    pdf.set_text_color(30, 58, 138)
    pdf.cell(0, 6, "Association Rules & Co-purchase Segments:", ln=1)
    rules = analysis.get_association_rules_data(min_support=0.001, min_confidence=0.01, **kwargs)
    if rules:
        table_header(pdf, ['Bought Item(s)', 'Also Bought...', 'Who Bought Them', 'Confidence'], [55, 55, 55, 25])
        fill = False
        for r in rules[:4]:
            table_row(pdf, [r['antecedents'], r['consequents'], r['buyers'], f"{(r['confidence']*100):.1f}%"], [55, 55, 55, 25], fill)
            fill = not fill
    else:
        add_paragraph(pdf, "No multi-item basket correlations detected in dataset.")
    pdf.ln(5)

    # -------------------------------------------------------------
    # SECTION 4: LINEAR ALGEBRA & ANALYTICAL VECTOR SPACE
    # -------------------------------------------------------------
    pdf.chapter_title("4", "Linear Algebra & Analytical Vector Space")
    
    linear_algebra_text = (
        "To perform behavioral similarity, customers are represented in a high-dimensional vector space "
        "where coordinates represent item quantities purchased. By calculating eigenvectors and eigenvalues, "
        "we decompose this purchase matrix using Singular Value Decomposition (SVD).\n\n"
        "SVD isolates the principal directions of variance, projecting sparse transactional data into low-dimensional "
        "latent vectors representing 'Customer Personas'. This reduces noise and uncovers hidden thematic buying "
        "relationships. Below are the top personas detected in the user-product space based on coordinate weights:"
    )
    add_paragraph(pdf, linear_algebra_text)
    
    # SVD Personas Table
    personas = analysis.get_svd_personas(**kwargs)
    if personas:
        table_header(pdf, ['Persona ID', 'Variance Strength (%)', 'Associated High-Weight Products'], [40, 40, 110])
        fill = False
        for p in personas:
            table_row(pdf, [p['persona_id'], f"{p['strength_pct']}%", p['key_products']], [40, 40, 110], fill)
            fill = not fill
    else:
        add_paragraph(pdf, "No SVD personas could be extracted. Coordinate projection requires active product variance.")
    pdf.ln(5)

    # -------------------------------------------------------------
    # SECTION 5: BUSINESS PERFORMANCE ANALYSIS
    # -------------------------------------------------------------
    pdf.add_page()
    pdf.chapter_title("5", "Business Performance Analysis")
    
    perf_text = (
        "Operational efficiency is analyzed by category margins and payment preferences. Understanding which "
        "categories drive gross volume versus transactions allows the company to balance marketing investments."
    )
    add_paragraph(pdf, perf_text)
    
    df_cat = analysis.get_category_analysis(**kwargs)
    df_pay = analysis.get_payment_analysis(**kwargs)
    
    # Dual performance columns in tables
    if not df_cat.empty:
        pdf.set_font('Arial', 'B', 10)
        pdf.set_text_color(30, 58, 138)
        pdf.cell(0, 6, "Gross Revenue Contribution by Product Category:", ln=1)
        table_header(pdf, ['Category Name', 'Items Sold', 'Revenue Generated ($)'], [70, 50, 70])
        fill = False
        for _, row in df_cat.head(4).iterrows():
            table_row(pdf, [row['category'], str(row['items_sold']), f"${row['revenue']:,.2f}"], [70, 50, 70], fill)
            fill = not fill
        pdf.ln(4)
        
    if not df_pay.empty:
        pdf.set_font('Arial', 'B', 10)
        pdf.set_text_color(30, 58, 138)
        pdf.cell(0, 6, "Transactional Volumes by Payment Channel:", ln=1)
        table_header(pdf, ['Payment Method', 'Completed Transactions', 'Gross Value ($)'], [70, 50, 70])
        fill = False
        for _, row in df_pay.head(4).iterrows():
            table_row(pdf, [row['payment_method'], str(row['num_transactions']), f"${row['total_revenue']:,.2f}"], [70, 50, 70], fill)
            fill = not fill
        pdf.ln(5)

    # -------------------------------------------------------------
    # SECTION 6: COMPREHENSIVE RISK ASSESSMENT
    # -------------------------------------------------------------
    pdf.chapter_title("6", "Comprehensive Risk Assessment")
    
    risk_text = (
        "Risk metrics pinpoint customer retention failures. Users who remain absent beyond a 30-day window "
        "are flagged in our retention pipeline. Based on their historical spend and recency, they are classified "
        "into at-risk churn phases. Immediate promotional re-engagement is vital to prevent permanent customer loss."
    )
    add_paragraph(pdf, risk_text)
    
    # Churn Risk Table
    churn_data = analysis.get_churn_risk_analysis(limit=4, **kwargs)
    if churn_data:
        table_header(pdf, ['Customer Name', 'Last Bought', 'Days Absent', 'Spent ($)', 'Risk Phase', 'Recommended Offer'], [35, 35, 20, 20, 20, 60])
        fill = False
        for r in churn_data:
            table_row(pdf, [
                r['customer_name'], 
                r.get('interested_product', 'N/A'),
                f"{r['days_absent']} days", 
                f"${r['total_spent']:,.2f}", 
                r['status'], 
                r['action']
            ], [35, 35, 20, 20, 20, 60], fill)
            fill = not fill
    else:
        add_paragraph(pdf, "No churned or at-risk customers identified. Customer retention is healthy.")
    pdf.ln(5)

    # -------------------------------------------------------------
    # SECTION 7: OPERATIONAL & STRATEGIC RECOMMENDATIONS
    # -------------------------------------------------------------
    pdf.add_page()
    pdf.chapter_title("7", "Operational & Strategic Recommendations")
    
    recommendation_intro = (
        "Inventory optimization is critical for capital health. By matching sales velocities with wholesale costs, "
        "our analytical recommendations isolate stockouts that threaten profit margins. Prioritize critical restocking "
        "orders to minimize lost potential revenue:"
    )
    add_paragraph(pdf, recommendation_intro)
    
    # Restock Recommendations Table
    restock_data = analysis.get_restock_recommendations(**kwargs)
    if restock_data:
        table_header(pdf, ['Product Name', 'Category', 'Stock Left', 'Suggested Refill', 'Est. Profit Gain ($)', 'Priority'], [55, 35, 25, 30, 25, 20])
        fill = False
        for r in restock_data[:4]:
            table_row(pdf, [
                r['product_name'],
                r['category'],
                f"{r['current_stock']} units",
                f"+{r['suggested_restock_qty']}",
                f"${r['estimated_profit']:,.2f}",
                r['priority']
            ], [55, 35, 25, 30, 25, 20], fill)
            fill = not fill
    else:
        add_paragraph(pdf, "Inventory levels are fully optimized. No critical restocking recommendations exist currently.")
    pdf.ln(5)

    # -------------------------------------------------------------
    # SECTION 8: SEASONAL TRENDS & SALES GROWTH ADVISORY
    # -------------------------------------------------------------
    pdf.add_page()
    pdf.chapter_title("8", "Seasonal Trends & Sales Growth Advisory")
    
    seasonal_intro = (
        "Understanding product performance across seasons and identifying clear growth recommendations "
        "enables optimal promotion budgets and resource allocation. The table below lists the top-selling "
        "products per season in the current dataset, detailing units sold and total revenue generated:"
    )
    add_paragraph(pdf, seasonal_intro)
    
    # Seasonal Sales Table
    seasonal_data = analysis.get_seasonal_product_sales(**kwargs)
    if seasonal_data:
        table_header(pdf, ['Season', 'Top Product', 'Category', 'Units Sold', 'Revenue ($)'], [30, 60, 45, 25, 30])
        fill = False
        for s in seasonal_data:
            table_row(pdf, [
                s['season'],
                s['product_name'],
                s['category'],
                f"{s['total_sold']:,}",
                f"${s['revenue']:,.2f}"
            ], [30, 60, 45, 25, 30], fill)
            fill = not fill
    else:
        add_paragraph(pdf, "No seasonal trends found or insufficient date variety exists.")
    pdf.ln(5)
    
    growth_intro = (
        "By combining transaction velocities (demand indicators) with profit margins and inventory status, "
        "our AI advisory categorizes products to recommend promotion scaling or inventory holds. "
        "Prioritize the following growth actions to maximize margins:"
    )
    add_paragraph(pdf, growth_intro)
    
    # Growth Recommendations Table
    growth_data = analysis.get_sales_growth_recommendations(**kwargs)
    if growth_data:
        table_header(pdf, ['Product Name', 'Sales Vol', 'Growth Recommendation', 'Status', 'Reason'], [50, 20, 45, 30, 45])
        fill = False
        for g in growth_data[:5]: # Limit to top 5 for page layout space
            table_row(pdf, [
                g['product_name'],
                f"{g['quantity_sold']}",
                g['recommendation'],
                g['status'],
                g['reason']
            ], [50, 20, 45, 30, 45], fill)
            fill = not fill
    else:
        add_paragraph(pdf, "No product metrics available to compute growth recommendations.")
    pdf.ln(5)

    # -------------------------------------------------------------
    # SECTION 9: FUTURE FORECASTS & CUSTOMER LTV PREDICTIONS
    # -------------------------------------------------------------
    pdf.chapter_title("9", "Future Forecasts & Customer LTV Predictions")
    
    # Calculate simple forecast projection
    growth_rate = 0.05 # default
    if not df_trend.empty and len(df_trend) >= 2:
        try:
            revs = df_trend['total_revenue'].values
            change = (revs[-1] - revs[0]) / revs[0]
            growth_rate = max(-0.2, min(0.3, change / len(revs)))
        except:
            pass
            
    proj_rev_1 = kpis['revenue'] * (1 + growth_rate) / max(1, len(df_trend))
    proj_rev_2 = proj_rev_1 * (1 + growth_rate)
    
    forecast_text = (
        f"Based on historical transactional velocities and seasonal growth calculations, we project a short-term trend "
        f"trajectory of {growth_rate*100:,.1f}% per period. Under this baseline forecast, the next consecutive month "
        f"is projected to generate approximately ${proj_rev_1:,.2f} in sales volume, growing to ${proj_rev_2:,.2f} in month 2.\n\n"
        f"Demand forecasting indicates that categories showing high volume will face increased strain. Pre-allocating warehouse stock 15 days prior to seasonal surges is highly advised to avoid bottleneck issues."
    )
    add_paragraph(pdf, forecast_text)
    
    # Add Customer Lifetime Value Predictions
    try:
        ltv_data = analysis.get_ltv_predictions(**kwargs)
        if ltv_data and ltv_data.get("users"):
            metrics = ltv_data.get("metrics", {})
            users = ltv_data.get("users", [])
            
            ltv_intro = (
                f"Furthermore, using a scikit-learn Gradient Boosting Regressor (GBDT), we predict the Customer Lifetime Value (LTV) "
                f"of each client based on their first 30 days of transaction behavior. The prediction model achieves a validation "
                f"R² accuracy of {metrics.get('r2', 0.0):.3f} with a Mean Absolute Error (MAE) of ${metrics.get('mae', 0.0):,.2f}.\n"
                f"Model status: {metrics.get('status', '')}. Below are the top predicted high-value customers:"
            )
            add_paragraph(pdf, ltv_intro)
            
            table_header(pdf, ['Customer Name', 'Country', 'Initial Spent (30d)', 'Future Spent (Est)', 'Predicted Total LTV'], [45, 30, 35, 40, 40])
            fill = False
            for u in users[:4]:
                table_row(pdf, [
                    u['name'],
                    u['country'],
                    f"${u['initial_spent']:,.2f}",
                    f"${u['predicted_future_spent']:,.2f}",
                    f"${u['predicted_total_ltv']:,.2f}"
                ], [45, 30, 35, 40, 40], fill)
                fill = not fill
        else:
            add_paragraph(pdf, "Customer Lifetime Value predictions are currently unavailable due to insufficient order histories.")
    except Exception as ltv_pdf_err:
        print(f"Error writing LTV section to PDF: {ltv_pdf_err}")
        add_paragraph(pdf, "An error occurred compiling dynamic LTV predictions.")
        
    pdf.ln(5)

    # -------------------------------------------------------------
    # SECTION 10: ACTIONABLE TARGETING & MARKETING STRATEGIES
    # -------------------------------------------------------------
    pdf.chapter_title("10", "Actionable Targeting & Marketing")
    
    marketing_text = (
        "To maximize customer lifetime value (LTV) and reduce customer churn, we suggest deploying targeted actions:\n"
        "1. Dynamic Cross-Selling: Display the Frequently Bought Together items resolved in Section 3 at the online checkout page to encourage impulse buys.\n"
        "2. Automate Email Workflows: Enable the automated daily campaigner to automatically email 20% discount coupons to Dormant customers and 40% coupons to Churned customers.\n"
        "3. Personalized Demographics: Allocate targeted ad spend to matching products preferred by the 18-25 and 26-35 age brackets as discovered in behavioral logs."
    )
    add_paragraph(pdf, marketing_text)
    pdf.ln(5)

    # -------------------------------------------------------------
    # SECTION 11: FINAL CONCLUSIONS & NEXT STEPS
    # -------------------------------------------------------------
    pdf.chapter_title("11", "Final Conclusions & Next Steps")
    
    conclusion_text = (
        f"In summary, {company_name} displays strong business foundations with a robust base of {kpis['customers']:,} customers "
        f"generating ${kpis['revenue']:,.2f}. The primary strength lies in high-performing product groups and clear customer "
        f"association rules. However, the business faces vulnerability in customer retention and potential margins lost "
        f"to low stock levels.\n\n"
        f"Important Next Steps:\n"
        f"- Execute the critical restock recommendations in Section 7 to capture lost profit margins.\n"
        f"- Deploy the automatic email campaigner to recover at-risk customers from Section 6.\n"
        f"- Enhance checkout user experience by embedding dynamic cross-selling product cards."
    )
    add_paragraph(pdf, conclusion_text)

    
    if output_path is not None:
        pdf.output(output_path)
        return output_path
    else:
        out = pdf.output(dest='S')
        if isinstance(out, (bytes, bytearray)):
            return bytes(out)
        return out.encode('latin1')
