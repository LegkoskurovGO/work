from _base import Base_Class, pandasModel

from PyQt6.QtCore import QRegularExpression
from PyQt6.QtGui import QRegularExpressionValidator

import pandas as pd
from pandas.api.types import is_datetime64_any_dtype


class Add_Row(Base_Class):
    
    
    def fill_add_lineEdit(self) -> None:    
        validator_grnti = QRegularExpressionValidator()
        validator_grnti.setRegularExpression(QRegularExpression(r'^\d{2}\.\d{2}\,\ \d{2}\.\d{2}$'))
        self.addexpert_reg_comboBox.clear()
        self.addexpert_reg_comboBox.addItems([''] + sorted(self.df_reg['Округ'].unique()))
        self.addexpert_grnti_lineEdit.setValidator(validator_grnti)
        self.addexpert_name_lineEdit.setPlaceholderText('ФИО')
        self.addexpert_city_lineEdit.setPlaceholderText('Город')
        self.addexpert_grnti_lineEdit.setPlaceholderText('ГРНТИ в формате:  00.00')
        self.addexpert_keywords_lineEdit.setPlaceholderText('Ключевые слова')
    
    
    def reset_add_widget(self) -> None:
        self.addexpert_reg_comboBox.setCurrentIndex(0)
        self.addexpert_name_lineEdit.setText('')
        self.addexpert_city_lineEdit.setText('')
        self.addexpert_grnti_lineEdit.setText('')
        self.addexpert_keywords_lineEdit.setText('')
        
        
    def show_addexpert_widget(self, hide: bool) -> None: 
        self.addexpert_widget.setHidden(hide)
        self.fill_add_lineEdit()
    
    
    def varify_adding_row(self, row: pd.Series) -> bool:
        # ['ФИО', 'Округ', 'Город', 'ГРНТИ', 'Ключевые слова']
        query_string = r'`ФИО` == @row["ФИО"] and `Округ` == @row["Округ"] and `Город` == @row["Город"]'
        return not (~row.drop(['Ключевые слова', 'Участие']).astype(bool)).sum()  and self.settings_dict[self.cur_name]['df'].query(query_string).empty
            
        
    def add_row(self, row: pd.DataFrame) -> None:
        # ['Номер', 'ФИО', 'Округ', 'Город', 'ГРНТИ', 'Ключевые слова', 'Участие', 'Дата добавления']
        self.settings_dict[self.cur_name]['df'] = pd.concat([self.settings_dict[self.cur_name]['df'], row], ignore_index=True)
        self.df_ntp = pd.concat([self.df_ntp, row], ignore_index=True)
        self.df_ntp = self.df_ntp.astype(self.df_ntp.dtypes)
        self.settings_dict[self.cur_name]['df'] = self.settings_dict[self.cur_name]['df'].astype(self.settings_dict[self.cur_name]['df'].dtypes)
        self.init_table.setModel(pandasModel(self.settings_dict[self.cur_name]['df']))
        self.init_table.scrollToBottom()
        self.reset_add_widget()
    
    
    def apply_add_widget(self) -> None:
        new_row = pd.Series([
            self.df_ntp['Номер'].max()+1,
            self.addexpert_name_lineEdit.text(),
            self.addexpert_reg_comboBox.currentText(),
            self.addexpert_city_lineEdit.text(),
            self.addexpert_grnti_lineEdit.text(),
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
        if self.varify_adding_row(new_row.iloc[0]):
            self.add_row(new_row)
            self.addexpert_widget.setHidden(True)