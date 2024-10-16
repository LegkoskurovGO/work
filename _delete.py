from _base import Base_Class, pandasModel
from _edit import Edit_Row

class Delete_rows(Base_Class):
    
    def before_delete_widget(self):
        return len(Edit_Row.rows_selected(self)) > 0
    
    def apply_delete_widget(self) -> None:
        sr = Edit_Row.rows_selected(self)
        rows = self.init_table.model().init_data.iloc[sr, :]
        ids = self.settings_dict[self.cur_name]['df'].query('`Номер` == @rows["Номер"].to_list()').index.to_list()
        
        self.settings_dict[self.cur_name]['df'] = self.settings_dict[self.cur_name]['df'].drop(ids)
        self.df_ntp = self.df_ntp.drop(ids)
        self.init_table.setModel(pandasModel(self.settings_dict[self.cur_name]['df']))