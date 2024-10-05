from _base import Base_Class, pandasModel

from PyQt6.QtCore import QRegularExpression, QTimer
from PyQt6.QtGui import QRegularExpressionValidator

import pandas as pd
from pandas.api.types import is_datetime64_any_dtype


class Add_Row(Base_Class):
    # ['Номер', 'ФИО', 'Округ', "Регион", 'Город', 'ГРНТИ', "Расшифровка", 'Ключевые слова', 'Участие', 'Дата добавления']
    
    def fill_add_widget(self) -> None:    
        validator_grnti = QRegularExpressionValidator()
        validator_grnti.setRegularExpression(QRegularExpression(r'^\d{2}\.\d{2}\,\ \d{2}\.\d{2}$'))
        self.addexpert_reg_comboBox.clear()
        self.addexpert_reg_comboBox.addItems([''] + sorted(self.df_reg['Округ'].unique()))
        self.addexpert_grnti_lineEdit.setValidator(validator_grnti)
        self.addexpert_name_lineEdit.setPlaceholderText('Введите ФИО эксперта')
        self.addexpert_city_lineEdit.setPlaceholderText('Введите город эксперта')
        self.addexpert_grnti_lineEdit.setPlaceholderText('Введите ГРНТИ в формате:  00.00')
        self.addexpert_keywords_lineEdit.setPlaceholderText('Введите ключевые слова')
        
        self.addexpert_name_lineEdit.setStyleSheet("")
        self.addexpert_reg_comboBox.setStyleSheet("")
        self.addexpert_city_lineEdit.setStyleSheet("")
        self.addexpert_grnti_lineEdit.setStyleSheet("")
        self.addexpert_keywords_lineEdit.setStyleSheet("")
    
    
    def reset_add_widget(self) -> None:
        self.addexpert_reg_comboBox.setCurrentIndex(0)
        self.addexpert_name_lineEdit.setText('')
        self.addexpert_city_lineEdit.setText('')
        self.addexpert_grnti_lineEdit.setText('')
        self.addexpert_keywords_lineEdit.setText('')
        
        
    def show_add_widget(self, hide: bool) -> None: 
        self.addexpert_widget.setHidden(hide)
        self.fill_add_widget()
            
    
    def get_row_add_widget(self) -> pd.DataFrame:
        new_row = pd.Series([
            self.df_ntp['Номер'].max()+1,
            self.addexpert_name_lineEdit.text(),
            self.addexpert_reg_comboBox.currentText(),
            self.dict_reg.get(self.addexpert_city_lineEdit.text(), ''), # self.addexpert_region_comboBox
            self.addexpert_city_lineEdit.text(),
            self.addexpert_grnti_lineEdit.text(),
            self.dict_grnti.get(int(self.addexpert_grnti_lineEdit.text().split(r'.')[0]), ''),
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
        self.df_ntp = pd.concat([self.df_ntp, row], ignore_index=True)
        self.df_ntp = self.df_ntp.astype(self.df_ntp.dtypes)
        self.settings_dict[self.cur_name]['df'] = self.settings_dict[self.cur_name]['df'].astype(self.settings_dict[self.cur_name]['df'].dtypes)
        self.init_table.setModel(pandasModel(self.settings_dict[self.cur_name]['df']))
        self.init_table.scrollToBottom()
        self.reset_add_widget()
        self.addexpert_widget.setHidden(True)
    
    
    def is_unique_row(self, row: pd.Series) -> bool:
        query_string = r'`ФИО` == @row["ФИО"] and `Округ` == @row["Округ"] and `Город` == @row["Город"]'
        return not self.settings_dict[self.cur_name]['df'].query(query_string).empty
    
    def is_empty_filed(self, row: pd.Series) -> bool:
        return (~row.drop(['Ключевые слова', 'Участие']).astype(bool)).sum()
    
    
    def checkers_add_widget(self) -> bool:
        new_row = self.get_row_add_widget()
        
        if self.is_unique_row(new_row.iloc[0]):
            self.warning_addexpert_label.setHidden(False)
            QTimer.singleShot(3000, lambda: self.warning_addexpert_label.setHidden(True))
            return False
        
        if self.is_empty_filed(new_row.iloc[0]):
            if self.addexpert_reg_comboBox.currentText() == '':
                self.addexpert_reg_comboBox.setStyleSheet("border: 1px solid red;")
            for i in ['name', 'city', 'grnti']:
                if getattr(self, f'addexpert_{i}_lineEdit').text() == '':
                    getattr(self, f'addexpert_{i}_lineEdit').setStyleSheet("border: 1px solid red;")
                else:
                    getattr(self, f'addexpert_{i}_lineEdit').setStyleSheet("")
            return False
        
        return True
    
    def apply_add_widget(self) -> None:
        new_row = self.get_row_add_widget()
        self.add_row(new_row)
