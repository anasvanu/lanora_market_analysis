#!/usr/bin/env python3
"""
Lanora Gold Trading LLC — Production Multi-Channel Dispatch Engine
Supports SMTP Email sending and WhatsApp API / Webhook delivery with GitHub Secrets support.
Compatible with Green API, UltraMsg, Twilio, and custom webhooks.
"""

import sys
import os
import json
import smtplib
import urllib.request
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from market_engine import get_market_data

DEFAULT_EMAIL = os.getenv("RECIPIENT_EMAIL", "anasvanu@gmail.com")
DEFAULT_WHATSAPP = os.getenv("WHATSAPP_PHONE", "7012926066")

def build_whatsapp_summary_text(data: dict) -> str:
    gold = data['gold']
    silver = data['silver']
    date_str = data['report_metadata']['date']
    
    return (
        f"🏆 *LANORA GOLD TRADING LLC — DAILY TECHNICAL REPORT*\n"
        f"📅 Date: {date_str} | 🕗 08:00 AM GST (Dubai)\n\n"
        f"📊 *SPOT GOLD (XAU/USD)*\n"
        f"• Current Spot: ${gold['spot']:.2f}\n"
        f"• Central Pivot (P): ${gold['pivots']['P']:.2f}\n"
        f"• Support 1 (S1): ${gold['pivots']['S1']:.2f} | Resistance 1 (R1): ${gold['pivots']['R1']:.2f}\n"
        f"• 📈 {gold['trade_plan']['buy']['trigger']} (Targets: {gold['trade_plan']['buy']['target1']} | {gold['trade_plan']['buy']['target2']})\n"
        f"• 📉 {gold['trade_plan']['sell']['trigger']} (Targets: {gold['trade_plan']['sell']['target1']} | {gold['trade_plan']['sell']['target2']})\n\n"
        f"⚪ *SPOT SILVER (XAG/USD)*\n"
        f"• Current Spot: ${silver['spot']:.3f}\n"
        f"• Central Pivot (P): ${silver['pivots']['P']:.3f}\n"
        f"• Support 1 (S1): ${silver['pivots']['S1']:.3f} | Resistance 1 (R1): ${silver['pivots']['R1']:.3f}\n\n"
        f"📌 *Official Contact Desk*\n"
        f"📍 Shop No. 18, Nasser Lootah Bldg., Al Ras, Dubai\n"
        f"📞 04-3215916 / 0505395916 | ✉️ {data['company']['email']}"
    )

