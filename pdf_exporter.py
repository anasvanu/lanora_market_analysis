#!/usr/bin/env python3
"""
Lanora Gold Trading LLC — PDF Presentation Exporter
Compiles print-perfect 5-page 16:9 landscape PDF technical reports with H4 Candlestick Charts embedded.
"""

import sys
import os
from datetime import datetime
from market_engine import get_market_data
from chart_generator import generate_gold_chart, generate_silver_chart

def generate_pdf_report(output_filename="Lanora_Gold_Daily_Technical_Report.pdf"):
    print(f"Generating PDF Technical Report: {output_filename}...")
    data = get_market_data()

    # Generate dynamic H4 Technical Graphs for Gold & Silver
    gold_chart_path = generate_gold_chart(data['gold']['spot'], data['gold']['pivots']['P'], "assets/gold_chart.png")
    silver_chart_path = generate_silver_chart(data['silver']['spot'], data['silver']['pivots']['P'], "assets/silver_chart.png")

    try:
        from reportlab.lib.pagesizes import landscape, A4
        from reportlab.lib import colors
        from reportlab.platypus import (
            SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, KeepTogether
        )
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch

        # 16:9 Widescreen Page Dimensions (11 x 6.1875 inches)
        PAGE_WIDTH = 11 * inch
        PAGE_HEIGHT = 6.1875 * inch

        doc = SimpleDocTemplate(
            output_filename,
            pagesize=(PAGE_WIDTH, PAGE_HEIGHT),
            rightMargin=0.4 * inch,
            leftMargin=0.4 * inch,
            topMargin=0.35 * inch,
            bottomMargin=0.35 * inch
        )

        styles = getSampleStyleSheet()
        
        NAVY_DARK = colors.HexColor("#060d1d")
        NAVY_BLUE = colors.HexColor("#0b1930")
        GOLD_PRIMARY = colors.HexColor("#dfb256")
        GOLD_ACCENT = colors.HexColor("#b8860b")
        SLATE_BG = colors.HexColor("#f5f8fc")
        MUTED_TEXT = colors.HexColor("#5a6e85")

        title_style = ParagraphStyle(
            'TitleStyle',
            fontName='Helvetica-Bold',
            fontSize=22,
            leading=26,
            textColor=NAVY_BLUE
        )

        gold_title_style = ParagraphStyle(
            'GoldTitleStyle',
            fontName='Helvetica-Bold',
            fontSize=22,
            leading=26,
            textColor=GOLD_ACCENT
        )

        subtitle_style = ParagraphStyle(
            'SubtitleStyle',
            fontName='Helvetica',
            fontSize=11,
            leading=14,
            textColor=MUTED_TEXT
        )

        body_style = ParagraphStyle(
            'BodyStyle',
            fontName='Helvetica',
            fontSize=10,
            leading=14,
            textColor=NAVY_DARK
        )

        header_badge_style = ParagraphStyle(
            'HeaderBadge',
            fontName='Helvetica-Bold',
            fontSize=8,
            leading=10,
            textColor=colors.HexColor("#8c630d"),
            backColor=colors.HexColor("#fef9e7"),
            borderColor=GOLD_PRIMARY,
            borderWidth=1,
            borderPadding=4,
            spaceAfter=0
        )

        logo_path = os.path.abspath("assets/lanora_logo_badge.jpg")
        gold_img_path = os.path.abspath("assets/gold_1kg_feature.jpg")
        pamp_img_path = os.path.abspath("assets/pamp_fortuna_feature.jpg")

        story = []

        def make_header(title_text, badge_text=""):
            logo_img = Image(logo_path, width=0.6*inch, height=0.6*inch)
            title_p = Paragraph(f"<b>{title_text}</b>", title_style)
            if badge_text:
                badge_p = Paragraph(f"<b>{badge_text}</b>", header_badge_style)
                title_table = Table([[title_p, badge_p, logo_img]], colWidths=[6.5*inch, 2.5*inch, 1*inch])
            else:
                title_table = Table([[title_p, "", logo_img]], colWidths=[7.5*inch, 1.5*inch, 1*inch])
            
            title_table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('ALIGN', (2, 0), (2, 0), 'RIGHT'),
            ]))
            return title_table

        # ---------------- SLIDE 1: COVER PAGE ----------------
        story.append(make_header("Precious Metals Technical Report"))
        story.append(Paragraph("Daily Pivot Points, Support/Resistance & Trade Strategies", subtitle_style))
        story.append(Spacer(1, 15))

        meta_content = [
            [Paragraph("<b>FIRM NAME</b>", subtitle_style), Paragraph("<b>REPORT DATE</b>", subtitle_style)],
            [Paragraph(f"<b>{data['company']['name']}</b>", body_style), Paragraph(f"<b>{data['report_metadata']['date']}</b>", body_style)],
            [Spacer(1, 8), Spacer(1, 8)],
            [Paragraph("<b>LOCATION</b>", subtitle_style), Paragraph("<b>TRADING DESK</b>", subtitle_style)],
            [Paragraph(f"<b>{data['company']['location']}</b>", body_style), Paragraph("<b>Al Ras, Gold Center</b>", body_style)]
        ]
        meta_table = Table(meta_content, colWidths=[2.2*inch, 2.2*inch])
        meta_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#eef4fc")),
            ('PADDING', (0, 0), (-1, -1), 8),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#d0e1f9")),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))

        gold_img = Image(gold_img_path, width=4.2*inch, height=2.8*inch)
        right_box = [
            [gold_img],
            [Paragraph("<font color='#dfb256'><b>Hold Real Value In Your Hands</b></font>", body_style)],
            [Paragraph('"Pure value. Timeless Power." — Official 1 Kilo Fine Gold 999.9 physical bullion technical research for Dubai market desks.', ParagraphStyle('W', parent=body_style, textColor=colors.white, fontSize=8))],
            [Paragraph(f"<font color='#94a3b8'>Gold Spot Reference</font> <font color='#dfb256'><b>${data['gold']['spot']:.2f}</b></font>", body_style)]
        ]
        right_table = Table(right_box, colWidths=[4.4*inch])
        right_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), NAVY_BLUE),
            ('PADDING', (0, 0), (-1, -1), 6),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))

        slide1_grid = Table([[meta_table, right_table]], colWidths=[4.8*inch, 5.2*inch])
        slide1_grid.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(slide1_grid)
        story.append(PageBreak())

        # ---------------- SLIDE 2: MACROECONOMIC CALENDAR ----------------
        story.append(make_header("Macro Economic Calendar", "DUBAI TIME (GMT+4)"))
        story.append(Paragraph("Key macroeconomic releases scheduled for today impacting USD volatility and precious metals spot pricing:", subtitle_style))
        story.append(Spacer(1, 10))

        macro_rows = [["Time", "Cur.", "Economic Event", "Forecast", "Previous"]]
        for row in data['macro_calendar']:
            macro_rows.append([row['time'], row['currency'], row['event'], row['forecast'], row['previous']])
        
        t_macro = Table(macro_rows, colWidths=[1.1*inch, 0.7*inch, 2.7*inch, 1*inch, 1*inch])
        t_macro.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), NAVY_BLUE),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('PADDING', (0, 0), (-1, -1), 6),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ]))

        pamp_img = Image(pamp_img_path, width=3.4*inch, height=3.4*inch)
        slide2_grid = Table([[t_macro, pamp_img]], colWidths=[6.8*inch, 3.4*inch])
        slide2_grid.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'MIDDLE')]))
        story.append(slide2_grid)
        story.append(PageBreak())

        # ---------------- SLIDE 3: SPOT GOLD TECHNICAL MATRIX ----------------
        story.append(make_header("Spot Gold (XAU/USD) Technical Analysis", "H4 PRICE GRAPH"))
        story.append(Spacer(1, 10))

        gold_p = data['gold']['pivots']
        g_stat = Table([
            [Paragraph("CURRENT PRICE", subtitle_style), Paragraph("PIVOT POINT", subtitle_style), Paragraph("TARGET (R1)", subtitle_style)],
            [Paragraph(f"<b>${data['gold']['spot']:.2f}</b>", title_style), Paragraph(f"<b>${gold_p['P']:.2f}</b>", gold_title_style), Paragraph(f"<b>${gold_p['R1']:.2f}</b>", title_style)]
        ], colWidths=[2.2*inch, 2.2*inch, 2.2*inch])
        g_stat.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.white),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#e2e8f0")),
            ('BACKGROUND', (1, 0), (1, 1), colors.HexColor("#fef9e7")),
            ('BOX', (1, 0), (1, 1), 1.5, GOLD_PRIMARY),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('PADDING', (0, 0), (-1, -1), 4)
        ]))

        g_matrix = Table([
            ["Support Levels", "Resistance Levels"],
            [f"S1: {gold_p['S1']:.2f}", f"R1: {gold_p['R1']:.2f}"],
            [f"S2: {gold_p['S2']:.2f}", f"R2: {gold_p['R2']:.2f}"],
            [f"S3: {gold_p['S3']:.2f}", f"R3: {gold_p['R3']:.2f}"]
        ], colWidths=[3.3*inch, 3.3*inch])
        g_matrix.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), NAVY_BLUE),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('PADDING', (0, 0), (-1, -1), 5),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0"))
        ]))

        buy_plan = Paragraph(f"<b>📈 Buy Above {gold_p['P']:.2f}</b><br/>Targets: {gold_p['R1']:.2f} | {gold_p['R2']:.2f}<br/>Stop Loss: {gold_p['S1']:.2f}", body_style)
        sell_plan = Paragraph(f"<b>📉 Sell Below {gold_p['P']:.2f}</b><br/>Targets: {gold_p['S1']:.2f} | {gold_p['S2']:.2f}<br/>Stop Loss: {gold_p['R1']:.2f}", body_style)
        trade_t = Table([[buy_plan, sell_plan]], colWidths=[3.3*inch, 3.3*inch])
        trade_t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, 0), colors.HexColor("#eefbf4")),
            ('BOX', (0, 0), (0, 0), 1, colors.HexColor("#a3e6be")),
            ('BACKGROUND', (1, 0), (1, 0), colors.HexColor("#fdeeee")),
            ('BOX', (1, 0), (1, 0), 1, colors.HexColor("#f8b4b4")),
            ('PADDING', (0, 0), (-1, -1), 6)
        ]))

        left_gold = [g_stat, Spacer(1, 6), g_matrix, Spacer(1, 6), trade_t]
        gold_chart_img = Image(gold_chart_path, width=3.4*inch, height=3.3*inch)
        story.append(Table([[left_gold, gold_chart_img]], colWidths=[6.8*inch, 3.4*inch]))
        story.append(PageBreak())

        # ---------------- SLIDE 4: SPOT SILVER TECHNICAL MATRIX ----------------
        story.append(make_header("Spot Silver (XAG/USD) Technical Analysis", "H4 PRICE GRAPH"))
        story.append(Spacer(1, 10))

        silver_p = data['silver']['pivots']
        s_stat = Table([
            [Paragraph("CURRENT PRICE", subtitle_style), Paragraph("PIVOT POINT", subtitle_style)],
            [Paragraph(f"<b>${data['silver']['spot']:.3f}</b>", title_style), Paragraph(f"<b>${silver_p['P']:.3f}</b>", gold_title_style)]
        ], colWidths=[3.3*inch, 3.3*inch])
        s_stat.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.white),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#e2e8f0")),
            ('BACKGROUND', (1, 0), (1, 1), colors.HexColor("#fef9e7")),
            ('BOX', (1, 0), (1, 1), 1.5, GOLD_PRIMARY),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('PADDING', (0, 0), (-1, -1), 4)
        ]))

        s_matrix = Table([
            ["Key Support", "Key Resistance"],
            [f"S1: {silver_p['S1']:.3f}", f"R1: {silver_p['R1']:.3f}"],
            [f"S2: {silver_p['S2']:.3f}", f"R2: {silver_p['R2']:.3f}"],
            [f"S3: {silver_p['S3']:.3f}", f"R3: {silver_p['R3']:.3f}"]
        ], colWidths=[3.3*inch, 3.3*inch])
        s_matrix.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), NAVY_BLUE),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('PADDING', (0, 0), (-1, -1), 5),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0"))
        ]))

        s_buy_plan = Paragraph(f"<b>📈 Buy Above {silver_p['P']:.3f}</b><br/>Targets: {silver_p['R1']:.3f} / {silver_p['R2']:.3f} | SL: {silver_p['S1']:.3f}", body_style)
        s_sell_plan = Paragraph(f"<b>📉 Sell Below {silver_p['P']:.3f}</b><br/>Targets: {silver_p['S1']:.3f} / {silver_p['S2']:.3f} | SL: {silver_p['R1']:.3f}", body_style)
        s_trade_t = Table([[s_buy_plan, s_sell_plan]], colWidths=[3.3*inch, 3.3*inch])
        s_trade_t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, 0), colors.HexColor("#eefbf4")),
            ('BOX', (0, 0), (0, 0), 1, colors.HexColor("#a3e6be")),
            ('BACKGROUND', (1, 0), (1, 0), colors.HexColor("#fdeeee")),
            ('BOX', (1, 0), (1, 0), 1, colors.HexColor("#f8b4b4")),
            ('PADDING', (0, 0), (-1, -1), 6)
        ]))

        left_silver = [s_stat, Spacer(1, 6), s_matrix, Spacer(1, 6), s_trade_t]
        silver_chart_img = Image(silver_chart_path, width=3.4*inch, height=3.3*inch)
        story.append(Table([[left_silver, silver_chart_img]], colWidths=[6.8*inch, 3.4*inch]))
        story.append(PageBreak())

        # ---------------- SLIDE 5: CLOSING & TRADING DESK ----------------
        banner_content = [
            [Paragraph("<font color='#dfb256'><b>Thank You</b></font>", title_style)],
            [Paragraph("<b>\"Hold Real Value In Your Hands — Pure Value. Timeless Power.\"</b>", ParagraphStyle('B1', parent=body_style, textColor=colors.white, alignment=1))],
            [Paragraph("Lanora Gold Trading LLC — Physical Bullion & Precious Metals Trading Desk", ParagraphStyle('B2', parent=body_style, textColor=colors.HexColor("#94a3b8"), alignment=1))]
        ]
        banner_table = Table(banner_content, colWidths=[9.8*inch])
        banner_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), NAVY_BLUE),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('PADDING', (0, 0), (-1, -1), 10),
            ('BOX', (0, 0), (-1, -1), 1, GOLD_PRIMARY)
        ]))
        story.append(banner_table)
        story.append(Spacer(1, 15))

        contacts = Table([
            [
                Paragraph("<b>Trading Desk Location</b><br/>Shop No. 18, Nasser Lootah Bldg.<br/>Next to Gold Center, Al Ras, Dubai, U.A.E.", body_style),
                Paragraph("<b>Direct Phone Lines</b><br/>04-3215916<br/>0505395916", body_style),
                Paragraph("<b>Email & Social Desk</b><br/>lanoragoldtrading@gmail.com<br/>@lanoragoldtrading", body_style)
            ]
        ], colWidths=[3.2*inch, 3.2*inch, 3.2*inch])
        contacts.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.white),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#e2e8f0")),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#edf2f7")),
            ('PADDING', (0, 0), (-1, -1), 12),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER')
        ]))
        story.append(contacts)
        story.append(Spacer(1, 15))

        disclaimer = Paragraph("<b>Risk Statement & Legal Disclaimer:</b> Trading physical bullion, precious metals, and spot contracts carries substantial market risk and is not suitable for all investors. The technical pivot levels and strategies published herein are for informational and market research purposes only. Lanora Gold Trading LLC accepts no liability for trading decisions or losses incurred as a result of using this research.", ParagraphStyle('D', parent=body_style, fontSize=7, leading=10, textColor=colors.HexColor("#475569")))
        disclaimer_table = Table([[disclaimer]], colWidths=[9.8*inch])
        disclaimer_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#edf2f7")),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#cbd5e1")),
            ('PADDING', (0, 0), (-1, -1), 8)
        ]))
        story.append(disclaimer_table)

        doc.build(story)
        print(f"PDF Successfully Generated: {output_filename}")
        return True

    except Exception as e:
        print(f"ReportLab PDF Generation Error: {e}")
        return False

if __name__ == "__main__":
    out_file = sys.argv[1] if len(sys.argv) > 1 else "Lanora_Gold_Daily_Technical_Report.pdf"
    generate_pdf_report(out_file)
