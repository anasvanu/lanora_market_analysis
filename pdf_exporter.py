#!/usr/bin/env python3
"""
Lanora Gold Trading LLC — Premium PDF Presentation Exporter
Compiles print-perfect 5-page 16:9 landscape PDF technical reports.
"""

import sys
import os
from datetime import datetime
from market_engine import get_market_data
from chart_generator import generate_gold_chart, generate_silver_chart

def generate_pdf_report(output_filename="Lanora_Gold_Daily_Technical_Report.pdf"):
    print(f"Generating PDF Technical Report: {output_filename}...")
    data = get_market_data()

    # Generate dynamic price charts for Gold & Silver
    gold_chart_path = generate_gold_chart(data['gold']['spot'], data['gold']['pivots']['P'], "assets/gold_chart.png")
    silver_chart_path = generate_silver_chart(data['silver']['spot'], data['silver']['pivots']['P'], "assets/silver_chart.png")

    try:
        from reportlab.lib.pagesizes import landscape
        from reportlab.lib import colors
        from reportlab.platypus import (
            SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
            Image, PageBreak, HRFlowable
        )
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

        # ── Page: 16:9 Widescreen (11 × 6.1875 in) ──────────────────────────
        PW = 11 * inch
        PH = 6.1875 * inch
        M  = 0.38 * inch   # uniform margin

        doc = SimpleDocTemplate(
            output_filename,
            pagesize=(PW, PH),
            rightMargin=M, leftMargin=M,
            topMargin=M,   bottomMargin=M
        )

        # ── Brand Palette ─────────────────────────────────────────────────────
        NAVY      = colors.HexColor("#060d1d")
        NAVY_MID  = colors.HexColor("#0b1930")
        NAVY_CARD = colors.HexColor("#0f2244")
        GOLD      = colors.HexColor("#dfb256")
        GOLD_DARK = colors.HexColor("#b8860b")
        GOLD_PALE = colors.HexColor("#fef9e7")
        SILVER_C  = colors.HexColor("#c0c9d8")
        SLATE     = colors.HexColor("#94a3b8")
        WHITE     = colors.white
        GREEN_BG  = colors.HexColor("#0d2b1a")
        GREEN_ACC = colors.HexColor("#22c55e")
        RED_BG    = colors.HexColor("#2b0d0d")
        RED_ACC   = colors.HexColor("#ef4444")
        DIVIDER   = colors.HexColor("#1e3a5f")

        # ── Typography ────────────────────────────────────────────────────────
        def style(name, **kw):
            base = kw.pop("parent", None)
            p = ParagraphStyle(name, **kw)
            return p

        ST_PAGE_TITLE = style("PageTitle",
            fontName="Helvetica-Bold", fontSize=17, leading=20,
            textColor=WHITE, spaceAfter=0)

        ST_PAGE_TITLE_GOLD = style("PageTitleGold",
            fontName="Helvetica-Bold", fontSize=17, leading=20,
            textColor=GOLD, spaceAfter=0)

        ST_SUBTITLE = style("Subtitle",
            fontName="Helvetica", fontSize=9, leading=12,
            textColor=SLATE, spaceAfter=0)

        ST_LABEL = style("Label",
            fontName="Helvetica-Bold", fontSize=7, leading=9,
            textColor=SLATE, spaceAfter=0, spaceBefore=0)

        ST_VALUE_BIG = style("ValueBig",
            fontName="Helvetica-Bold", fontSize=20, leading=24,
            textColor=WHITE, alignment=TA_CENTER)

        ST_VALUE_GOLD = style("ValueGold",
            fontName="Helvetica-Bold", fontSize=20, leading=24,
            textColor=GOLD, alignment=TA_CENTER)

        ST_BODY = style("Body",
            fontName="Helvetica", fontSize=8.5, leading=12,
            textColor=WHITE)

        ST_BODY_DARK = style("BodyDark",
            fontName="Helvetica", fontSize=8.5, leading=12,
            textColor=NAVY)

        ST_TABLE_HDR = style("TableHdr",
            fontName="Helvetica-Bold", fontSize=8, leading=10,
            textColor=WHITE, alignment=TA_CENTER)

        ST_TABLE_CELL = style("TableCell",
            fontName="Helvetica", fontSize=8, leading=11,
            textColor=WHITE, alignment=TA_CENTER)

        ST_PIVOT_LBL = style("PivotLbl",
            fontName="Helvetica-Bold", fontSize=9, leading=11,
            textColor=SLATE, alignment=TA_LEFT)

        ST_PIVOT_VAL = style("PivotVal",
            fontName="Helvetica-Bold", fontSize=9, leading=11,
            textColor=WHITE, alignment=TA_RIGHT)

        ST_CONTACT = style("Contact",
            fontName="Helvetica", fontSize=8, leading=12,
            textColor=SILVER_C, alignment=TA_CENTER)

        ST_DISCLAIMER = style("Disclaimer",
            fontName="Helvetica", fontSize=6.5, leading=9,
            textColor=SLATE, alignment=TA_CENTER)

        # ── Asset Paths ───────────────────────────────────────────────────────
        LOGO     = os.path.abspath("assets/lanora_logo_badge.png")
        GOLD_IMG = os.path.abspath("assets/gold_1kg_feature.jpg")
        PAMP_IMG = os.path.abspath("assets/pamp_fortuna_feature.jpg")

        story = []
        IW = PW - 2 * M   # inner content width

        # ══════════════════════════════════════════════════════════════════════
        # SHARED HELPER: Premium Dark Header Bar
        # ══════════════════════════════════════════════════════════════════════
        def make_header(title, badge=None):
            logo_img = Image(LOGO, width=0.65*inch, height=0.65*inch)
            title_p  = Paragraph(f"<b>{title}</b>", ST_PAGE_TITLE)

            if badge:
                badge_p = Paragraph(
                    f"<b>{badge}</b>",
                    style("Badge",
                          fontName="Helvetica-Bold", fontSize=7, leading=9,
                          textColor=GOLD_DARK,
                          backColor=GOLD_PALE,
                          borderPadding=(3,6,3,6)))
                cols = [IW - 1.2*inch - 1.3*inch, 1.2*inch, 1.3*inch]
                cells = [[title_p, badge_p, logo_img]]
            else:
                cols = [IW - 1.3*inch, 0.5*inch, 1.3*inch]
                cells = [[title_p, "", logo_img]]

            hdr = Table(cells, colWidths=cols)
            hdr.setStyle(TableStyle([
                ("VALIGN",  (0,0), (-1,-1), "MIDDLE"),
                ("ALIGN",   (-1,0), (-1,0),  "RIGHT"),
                ("ALIGN",   (-2,0), (-2,0),  "CENTER"),
                ("LEFTPADDING",  (0,0), (0,0), 0),
                ("RIGHTPADDING", (-1,0), (-1,0), 0),
                ("TOPPADDING",   (0,0), (-1,-1), 0),
                ("BOTTOMPADDING",(0,0), (-1,-1), 0),
            ]))
            return [hdr, Spacer(1, 4),
                    HRFlowable(width=IW, thickness=1.5, color=GOLD, spaceAfter=6)]

        # ══════════════════════════════════════════════════════════════════════
        # SLIDE 1 — COVER PAGE
        # ══════════════════════════════════════════════════════════════════════
        story += make_header("Precious Metals Daily Technical Report")
        story.append(Paragraph(
            "Floor Pivot Point Analysis · Support &amp; Resistance Levels · Intraday Trade Strategy",
            ST_SUBTITLE))
        story.append(Spacer(1, 10))

        co   = data['company']
        meta = data['report_metadata']

        # --- LEFT: Info cards ---
        def info_card(lbl, val, lbl_color=SLATE, val_color=WHITE):
            return Table(
                [[Paragraph(lbl, style("IL", fontName="Helvetica-Bold", fontSize=6.5,
                                       leading=8, textColor=lbl_color))],
                 [Paragraph(f"<b>{val}</b>", style("IV", fontName="Helvetica-Bold",
                                                    fontSize=9.5, leading=12, textColor=val_color))]],
                colWidths=[2.1*inch])

        card_table = Table([
            [info_card("FIRM",    co['name']),
             info_card("DATE",    meta['date']),
             info_card("GOLD SPOT", f"${data['gold']['spot']:.2f}", val_color=GOLD),
             info_card("SILVER SPOT", f"${data['silver']['spot']:.3f}", val_color=SILVER_C)],
        ], colWidths=[2.1*inch]*4)
        card_table.setStyle(TableStyle([
            ("BACKGROUND",  (0,0), (-1,-1), NAVY_CARD),
            ("BOX",         (0,0), (-1,-1), 1,   DIVIDER),
            ("INNERGRID",   (0,0), (-1,-1), 0.5, DIVIDER),
            ("PADDING",     (0,0), (-1,-1), 10),
            ("VALIGN",      (0,0), (-1,-1), "MIDDLE"),
            ("LINEABOVE",   (0,0), (-1,0), 2, GOLD),
        ]))

        # --- RIGHT: Feature image panel ---
        cover_img = Image(GOLD_IMG, width=4.5*inch, height=2.4*inch)
        tagline = Paragraph(
            "<font color='#dfb256'><b>Hold Real Value In Your Hands</b></font><br/>"
            "<font color='#94a3b8'>Pure Value. Timeless Power.</font>",
            style("Tag", fontName="Helvetica", fontSize=9, leading=14,
                  textColor=WHITE, alignment=TA_CENTER))
        subtitle_cover = Paragraph(
            f"Lanora Gold Trading LLC · Al Ras, Dubai, U.A.E. · {meta['execution_time']}",
            style("SC", fontName="Helvetica", fontSize=7.5, leading=10,
                  textColor=SLATE, alignment=TA_CENTER))

        right_panel = Table([
            [cover_img],
            [tagline],
            [subtitle_cover],
        ], colWidths=[4.6*inch])
        right_panel.setStyle(TableStyle([
            ("BACKGROUND",  (0,0), (-1,-1), NAVY_CARD),
            ("BOX",         (0,0), (-1,-1), 1, DIVIDER),
            ("LINEABOVE",   (0,0), (-1,0), 2, GOLD),
            ("ALIGN",       (0,0), (-1,-1), "CENTER"),
            ("VALIGN",      (0,0), (-1,-1), "MIDDLE"),
            ("PADDING",     (0,0), (-1,-1), 8),
        ]))

        # --- Location / Contact strip ---
        contact_strip = Table([[
            Paragraph("📍 Shop No. 18, Nasser Lootah Bldg., Gold Center, Al Ras, Dubai, U.A.E.",
                      style("CS", fontName="Helvetica", fontSize=7.5, leading=10, textColor=SLATE)),
            Paragraph("📞 04-3215916 / 0505395916",
                      style("CS2", fontName="Helvetica", fontSize=7.5, leading=10,
                             textColor=SLATE, alignment=TA_CENTER)),
            Paragraph("✉ lanoragoldtrading@gmail.com  ·  @lanoragoldtrading",
                      style("CS3", fontName="Helvetica", fontSize=7.5, leading=10,
                             textColor=SLATE, alignment=TA_RIGHT)),
        ]], colWidths=[3.5*inch, 2.5*inch, 4.3*inch])
        contact_strip.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,-1), NAVY_MID),
            ("PADDING",    (0,0), (-1,-1), 6),
            ("TOPLINE",    (0,0), (-1,-1), 1, DIVIDER),
        ]))

        slide1 = Table([[card_table, right_panel]], colWidths=[5.6*inch, 4.6*inch])
        slide1.setStyle(TableStyle([
            ("VALIGN", (0,0), (-1,-1), "TOP"),
            ("LEFTPADDING",  (1,0), (1,0), 8),
        ]))
        story.append(slide1)
        story.append(Spacer(1, 8))
        story.append(contact_strip)
        story.append(PageBreak())

        # ══════════════════════════════════════════════════════════════════════
        # SLIDE 2 — MACROECONOMIC CALENDAR
        # ══════════════════════════════════════════════════════════════════════
        story += make_header("Macroeconomic Calendar", "DUBAI TIME (GMT+4)")
        story.append(Paragraph(
            "High-impact economic releases scheduled today affecting USD volatility and precious metals pricing:",
            ST_SUBTITLE))
        story.append(Spacer(1, 8))

        # Calendar table
        cal_rows = [[
            Paragraph("TIME",   ST_TABLE_HDR),
            Paragraph("CURR.",  ST_TABLE_HDR),
            Paragraph("EVENT",  ST_TABLE_HDR),
            Paragraph("FORECAST", ST_TABLE_HDR),
            Paragraph("PREVIOUS", ST_TABLE_HDR),
        ]]
        for row in data['macro_calendar']:
            cal_rows.append([
                Paragraph(row['time'],     ST_TABLE_CELL),
                Paragraph(row['currency'], ST_TABLE_CELL),
                Paragraph(row['event'],    style("Ev", fontName="Helvetica", fontSize=8,
                                                  leading=11, textColor=WHITE, alignment=TA_LEFT)),
                Paragraph(row['forecast'], ST_TABLE_CELL),
                Paragraph(row['previous'], ST_TABLE_CELL),
            ])

        t_cal = Table(cal_rows, colWidths=[1.0*inch, 0.65*inch, 3.4*inch, 1.1*inch, 1.1*inch])
        row_bg = [NAVY_CARD, NAVY_MID]
        t_cal.setStyle(TableStyle([
            ("BACKGROUND",  (0,0), (-1,0), NAVY),
            ("LINEBELOW",   (0,0), (-1,0), 1.5, GOLD),
            ("ROWBACKGROUNDS", (0,1), (-1,-1), row_bg),
            ("GRID",        (0,0), (-1,-1), 0.3, DIVIDER),
            ("PADDING",     (0,0), (-1,-1), 7),
            ("VALIGN",      (0,0), (-1,-1), "MIDDLE"),
            ("BOX",         (0,0), (-1,-1), 1, DIVIDER),
        ]))

        # PAMP image
        pamp_img = Image(PAMP_IMG, width=3.0*inch, height=3.4*inch)
        pamp_caption = Paragraph(
            "<font color='#dfb256'><b>PAMP Suisse Fortuna</b></font><br/>"
            "<font color='#94a3b8'>Official Fine Gold Bullion 999.9</font>",
            style("PC", fontName="Helvetica", fontSize=8, leading=11,
                  textColor=WHITE, alignment=TA_CENTER))
        pamp_panel = Table([[pamp_img], [pamp_caption]], colWidths=[3.2*inch])
        pamp_panel.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,-1), NAVY_CARD),
            ("BOX",        (0,0), (-1,-1), 1, DIVIDER),
            ("ALIGN",      (0,0), (-1,-1), "CENTER"),
            ("VALIGN",     (0,0), (-1,-1), "MIDDLE"),
            ("PADDING",    (0,0), (-1,-1), 8),
            ("LINEABOVE",  (0,0), (-1,0), 2, GOLD),
        ]))

        slide2 = Table([[t_cal, pamp_panel]], colWidths=[7.1*inch, 3.1*inch])
        slide2.setStyle(TableStyle([
            ("VALIGN",       (0,0), (-1,-1), "TOP"),
            ("LEFTPADDING",  (1,0), (1,0), 10),
        ]))
        story.append(slide2)
        story.append(PageBreak())

        # ══════════════════════════════════════════════════════════════════════
        # SHARED: Pivot matrix helper
        # ══════════════════════════════════════════════════════════════════════
        def pivot_row(lbl, val, row_bg_color, highlight=False):
            lbl_style = style("PL", fontName="Helvetica-Bold", fontSize=9, leading=11,
                               textColor=GOLD if highlight else SLATE, alignment=TA_LEFT)
            val_style = style("PV", fontName="Helvetica-Bold", fontSize=9, leading=11,
                               textColor=GOLD if highlight else WHITE, alignment=TA_RIGHT)
            return [Paragraph(lbl, lbl_style), Paragraph(val, val_style)]

        def pivot_section(p, decimals=2):
            fmt = f"{{:.{decimals}f}}"
            rows = [
                [Paragraph("SUPPORT",    ST_TABLE_HDR),
                 Paragraph("RESISTANCE", ST_TABLE_HDR)],
                [Paragraph(f"S1  {fmt.format(p['S1'])}", style("s1", fontName="Helvetica-Bold",
                    fontSize=9.5, leading=12, textColor=GREEN_ACC, alignment=TA_CENTER)),
                 Paragraph(f"R1  {fmt.format(p['R1'])}", style("r1", fontName="Helvetica-Bold",
                    fontSize=9.5, leading=12, textColor=RED_ACC, alignment=TA_CENTER))],
                [Paragraph(f"S2  {fmt.format(p['S2'])}", style("s2", fontName="Helvetica",
                    fontSize=8.5, leading=11, textColor=GREEN_ACC, alignment=TA_CENTER)),
                 Paragraph(f"R2  {fmt.format(p['R2'])}", style("r2", fontName="Helvetica",
                    fontSize=8.5, leading=11, textColor=RED_ACC, alignment=TA_CENTER))],
                [Paragraph(f"S3  {fmt.format(p['S3'])}", style("s3", fontName="Helvetica",
                    fontSize=8, leading=11, textColor=colors.HexColor("#86efac"), alignment=TA_CENTER)),
                 Paragraph(f"R3  {fmt.format(p['R3'])}", style("r3", fontName="Helvetica",
                    fontSize=8, leading=11, textColor=colors.HexColor("#fca5a5"), alignment=TA_CENTER))],
            ]
            t = Table(rows, colWidths=[2.6*inch, 2.6*inch])
            t.setStyle(TableStyle([
                ("BACKGROUND",  (0,0), (-1,0), NAVY),
                ("LINEBELOW",   (0,0), (-1,0), 1.5, GOLD),
                ("BACKGROUND",  (0,1), (0,1), GREEN_BG),
                ("BACKGROUND",  (1,1), (1,1), RED_BG),
                ("BACKGROUND",  (0,2), (0,2), NAVY_CARD),
                ("BACKGROUND",  (1,2), (1,2), NAVY_CARD),
                ("BACKGROUND",  (0,3), (0,3), NAVY_MID),
                ("BACKGROUND",  (1,3), (1,3), NAVY_MID),
                ("BOX",         (0,0), (-1,-1), 1, DIVIDER),
                ("INNERGRID",   (0,0), (-1,-1), 0.3, DIVIDER),
                ("PADDING",     (0,0), (-1,-1), 8),
                ("VALIGN",      (0,0), (-1,-1), "MIDDLE"),
            ]))
            return t

        def trade_plan_table(p, decimals=2):
            fmt  = f"{{:.{decimals}f}}"
            buy  = (f"<b>▲  BUY ABOVE PIVOT  {fmt.format(p['P'])}</b><br/>"
                    f"<font color='#86efac'>Targets: {fmt.format(p['R1'])} → {fmt.format(p['R2'])}</font>   "
                    f"<font color='#fca5a5'>Stop Loss: {fmt.format(p['S1'])}</font>")
            sell = (f"<b>▼  SELL BELOW PIVOT  {fmt.format(p['P'])}</b><br/>"
                    f"<font color='#fca5a5'>Targets: {fmt.format(p['S1'])} → {fmt.format(p['S2'])}</font>   "
                    f"<font color='#86efac'>Stop Loss: {fmt.format(p['R1'])}</font>")
            def ts(name, color):
                return style(name, fontName="Helvetica", fontSize=8, leading=13,
                             textColor=color)
            t = Table([
                [Paragraph(buy,  ts("buy_t",  GREEN_ACC)),
                 Paragraph(sell, ts("sell_t", RED_ACC))],
            ], colWidths=[2.6*inch, 2.6*inch])
            t.setStyle(TableStyle([
                ("BACKGROUND", (0,0), (0,0), GREEN_BG),
                ("BACKGROUND", (1,0), (1,0), RED_BG),
                ("BOX",        (0,0), (0,0), 1, GREEN_ACC),
                ("BOX",        (1,0), (1,0), 1, RED_ACC),
                ("PADDING",    (0,0), (-1,-1), 8),
                ("VALIGN",     (0,0), (-1,-1), "MIDDLE"),
            ]))
            return t

        def pivot_badge(p_val, spot_val, decimals=2):
            fmt    = f"{{:.{decimals}f}}"
            p_str  = fmt.format(p_val)
            sp_str = fmt.format(spot_val)
            return Table([
                [Paragraph("SPOT PRICE", style("SL", fontName="Helvetica-Bold", fontSize=6.5,
                                                leading=8, textColor=SLATE, alignment=TA_CENTER)),
                 Paragraph("PIVOT POINT", style("PivL", fontName="Helvetica-Bold", fontSize=6.5,
                                                 leading=8, textColor=SLATE, alignment=TA_CENTER))],
                [Paragraph(f"<b>{sp_str}</b>",
                            style("SV", fontName="Helvetica-Bold", fontSize=16, leading=20,
                                  textColor=WHITE, alignment=TA_CENTER)),
                 Paragraph(f"<b>{p_str}</b>",
                            style("PV2", fontName="Helvetica-Bold", fontSize=16, leading=20,
                                  textColor=GOLD, alignment=TA_CENTER))],
            ], colWidths=[2.6*inch, 2.6*inch])

        def badge_style(t):
            t.setStyle(TableStyle([
                ("BACKGROUND",  (0,0), (-1,-1), NAVY_CARD),
                ("BOX",         (0,0), (-1,-1), 1, DIVIDER),
                ("INNERGRID",   (0,0), (-1,-1), 0.5, DIVIDER),
                ("LINEABOVE",   (0,0), (-1,0), 2, GOLD),
                ("LINEABOVE",   (0,1), (-1,1), 1, DIVIDER),
                ("ALIGN",       (0,0), (-1,-1), "CENTER"),
                ("PADDING",     (0,0), (-1,-1), 8),
                ("VALIGN",      (0,0), (-1,-1), "MIDDLE"),
            ]))
            return t

        # ══════════════════════════════════════════════════════════════════════
        # SLIDE 3 — SPOT GOLD TECHNICAL MATRIX
        # ══════════════════════════════════════════════════════════════════════
        story += make_header("Spot Gold (XAU/USD) — Technical Analysis")
        story.append(Paragraph(
            "Classic Floor Pivot Point Analysis · Daily Session Levels · Dubai (GMT+4)",
            ST_SUBTITLE))
        story.append(Spacer(1, 8))

        gp = data['gold']['pivots']
        g_badge = badge_style(pivot_badge(gp['P'], data['gold']['spot'], decimals=2))
        g_pivot = pivot_section(gp, decimals=2)
        g_trade = trade_plan_table(gp, decimals=2)

        left_gold = Table([
            [g_badge],
            [Spacer(1, 7)],
            [g_pivot],
            [Spacer(1, 7)],
            [g_trade],
        ], colWidths=[5.3*inch])
        left_gold.setStyle(TableStyle([
            ("VALIGN", (0,0), (-1,-1), "TOP"),
            ("PADDING",(0,0), (-1,-1), 0),
        ]))

        gold_chart_img = Image(gold_chart_path, width=4.5*inch, height=3.6*inch)
        chart_panel_g = Table([[gold_chart_img]], colWidths=[4.7*inch])
        chart_panel_g.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,-1), NAVY_CARD),
            ("BOX",        (0,0), (-1,-1), 1, DIVIDER),
            ("LINEABOVE",  (0,0), (-1,0), 2, GOLD),
            ("ALIGN",      (0,0), (-1,-1), "CENTER"),
            ("VALIGN",     (0,0), (-1,-1), "MIDDLE"),
            ("PADDING",    (0,0), (-1,-1), 6),
        ]))

        slide3 = Table([[left_gold, chart_panel_g]], colWidths=[5.4*inch, 4.8*inch])
        slide3.setStyle(TableStyle([
            ("VALIGN",      (0,0), (-1,-1), "TOP"),
            ("LEFTPADDING", (1,0), (1,0), 10),
        ]))
        story.append(slide3)
        story.append(PageBreak())

        # ══════════════════════════════════════════════════════════════════════
        # SLIDE 4 — SPOT SILVER TECHNICAL MATRIX
        # ══════════════════════════════════════════════════════════════════════
        story += make_header("Spot Silver (XAG/USD) — Technical Analysis")
        story.append(Paragraph(
            "Classic Floor Pivot Point Analysis · Daily Session Levels · Dubai (GMT+4)",
            ST_SUBTITLE))
        story.append(Spacer(1, 8))

        sp = data['silver']['pivots']
        s_badge = badge_style(pivot_badge(sp['P'], data['silver']['spot'], decimals=3))
        s_pivot = pivot_section(sp, decimals=3)
        s_trade = trade_plan_table(sp, decimals=3)

        left_silver = Table([
            [s_badge],
            [Spacer(1, 7)],
            [s_pivot],
            [Spacer(1, 7)],
            [s_trade],
        ], colWidths=[5.3*inch])
        left_silver.setStyle(TableStyle([
            ("VALIGN", (0,0), (-1,-1), "TOP"),
            ("PADDING",(0,0), (-1,-1), 0),
        ]))

        silver_chart_img = Image(silver_chart_path, width=4.5*inch, height=3.6*inch)
        chart_panel_s = Table([[silver_chart_img]], colWidths=[4.7*inch])
        chart_panel_s.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,-1), NAVY_CARD),
            ("BOX",        (0,0), (-1,-1), 1, DIVIDER),
            ("LINEABOVE",  (0,0), (-1,0), 2, SILVER_C),
            ("ALIGN",      (0,0), (-1,-1), "CENTER"),
            ("VALIGN",     (0,0), (-1,-1), "MIDDLE"),
            ("PADDING",    (0,0), (-1,-1), 6),
        ]))

        slide4 = Table([[left_silver, chart_panel_s]], colWidths=[5.4*inch, 4.8*inch])
        slide4.setStyle(TableStyle([
            ("VALIGN",      (0,0), (-1,-1), "TOP"),
            ("LEFTPADDING", (1,0), (1,0), 10),
        ]))
        story.append(slide4)
        story.append(PageBreak())

        # ══════════════════════════════════════════════════════════════════════
        # SLIDE 5 — CLOSING & TRADING DESK
        # ══════════════════════════════════════════════════════════════════════
        logo_img_lg = Image(LOGO, width=1.0*inch, height=1.0*inch)
        thank_you   = Paragraph(
            "<font color='#dfb256'><b>Thank You</b></font>",
            style("TY", fontName="Helvetica-Bold", fontSize=28, leading=32,
                  textColor=GOLD, alignment=TA_CENTER))
        tagline5 = Paragraph(
            "<b>\"Hold Real Value In Your Hands — Pure Value. Timeless Power.\"</b>",
            style("T5", fontName="Helvetica", fontSize=11, leading=16,
                  textColor=WHITE, alignment=TA_CENTER))
        sub5 = Paragraph(
            "Lanora Gold Trading LLC · Physical Bullion &amp; Precious Metals Research Desk",
            style("S5", fontName="Helvetica", fontSize=8.5, leading=12,
                  textColor=SLATE, alignment=TA_CENTER))

        hero = Table([
            [logo_img_lg],
            [Spacer(1, 8)],
            [thank_you],
            [Spacer(1, 6)],
            [tagline5],
            [Spacer(1, 4)],
            [sub5],
        ], colWidths=[IW])
        hero.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,-1), NAVY_CARD),
            ("BOX",        (0,0), (-1,-1), 1.5, GOLD),
            ("ALIGN",      (0,0), (-1,-1), "CENTER"),
            ("VALIGN",     (0,0), (-1,-1), "MIDDLE"),
            ("PADDING",    (0,0), (-1,-1), 14),
        ]))
        story.append(hero)
        story.append(Spacer(1, 10))

        # Contact Cards Row
        def ccard(icon, title, lines):
            return Table([
                [Paragraph(f"<b>{icon}  {title}</b>",
                            style("CC", fontName="Helvetica-Bold", fontSize=8, leading=10,
                                  textColor=GOLD))],
                [Paragraph("<br/>".join(lines), ST_CONTACT)],
            ], colWidths=[3.0*inch])

        c1 = ccard("📍", "Trading Desk",
                   ["Shop No. 18, Nasser Lootah Bldg.",
                    "Gold Center, Al Ras, Dubai, U.A.E."])
        c2 = ccard("📞", "Phone",
                   ["04-3215916", "0505395916"])
        c3 = ccard("✉", "Email &amp; Social",
                   ["lanoragoldtrading@gmail.com", "@lanoragoldtrading"])

        crow = Table([[c1, c2, c3]], colWidths=[3.2*inch]*3)
        crow.setStyle(TableStyle([
            ("BACKGROUND",  (0,0), (-1,-1), NAVY_CARD),
            ("BOX",         (0,0), (-1,-1), 1, DIVIDER),
            ("INNERGRID",   (0,0), (-1,-1), 0.5, DIVIDER),
            ("PADDING",     (0,0), (-1,-1), 10),
            ("ALIGN",       (0,0), (-1,-1), "CENTER"),
            ("VALIGN",      (0,0), (-1,-1), "MIDDLE"),
            ("LINEABOVE",   (0,0), (-1,0), 2, GOLD),
        ]))
        story.append(crow)
        story.append(Spacer(1, 8))

        # Disclaimer
        disc = Table([[Paragraph(
            "<b>Risk Disclaimer:</b> Trading physical bullion, precious metals, and spot "
            "contracts carries substantial market risk and is not suitable for all investors. "
            "Technical pivot levels and strategies are for informational and market research "
            "purposes only. Lanora Gold Trading LLC accepts no liability for trading decisions "
            "or losses incurred as a result of using this research.",
            ST_DISCLAIMER)]], colWidths=[IW])
        disc.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,-1), NAVY_MID),
            ("BOX",        (0,0), (-1,-1), 0.5, DIVIDER),
            ("PADDING",    (0,0), (-1,-1), 7),
        ]))
        story.append(disc)

        # ── Build ─────────────────────────────────────────────────────────────
        doc.build(story)
        print(f"PDF Successfully Generated: {output_filename}")
        return True

    except Exception as e:
        import traceback
        print(f"PDF Generation Error: {e}")
        traceback.print_exc()
        return False


if __name__ == "__main__":
    out_file = sys.argv[1] if len(sys.argv) > 1 else "Lanora_Gold_Daily_Technical_Report.pdf"
    generate_pdf_report(out_file)
