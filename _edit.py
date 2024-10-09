from _base import Base_Class, pandasModel

from PyQt6.QtWidgets import QTableView
from PyQt6.QtCore import QRegularExpression
from PyQt6.QtGui import QRegularExpressionValidator

import pandas as pd
import re

class Edit_Row(Base_Class):
    
    def fill_edit_lineEdit(self) -> None:
        cbv = self.df_ntp['Округ'].unique().tolist()
        self.edit_reg_comboBox.clear()
        self.edit_reg_comboBox.addItems(cbv)
    
    def show_edit_widget(self, hide: bool) -> None: 
        if not hide and len(sr := self.rows_selected()) != 1:
            return
        elif hide:
            self.edit_widget.setHidden(hide)
            self.fill_edit_lineEdit()
            self.init_table.setSelectionMode(self.settings_dict[self.cur_name]['mode'])
        else:
            old_row = self.init_table.model().init_data.iloc[sr[0], :].fillna('')
            
            self.init_table.setSelectionMode(QTableView.SelectionMode.NoSelection)
            
            # Заполняем поля значениями выбранной строчки
            self.edit_name_lineEdit.setText(old_row['ФИО'])
            
            cbv = self.df_ntp['Округ'].unique().tolist()
            self.edit_reg_comboBox.setCurrentIndex(cbv.index(old_row['Округ']))
            
            self.edit_city_lineEdit.setText(old_row['Город'])
            
            validator_grnti = QRegularExpressionValidator()
            validator_grnti.setRegularExpression(QRegularExpression(r'^\d{1,2}(\.\d{2}(\.\d{2})?)?(((\,|\;| ){1} *){1}\d{1,2}(\.\d{2}(\.\d{2})?)?)?$'))
            self.edit_grnti_lineEdit.setValidator(validator_grnti)
            self.edit_grnti_lineEdit.setText(old_row['ГРНТИ'])
            
            self.edit_keywords_lineEdit.setText(old_row['Ключевые слова'])
            
            self.edit_widget.setHidden(hide)
    
    
    def apply_edit_widget(self):
        # ['Номер', 'ФИО', 'Округ', 'Город', 'ГРНТИ', 'Ключевые слова', 'Участие', 'Дата добавления']
        sr = self.rows_selected()
        old_row = self.init_table.model().init_data.iloc[sr[0], :]
        
        grntis = ['0'*(len(i.split(r'.')[0]) % 2) + i for i in self.edit_grnti_lineEdit.text().split(r', ')]
        
        new_row = pd.Series(
            [
            old_row['Номер'],
            self.edit_name_lineEdit.text(),
            self.edit_reg_comboBox.currentText(),
            self.dict_reg.get(self.edit_city_lineEdit.text(), ''), # self.edit_region_comboBox
            self.edit_city_lineEdit.text(),
            self.edit_grnti_lineEdit.text(),
            ', '.join(dict.fromkeys([raschif for num in grntis if (raschif := self.dict_grnti.get(num, ''))])), 
            self.edit_keywords_lineEdit.text(),
            old_row['Участие'],
            old_row['Дата добавления']
            ], 
            index=old_row.index
        )
        if self.varify_edding_row(new_row, old_row):
            id = self.settings_dict[self.cur_name]['df'].query('`Номер` == @old_row["Номер"]').index.to_list()[0]
            self.settings_dict[self.cur_name]['df'].iloc[id, :] = new_row
            self.init_table.model().init_data.iloc[sr[0], :] = new_row
            
            self.init_table.setModel(pandasModel(self.init_table.model().init_data))
            self.edit_widget.setHidden(True)
            self.init_table.setSelectionMode(self.settings_dict[self.cur_name]['mode'])


    
    def rows_selected(self) -> list:
        return list(set(i.row() for i in self.init_table.selectedIndexes()))
    
    
    
    def varify_edding_row(self, new_row, old_row) -> bool:
        if not (bool(re.match(r'^[А-Яа-я\s\.]+$', new_row['ФИО'])) and bool(re.match(r'^[А-Яа-я\s\.]+$', new_row['Город']))):
            return False
        query_string = r'`ФИО` == @new_row["ФИО"] and `Округ` == @new_row["Округ"] and `Город` == @new_row["Город"] and `ГРНТИ` == @new_row["ГРНТИ"] and `Ключевые слова` == @new_row["Ключевые слова"]'
        return not (~new_row.loc[['ФИО', 'Округ', 'Город', 'ГРНТИ']].astype(bool)).sum() and self.settings_dict[self.cur_name]['df'].query(query_string).empty
        edding_row = (
            self.edit_name_lineEdit.text(),
            self.edit_reg_comboBox.currentText(),
            self.edit_city_lineEdit.text(),
            self.edit_grnti_lineEdit.text(),
            self.edit_keywords_lineEdit.text()
        )
            
            
