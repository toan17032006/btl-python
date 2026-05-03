from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import sqlite3
import time

conn = sqlite3.connect('ngoaihanganh.db')
cursor = conn.cursor()
cursor.execute('DROP TABLE IF EXISTS player_stats')

cursor.execute('''
    CREATE TABLE player_stats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        player TEXT, nation TEXT, pos TEXT, squad TEXT, age TEXT, 
        born TEXT, mp TEXT, starts TEXT, minutes INTEGER, 
        min_90s TEXT, gls TEXT, ast TEXT, g_plus_a TEXT, 
        g_minus_pk TEXT, pk TEXT, pkatt TEXT, crdy TEXT, crdr TEXT, 
        per90_gls TEXT, per90_ast TEXT, per90_g_a TEXT, 
        per90_g_minus_pk TEXT, per90_g_a_minus_pk TEXT
    )
''')
conn.commit()

# --- MỞ CHROME TỰ ĐỘNG ---
chrome_options = Options()
chrome_options.add_argument('--disable-blink-features=AutomationControlled')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--window-size=1920,1080')
chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
chrome_options.add_experimental_option('useAutomationExtension', False)

driver = webdriver.Chrome(options=chrome_options)

driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
    'source': '''
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        })
    '''
})

# --- TỰ ĐỘNG TRUY CẬP LINK ---
print("Đang truy cập FBref...")
driver.get("https://fbref.com/en/comps/9/Premier-League-Stats")

print("Nếu có CAPTCHA, hãy solve nó thủ công...")
print("Sau khi solve xong, đợi 5 giây script sẽ tự chạy...")
time.sleep(5)

print("Đang quét dữ liệu từ bảng...")

wait = WebDriverWait(driver, 20)
table = wait.until(EC.presence_of_element_located((By.ID, "stats_standard")))
rows = table.find_elements(By.CSS_SELECTOR, "tbody tr:not(.thead)")

data_to_save = []

for row in rows:
    cells = row.find_elements(By.TAG_NAME, "td")
    
    if len(cells) == 24:
        min_text = cells[8].text.replace(',', '')
        minutes = int(min_text) if min_text else 0
        
        if minutes > 90:
            row_data = []
            for i in range(23):
                if i == 8:
                    row_data.append(minutes) 
                else:
                    row_data.append(cells[i].text)
            
            data_to_save.append(tuple(row_data))

column_names = (
    "player, nation, pos, squad, age, born, mp, starts, minutes, "
    "min_90s, gls, ast, g_plus_a, g_minus_pk, pk, pkatt, "
    "crdy, crdr, per90_gls, per90_ast, per90_g_a, per90_g_minus_pk, per90_g_a_minus_pk"
)

placeholders = ', '.join(['?'] * 23)
query = f'INSERT INTO player_stats ({column_names}) VALUES ({placeholders})'

cursor.executemany(query, data_to_save)
conn.commit()

print(f"XONG! Đã cào thành công {len(data_to_save)} cầu thủ và lưu vào ngoaihanganh.db")
conn.close()
driver.quit()
