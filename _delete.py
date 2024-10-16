from _base import Base_Class, pandasModel
from _edit import Edit_Row

from PyQt6.QtCore import QTimer

class Delete_rows(Base_Class):
    
    def __init__(self):
        self.warning_delete_label.setHidden(True)
    
    def before_delete_widget(self):
        if len(Edit_Row.rows_selected(self)) > 0:
            self.warning_delete_label.setHidden(True)
            return True
        else: 
            self.warning_delete_label.setHidden(False)
            QTimer.singleShot(3000, lambda: self.warning_delete_label.setHidden(True))
            return False
    
    def apply_delete_widget(self) -> None:
        sr = Edit_Row.rows_selected(self)
        rows = self.init_table.model().init_data.iloc[sr, :]
        ids = self.settings_dict[self.cur_name]['df'].query('`Номер` == @rows["Номер"].to_list()').index.to_list()
        
        self.settings_dict[self.cur_name]['df'] = self.settings_dict[self.cur_name]['df'].drop(ids)
        self.df_ntp = self.df_ntp.drop(ids)
        self.init_table.setModel(pandasModel(self.settings_dict[self.cur_name]['df']))