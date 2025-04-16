import pandas as pd

from db.DBConfig import DBConfig
from services.Utils import Utils
from services.AutomationBrowser import AutomationBrowser
from datetime import datetime

LIMIT_PER_ROUND = 99
INITIAL_URL = 'https://consultanumero.abrtelecom.com.br/consultanumero/consulta/consultaHistoricoRecenteCtg'

db = DBConfig(name_db='data')
automation = AutomationBrowser(INITIAL_URL)
utils = Utils()

filename_default = utils.select_file()

is_continue = True
while is_continue:
    is_continue = automation.send_file(id_element='arquivo', filename=filename_default, limit_per_line=LIMIT_PER_ROUND)
    is_warning_recaptcha_valid = True

    is_recaptcha_response = False

    while not is_recaptcha_response:
        is_recaptcha_response = automation.get_recaptcha_response()

        if is_recaptcha_response:
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

utils.remove(utils.FILE_PATH)
automation.set_zoom(100, delay_after=2)
automation.close()
db.close()