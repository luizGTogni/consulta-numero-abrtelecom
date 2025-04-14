import time
import pandas as pd
import shutil
import math

from db.DBConfig import DBConfig

from os import path, getcwd, makedirs, rename, remove
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from tkinter import Tk
from tkinter.filedialog import askopenfilename
from datetime import datetime

FILE_PATH = path.join(path.dirname(__file__), 'temp')

db = DBConfig(name_db='data')

options = Options()
options.add_argument('--start-maximized')
options.add_argument('--user-data-dir=/chrome_profile')
options.add_experimental_option("detach", True)


driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.get('https://consultanumero.abrtelecom.com.br/consultanumero/consulta/consultaHistoricoRecenteCtg')

Tk().withdraw()

if path.exists(f'{FILE_PATH}/phones.csv'):
    remove(f'{FILE_PATH}/phones.csv')

file = askopenfilename(title='Selecione o arquivo de número de telefones', filetypes=[('Arquivo, CSV', '*.csv'), ("Arquivos Excel", "*.xlsx *.xls")])
filename = path.basename(file)
makedirs(FILE_PATH, exist_ok=True)
shutil.copy(file, FILE_PATH)
rename(f'{FILE_PATH}/{filename}', f'{FILE_PATH}/phones.csv')

# 99 LINES MAX

df_phones = pd.read_csv(f'{FILE_PATH}/phones.csv')
rounds_scrapping = math.ceil(len(df_phones) / 99)
print(f'Tem {len(df_phones)} linhas nesse arquivo')
print(f'São necessários {rounds_scrapping} voltas nesse arquivo')

count = 0

while count < rounds_scrapping:
    start = 99 * count
    count += 1
    end = count * 99

    df_phones[start:end].to_csv('temp/datas.csv', index=False)

    input_file = driver.find_element(By.ID, 'arquivo')
    input_file.send_keys(path.join(getcwd(), 'temp', 'datas.csv'))

    is_recaptcha_resolved = False
    is_warning_recaptcha_valid = True

    while not is_recaptcha_resolved:
        
        is_recaptcha_resolved = driver.execute_script('return document.getElementById("g-recaptcha-response").value')

        if is_recaptcha_resolved:
            driver.execute_script("document.body.style.zoom='50%'")
            time.sleep(2)
            button_consult = driver.find_element(By.ID, 'idSubmit')
            button_consult.click()

            time.sleep(4)

            table = driver.find_element(By.ID, 'resultado')
            table_body = table.find_element(By.TAG_NAME, "tbody")
            table_lines = table_body.find_elements(By.TAG_NAME, 'tr')

            for line in table_lines:
                column = line.find_elements(By.TAG_NAME, 'td')
                phone = column[0].text
                provider_name = column[1].text
                date_recent = column[3].text
                message = column[4].text

                consult = db.cursor.execute('SELECT * FROM consults WHERE phone = (?)', (phone,)).fetchone()

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
                    db.cursor.execute('UPDATE consults SET phone = ?, provider_name = ?, date_recent = ?, number_months = ?, message = ? WHERE phone = ?', (phone, provider_name, date_recent_format, number_months, message, phone))
                else:
                    db.cursor.execute("INSERT INTO consults (phone, provider_name, date_recent, number_months, message) VALUES (?, ?, ?, ?, ?)", (phone, provider_name, date_recent_format, number_months, message))
                
                db.conn.commit()

                # CONVERTER EM EXCEL
                df = pd.read_sql_query('SELECT * FROM consults', db.conn)
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

if path.exists(f'{FILE_PATH}/phones.csv'):
    remove(f'{FILE_PATH}/phones.csv')

driver.execute_script("document.body.style.zoom='100%'")
time.sleep(2)
driver.quit()
db.close()