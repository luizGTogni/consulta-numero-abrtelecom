import os
import time
import pandas as pd

class Consult:
    def __init__(self, db):
        self.db = db

    def select_by_phone(self, phone):
        return self.db.cursor.execute('SELECT * FROM consults WHERE phone = (?)', (phone,)).fetchone()
    
    def update_by_phone(self, phone, provider_name, date_recent_format, number_months, message):
        self.db.cursor.execute('UPDATE consults SET phone = ?, provider_name = ?, date_recent = ?, number_months = ?, message = ? WHERE phone = ?', (phone, provider_name, date_recent_format, number_months, message, phone))
        self.db.conn.commit()

    def create_by_phone(self, phone, provider_name, date_recent_format, number_months, message):
        consult_response = self.select_by_phone(phone)

        if consult_response:
            self.update_by_phone(phone, provider_name, date_recent_format, number_months, message)
            return 
        
        self.db.cursor.execute("INSERT INTO consults (phone, provider_name, date_recent, number_months, message) VALUES (?, ?, ?, ?, ?)", (phone, provider_name, date_recent_format, number_months, message))
        self.db.conn.commit()

    def to_excel(self):
        print('CRIANDO ARQUIVO FINAL DE CONSULTAS...\n')
        df = pd.read_sql_query('SELECT * FROM consults', self.db.conn)
        df.rename(columns={
            'phone': 'TELEFONE',
            'provider_name': 'PRESTADORA',
            'date_recent': 'DATA',
            'number_months': 'M',
            'message': 'MENSAGEM',
        }, inplace=True)
        os.makedirs(os.path.join(os.getcwd(), 'final'), exist_ok=True)
        filename = f'{time.time()}-consults.xlsx'
        df.to_excel(os.path.join(os.getcwd(), 'final', filename), index=False)
        print('ARQUIVO FINAL DE CONSULTAS CRIADO...\n')