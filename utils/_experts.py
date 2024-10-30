from utils._base import Base_Class, pandasModel
from utils._edit import Edit_Row

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
        df = self.load_groups(file_name)
        self.work_table.setModel(pandasModel(df))
        self.table_name_label.setText(group_name)
        self.work_table.resizeColumnsToContents()
        # Укорачивание столбца Расшифровка
        for id, col in enumerate(self.work_table.model().init_data.columns):
            if col == 'Расшифровка':
                self.work_table.setColumnWidth(id, 487); break
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
        self.check_table.setGeometry(QtCore.QRect(1095, 80, 82, 620))
        self.check_table.setSelectionMode(QTableView.SelectionMode.NoSelection)
        self.check_table.horizontalHeader().sectionClicked.connect(self.on_header_clicked)
        # self.check_table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        
    def on_header_clicked(self, *args):
        """Обработчик клика на заголовок столбца."""
        # Получаем все QCheckBox из таблицы
        checkboxes = [self.check_table.cellWidget(row, 0) for row in range(self.check_table.rowCount())]
        # Проверяем, проставлен ли флажок на всех QCheckBox
        all_checked = all(checkbox.isChecked() for checkbox in checkboxes)
        # Если все флажки проставлены, то снимаем их, иначе проставляем
        for checkbox in checkboxes: checkbox.setChecked(not all_checked)
    
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
        if self.stackedWidget.currentWidget() == self.page:
            rows = self.work_table.model().init_data
            if len(sr := self.rows_selected_expert()) > 1:
                rows = rows.iloc[sr, :]
            sr = sorted(rows['Номер'])
            settings = QSettings("MyCompany", "MyApp")
            settings.setValue("string_to_group", sr) # Сохраняем значение
            return True
        elif self.stackedWidget.currentWidget() == self.page_1:
            sr = Edit_Row.rows_selected(self)
            sr = sorted(self.init_table.model().init_data.iloc[sr, :]['Номер'])
            settings = QSettings("MyCompany", "MyApp")
            settings.setValue("string_to_group", sr) # Сохраняем значение
            return len(sr) > 0
    
    
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
            sr = Edit_Row.rows_selected(self)
            rows = self.init_table.model().init_data.iloc[sr, :]
        elif self.stackedWidget.currentWidget() == self.page:
            rows = self.work_table.model().init_data
            if len(sr := self.rows_selected_expert()) > 1:
                rows = rows.iloc[sr, :]
            else:
                self.erase_group()
        else:
            return
        self.save_dataframe_with_names(rows, group_name)
        self.table_name_label.setText(group_name)
    
    
    def save_or_new_group(self):
        match self.stackedWidget.currentWidget():
            case self.page:
                return 'save_group'
            case self.page_1 | _:
                return 'new_group'
    

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

        # Сохранение DataFrame в файл CSV
        df.to_csv(file_name, index=False, encoding="utf-8", date_format='%d-%b-%y')
        # df.to_pickle(file_name)

        # Запись имени файла и его русского названия в текстовый документ
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(f"{file_name},{group_name}\n")


    def dublicate_check(self, group_name):
        file_path = os.path.join('.', 'groups', 'names.txt')
        # Определение наличие дубликатов
        flag = True
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                for line in f:
                    if group_name.strip() == ','.join(line.split(',')[1:]).strip():
                        flag = False
        return flag

    # -------------------- Удаление --------------------
    
    
    def rows_selected_expert(self) -> list:
        return list(set(i.row() for i in self.work_table.selectedIndexes()))
    
    
    def before_delete_expert_part_widget(self):
        if not self.stackedWidget.currentWidget() == self.page:
            return False
        if len(sr := self.rows_selected_expert()) > 0:
            rows = self.work_table.model().init_data.iloc[sr, :]
            ids = sorted(rows['Номер'])
            settings = QSettings("MyCompany", "MyApp")
            settings.setValue("string_to_delete", ids) # Сохраняем значение
            # self.warning_delete_label.setHidden(True)
            return True
        else: 
            # self.warning_delete_label.setHidden(False)
            # QTimer.singleShot(3000, lambda: self.warning_delete_label.setHidden(True))
            return False
    
    
    def before_delete_expert_widget(self):
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
        file_name_new = self.dict_of_groups().get(group_name_new)
        df_new = self.load_groups(file_name_new)
        
        group_name_old = self.table_name_label.text()
        df_old = self.work_table.model().init_data
        df = pd.concat([df_old, df_new], ignore_index=True).drop_duplicates(subset=['Номер'], keep='last')
        df = df.sort_values(by='Номер', axis=0, ascending=True)

        group_name = f'{group_name_old}+{group_name_new}'
        
        self.table_name_label.setText(group_name)
        if self.dict_of_groups().get(group_name, False):
            self.erase_group()
        
        self.save_dataframe_with_names(df, group_name)
        file_name = self.dict_of_groups().get(group_name, False)
        self.show_group_table(file_name, group_name)


# -------------------- Утверждение --------------------


    def approve_group_final(self):
        # Булевый список строк
        checkboxes = [self.check_table.cellWidget(row, 0) for row in range(self.check_table.rowCount())]
        checked_rows = (checkbox.isChecked() for checkbox in checkboxes)
        
        sr = [row for row, flag in enumerate(checked_rows) if flag]
        df = self.work_table.model().init_data
        rows = df.iloc[sr, :]
        ids = self.df_ntp.query('`Номер` == @rows["Номер"].to_list()').index.to_list()
        # Сохраняем в основную таблицу 1
        self.df_ntp.loc[self.df_ntp['Номер'].isin(ids), 'Участие'] += 1
        self.settings_dict[self.cur_name]['df'] = self.df_ntp
        # Сохраняем в work таблицу 1
        df.loc[self.df_ntp['Номер'].isin(ids), 'Участие'] += 1
        group_name = self.table_name_label.text()
        self.erase_group()
        self.save_dataframe_with_names(df, group_name)
        file_name = self.dict_of_groups().get(group_name)
        self.show_group_table(file_name, group_name)