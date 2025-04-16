import os
import shutil
import time

from tkinter import Tk
from tkinter.filedialog import askopenfilename

class Utils:
    def __init__(self):
        self.FILE_PATH = os.path.join(os.getcwd(), 'temp')

    def remove(self, path, is_purge=False):
        if os.path.exists(path):
            if is_purge:
                files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]

                for file in files:
                    os.remove(os.path.join(path, file))
                
                os.removedirs(path)
                return

            os.remove(path)

    def select_file(self, title='Selecione o arquivo', filename_default=f'{time.time()}'):
        Tk().withdraw()

        self.remove(os.path.join(self.FILE_PATH, filename_default))
            
        file = askopenfilename(title=title, filetypes=(('Excel files', ['*.xlsx', '*.xls']), ('CSV files', '*.csv')))
        filename = os.path.basename(file)
        ext = filename.split('.')[1]
        new_filename = f'{filename_default}.{ext}'
        os.makedirs(self.FILE_PATH, exist_ok=True)
        shutil.copy(file, self.FILE_PATH)
        os.rename(os.path.join(self.FILE_PATH, filename), os.path.join(self.FILE_PATH, new_filename))

        return new_filename