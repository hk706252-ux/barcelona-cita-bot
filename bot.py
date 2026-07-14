import os
import requests

# GitHub secrets / values
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "8764819127:AAGtHY9HMyfoLDou9aQbz9APehGBd9ytTTo")
CHAT_ID = os.getenv("CHAT_ID", "8246088794")

# Testing ke liye "Badajoz" set hai. Jab test ho jaye toh ise wapas "Barcelona" kar lijiyega.
PROVINCE_NAME = "Badajoz" 
TRAMITE_NAME = "POLICIA-TOMA DE HUELLAS (EXPEDICIÓN DE TARJETA) INICIAL, RENOVACIÓN, DUPLICADO Y LEY 14/2013"

def send_telegram_alert(province, office_name):
    telegram_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    message_text = (
        "🚨 !!! APPOINTMENT SLOT FOUND !!! 🚨\n\n"
        f"📍 *Province:* {province}\n"
        f"💼 *Tramite:* {TRAMITE_NAME[:40]}...\n"
        f"🏢 *Office:* {office_name}\n\n"
        "🔗 *Book Here:* https://icp.administracionelectronica.gob.es/icpplus/index.html"
    )
    payload = {"chat_id": CHAT_ID, "text": message_text, "parse_mode": "Markdown"}
    try:
        requests.post(telegram_url, json=payload)
        print(f"🚀 Telegram Alert Sent for {office_name}!")
    except Exception as e:
        print(f"Telegram Error: {e}")

def check_cita():
    print(f"🔄 Checking Cita Previa for {PROVINCE_NAME}...")
    
    # Government site URL to simulate form posting
    post_url = "https://icp.administracionelectronica.gob.es/icpplus/citar"
    
    # Headers to look like a real browser request
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://icp.administracionelectronica.gob.es/icpplus/index.html",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    # Step 1: Submit province selection
    # Province IDs: Badajoz is typically "06", Barcelona is "08"
    province_id = "06" if PROVINCE_NAME == "Badajoz" else "08"
    
    payload = {
        "conFormat": "true",
        "provincia": province_id,
        "btnAceptar": "Aceptar"
    }
    
    session = requests.Session()
    try:
        # Connect first to establish cookies
        session.get("https://icp.administracionelectronica.gob.es/icpplus/index.html", headers=headers, timeout=15)
        
        # Submit the province form
        response = session.post(post_url, data=payload, headers=headers, timeout=15)
        
        if "No hay citas disponibles" in response.text or "En este momento no hay citas" in response.text:
            print("❌ No slots available at the moment.")
        else:
            # If the output doesn't contain the "No appointments" text, it means slots might be open!
            print("🎉 SLOTS MIGHT BE AVAILABLE! Sending notification...")
            send_telegram_alert(PROVINCE_NAME, "Oficina Principal / Sede")
            
    except Exception as e:
        print(f"❌ Connection/Request Error: {e}")

if __name__ == "__main__":
    check_cita()
