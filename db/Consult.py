class Consult:
    def __init__(self, db):
        self.db = db

    def select_by_phone(self, phone):
        return self.db.cursor.execute('SELECT * FROM consults WHERE phone = (?)', (phone,)).fetchone()
    
    def update_by_phone(self, phone, provider_name, date_recent_format, number_months, message):
        self.db.cursor.execute('UPDATE consults SET phone = ?, provider_name = ?, date_recent = ?, number_months = ?, message = ? WHERE phone = ?', (phone, provider_name, date_recent_format, number_months, message, phone))
        self.db.conn.commit()

    def create_by_phone(self, phone, provider_name, date_recent_format, number_months, message):
        self.db.cursor.execute("INSERT INTO consults (phone, provider_name, date_recent, number_months, message) VALUES (?, ?, ?, ?, ?)", (phone, provider_name, date_recent_format, number_months, message))
        self.db.conn.commit()

    def to_excel(self):
        pass