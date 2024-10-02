from _base import Base_Class, pandasModel
from _edit import Edit_Row

class Delete_rows(Base_Class):
    
    def delete_selected_rows(self) -> None:
        sr = Edit_Row.rows_selected(self)
        rows = self.init_table.model().init_data.iloc[sr, :]
        ids = self.settings_dict[self.cur_name]['df'].query('`Номер` == @rows["Номер"].to_list()').index.to_list()
        
        if (self.approve_delete() and len(sr) > 0):
            self.settings_dict[self.cur_name]['df'] = self.settings_dict[self.cur_name]['df'].drop(ids)
            self.df_ntp = self.df_ntp.drop(ids)
            self.init_table.setModel(pandasModel(self.settings_dict[self.cur_name]['df']))
        
        
    def approve_delete(self) -> bool:
        return True