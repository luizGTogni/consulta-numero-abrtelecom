import time

from os import path, getcwd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver.get('https://consultanumero.abrtelecom.com.br/consultanumero/consulta/consultaHistoricoRecenteCtg')

input_file = driver.find_element(By.ID, 'arquivo')
input_file.send_keys(path.join(getcwd(), 'temp', 'phones.csv'))

is_recaptcha_resolved = False
is_warning_recaptcha_valid = True

while not is_recaptcha_resolved:
    
    is_recaptcha_resolved = driver.execute_script("return document.getElementById('g-recaptcha-response').value")

    if is_recaptcha_resolved:
        print("CAPTCHA resolvido!")
    else:
        if is_warning_recaptcha_valid:
            print("RESOLVA O RECAPTCHA MANUALMENTE")
            is_warning_recaptcha_valid = False

time.sleep(5)
driver.quit()