from _base import Base_Class, pandasModel, Ui_Dialog_lineEdit
from _edit import Edit_Row

from PyQt6.QtCore import QSettings
from PyQt6.QtWidgets import QTableView
from PyQt6 import QtWidgets, QtCore

import os
import pandas as pd

class Experts(Base_Class):
    
    def __init__(self):
        self.work_table.setSelectionMode(QTableView.SelectionMode.ExtendedSelection)
        self.work_table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.work_table.setSortingEnabled(True)
        self.flag_sort: bool = True
        self.col_sort: int = 0
        self.work_table.horizontalHeader().sectionClicked.connect(self.sort_table_expert)
    
    # -------------------- Загрузка --------------------
    
    def groups_show(self) -> None:
        settings = QSettings("MyCompany", "MyApp")
        group_name = settings.value("choose_comboBox") # Читаем значение
        file_name = self.dict_of_groups().get(group_name, False)
        
        if file_name:
            self.show_group_table(file_name, group_name)
            self.stackedWidget.setCurrentWidget(self.page)
    
    
    def show_group_table(self, file_name: str, group_name: str) -> None:
        file_path = os.path.join('.', 'groups', 'names.txt')

        df = self.load_groups(file_name)
        self.work_table.setModel(pandasModel(df))
        self.table_name_label.setText(group_name)
        self.work_table.resizeColumnsToContents()
        # Укорачивание столбца Расшифровка
        for id, col in enumerate(self.work_table.model().init_data.columns):
            if col == 'Расшифровка':
                self.work_table.setColumnWidth(id, 500); break
        self.setup_check_table(df)
        self.check_table.verticalScrollBar().valueChanged.connect(self.sync_scroll)
        self.work_table.verticalScrollBar().valueChanged.connect(self.sync_scroll)
        self.check_table.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.work_table.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.check_table.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.work_table.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        
    def load_groups(self, file_name) -> pd.DataFrame:
        # file_name = os.path.join('.', 'groups', f"group{name}.csv")
        params = {'dtype': { 'kod': 'int16', 'take_part': 'int8'}, 'parse_dates': [9], 'date_format': '%d-%b-%y'}
        df = pd.read_csv(file_name, **params).sort_values(by='Номер', axis=0, ascending=True)
        # df = pd.read_pickle(file_name)
        return df
    
    
    def setup_check_table(self, work_df: pd.DataFrame):
        rows, cols = work_df.shape
        self.check_table.setColumnCount(1)
        self.check_table.setRowCount(rows)
        self.check_table.verticalHeader().setVisible(False)
        self.check_table.setHorizontalHeaderLabels(['Включить'])
        for row in range(rows):
            # item = QtWidgets.QTableWidgetItem()
            # checkbox = QtWidgets.QCheckBox()
            # checkbox.setStyleSheet("QCheckBox::indicator{width:64px;}")
            # item.setData(QtCore.Qt.ItemDataRole.CheckStateRole, QtCore.Qt.CheckState.Unchecked)
            # item.setData(QtCore.Qt.ItemDataRole.UserRole, checkbox)
            # self.check_table.setItem(row, 0, item)
            # ------
            checkbox = QtWidgets.QCheckBox()
            checkbox.setStyleSheet("QCheckBox::indicator{width:59px;height:30px;}") 
            self.check_table.setCellWidget(row, 0, checkbox)
            self.check_table.setContentsMargins(0,0,0,0)
        self.check_table.resizeColumnsToContents()
        self.check_table.setGeometry(QtCore.QRect(1095, 70, 82, 620))
        self.check_table.setSelectionMode(QTableView.SelectionMode.NoSelection)
        # self.check_table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        
        
    def checkbox_state_changed(self, state, row):
        item = self.check_table.item(row, 0)
        if state == QtCore.Qt.CheckState.Checked:
            item.setData(QtCore.Qt.ItemDataRole.CheckStateRole, QtCore.Qt.CheckState.Checked)
        else:
            item.setData(QtCore.Qt.ItemDataRole.CheckStateRole, QtCore.Qt.CheckState.Unchecked)
    
    def sync_scroll(self, value):
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
        
        
    def before_group_widget(self):
        if not self.stackedWidget.currentWidget() == self.page_1:
            return True
        else:
            return len(Edit_Row.rows_selected(self)) > 0
    
    
    def dict_of_groups(self) -> dict:
        name_group_dict = dict()
        file_path = os.path.join('.', 'groups', 'names.txt')
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                name_group_dict = {','.join(line.split(',')[1:]).strip(): line.split(',')[0] for line in f}
        return name_group_dict
    
    
    # -------------------- Сохранение --------------------


    def save_group_widget(self) -> None:
        settings = QSettings("MyCompany", "MyApp")
        group_name = settings.value("name_lineEdit")

        if self.stackedWidget.currentWidget() == self.page_1:
            self.save_selected_rows(group_name)
        elif self.stackedWidget.currentWidget() == self.page:
            df = self.work_table.model().init_data
            self.save_dataframe_with_names(df, group_name)
        self.table_name_label.setText(group_name)
            
    
    def save_selected_rows(self, group_name: str):
        sr = Edit_Row.rows_selected(self)
        rows = self.init_table.model().init_data.iloc[sr, :]
        
        if self.approve_save(group_name):
            self.save_dataframe_with_names(rows, group_name)
    
    
    def approve_save(self, group_name) -> bool:
        if self.dict_of_groups().get(group_name, False):
            return False
        else:
            return True
            

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
        
        # # Определение наличие дубликатов
        # flag = True
        # if os.path.exists(file_path):
        #     with open(file_path, "r", encoding="utf-8") as f:
        #         for line in f:
        #             if group_name == ','.join(line.split(',')[1:]).strip():
        #                 flag = False
        # if not flag: return False

        # Формирование имени файла
        file_name = os.path.join('.', 'groups', f"group{next_number}.csv")

        # Сохранение DataFrame в файл CSV
        df.to_csv(file_name, index=False, encoding="utf-8", date_format='%d-%b-%y')
        # df.to_pickle(file_name)

        # Запись имени файла и его русского названия в текстовый документ
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(f"{file_name},{group_name}\n")


    # -------------------- Удаление --------------------
    
    
    def rows_selected_expert(self) -> list:
        return list(set(i.row() for i in self.work_table.selectedIndexes()))
    
    
    def before_delete_expert_widget(self):
        if not self.stackedWidget.currentWidget() == self.page:
            return False
        if len(self.rows_selected_expert()) > 0:
            # self.warning_delete_label.setHidden(True)
            return True
        else: 
            # self.warning_delete_label.setHidden(False)
            # QTimer.singleShot(3000, lambda: self.warning_delete_label.setHidden(True))
            return False
    
    
    def before_delete_expert_part_widget(self):
        if not self.stackedWidget.currentWidget() == self.page:
            return False
        else: 
            return True
    
    
    def erase_group(self):
        group_name = self.table_name_label.text()
        file_name = self.dict_of_groups().get(group_name)
        file_path = os.path.join('.', 'groups', 'names.txt')
        
        # Удаление файла
        os.remove(file_name)
        # Удаление группы из списка
        with open(file_path, 'r') as file:
            lines = file.readlines()
        with open(file_path, 'w') as file:
            for line in lines:
                if ','.join(line.strip().split(',')[1:]) != group_name:
                    file.write(line)
    
    
    def apply_delete_expert_widget(self):
        self.erase_group()
        self.stackedWidget.setCurrentWidget(self.page_1)
    
    
    def apply_delete_expert_part_widget(self) -> None:
        sr = self.rows_selected_expert()
        rows = self.work_table.model().init_data.iloc[sr, :]
        ids = self.work_table.model().init_data.query('`Номер` == @rows["Номер"].to_list()').index.to_list()
        
        df = self.work_table.model().init_data.drop(ids)
        
        if df.empty:
            self.apply_delete_expert_widget()
            return
        
        self.erase_group()
        
        group_name = self.table_name_label.text()
        self.save_dataframe_with_names(df, group_name)
        file_name = self.dict_of_groups().get(group_name)
        self.show_group_table(file_name, group_name)
        # sr = self.rows_selected_expert()
        # rows = self.work_table.model().init_data.iloc[sr, :]
        # ids = self.work_table.model().init_data.query('`Номер` == @rows["Номер"].to_list()').index.to_list()
        # df = self.work_table.model().init_data.drop(ids)
        
        # self.work_table.setModel(pandasModel(df))
        # self.setup_check_table(df)


    # -------------------- Объединение --------------------


    def merge_group_widget(self):
        settings = QSettings("MyCompany", "MyApp")
        group_name_new = settings.value("choose_comboBox") # Читаем значение
        file_name_new = self.dict_of_groups().get(group_name_new, False)
        df_new = self.load_groups(file_name_new)
        
        group_name_old = self.table_name_label.text()
        df_old = self.work_table.model().init_data
        df = pd.concat([df_old, df_new], ignore_index=True).drop_duplicates(subset=['Номер'], keep='last')
        df = df.sort_values(by='Номер', axis=0, ascending=True)

        group_name = f'{group_name_old}+{group_name_new}'
        
        self.save_dataframe_with_names(df, group_name)
        file_name = self.dict_of_groups().get(group_name, False)
        self.show_group_table(file_name, group_name)