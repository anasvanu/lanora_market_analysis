#!/usr/bin/env python3
"""
Lanora Gold Trading LLC — Production Web Application & AI Studio Server
Serves the interactive web UI, handles on-demand PDF generation, live PDF streaming,
multi-recipient email dispatch, and processes natural language AI commands to alter the deck/PDF in real-time.
"""

import sys
import os
import re
import json
import mimetypes
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from datetime import datetime, timezone, timedelta

# Import domain modules
from market_engine import get_market_data, calculate_pivot_points, is_market_open
from pdf_exporter import generate_pdf_report
from dispatch_engine import send_email_report, send_whatsapp_report

PORT = int(os.getenv("PORT", 8080))
PDF_FILENAME = "Lanora_Gold_Daily_Technical_Report.pdf"

# In-Memory Active Report State
ACTIVE_STATE = None

def get_active_state():
    global ACTIVE_STATE
    if ACTIVE_STATE is None:
        ACTIVE_STATE = get_market_data()
    return ACTIVE_STATE

def recalculate_gold_levels(state):
    g = state['gold']
    pivots = calculate_pivot_points(g['high'], g['low'], g['close'], decimals=2)
    g['pivots'] = pivots
    g['trade_plan']['buy']['trigger'] = f"Buy Above {pivots['P']:.2f}"
    g['trade_plan']['buy']['target1'] = f"{pivots['R1']:.2f}"
    g['trade_plan']['buy']['target2'] = f"{pivots['R2']:.2f}"
    g['trade_plan']['buy']['stop_loss'] = f"{pivots['S1']:.2f}"
    
    g['trade_plan']['sell']['trigger'] = f"Sell Below {pivots['P']:.2f}"
    g['trade_plan']['sell']['target1'] = f"{pivots['S1']:.2f}"
    g['trade_plan']['sell']['target2'] = f"{pivots['S2']:.2f}"
    g['trade_plan']['sell']['stop_loss'] = f"{pivots['R1']:.2f}"

def recalculate_silver_levels(state):
    s = state['silver']
    pivots = calculate_pivot_points(s['high'], s['low'], s['close'], decimals=3)
    s['pivots'] = pivots
    s['trade_plan']['buy']['trigger'] = f"Buy Above {pivots['P']:.3f}"
    s['trade_plan']['buy']['target1'] = f"{pivots['R1']:.3f}"
    s['trade_plan']['buy']['target2'] = f"{pivots['R2']:.3f}"
    s['trade_plan']['buy']['stop_loss'] = f"{pivots['S1']:.3f}"
    
    s['trade_plan']['sell']['trigger'] = f"Sell Below {pivots['P']:.3f}"
    s['trade_plan']['sell']['target1'] = f"{pivots['S1']:.3f}"
    s['trade_plan']['sell']['target2'] = f"{pivots['S2']:.3f}"
    s['trade_plan']['sell']['stop_loss'] = f"{pivots['R1']:.3f}"

