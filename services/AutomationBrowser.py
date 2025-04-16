import os
import math
import time
import pandas as pd

from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

class AutomationBrowser:
    def __init__(self, initial_url=''):
        options = Options()
        options.add_argument('--start-maximized')
        options.add_argument('--user-data-dir=/chrome_profile')
        options.add_experimental_option("detach", True)

        self._driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

        if len(initial_url) > 0:
            self.open_page(initial_url)

    def open_page(self, url):
        self._driver.get(url)

    def save_temp_path(self, filename):
        name_dir = 'temp'
        os.makedirs(os.path.join(os.getcwd(), name_dir), exist_ok=True)
        return os.path.join(os.getcwd(), name_dir, filename)

    def send_file(self, id_element, filename, limit_per_line=0, delay_before=0):
        file_path = self.save_temp_path(filename)
        final_file_path = self.save_temp_path(f'{time.time()}.csv')
        sleep(delay_before)
        
        element = self._driver.find_element(By.ID, id_element)

        if limit_per_line > 0:
            df_phones = pd.read_csv(file_path)
            rounds = math.ceil(len(df_phones) / 99)
            #print(f'Tem {len(df_phones)} linhas nesse arquivo')
            #print(f'São necessários {rounds} voltas nesse arquivo')

            df_phones[:limit_per_line].to_csv(final_file_path, index=False)
            df_phones[limit_per_line:].to_csv(file_path, index=False)
            element.send_keys(final_file_path)
            
            #print(len(df_phones[limit_per_line:]))
            if len(df_phones[limit_per_line:]) == 0:
                return False
            
            return True
        
        element.send_keys(file_path)
        return False

    def click_button(self, id_element, delay_before=0, delay_after=0):
        sleep(delay_before)
        button = self._driver.find_element(By.ID, id_element)
        button.click()
        sleep(delay_after)

    def get_lines_table(self, id_table):
        table = self._driver.find_element(By.ID, id_table)
        table_body = table.find_element(By.TAG_NAME, "tbody")
        return table_body.find_elements(By.TAG_NAME, 'tr')
    
    def get_value_column(self, line_element):
        column = line_element.find_elements(By.TAG_NAME, 'td')
        return { 'phone': column[0].text, 'provider_name': column[1].text, 'date_recent': column[3].text, 'message': column[4].text }

    def get_recaptcha_response(self):
        sleep(2)
        value = self._driver.execute_script('return document.getElementById("g-recaptcha-response").value')
        return value
    
    def set_zoom(self, value, delay_before=0, delay_after=0):
        sleep(delay_before)
        self._driver.execute_script(f'document.body.style.zoom="{value}%"')
        sleep(delay_after)

    def close(self):
        self._driver.close()