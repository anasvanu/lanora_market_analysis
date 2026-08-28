#!/usr/bin/env python3
"""
Lanora Gold Trading LLC — Automated Morning Scheduler
Runs every morning at 08:00 AM GST (GMT+4). Checks if market is open (Mon-Fri),
fetches live spot data, generates 5-page PDF presentation report, and dispatches via Email & WhatsApp.
"""

import sys
import os
import time
import json
from datetime import datetime, timezone, timedelta
from market_engine import get_market_data, is_market_open
from pdf_exporter import generate_pdf_report
from dispatch_engine import send_email_report, send_whatsapp_report

def run_daily_workflow():
    gst_now = datetime.now(timezone(timedelta(hours=4)))
    print(f"==================================================")
    print(f"LANORA GOLD TRADING — MORNING AUTOMATION RUN")
    print(f"Timestamp (GST): {gst_now.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    print(f"==================================================")

    # Market Open Check (Mon - Fri)
    if not is_market_open(gst_now):
        print("ℹ️ Market Status: CLOSED (Weekend). Skipping daily report generation & dispatch.")
        return {
            "status": "SKIPPED_MARKET_CLOSED",
            "reason": "Precious metals spot markets closed on weekends.",
            "timestamp": gst_now.isoformat()
        }

    print("✅ Market Status: OPEN. Initiating daily technical workflow...")

    # Step 1: Gather Market Data
    data = get_market_data()
    date_str = data['report_metadata']['date']
    pdf_filename = f"Lanora_Gold_Daily_Technical_Report_{gst_now.strftime('%Y%m%d')}.pdf"

    # Step 2: Generate PDF Presentation Report
    print(f"📊 Step 1/3: Compiling 5-Page PDF Deck ({pdf_filename})...")
    generate_pdf_report(pdf_filename)

    # Step 3: Multi-Channel Dispatch
    print("✉️ Step 2/3: Dispatching Email Report to anasvanu@gmail.com...")
    email_status = send_email_report(pdf_filename, "anasvanu@gmail.com")

    print("📱 Step 3/3: Dispatching WhatsApp Summary & PDF to 7012926066...")
    wa_status = send_whatsapp_report(pdf_filename, "7012926066")

    print("\n🎉 Daily Workflow Execution Successfully Completed!")
    return {
        "status": "COMPLETED_SUCCESS",
        "pdf_report": pdf_filename,
        "email": email_status,
        "whatsapp": wa_status,
        "timestamp": gst_now.isoformat()
    }

if __name__ == "__main__":
    res = run_daily_workflow()
    print(json.dumps(res, indent=2))
