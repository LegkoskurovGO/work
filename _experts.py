from _base import Base_Class, pandasModel, Ui_Dialog2
from _edit import Edit_Row

from PyQt6.QtCore import QSettings
from PyQt6.QtWidgets import QTableView
from PyQt6 import QtWidgets, QtCore

import os
import pandas as pd

class Experts(Base_Class):
    
    def groups_show(self) -> None:
        self.stackedWidget.setCurrentIndex(1)
        self.show_group_table()
    
    def show_group_table(self, group_name='abc') -> None:
        file_path = os.path.join('.', 'groups', 'names.txt')
        
        # Определение следующего свободного номера файла
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                for line in f:
                    if group_name.strip() == line.split(",")[1].strip():
                        file_name = line.split(",")[0].strip()
        else: raise NameError
        df = self.load_groups(file_name)
        self.work_table.setModel(pandasModel(df))
        self.work_table.setSelectionMode(QTableView.SelectionMode.ExtendedSelection)
        self.work_table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.table_name_label.setText(group_name)
        self.work_table.resizeColumnsToContents()
        self.init_table.setSortingEnabled(True)
        self.flag_sort: bool = True
        self.col_sort: int = 0
        self.work_table.horizontalHeader().sectionClicked.connect(self.sort_table_expert)
        rows, cols = df.shape
        self.check_table.setColumnCount(1)
        self.check_table.setRowCount(rows)
        self.check_table.verticalHeader().setVisible(False)
        self.check_table.setHorizontalHeaderLabels(['Включить эксперта'])
        for row in range(rows):
            # item = QtWidgets.QTableWidgetItem()
            # checkbox = QtWidgets.QCheckBox()
            checkbox = QtWidgets.QTableWidgetItem()
            # checkbox.setStyleSheet('QCheckBox:{margin: 10px;}')
            # checkbox.stateChanged.connect(lambda state, row=row: self.checkbox_state_changed(state, row))
            # item.setData(QtCore.Qt.ItemDataRole.CheckStateRole, QtCore.Qt.CheckState.Unchecked)
            # item.setData(QtCore.Qt.ItemDataRole.UserRole, checkbox)
            checkbox.setFlags(QtCore.Qt.ItemFlag.ItemIsUserCheckable | QtCore.Qt.ItemFlag.ItemIsEnabled)
            checkbox.setCheckState(QtCore.Qt.CheckState.Unchecked) 
            self.check_table.setItem(row, 0, checkbox)
            # self.check_table.setItem(row, 0, item)
        self.check_table.verticalScrollBar().valueChanged.connect(self.sync_scroll)
        self.work_table.verticalScrollBar().valueChanged.connect(self.sync_scroll)
        
        self.check_table.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.work_table.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        self.check_table.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.work_table.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
    
    def checkbox_state_changed(self, state, row):
        item = self.check_table.item(row, 0)
        checkbox = item.data(QtCore.Qt.ItemDataRole.UserRole)
        if state == QtCore.Qt.CheckState.Checked:
            item.setData(QtCore.Qt.ItemDataRole.CheckStateRole, QtCore.Qt.CheckState.Checked)
        else:
            item.setData(QtCore.Qt.ItemDataRole.CheckStateRole, QtCore.Qt.CheckState.Unchecked)
    
    def sync_scroll(self, value):
        """Синхронизация скроллинга"""
        self.check_table.verticalScrollBar().setValue(value)
        self.work_table.verticalScrollBar().setValue(value)
        
    
    def sort_table_expert(self, col: int) -> None:
        if self.col_sort == col:
            self.flag_sort = not self.flag_sort
        else:
            self.flag_sort = True
        self.col_sort = col
        a = self.work_table.model().init_data
        a = a.sort_values(by=a.columns[col], axis=0, ascending=self.flag_sort)
        self.work_table.model().init_data = a
        self.work_table.setModel(pandasModel(self.work_table.model().init_data))
        return
    
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
    
    
    def load_groups(self, file_name) -> pd.DataFrame:
        # file_name = os.path.join('.', 'groups', f"group{name}.csv")
        params = {'dtype': { 'kod': 'int16', 'take_part': 'int8'}, 'parse_dates': [9], 'date_format': '%d-%b-%y'}
        df = pd.read_csv(file_name, **params).sort_values(by='Номер', axis=0, ascending=True)
        # df = pd.read_pickle(file_name)
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
                    file_numbers.append(int(os.path.split(line.split(',')[0])[1].split('group')[1].split('.')[0]))
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
        # df.to_pickle(file_name)

        # Запись имени файла и его русского названия в текстовый документ
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(f"{file_name},{group_name}\n")

    
        
    
    
# pd.DataFrame.to_csv(f'{name}.csv')