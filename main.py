import time

from db.DBConfig import DBConfig
from db.Consult import Consult
from services.Utils import Utils
from services.AutomationBrowser import AutomationBrowser

def main():
    db = DBConfig(name_db='data')
    consultDB = Consult(db)
    utils = Utils()

    LIMIT_PER_ROUND = 99
    INITIAL_URL = 'https://consultanumero.abrtelecom.com.br/consultanumero/consulta/consultaHistoricoRecenteCtg'

    automation = AutomationBrowser(INITIAL_URL)

    filename_default = utils.select_file()

    is_continue = True
    start_total_time = time.time()
    consults = []
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

                    date_recent_format = utils.date_format(column['date_recent'])
                    number_months = utils.calc_number_months(column['date_recent'])
                    consults.append({'phone': column['phone'], 'provider_name': column['provider_name'], 'date_recent_format': date_recent_format, 'number_months': number_months, 'message': column['message']})
                    #print(column['phone'], column['provider_name'], date_recent_format, number_months, column['message'])
            else:
                if is_warning_recaptcha_valid:
                    print('RESOLVA O RECAPTCHA MANUALMENTE')
                    is_warning_recaptcha_valid = False
    
    for consult in consults:
        consultDB.create_by_phone(consult['phone'], consult['provider_name'], consult['date_recent_format'], consult['number_months'], consult['message'])

    utils.remove(utils.FILE_PATH, is_purge=True)
    automation.set_zoom(100, delay_after=2)
    
    consultDB.to_excel()
    db.close()
    automation.close()

    end_total_time = time.time()
    print(f"[RT] Scrapper: {end_total_time - start_total_time:.2f} seconds")

if __name__ == "__main__":
    main()