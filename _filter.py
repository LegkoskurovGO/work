from _base import Base_Class, pandasModel

from PyQt6.QtCore import QRegularExpression
from PyQt6.QtGui import QRegularExpressionValidator

import pandas as pd
import re

class Filter_table(Base_Class):
    
    def fill_filter_lineEdit(self) -> None:
        
        # Раздел Фильтр:
        validator_grnti = QRegularExpressionValidator()
        validator_grnti.setRegularExpression(QRegularExpression(r'^\d{1,2}(\.\d{2}(\.\d{2})?)?(((\,|\;| ){1} *){1}\d{1,2}(\.\d{2}(\.\d{2})?)?)?$'))
        
        a = self.filter_reg_comboBox.currentText()
        self.filter_name_lineEdit.setPlaceholderText('Введите ФИО эксперта:')
        self.filter_region_lineEdit.setPlaceholderText('Введите регион эксперта:')
        self.filter_reg_comboBox.clear()
        self.filter_reg_comboBox.addItems([''] + sorted(self.df_ntp['Округ'].unique()))
        self.filter_reg_comboBox.setCurrentText(a)
        self.filter_grnti_lineEdit.setValidator(validator_grnti)
        self.filter_city_lineEdit.setPlaceholderText('Введите город эксперта:')
        self.filter_grnti_lineEdit.setPlaceholderText('Введите коды ГРНТИ через запятую:')
        self.filter_keywords_lineEdit.setPlaceholderText('Введите ключевые слова через запятую:')
        
    
    def show_filter_widget(self, hide: bool) -> None: 
        self.filter_widget.setHidden(hide)
        self.fill_filter_lineEdit()
    
    
    def varify_filter(self, filters: tuple[str, str, str, str, str, str], cols) -> str:
        filter_string: str = ''
        for filter_, col_ in zip(filters, cols):
            if filter_ != '':
                if len(filter_string) > 1: filter_string += ' and '
                if col_ != 'ГРНТИ' and col_ != 'Ключевые слова':
                    filter_string += f'`{col_}`.str.contains("{filter_}", na=False, case=False)'
                elif col_ == 'Ключевые слова':
                    filter_ = re.split(r'(?:\s*,\s*|\s*;\s*|\s+)', filter_.strip())
                    for n, i in enumerate(filter_):
                        filter_string += f'`{col_}`.str.contains("{i}", na=False, case=False, regex=True)'
                        if len(filter_) - (n + 1):
                            filter_string += ' and '
                else:
                    filter_ = re.split(r'(?:\s*,\s*|\s*;\s*|\s+)', filter_.strip())
                    for n, i in enumerate(filter_):
                        if len(i.split(r'.')[0]) == 1: i = '0' + i
                        filter_string += f'`{col_}`.str.contains(r"(^{i}|, {i})", regex=True)'
                        # filter_string += f'`{col_}`.str.contains(r"\b{i}", regex=True)'
                        if len(filter_) - (n + 1):
                            filter_string += ' and '
        return filter_string
    
    
    def apply_filter_widget(self) -> None:
        filters = (
            self.filter_name_lineEdit.text(),
            self.filter_region_lineEdit.text(),
            self.filter_reg_comboBox.currentText(),
            self.filter_city_lineEdit.text(),
            self.filter_grnti_lineEdit.text(),
            self.filter_keywords_lineEdit.text()
        )
        cols = ['ФИО', 'Регион', 'Округ', 'Город', 'ГРНТИ', 'Ключевые слова']
        
        filter_string: str = self.varify_filter(filters, cols)
        if filter_string:
            self.init_table.setModel(pandasModel(self.settings_dict[self.cur_name]['df'].query(filter_string)))
        else:
            self.init_table.setModel(pandasModel(self.settings_dict[self.cur_name]['df']))
        self.filter_widget.setHidden(True)
    
    
    def reset_filter_widget(self) -> None:
        self.init_table.setModel(pandasModel(self.settings_dict[self.cur_name]['df']))
        self.filter_name_lineEdit.setText('')
        self.filter_region_lineEdit.setText('')
        self.filter_reg_comboBox.setCurrentIndex(0),
        self.filter_city_lineEdit.setText(''),
        self.filter_grnti_lineEdit.setText(''),
        self.filter_keywords_lineEdit.setText('')
        

# pd.DataFrame.join()
# self.df_ntp.join(self.df_reg.set_index('Город').drop('Округ'), on='Город')
# .join(self.df_grnti.set_index('Код'), on='ГРНТИ')
# self.df_grnti