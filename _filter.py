from _base import Base_Class, pandasModel

from PyQt6.QtCore import QRegularExpression
from PyQt6.QtGui import QRegularExpressionValidator

import pandas as pd

class Filter_table(Base_Class):
    
    def fill_filter_lineEdit(self) -> None:
        
        # Раздел Фильтр:
        validator_grnti = QRegularExpressionValidator()
        validator_grnti.setRegularExpression(QRegularExpression(r'^\d{2}\.\d{2}$'))
        
        a = self.filter_reg_comboBox.currentText()
        self.filter_reg_comboBox.clear()
        self.filter_reg_comboBox.addItems([''] + sorted(self.df_ntp['Округ'].unique()))
        self.filter_reg_comboBox.setCurrentText(a)
        self.filter_grnti_lineEdit.setValidator(validator_grnti)
        self.filter_city_lineEdit.setPlaceholderText('Город')
        self.filter_grnti_lineEdit.setPlaceholderText('ГРНТИ в формате:  00.00')
        self.filter_keywords_lineEdit.setPlaceholderText('Ключевые слова')
        
    
    def show_filter_widget(self, hide: bool) -> None: 
        self.filter_widget.setHidden(hide)
        self.fill_filter_lineEdit()
    
    
    def varify_filter(self, filters: tuple[str, str, str, str], cols) -> str:
        filter_string: str = ''
        for filter_, col_ in zip(filters, cols):
            if filter_ != '':
                if len(filter_string) > 1: filter_string += ' and '
                if col_ != 'ГРНТИ':
                    filter_string += f'`{col_}` == "{filter_}"'
                else:
                    if len(filter_) == 1: filter_ = '0' + filter_
                    filter_string += f'`{col_}`.str.contains(r"^({filter_})| ({filter_})")'
        return filter_string
    
    
    def apply_filter_widget(self) -> None:
        filters = (
            self.filter_reg_comboBox.currentText(),
            self.filter_city_lineEdit.text(),
            self.filter_grnti_lineEdit.text(),
            self.filter_keywords_lineEdit.text()
        )
        cols = ['Округ', 'Город', 'ГРНТИ', 'Ключевые слова']
        
        filter_string: str = self.varify_filter(filters, cols)
        if filter_string:
            self.init_table.setModel(pandasModel(self.settings_dict[self.cur_name]['df'].query(filter_string)))
        else:
            self.init_table.setModel(pandasModel(self.settings_dict[self.cur_name]['df']))
        self.filter_widget.setHidden(True)
    
    
    def reset_filter_widget(self) -> None:
        self.filter_reg_comboBox.setCurrentIndex(0),
        self.filter_city_lineEdit.setText(''),
        self.filter_grnti_lineEdit.setText(''),
        self.filter_keywords_lineEdit.setText('')


# pd.DataFrame.join()
# self.df_ntp.join(self.df_reg.set_index('Город').drop('Округ'), on='Город')
# .join(self.df_grnti.set_index('Код'), on='ГРНТИ')
# self.df_grnti