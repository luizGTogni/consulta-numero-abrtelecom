import time

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver.get('https://consultanumero.abrtelecom.com.br/consultanumero/consulta/consultaHistoricoRecenteCtg')

input_file = driver.find_element(By.ID, 'arquivo')
input_file.send_keys()

time.sleep(5)
driver.quit()