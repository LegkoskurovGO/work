from _base import Base_Class, pandasModel

from PyQt6.QtWidgets import QTableView
from PyQt6.QtCore import QRegularExpression
from PyQt6.QtGui import QRegularExpressionValidator

import pandas as pd
import re

class Edit_Row(Base_Class):
    
    def __init__(self):
        # Placeholder
        self.edit_name_lineEdit.setPlaceholderText('ФИО эксперта')
        self.edit_grnti_lineEdit.setPlaceholderText('Формат: 00.00.00')
        self.edit_grnti2_lineEdit.setPlaceholderText('Формат: 00.00.00')
        self.edit_keywords_lineEdit.setPlaceholderText('Ключевые слова через запятую:')
        # Валидация
        self.edit_name_lineEdit.setValidator(self.validator_name)
        self.edit_grnti_lineEdit.setValidator(self.validator_grnti)
        self.edit_grnti2_lineEdit.setValidator(self.validator_grnti)
        self.edit_keywords_lineEdit.setValidator(self.validator_multi)
        # Заполнение CheckBox
        self.edit_reg_comboBox.clear()
        self.edit_reg_comboBox.addItems([''] + sorted(self.df_reg['Округ'].unique()))
        self.edit_region_comboBox.clear()
        self.edit_region_comboBox.addItems([''] + sorted(self.df_reg['Регион'].unique()))
        self.edit_city_comboBox.clear()
        self.edit_city_comboBox.addItems([''] + sorted(self.df_reg['Город'].unique()))
    
    
    def fill_edit_lineEdit(self, row: pd.Series) -> None:
        # 'ФИО', 'Округ', 'Город', 'ГРНТИ', 'ГРНТИ', 'Ключевые слова'
        self.edit_name_lineEdit.setText(row['ФИО'])
        self.edit_reg_comboBox.setCurrentText(row['Округ'])
        self.edit_region_comboBox.setCurrentText(row['Регион'])
        self.edit_city_comboBox.setCurrentText(row['Город'])
        self.edit_grnti_lineEdit.setText(row['ГРНТИ'].split(', ')[0])
        if len(row['ГРНТИ'].split(', ')) > 1:
            self.edit_grnti2_lineEdit.setText(row['ГРНТИ'].split(', ')[1])
        else:
            self.edit_grnti2_lineEdit.setText('')
        self.edit_keywords_lineEdit.setText(row['Ключевые слова'])
    
    
    def show_edit_widget(self, hide: bool) -> None: 
        if not hide and len(sr := self.rows_selected()) != 1:
            return
        elif hide:
            self.edit_widget.setHidden(hide)
            self.reset_edit_widget()
            self.init_table.setSelectionMode(self.settings_dict[self.cur_name]['mode'])
        else:
            old_row = self.init_table.model().init_data.iloc[sr[0], :].fillna('')
            self.init_table.setSelectionMode(QTableView.SelectionMode.NoSelection)
            self.fill_edit_lineEdit(old_row)
            self.edit_widget.setHidden(hide)
    
    
    def apply_edit_widget(self):
        # ['Номер', 'ФИО', 'Округ', 'Город', 'ГРНТИ', 'Ключевые слова', 'Участие', 'Дата добавления']
        sr = self.rows_selected()
        old_row = self.init_table.model().init_data.iloc[sr[0], :]
        
        # Формирование ГРНТИ
        grntis = sorted((str(self.edit_grnti_lineEdit.text()), str(self.edit_grnti2_lineEdit.text())))
        str_grntis = ''
        for item in grntis:
            if item:
                if str_grntis: str_grntis += ', '
            str_grntis += item
        
        new_row = pd.Series([
            old_row['Номер'],
            self.edit_name_lineEdit.text(),
            self.edit_reg_comboBox.currentText(),
            self.edit_region_comboBox.currentText(),
            self.edit_city_comboBox.currentText(),
            str_grntis,
            ', '.join(dict.fromkeys([raschif for num in grntis if (raschif := self.dict_grnti.get(num, ''))])), 
            self.edit_keywords_lineEdit.text(),
            old_row['Участие'],
            old_row['Дата добавления']
        ], 
        index=old_row.index
        )
        print(f'edit: {new_row['ГРНТИ'] = }')
        if self.varify_edding_row(new_row):
            id = self.settings_dict[self.cur_name]['df'].query('`Номер` == @old_row["Номер"]').index.to_list()[0]
            self.settings_dict[self.cur_name]['df'].iloc[id, :] = new_row
            self.init_table.model().init_data.iloc[sr[0], :] = new_row
            
            self.init_table.setModel(pandasModel(self.init_table.model().init_data))
            self.edit_widget.setHidden(True)
            self.init_table.setSelectionMode(self.settings_dict[self.cur_name]['mode'])


    
    def rows_selected(self) -> list:
        return list(set(i.row() for i in self.init_table.selectedIndexes()))
    
    
    def before_edit_widget(self):
        return len(self.rows_selected()) == 1
    
    
    def varify_edding_row(self, row: pd.Series) -> bool:        
        query_string = r'`ФИО` == @row["ФИО"] and `Город` == @row["Город"] and `ГРНТИ` == @row["ГРНТИ"] and `Ключевые слова` == @row["Ключевые слова"]'
        flag = (
            bool(re.match(self.regex_grntis, row['ГРНТИ'])),
            not (~row.loc[['ФИО', 'Округ', 'Регион', 'Город', 'ГРНТИ']].astype(bool)).sum(),
            self.settings_dict[self.cur_name]['df'].query(query_string).empty
        )
        return all(flag)
            
            
    def reset_edit_widget(self) -> None:
        self.edit_name_lineEdit.setText('')
        self.edit_reg_comboBox.setCurrentText('')
        self.edit_region_comboBox.setCurrentText('')
        self.edit_city_comboBox.setCurrentText('')
        self.edit_grnti_lineEdit.setText('')
        self.edit_grnti2_lineEdit.setText('')
        self.edit_keywords_lineEdit.setText('')