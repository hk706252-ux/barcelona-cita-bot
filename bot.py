import os
import requests

# GitHub secrets / values
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "8764819127:AAGtHY9HMyfoLDou9aQbz9APehGBd9ytTTo")
CHAT_ID = os.getenv("CHAT_ID", "8246088794")

# Testing ke liye "Badajoz" set hai. 
PROVINCE_NAME = "Badajoz" 
TRAMITE_NAME = "POLICIA-TOMA DE HUELLAS (EXPEDICIÓN DE TARJETA) INICIAL, RENOVACIÓN, DUPLICADO Y LEY 14/2013"

def send_telegram_alert(province, office_name):
    telegram_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    message_text = (
        "🚨 !!! APPOINTMENT SLOT FOUND !!! 🚨\n\n"
        f"📍 *Province:* {province}\n"
        f"🏢 *Office:* {office_name}\n\n"
        "🔗 *Book Here:* https://icp.administracionelectronica.gob.es/icpplus/index.html"
    )
    payload = {"chat_id": CHAT_ID, "text": message_text, "parse_mode": "Markdown"}
    try:
        requests.post(telegram_url, json=payload)
        print(f"🚀 Telegram Alert Sent!")
    except Exception as e:
        print(f"Telegram Error: {e}")

def check_cita():
    print(f"🔄 Connecting to Spain Govt Portal for {PROVINCE_NAME}...")
    
    url = "https://icp.administracionelectronica.gob.es/icpplus/index.html"
    
    # Advanced headers to bypass GitHub Cloud IP detection
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }
    
    try:
        # Hum connection time out badha kar 30 seconds kar rahe hain aur redirects allow kar rahe hain
        response = requests.get(url, headers=headers, timeout=30, allow_redirects=True)
        
        print(f"📡 Response Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Successfully connected to Spain Govt Site!")
            # Agar connection chal gaya, toh hum check karte hain
            if "No hay citas disponibles" in response.text or "En este momento no hay citas" in response.text:
                print("❌ No slots available right now.")
            else:
                print("🎉 Slots might be open! Testing notification...")
                send_telegram_alert(PROVINCE_NAME, "Oficina Badajoz")
        else:
            print(f"⚠️ Government server returned status: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Connection failed. Let's try alternative connection...")
        # Alternet link check
        try:
            alt_response = requests.get("https://api.telegram.org", timeout=10)
            print(f"🌐 Internet status: Telegram API is reachable ({alt_response.status_code})")
        except:
            print("🌐 Internet status: Github runner has no internet.")
        print(f"Error Details: {e}")

if __name__ == "__main__":
    check_cita()