def send_email_report(pdf_filepath: str, to_email: str = DEFAULT_EMAIL, data: dict = None):
    if data is None:
        data = get_market_data()
    date_str = data['report_metadata']['date']
    subject = f"Lanora Gold Trading - Daily Technical Report [{date_str}]"

    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASSWORD")

    gold_spot = f"${data['gold']['spot']:.2f}"
    gold_pivot = f"${data['gold']['pivots']['P']:.2f}"
    silver_spot = f"${data['silver']['spot']:.3f}"
    silver_pivot = f"${data['silver']['pivots']['P']:.3f}"

    body_html = f"""
    <html>
      <body style="font-family: 'Trebuchet MS', sans-serif; color: #0b1930; background-color: #f5f8fc; padding: 20px;">
        <div style="max-width: 600px; margin: 0 auto; background: #ffffff; border-radius: 12px; overflow: hidden; border: 1px solid #e2e8f0; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
          <div style="background: #0b1930; padding: 20px; text-align: center; color: #ffffff;">
            <h1 style="color: #dfb256; margin: 0; font-size: 24px;">LANORA GOLD TRADING LLC</h1>
            <p style="margin-top: 6px; font-size: 14px; color: #cbd5e1;">Daily Technical Market Intelligence Report</p>
          </div>
          <div style="padding: 24px;">
            <p style="font-size: 15px;">Dear Valued Client,</p>
            <p style="font-size: 14px; color: #475569;">Please find attached the official Daily Technical Report for <strong>{date_str}</strong> (Dubai Time GMT+4).</p>

            <div style="background: #fef9e7; border: 1px solid #dfb256; border-radius: 8px; padding: 16px; margin: 20px 0;">
              <h3 style="color: #b8860b; margin-top: 0;">Market Highlights</h3>
              <p style="margin: 4px 0;">• <strong>Spot Gold (XAU/USD):</strong> Current: {gold_spot} | Pivot: {gold_pivot}</p>
              <p style="margin: 4px 0;">• <strong>Spot Silver (XAG/USD):</strong> Current: {silver_spot} | Pivot: {silver_pivot}</p>
            </div>

            <p style="font-size: 13px; color: #64748b;">The complete 5-slide technical presentation deck is attached as a PDF document.</p>
          </div>
          <div style="background: #edf2f7; padding: 16px; font-size: 12px; color: #64748b; text-align: center; border-top: 1px solid #e2e8f0;">
            <p style="margin: 0;"><strong>Lanora Gold Trading LLC</strong> — Shop No. 18, Nasser Lootah Bldg., Al Ras, Dubai, U.A.E.</p>
            <p style="margin: 4px 0 0 0;">Tel: 04-3215916 / 0505395916 | Email: {data['company']['email']}</p>
          </div>
        </div>
      </body>
    </html>
    """

    # Parse recipients list
    if isinstance(to_email, list):
        recipients = [e.strip() for e in to_email if e and e.strip()]
    elif isinstance(to_email, str):
        recipients = [e.strip() for e in to_email.replace(";", ",").split(",") if e.strip()]
    else:
        recipients = [DEFAULT_EMAIL]

    if not recipients:
        recipients = [DEFAULT_EMAIL]

    print(f"📧 [EMAIL DISPATCH] Recipients: {', '.join(recipients)}")
    print(f"   Subject: {subject}")

    if smtp_user and smtp_pass:
        try:
            msg = MIMEMultipart()
            msg['From'] = smtp_user
            msg['To'] = ", ".join(recipients)
            msg['Subject'] = subject
            msg.attach(MIMEText(body_html, 'html'))

            if os.path.exists(pdf_filepath):
                with open(pdf_filepath, 'rb') as f:
                    part = MIMEApplication(f.read(), Name=os.path.basename(pdf_filepath))
                    part['Content-Disposition'] = f'attachment; filename="{os.path.basename(pdf_filepath)}"'
                    msg.attach(part)

            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.sendmail(smtp_user, recipients, msg.as_string())
            server.quit()
            print(f"✅ Email successfully sent via SMTP to {len(recipients)} recipient(s)!")
            return {"status": "SENT_SMTP_SUCCESS", "recipients": recipients, "count": len(recipients)}
        except Exception as e:
            print(f"⚠️ SMTP Error: {e}. Falling back to simulated log dispatch.")
            return {"status": "ERROR_SMTP", "error": str(e), "recipients": recipients}

    return {
        "status": "SENT_SIMULATED",
        "recipients": recipients,
        "subject": subject,
        "attachment": pdf_filepath,
        "note": "SMTP credentials not provided in environment. Logged simulated dispatch."
    }

def send_whatsapp_report(pdf_filepath: str, phone: str = DEFAULT_WHATSAPP, data: dict = None):
    if data is None:
        data = get_market_data()
    summary_text = build_whatsapp_summary_text(data)
    webhook_url = os.getenv("WHATSAPP_WEBHOOK_URL")

    # Clean phone number (strip + and spaces)
    clean_phone = "".join([c for c in phone if c.isdigit()])
    if len(clean_phone) == 10 and not clean_phone.startswith("91") and not clean_phone.startswith("971"):
        # Default to UAE 971 or India 91 prefix if needed
        clean_phone = "91" + clean_phone if phone.startswith("70") or phone.startswith("9") else "971" + clean_phone

    print(f"📱 [WHATSAPP DISPATCH] Target Phone: {clean_phone}")

    if webhook_url:
        try:
            # Format request depending on API provider
            if "green-api.com" in webhook_url or "greenapi.com" in webhook_url:
                payload = {
                    "chatId": f"{clean_phone}@c.us",
                    "message": summary_text
                }
            elif "ultramsg.com" in webhook_url:
                payload = {
                    "to": clean_phone,
                    "body": summary_text
                }
            else:
                payload = {
                    "to": clean_phone,
                    "message": summary_text,
                    "attachment": os.path.basename(pdf_filepath)
                }

            req_data = json.dumps(payload).encode('utf-8')
            req = urllib.request.Request(
                webhook_url,
                data=req_data,
                headers={'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'}
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                print(f"✅ WhatsApp API message sent successfully (HTTP {resp.status})!")
                return {"status": "SENT_WEBHOOK_SUCCESS", "phone": clean_phone}
        except Exception as e:
            print(f"⚠️ WhatsApp Webhook Error: {e}. Falling back to simulated log dispatch.")

    print(f"ℹ️ Simulated WhatsApp Summary Message:\n{summary_text}")
    return {"status": "SENT_SIMULATED", "phone": clean_phone, "message": summary_text}

if __name__ == "__main__":
    pdf_file = sys.argv[1] if len(sys.argv) > 1 else "Lanora_Gold_Daily_Technical_Report.pdf"
    if not os.path.exists(pdf_file):
        from pdf_exporter import generate_pdf_report
        generate_pdf_report(pdf_file)

    send_email_report(pdf_file)
    send_whatsapp_report(pdf_file)
