import pandas as pd
import shutil
import math

from db.DBConfig import DBConfig
from services.AutomationBrowser import AutomationBrowser

from os import path, makedirs, rename, remove
from tkinter import Tk
from tkinter.filedialog import askopenfilename
from datetime import datetime

FILE_PATH = path.join(path.dirname(__file__), 'temp')
INITIAL_URL = 'https://consultanumero.abrtelecom.com.br/consultanumero/consulta/consultaHistoricoRecenteCtg'

db = DBConfig(name_db='data')
automation = AutomationBrowser(INITIAL_URL)

Tk().withdraw()

if path.exists(f'{FILE_PATH}/phones.csv'):
    remove(f'{FILE_PATH}/phones.csv')

file = askopenfilename(title='Selecione o arquivo de número de telefones', filetypes=[('Arquivo, CSV', '*.csv'), ("Arquivos Excel", "*.xlsx *.xls")])
filename = path.basename(file)
makedirs(FILE_PATH, exist_ok=True)
shutil.copy(file, FILE_PATH)
rename(f'{FILE_PATH}/{filename}', f'{FILE_PATH}/phones.csv')

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

    automation.send_file(id_element='arquivo', filename='datas.csv')

    is_recaptcha_resolved = automation.get_recaptcha_response()
    is_warning_recaptcha_valid = True

    while not is_recaptcha_resolved:
        if is_recaptcha_resolved:
            automation.set_zoom(value=50, delay_after=2)
            automation.click_button(id_element='idSubmit', delay_after=4)
            table_lines = automation.get_lines_table(id_table='resultado')
    
            for line in table_lines:
                column = automation.get_value_column(line_element=line)
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

automation.set_zoom(100, delay_after=2)
automation.close()
db.close()