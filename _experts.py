from _base import Base_Class, pandasModel, Ui_Dialog2
from _edit import Edit_Row

from PyQt6.QtCore import QSettings

import os
import pandas as pd

class Experts(Base_Class):
    
    def save_group_widget(self) -> None:
        settings = QSettings("MyCompany", "MyApp")
        file_name = settings.value("file_name") # Читаем значение

        self.save_selected_rows(file_name)
    
    
    def save_selected_rows(self, name):
        sr = Edit_Row.rows_selected(self)
        rows = self.init_table.model().init_data.iloc[sr, :]
        
        if self.approve_save(name):
            self.save_dataframe_with_names(rows, name)
    
    
    def approve_save(self, name) -> bool:
        return True
        # return not os.path.isfile(os.path.join('.', 'groups', f'{name}.csv'))
    
    
    def load_groups(self, name) -> pd.DataFrame:
        params = {'dtype': { 'kod': 'int16', 'take_part': 'int8'}, 'parse_dates': [9], 'date_format': '%d-%b-%y'}
        df = pd.read_csv(os.path.join('.', 'groups', f'{name}.csv'), **params)
        return df
    
    def list_of_groups(self):
        pass

    def save_dataframe_with_names(self, df: pd.DataFrame, group_name: str):
        if not os.path.isdir(os.path.join('.', 'groups')):
            os.mkdir(os.path.join('.', 'groups'))
        
        file_path = os.path.join('.', 'groups', 'names.txt')
        
        # Определение следующего свободного номера файла
        file_numbers = []
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                for line in f:
                    file_numbers.append(int(line.split(",")[0].split("groups")[1].split("group")[1].split(".")[0]))
        next_number = max(file_numbers) + 1 if file_numbers else 1

        # Формирование имени файла
        file_name = os.path.join('.', 'groups', f"group{next_number}.csv")
        print(f'{file_name = }')
        print(f'{group_name = }', '\n\n')
        # Проверка на дублирование русского названия
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                for line in f:
                    if group_name == line.split(",")[1].strip():
                        print(f"Файл с таким русским названием ({group_name}) уже существует!")
                        return
                        # return self.warning('Такое имя уже зарезервировано')

        # Сохранение DataFrame в файл CSV
        df.to_csv(file_name, index=False, encoding="utf-8", date_format='%d-%b-%y')

        # Запись имени файла и его русского названия в текстовый документ
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(f"{file_name},{group_name}\n")

    
        
    
    
# pd.DataFrame.to_csv(f'{name}.csv')