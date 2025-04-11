import time
import sqlite3
import pandas as pd

from os import path, getcwd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime

conn = sqlite3.connect('abrtelecom_datas.db') 
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS consults (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    phone TEXT UNIQUE NOT NULL,
    provider_name TEXT NOT NULL,
    date_recent TEXT,
    number_months INTEGER,
    message TEXT NOT NULL
)
""")

conn.commit()

options = Options()
options.add_argument('--start-maximized')

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.get('https://consultanumero.abrtelecom.com.br/consultanumero/consulta/consultaHistoricoRecenteCtg')

input_file = driver.find_element(By.ID, 'arquivo')
input_file.send_keys(path.join(getcwd(), 'temp', 'phones.csv'))

is_recaptcha_resolved = False
is_warning_recaptcha_valid = True

while not is_recaptcha_resolved:
    
    is_recaptcha_resolved = driver.execute_script('return document.getElementById("g-recaptcha-response").value')

    if is_recaptcha_resolved:
        driver.execute_script("document.body.style.zoom='50%'")
        time.sleep(2)
        button_consult = driver.find_element(By.ID, 'idSubmit')
        button_consult.click()

        table = driver.find_element(By.ID, 'resultado')
        table_body = table.find_element(By.TAG_NAME, "tbody")
        table_lines = table_body.find_elements(By.TAG_NAME, 'tr')

        for line in table_lines:
            column = line.find_elements(By.TAG_NAME, 'td')
            phone = column[0].text
            provider_name = column[1].text
            date_recent = column[3].text
            message = column[4].text

            consult = cursor.execute('SELECT * FROM consults WHERE phone = (?)', (phone,)).fetchone()

            date_recent_format = None
            number_months = None
            if len(date_recent) > 0:
                date_recent_convert = datetime.strptime(date_recent, '%d/%m/%Y %H:%M')
                date_recent_format = date_recent_convert.strftime('%Y-%m-%d %H:%M:%S')

                today = datetime.now()

                years = today.year - date_recent_convert.year
                months = today.month - date_recent_convert.month

                number_months = years * 12 + months

            if consult:
                cursor.execute('UPDATE consults SET phone = ?, provider_name = ?, date_recent = ?, number_months = ?, message = ? WHERE phone = ?', (phone, provider_name, date_recent_format, number_months, message, phone))
            else:
                cursor.execute("INSERT INTO consults (phone, provider_name, date_recent, number_months, message) VALUES (?, ?, ?, ?, ?)", (phone, provider_name, date_recent_format, number_months, message))
            
            conn.commit()

            # CONVERTER EM EXCEL
            df = pd.read_sql_query('SELECT * FROM consults', conn)
            df.rename(columns={
                'phone': 'TELEFONE',
                'provider_name': 'PRESTADORA',
                'date_recent': 'DATA',
                'number_months': 'M',
                'message': 'MENSAGEM',
            }, inplace=True)
            df.to_excel('consults.xlsx', index=False)
    else:
        if is_warning_recaptcha_valid:
            print('RESOLVA O RECAPTCHA MANUALMENTE')
            is_warning_recaptcha_valid = False

driver.execute_script("document.body.style.zoom='100%'")
time.sleep(2)
driver.quit()
conn.close()