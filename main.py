import time

from db.DBConfig import DBConfig
from db.Consult import Consult
from services.Utils import Utils
from services.AutomationBrowser import AutomationBrowser

def main():
    db = DBConfig(name_db='data')
    consult = Consult(db)
    utils = Utils()

    LIMIT_PER_ROUND = 99
    INITIAL_URL = 'https://consultanumero.abrtelecom.com.br/consultanumero/consulta/consultaHistoricoRecenteCtg'

    automation = AutomationBrowser(INITIAL_URL)

    filename_default = utils.select_file()

    is_continue = True
    start_total_time = time.time()
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

                    date_recent_format = utils.date_format(date_recent)
                    number_months = utils.calc_number_months(date_recent)

                    consult.create_by_phone(phone, provider_name, date_recent_format, number_months, message)
            else:
                if is_warning_recaptcha_valid:
                    print('RESOLVA O RECAPTCHA MANUALMENTE')
                    is_warning_recaptcha_valid = False
    
    utils.remove(utils.FILE_PATH, is_purge=True)
    automation.set_zoom(100, delay_after=2)
    
    consult.to_excel()
    db.close()
    automation.close()

    end_total_time = time.time()
    print(f"[RT] Scrapper: {end_total_time - start_total_time:.2f} seconds")

if __name__ == "__main__":
    main()