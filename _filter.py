from _base import Base_Class, pandasModel

import pandas as pd
import re

class Filter_table(Base_Class):
    
    def __init__(self):
        # Placeholder
        self.filter_name_lineEdit.setPlaceholderText('Введите ФИО эксперта:')
        self.filter_grnti_lineEdit.setPlaceholderText('Формат: 00.00.00')
        self.filter_grnti2_lineEdit.setPlaceholderText('Формат: 00.00.00')
        self.filter_keywords_lineEdit.setPlaceholderText('Введите ключевые слова через запятую:')
        # Валидация
        self.filter_name_lineEdit.setValidator(self.validator_name)
        self.filter_grnti_lineEdit.setValidator(self.validator_grnti)
        self.filter_grnti2_lineEdit.setValidator(self.validator_grnti)
        self.filter_keywords_lineEdit.setValidator(self.validator_multi)
        # Заполнение CheckBox
        self.filter_reg_comboBox.clear()
        self.filter_reg_comboBox.addItems([''] + sorted(self.df_ntp['Округ'].unique()))
        self.filter_region_comboBox.clear()
        self.filter_region_comboBox.addItems([''] + sorted(self.df_ntp['Регион'].unique()))
        self.filter_city_comboBox.clear()
        self.filter_city_comboBox.addItems([''] + sorted(self.df_ntp['Город'].unique()))
        
    
    def apply_filter_widget(self) -> None:
        filters = (
            self.filter_name_lineEdit.text(),
            self.filter_region_comboBox.currentText(),
            self.filter_reg_comboBox.currentText(),
            self.filter_city_comboBox.currentText(),
            self.filter_grnti_lineEdit.text(),
            self.filter_grnti2_lineEdit.text(),
            self.filter_keywords_lineEdit.text()
        )
        cols = 'ФИО', 'Регион', 'Округ', 'Город', 'ГРНТИ', 'ГРНТИ', 'Ключевые слова'
        filter_string: str = self.get_filter_str(filters, cols)
        if filter_string: self.init_table.setModel(pandasModel(self.settings_dict[self.cur_name]['df'].query(filter_string)))
        else:             self.init_table.setModel(pandasModel(self.settings_dict[self.cur_name]['df']))
        self.filter_widget.setHidden(True)
        
        
    def get_filter_str(self, filters: tuple[str, ...], cols: tuple[str, ...]) -> str:
        filter_string: str = ''
        for filter_, col_ in zip(filters, cols):
            if filter_ == '': continue
            if len(filter_string) > 1: filter_string += ' and '
            match col_:
                case 'Ключевые слова':
                    filter_ = filter_.strip().split(',')
                    for n, i in enumerate(filter_):
                        filter_string += f'`{col_}`.str.contains(r"{i}", na=False, case=True, regex=True)'
                        if len(filter_) - (n + 1): filter_string += ' and '
                case 'ГРНТИ':
                    filter_ = re.split(r'(?:\s*,\s*|\s*;\s*|\s+)', filter_.strip())
                    for n, i in enumerate(filter_):
                        filter_string += f'`{col_}`.str.contains(r"(?:^{i}|, {i})", regex=True)'
                        if len(filter_) - (n + 1): filter_string += ' and '
                case _:
                    filter_string += f'`{col_}`.str.contains("{filter_}", na=False, case=False)'
        return filter_string
    
    
    def show_filter_widget(self, hide: bool) -> None: 
        self.filter_widget.setHidden(hide)  
        
        
    def reset_filter_widget(self) -> None:
        self.filter_name_lineEdit.setText('')
        self.filter_region_comboBox.setCurrentText('')
        self.filter_reg_comboBox.setCurrentText('')
        self.filter_city_comboBox.setCurrentText('')
        self.filter_grnti_lineEdit.setText('')
        self.filter_grnti2_lineEdit.setText('')
        self.filter_keywords_lineEdit.setText('')
        
        self.init_table.setModel(pandasModel(self.settings_dict[self.cur_name]['df']))