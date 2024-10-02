from _base import Base_Class, pandasModel

import os
import pandas as pd


class Table_Methods(Base_Class):
    
    def __init__(self):
        self.init_table.setSortingEnabled(True)
        self.flag_sort: bool = True
        self.col_sort: int = 0
        self.init_table.horizontalHeader().sectionClicked.connect(self.sort_table)
    
    
    def show_table(self, name: str) -> None:
        self.cur_name = name
        if name == 'empty':
            self.stackedWidget.setCurrentIndex(1)
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
        self.init_table.setModel(pandasModel(self.settings_dict[name]['df']))
        self.init_table.setSelectionMode(self.settings_dict[name]['mode'])
        self.init_table.setSelectionBehavior(self.settings_dict[name]['behave'])
        self.init_tablename.setText(self.settings_dict[name]['label'])
        self.init_table.resizeColumnsToContents()
        self.stackedWidget.setCurrentIndex(0)
    
    
    def save_table(self, name: str, df: pd.DataFrame) -> None:
        if not os.path.isdir(os.path.join('.', 'pickles')):
            os.mkdir(os.path.join('.', 'pickles'))
            
        if not os.path.isfile(pkl_path := os.path.join('.', 'pickles', f'{name}.pkl')):
            df.to_pickle(pkl_path)
        else:
            i = 1
            while os.path.isfile(pkl_path := os.path.join('.', 'pickles', f'{name}_{i}.pkl')):
                i += 1
            df.to_pickle(pkl_path)
    
    
    def read_table(self, pkl_path: str) -> tuple[pd.DataFrame|None, bool]:
        if os.path.isfile(pkl_path):
            return pd.read_pickle(pkl_path), True
        else:
            return None, False 
    
    
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