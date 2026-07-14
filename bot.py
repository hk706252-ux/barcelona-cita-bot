import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# GitHub secrets / values
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "8764819127:AAGtHY9HMyfoLDou9aQbz9APehGBd9ytTTo")
CHAT_ID = os.getenv("CHAT_ID", "8246088794")
URL = "https://icp.administracionelectronica.gob.es/icpplus/index.html"

PROVINCES_TO_CHECK = ["Barcelona"]
TRAMITES_TO_CHECK = [
    "POLICIA-TOMA DE HUELLAS (EXPEDICIÓN DE TARJETA) INICIAL, RENOVACIÓN, DUPLICADO Y LEY 14/2013"
]

def send_telegram_professional(province, tramite, office_name):
    telegram_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    message_text = (
        "🚨 !!! APPOINTMENT SLOT FOUND !!! 🚨\n\n"
        f"📍 *Province:* {province}\n"
        f"💼 *Tramite:* {tramite}\n"
        f"🏢 *Office:* {office_name}\n\n"
        "🔗 *Book Here:* https://icp.administracionelectronica.gob.es/icpplus/index.html"
    )
    payload = {"chat_id": CHAT_ID, "text": message_text, "parse_mode": "Markdown"}
    try:
        requests.post(telegram_url, json=payload)
        print(f"🚀 Alert sent for {office_name}!")
    except Exception as e:
        print(f"Telegram Error: {e}")

def check_cita_previa():
    options = webdriver.ChromeOptions()
    # GitHub Actions ke liye stable headless settings
    options.add_argument("--headless=new")  
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-extensions")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    wait = WebDriverWait(driver, 20)
    
    try:
        for province in PROVINCES_TO_CHECK:
            print(f"🔄 Connecting to site for {province}...")
            driver.get(URL)
            wait.until(EC.presence_of_element_located((By.NAME, "provincia")))
            time.sleep(2)
            
            Select(driver.find_element(By.NAME, "provincia")).select_by_visible_text(province)
            driver.find_element(By.ID, "btnAceptar").click()
            time.sleep(3)

            office_elements = driver.find_elements(By.NAME, "sede")
            if not office_elements:
                run_tramites(driver, province, "Cualquier Oficina")
            else:
                office_select = Select(office_elements[0])
                offices = [opt.text.strip() for opt in office_select.options if opt.text.strip() and "Seleccione" not in opt.text]
                
                for office in offices:
                    try:
                        print(f"🏢 Checking: {office[:30]}...")
                        Select(driver.find_element(By.NAME, "sede")).select_by_visible_text(office)
                        run_tramites(driver, province, office)
                        
                        # Reset for next office
                        driver.get(URL)
                        wait.until(EC.presence_of_element_located((By.NAME, "provincia")))
                        Select(driver.find_element(By.NAME, "provincia")).select_by_visible_text(province)
                        driver.find_element(By.ID, "btnAceptar").click()
                        time.sleep(3)
                    except Exception as e:
                        print(f"⚠️ Error checking office {office[:20]}: {e}")
                        driver.get(URL)
                        time.sleep(2)
                        continue
    except Exception as e:
        print(f"❌ Main Error: {e}")
    finally:
        driver.quit()

def run_tramites(driver, province, office_name):
    try:
        tramite_boxes = driver.find_elements(By.ID, "tramiteGrupo[0]") or driver.find_elements(By.ID, "tramiteGrupo[1]")
        if tramite_boxes:
            tramite_select = Select(tramite_boxes[0])
            options_text = [opt.text for opt in tramite_select.options]
            
            for tramite in TRAMITES_TO_CHECK:
                if any(tramite in opt for opt in options_text):
                    tramite_select.select_by_visible_text(tramite)
                    driver.find_element(By.ID, "btnAceptar").click()
                    time.sleep(2)

                    entrar_btn = driver.find_elements(By.ID, "btnEntrar")
                    if entrar_btn:
                        entrar_btn[0].click()
                        time.sleep(2)

                    content = driver.page_source
                    if "No hay citas disponibles" in content or "En este momento no hay citas" in content:
                        print(f"   ❌ No slots.")
                    else:
                        print(f"   🎉 SLOT FOUND IN {office_name}!!!")
                        send_telegram_professional(province, tramite, office_name)
    except Exception as e:
        print(f"⚠️ Error in run_tramites: {e}")

if __name__ == "__main__":
    check_cita_previa()
