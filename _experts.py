from _base import Base_Class, pandasModel
from _edit import Edit_Row

import os
import pandas as pd

class Experts(Base_Class):
    
    def save_selected_rows(self):
        sr = Edit_Row.rows_selected(self)
        rows = self.init_table.model().init_data.iloc[sr, :].reset_index(drop=True)
        
        name, flag = self.approve_save()
        
        if flag:
            rows.to_csv(f'{name}.csv')
    
    
    def load_groups(self, name) -> pd.DataFrame:
        params = {'dtype': { 'kod': 'int16', 'take_part': 'int8'}, 'parse_dates': [7], 'date_format': '%d-%b-%y'}
        df = pd.read_csv(os.path.join('.', 'groups', f'{name}.csv'), **params)
        return df
    
    def list_of_groups(self):
        pass

    def save_dataframe_with_names(df, group_name, file_path="names.txt"):
        # Определение следующего свободного номера файла
        file_numbers = []
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                for line in f:
                    file_numbers.append(int(line.split(",")[0].split("group")[1].split(".")[0]))
        next_number = max(file_numbers) + 1 if file_numbers else 1

        # Формирование имени файла
        file_name = f"group{next_number}.csv"
        
        # Проверка на дублирование русского названия
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                for line in f:
                    if group_name == line.split(",")[1].strip():
                        raise ValueError(f"Файл с таким русским названием ({group_name}) уже существует!")
                        # return self.warning('Такое имя уже зарезервировано')

        # Сохранение DataFrame в файл CSV
        df.to_csv(file_name, index=False, encoding="utf-8")

        # Запись имени файла и его русского названия в текстовый документ
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(f"{file_name},{group_name}\n")

    
        
    def approve_save(self) -> tuple[str, bool]:
        return self.get_name_file(), True

    def get_name_file(self) -> str:
        return 'name'
    
# pd.DataFrame.to_csv(f'{name}.csv')