def process_ai_command(prompt: str) -> dict:
    """
    Intelligent NLP Command Engine that parses natural language instructions
    and alters the market report data model and PDF presentation in real time.
    """
    state = get_active_state()
    p_lower = prompt.lower().strip()
    changes = []

    # 1. Reset Command
    if "reset" in p_lower or "fetch live" in p_lower or "reload live" in p_lower:
        global ACTIVE_STATE
        ACTIVE_STATE = get_market_data()
        state = ACTIVE_STATE
        generate_pdf_report(PDF_FILENAME, state)
        return {
            "success": True,
            "message": "🔄 Reset all data to live real-time spot market quotes and regenerated the PDF report.",
            "data": state
        }

    # 2. Gold Spot Price Modification
    gold_spot_match = re.search(r'(?:gold|xau).*?(?:spot|price|to|is|=)\s*[:\$]?\s*([0-9]+(?:\.[0-9]+)?)', p_lower)
    if not gold_spot_match and ("gold" in p_lower and any(w in p_lower for w in ["set", "change", "make", "update"])):
        gold_spot_match = re.search(r'([0-9]{4}(?:\.[0-9]+)?)', p_lower)

    if gold_spot_match:
        val = float(gold_spot_match.group(1))
        state['gold']['spot'] = val
        changes.append(f"• Updated Spot Gold reference to **${val:.2f}**")

    # 3. Silver Spot Price Modification
    silver_spot_match = re.search(r'(?:silver|xag).*?(?:spot|price|to|is|=)\s*[:\$]?\s*([0-9]+(?:\.[0-9]+)?)', p_lower)
    if not silver_spot_match and ("silver" in p_lower and any(w in p_lower for w in ["set", "change", "make", "update"])):
        silver_spot_match = re.search(r'([0-9]{2}(?:\.[0-9]+)?)', p_lower)

    if silver_spot_match:
        val = float(silver_spot_match.group(1))
        state['silver']['spot'] = val
        changes.append(f"• Updated Spot Silver reference to **${val:.3f}**")

    # 4. Gold Session High / Low / Close
    gh_match = re.search(r'gold.*?(?:high|h)\s*[:=]?\s*([0-9]+(?:\.[0-9]+)?)', p_lower)
    if gh_match:
        val = float(gh_match.group(1))
        state['gold']['high'] = val
        changes.append(f"• Set Gold Session High to **${val:.2f}**")
        
    gl_match = re.search(r'gold.*?(?:low|l)\s*[:=]?\s*([0-9]+(?:\.[0-9]+)?)', p_lower)
    if gl_match:
        val = float(gl_match.group(1))
        state['gold']['low'] = val
        changes.append(f"• Set Gold Session Low to **${val:.2f}**")

    gc_match = re.search(r'gold.*?(?:close|c)\s*[:=]?\s*([0-9]+(?:\.[0-9]+)?)', p_lower)
    if gc_match:
        val = float(gc_match.group(1))
        state['gold']['close'] = val
        changes.append(f"• Set Gold Session Close to **${val:.2f}**")

    # 5. Direct Pivot Override
    gpiv_match = re.search(r'(?:gold|xau).*?(?:pivot|p)\s*[:=]?\s*([0-9]+(?:\.[0-9]+)?)', p_lower)
    if gpiv_match and "silver" not in p_lower:
        val = float(gpiv_match.group(1))
        # Custom pivot point set manually
        state['gold']['pivots']['P'] = val
        # Recalculate derived S/R from high/low if available
        h = state['gold']['high']
        l = state['gold']['low']
        state['gold']['pivots']['R1'] = round((2.0 * val) - l, 2)
        state['gold']['pivots']['S1'] = round((2.0 * val) - h, 2)
        state['gold']['pivots']['R2'] = round(val + (h - l), 2)
        state['gold']['pivots']['S2'] = round(val - (h - l), 2)
        state['gold']['pivots']['R3'] = round(h + 2.0 * (val - l), 2)
        state['gold']['pivots']['S3'] = round(l - 2.0 * (h - val), 2)
        state['gold']['trade_plan']['buy']['trigger'] = f"Buy Above {val:.2f}"
        state['gold']['trade_plan']['sell']['trigger'] = f"Sell Below {val:.2f}"
        changes.append(f"• Set Custom Gold Central Pivot to **${val:.2f}** and recalculated Support/Resistance matrix")

    # 6. Silver Direct Pivot Override
    spiv_match = re.search(r'(?:silver|xag).*?(?:pivot|p)\s*[:=]?\s*([0-9]+(?:\.[0-9]+)?)', p_lower)
    if spiv_match:
        val = float(spiv_match.group(1))
        state['silver']['pivots']['P'] = val
        h = state['silver']['high']
        l = state['silver']['low']
        state['silver']['pivots']['R1'] = round((2.0 * val) - l, 3)
        state['silver']['pivots']['S1'] = round((2.0 * val) - h, 3)
        state['silver']['pivots']['R2'] = round(val + (h - l), 3)
        state['silver']['pivots']['S2'] = round(val - (h - l), 3)
        state['silver']['pivots']['R3'] = round(h + 2.0 * (val - l), 3)
        state['silver']['pivots']['S3'] = round(l - 2.0 * (h - val), 3)
        state['silver']['trade_plan']['buy']['trigger'] = f"Buy Above {val:.3f}"
        state['silver']['trade_plan']['sell']['trigger'] = f"Sell Below {val:.3f}"
        changes.append(f"• Set Custom Silver Central Pivot to **${val:.3f}** and recalculated Support/Resistance matrix")

    # Recalculate if high/low/close changed but not direct pivot
    if (gh_match or gl_match or gc_match) and not gpiv_match:
        recalculate_gold_levels(state)
        changes.append(f"• Recalculated Gold Pivot Levels (P: ${state['gold']['pivots']['P']:.2f})")

    # 7. Add Economic News Event
    if "add" in p_lower and any(w in p_lower for w in ["event", "news", "calendar", "release", "cpi", "pmi", "gdp", "fomc", "nfp", "payroll"]):
        time_match = re.search(r'([0-9]{1,2}:[0-9]{2}\s*(?:am|pm)?)', prompt, re.IGNORECASE)
        event_time = time_match.group(1).upper() if time_match else "4:30 PM"
        
        curr_match = re.search(r'\b(USD|CAD|EUR|GBP|AED|JPY)\b', prompt, re.IGNORECASE)
        curr = curr_match.group(1).upper() if curr_match else "USD"
        
        # Extract title
        clean_text = prompt
        for remove_word in ["add", "event", "calendar", "news", "at", event_time, curr, "forecast", "previous"]:
            clean_text = re.sub(re.escape(remove_word), "", clean_text, flags=re.IGNORECASE)
        event_title = clean_text.strip(": -.,") or "Key Economic Indicator"
        
        fc_match = re.search(r'forecast\s*[:=]?\s*([0-9]+(?:\.[0-9]+)?%?|[a-zA-Z0-9\.\-]+)', p_lower)
        fc = fc_match.group(1) if fc_match else "0.20%"
        
        prev_match = re.search(r'previous\s*[:=]?\s*([0-9]+(?:\.[0-9]+)?%?|[a-zA-Z0-9\.\-]+)', p_lower)
        prev = prev_match.group(1) if prev_match else "0.20%"

        new_event = {
            "time": event_time,
            "currency": curr,
            "event": event_title.title(),
            "forecast": fc,
            "previous": prev,
            "impact": "High"
        }
        state['macro_calendar'].insert(0, new_event)
        changes.append(f"• Added Economic Event: **{new_event['event']}** ({new_event['currency']} at {new_event['time']})")

    # 8. Delete / Remove Event
    if any(w in p_lower for w in ["delete", "remove", "clear event"]) and "calendar" not in p_lower:
        matched = False
        for i, ev in enumerate(state['macro_calendar']):
            if any(token in ev['event'].lower() for token in p_lower.split() if len(token) > 3):
                removed = state['macro_calendar'].pop(i)
                changes.append(f"• Removed Economic Event: **{removed['event']}**")
                matched = True
                break
        if not matched and "all" in p_lower:
            state['macro_calendar'] = []
            changes.append("• Cleared all economic calendar events.")

    # 9. Update Company Phone / Email / Desk Info
    phone_match = re.search(r'phone.*?(?:to|is|=)?\s*([0-9\+\s\-]{7,20})', p_lower)
    if phone_match:
        p_val = phone_match.group(1).strip()
        state['company']['phone'] = p_val
        changes.append(f"• Updated trading desk phone to **{p_val}**")

    email_match = re.search(r'email.*?(?:to|is|=)?\s*([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)', prompt)
    if email_match:
        e_val = email_match.group(1).strip()
        state['company']['email'] = e_val
        changes.append(f"• Updated official contact email to **{e_val}**")

    # 10. Title / Report Date
    title_match = re.search(r'title.*?(?:to|is|=)\s*["\']?([^"\']+)["\']?', prompt, re.IGNORECASE)
    if title_match and len(title_match.group(1).strip()) > 3:
        t_val = title_match.group(1).strip()
        state['report_metadata']['title'] = t_val
        changes.append(f"• Updated Report Title to **{t_val}**")

    date_match = re.search(r'date.*?(?:to|is|=)\s*["\']?([a-zA-Z0-9\s,]+)["\']?', prompt, re.IGNORECASE)
    if date_match and len(date_match.group(1).strip()) > 5:
        d_val = date_match.group(1).strip()
        state['report_metadata']['date'] = d_val
        changes.append(f"• Updated Report Date to **{d_val}**")

    # 11. Bullish / Bearish Trade Strategy Tweaks
    if "bullish" in p_lower or "buy target" in p_lower:
        tgt_match = re.search(r'(?:target|tgt)\s*[:=]?\s*([0-9]+(?:\.[0-9]+)?)', p_lower)
        if tgt_match:
            tgt = float(tgt_match.group(1))
            state['gold']['trade_plan']['buy']['target2'] = f"{tgt:.2f}"
            changes.append(f"• Set Extended Bullish Target 2 for Gold to **${tgt:.2f}**")

    # Re-generate PDF with modified state
    generate_pdf_report(PDF_FILENAME, state)

    if not changes:
        return {
            "success": True,
            "message": f"💡 Interpreted command: *\"{prompt}\"*. Refreshed and rebuilt the PDF report.",
            "data": state
        }

    return {
        "success": True,
        "message": "✨ **AI Modifications Applied Successfully:**\n" + "\n".join(changes) + "\n\n📄 *Rebuilt charts and 5-page PDF preview in real-time.*",
        "data": state
    }


class LanoraAppHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        # Disable browser caching for dynamic PDF and API responses
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        # 1. API: Get Current Market Data State
        if path == "/api/data":
            state = get_active_state()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
            self.end_headers()
            self.wfile.write(json.dumps(state).encode("utf-8"))
            return

        # 2. API: Stream PDF File for Direct Browser Preview
        if path == "/api/pdf" or path == "/download-pdf":
            if not os.path.exists(PDF_FILENAME):
                generate_pdf_report(PDF_FILENAME, get_active_state())
            try:
                with open(PDF_FILENAME, "rb") as f:
                    pdf_bytes = f.read()
                self.send_response(200)
                self.send_header("Content-Type", "application/pdf")
                if "download" in path:
                    self.send_header("Content-Disposition", f'attachment; filename="{PDF_FILENAME}"')
                else:
                    self.send_header("Content-Disposition", f'inline; filename="{PDF_FILENAME}"')
                self.send_header("Content-Length", str(len(pdf_bytes)))
                self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
                self.end_headers()
                self.wfile.write(pdf_bytes)
                return
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
                return

        # Default: Static files (index.html, styles.css, app.js, assets/...)
        return super().do_GET()

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path
        content_length = int(self.headers.get('Content-Length', 0))
        post_body = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else "{}"
        
        try:
            payload = json.loads(post_body) if post_body else {}
        except Exception:
            payload = {}

        # 1. API: Generate / Rebuild PDF
        if path == "/api/generate-pdf":
            state = get_active_state()
            success = generate_pdf_report(PDF_FILENAME, state)
            self.send_response(200 if success else 500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({
                "success": success,
                "filename": PDF_FILENAME,
                "timestamp": datetime.now(timezone(timedelta(hours=4))).strftime("%I:%M:%S %p GST")
            }).encode("utf-8"))
            return

        # 2. API: Reset Data to Live Spot
        if path == "/api/reset-data":
            global ACTIVE_STATE
            ACTIVE_STATE = get_market_data()
            generate_pdf_report(PDF_FILENAME, ACTIVE_STATE)
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({
                "success": True,
                "message": "Reset to live market data successfully",
                "data": ACTIVE_STATE
            }).encode("utf-8"))
            return

        # 3. API: AI Command Studio
        if path == "/api/ai-command":
            prompt = payload.get("prompt", "").strip()
            if not prompt:
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Empty prompt provided."}).encode("utf-8"))
                return

            result = process_ai_command(prompt)
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(result).encode("utf-8"))
            return

        # 4. API: Dispatch Email Report to custom recipient(s)
        if path == "/api/dispatch-email":
            recipients = payload.get("recipients", "")
            if not recipients:
                recipients = "anasvanu@gmail.com"

            state = get_active_state()
            if not os.path.exists(PDF_FILENAME):
                generate_pdf_report(PDF_FILENAME, state)

            res = send_email_report(PDF_FILENAME, to_email=recipients, data=state)
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(res).encode("utf-8"))
            return

        # 5. API: Dispatch WhatsApp Summary
        if path == "/api/dispatch-whatsapp":
            phone = payload.get("phone", "7012926066")
            state = get_active_state()
            if not os.path.exists(PDF_FILENAME):
                generate_pdf_report(PDF_FILENAME, state)

            res = send_whatsapp_report(PDF_FILENAME, phone=phone, data=state)
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(res).encode("utf-8"))
            return

        self.send_response(404)
        self.end_headers()


def run_server():
    # Pre-generate initial PDF report on startup
    state = get_active_state()
    generate_pdf_report(PDF_FILENAME, state)

    server = HTTPServer(("0.0.0.0", PORT), LanoraAppHandler)
    print(f"==================================================")
    print(f"🏆 LANORA GOLD WEB APP & AI STUDIO RUNNING")
    print(f"🚀 Server Address: http://localhost:{PORT}")
    print(f"📄 PDF Stream Endpoint: http://localhost:{PORT}/api/pdf")
    print(f"==================================================")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server...")
        server.server_close()

if __name__ == "__main__":
    run_server()
