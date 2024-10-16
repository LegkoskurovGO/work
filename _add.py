from _base import Base_Class, pandasModel

from PyQt6.QtCore import QTimer

import re

import pandas as pd
from pandas.api.types import is_datetime64_any_dtype


class Add_Row(Base_Class):
    
    def __init__(self):
        # Placeholder
        self.addexpert_name_lineEdit.setPlaceholderText('Введите ФИО эксперта:')
        self.addexpert_grnti_lineEdit.setPlaceholderText('Формат: 00.00.00')
        self.addexpert_grnti2_lineEdit.setPlaceholderText('Формат: 00.00.00')
        self.addexpert_keywords_lineEdit.setPlaceholderText('Введите ключевые слова через запятую:')
        # Валидация
        self.addexpert_name_lineEdit.setValidator(self.validator_name)
        self.addexpert_grnti_lineEdit.setValidator(self.validator_grnti)
        self.addexpert_grnti2_lineEdit.setValidator(self.validator_grnti)
        self.addexpert_keywords_lineEdit.setValidator(self.validator_multi)
        # Заполнение CheckBox
        self.addexpert_reg_comboBox.clear()
        self.addexpert_reg_comboBox.addItems([''] + sorted(self.df_reg['Округ'].unique()))
        self.addexpert_region_comboBox.clear()
        self.addexpert_region_comboBox.addItems([''] + sorted(self.df_reg['Регион'].unique()))
        self.addexpert_city_comboBox.clear()
        self.addexpert_city_comboBox.addItems([''] + sorted(self.df_reg['Город'].unique()))
        # Скрыть ошибку
        self.warning_addexpert_label.setHidden(True)
        
        
    def apply_add_widget(self) -> None:
        new_row = self.get_row_add_widget()
        self.add_row(new_row)
        
        
    def before_add_widget(self):
        return self.checkers_add_widget()
    
    
    def show_add_widget(self, hide: bool) -> None:
        self.reset_style_addexpert()
        self.reset_add_widget()
        self.addexpert_widget.setHidden(hide)
            
    
    def get_row_add_widget(self) -> pd.DataFrame:
        # Формирование ГРНТИ
        grntis = sorted((str(self.addexpert_grnti_lineEdit.text()), str(self.addexpert_grnti2_lineEdit.text())))
        str_grntis = ''
        for item in grntis:
            if item:
                if str_grntis: str_grntis += ', '
            str_grntis += item
            
        # ['Номер', 'ФИО', 'Округ', "Регион", 'Город', 'ГРНТИ', "Расшифровка", 'Ключевые слова', 'Участие', 'Дата добавления']
        new_row = pd.Series([
            self.df_ntp['Номер'].max()+1,
            self.addexpert_name_lineEdit.text(),
            self.addexpert_reg_comboBox.currentText(),
            self.addexpert_region_comboBox.currentText(),
            self.addexpert_city_comboBox.currentText(),
            str_grntis,
            ', '.join(dict.fromkeys([raschif for num in grntis if (raschif := self.dict_grnti.get(num, ''))])),
            self.addexpert_keywords_lineEdit.text(),
            0,
            pd.Timestamp.today().strftime('%d-%b-%y')
        ],
        index=self.settings_dict[self.cur_name]['df'].columns
        )
        new_row = new_row.to_frame().T
        for col in new_row.columns:
            if is_datetime64_any_dtype(new_row[col]):
                new_row[col] = new_row[col].dt.strftime('%d-%b-%y')
        return new_row
    
        
    def add_row(self, row: pd.DataFrame) -> None:        
        self.settings_dict[self.cur_name]['df'] = pd.concat([self.settings_dict[self.cur_name]['df'], row], ignore_index=True)
        self.settings_dict[self.cur_name]['df'] = self.settings_dict[self.cur_name]['df'].astype(self.settings_dict[self.cur_name]['df'].dtypes)
        self.df_ntp = pd.concat([self.df_ntp, row], ignore_index=True)
        self.df_ntp = self.df_ntp.astype(self.df_ntp.dtypes)
        self.init_table.setModel(pandasModel(self.settings_dict[self.cur_name]['df']))
        self.init_table.scrollToBottom()
        self.init_table.selectRow(self.settings_dict[self.cur_name]['df'].index.max())
        self.reset_add_widget()
        self.addexpert_widget.setHidden(True)
    
    
    def checkers_add_widget(self) -> bool:
        new_row = self.get_row_add_widget()
        
        def is_unique_row(row: pd.Series) -> bool:
            query_string = r'`ФИО` == @row["ФИО"] and `Город` == @row["Город"] and `ГРНТИ` == @row["ГРНТИ"]'
            return not self.settings_dict[self.cur_name]['df'].query(query_string).empty
        def is_empty_filed(row: pd.Series) -> bool:
            return (~row.loc[['ФИО', 'Округ', 'Регион', 'Город', 'ГРНТИ']].astype(bool)).sum()
        def regex_correct(row: pd.Series) -> bool:
            return not bool(re.match(self.regex_grntis, new_row.at[0, 'ГРНТИ']))
        
        if is_unique_row(new_row.iloc[0]):
            self.warning_addexpert_label.setText("Такой эксперт уже добавлен")
            self.warning_addexpert_label.setHidden(False)
            QTimer.singleShot(5000, lambda: self.warning_addexpert_label.setHidden(True))
            return False
        if is_empty_filed(new_row.iloc[0]):
            self.reset_style_addexpert()
            if self.addexpert_name_lineEdit.text() == '':
                self.addexpert_name_lineEdit.setStyleSheet("border: 1px solid red;")
            if self.addexpert_grnti_lineEdit.text() == '' and self.addexpert_grnti2_lineEdit.text() == '':
                for i in ['grnti', 'grnti2']: getattr(self, f'addexpert_{i}_lineEdit').setStyleSheet("border: 1px solid red;")
            for i in ['reg', 'region', 'city']:
                if getattr(self, f'addexpert_{i}_comboBox').currentText() == '':
                    getattr(self, f'addexpert_{i}_comboBox').setStyleSheet("border: 1px solid red;")
            return False
        if regex_correct(new_row.iloc[0]):
            self.warning_addexpert_label.setText("Не корректно введёны ГРНТИ номера")
            self.warning_addexpert_label.setHidden(False)
            QTimer.singleShot(5000, lambda: self.warning_addexpert_label.setHidden(True))
            return False
        
        return True


    def reset_style_addexpert(self) -> None:            
        self.addexpert_name_lineEdit.setStyleSheet("")
        self.addexpert_reg_comboBox.setStyleSheet("")
        self.addexpert_region_comboBox.setStyleSheet("")
        self.addexpert_city_comboBox.setStyleSheet("")
        self.addexpert_grnti_lineEdit.setStyleSheet("")
        self.addexpert_grnti2_lineEdit.setStyleSheet("")
        self.addexpert_keywords_lineEdit.setStyleSheet("")    
        
        
    def reset_add_widget(self) -> None:
        self.addexpert_name_lineEdit.setText('')
        self.addexpert_reg_comboBox.setCurrentText('')
        self.addexpert_region_comboBox.setCurrentText('')
        self.addexpert_city_comboBox.setCurrentText('')
        self.addexpert_grnti_lineEdit.setText('')
        self.addexpert_grnti2_lineEdit.setText('')
        self.addexpert_keywords_lineEdit.setText('')
        
        self.warning_addexpert_label.setHidden(True)