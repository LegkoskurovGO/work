from _base import Base_Class, pandasModel

import os
import pandas as pd

from PyQt6.QtCore import QRect

class Table_Methods(Base_Class):
    
    def __init__(self):
        self.init_table.setSortingEnabled(True)
        self.flag_sort: bool = True
        self.col_sort: int = 0
        self.init_table.horizontalHeader().sectionClicked.connect(self.sort_table)
        
    #     # Настройка выделения строк
    #     self.init_table.selectionModel().selectionChanged.connect(self.on_selection_changed)

    # def on_selection_changed(self, selected, deselected):
    #     """Срабатывает при изменении выделения строк"""
    #     if len(selected.indexes()) > 0:
    #         # Выделение нескольких строк уже обрабатывается SelectionMode.ExtendedSelection
    #         pass
    #     else:
    #         self.init_table.selectionModel().clearSelection()

    
    
    def show_table(self, name: str) -> None:
        self.cur_name = name
        if name == 'empty':
            self.stackedWidget.setCurrentWidget(self.empty_page)
            return
        if name in ['reg', 'grnti']:
            self.add_widget.setHidden(True)
            self.addexpert_widget.setHidden(True)
            self.edit_widget.setHidden(True)
            self.filter_widget.setHidden(True)
            self.ramka1.setHidden(True)
            self.ramka2.setHidden(True)
        else:
            self.add_widget.setHidden(False)
            self.addexpert_widget.setHidden(True)
            self.edit_widget.setHidden(True)
            self.filter_widget.setHidden(True)
            self.ramka1.setHidden(False)
            self.ramka2.setHidden(False)
        df_ = self.settings_dict[name]
        self.init_table.setModel(pandasModel(df_['df']))
        self.init_table.setSelectionMode(df_['mode'])
        self.init_table.setSelectionBehavior(df_['behave'])
        self.init_tablename.setText(df_['label'])
        self.init_table.resizeColumnsToContents()
        # total_width = sum(self.init_table.columnWidth(i) for i in range(len(df_['df'].columns)))
        # if total_width < 1000: self.init_table.setGeometry(QRect(25, 80, total_width+21, 651))
        self.stackedWidget.setCurrentIndex(0)
    
    
    
    # def read_table(self, pkl_path: str) -> tuple[pd.DataFrame|None, bool]:
    #     if os.path.isfile(pkl_path):
    #         return pd.read_pickle(pkl_path), True
    #     else:
    #         return None, False 
    
    
    def sort_table(self, col: int) -> None:
        if self.col_sort == col:
            self.flag_sort = not self.flag_sort
        else:
            self.flag_sort = True
        self.col_sort = col
        a = self.init_table.model().init_data
        a = a.sort_values(by=a.columns[col], axis=0, ascending=self.flag_sort)
        self.init_table.model().init_data = a
        self.init_table.setModel(pandasModel(self.init_table.model().init_data))
        return