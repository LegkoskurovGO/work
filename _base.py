from exit import Ui_MainWindow
from confirm_window import Ui_Dialog

from PyQt6 import uic
from PyQt6.QtWidgets import QMainWindow, QDialog, QTableView, QWidget, QLineEdit
from PyQt6.QtCore import QAbstractTableModel, Qt, QRect, QSettings
from PyQt6.QtGui import QShortcut, QKeySequence

import os
import pandas as pd
from pandas.api.types import is_datetime64_any_dtype

pd.set_option('future.no_silent_downcasting', True)


class pandasModel(QAbstractTableModel):
    def __init__(self, data: pd.DataFrame):
        QAbstractTableModel.__init__(self)
        
        self.init_data = data
        for col in data.columns:
            if is_datetime64_any_dtype(data[col]):
                data[col] = data[col].dt.strftime('%d-%b-%y')
        self._data = data.fillna('')
        
    def rowCount(self, parent=None): return self._data.shape[0]
    def columnCount(self, parnet=None): return self._data.shape[1]
    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if index.isValid() and role == Qt.ItemDataRole.DisplayRole:
            return str(self._data.iloc[index.row(), index.column()])
        return None
    def headerData(self, col, orientation, role):
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return self._data.columns[col]
        return None


class Ui_Dialog2(QDialog, Ui_Dialog):
    def __init__(self, string):
        QDialog.__init__(self)
        self.ui = uic.loadUi('confirm_window.ui', self)
        diag_label = {
            'add': 'Подтвердите добавление строчки',
            'edit': 'Подтвердите редактирование строчки',
            'delete': 'Подтвердите удаление строчки',
            'group': 'Введите имя группы'
        }
        self.confirmation_label.setText(diag_label[string])
        self.confirm_button.clicked.connect(self.accept)    # Подтверждение
        self.cancel_button.clicked.connect(self.reject)     # Отмена
        self.confirm_button.setShortcut('Ctrl+1')
        self.cancel_button.setShortcut('Ctrl+2')
        
        # TODO: Кастыль
        self.lfile_name = QLineEdit(self)
        self.lfile_name.setGeometry(QRect(40, 61, 441, 31))
        self.lfile_name.setObjectName("lfile_name")
        
        # Подключаем сигнал rejected к слоту
        self.accepted.connect(self.on_close)

    def on_close(self):
        # Читаем значения из объектов диалога
        settings = QSettings("MyCompany", "MyApp")
        settings.setValue("file_name", self.lfile_name.text()) # Сохраняем значение





class Base_Class(QMainWindow, Ui_MainWindow):

    def __init__(self):
        QMainWindow.__init__(self)
        self.ui = uic.loadUi('exit.ui', self) 
        
        # Загружаем все данные в формате pd.DataFrame
        self.df_ntp, self.df_reg, self.df_grnti = self.load_data('data')
        
        # Записываем переменные
        self.settings_dict = self.get_settings()
        self.cur_name: str = 'empty'
        # self.save_abc()
    
    
    def app_exit(self) -> None: 
        exit()
    def start_position(self) -> None:
        
        self.empty_page = QWidget()
        self.empty_page.setObjectName("empty_page")
        self.stackedWidget.addWidget(self.empty_page)
        
        self.stackedWidget.setCurrentWidget(self.empty_page)
        self.filter_widget.setHidden(True)
        self.addexpert_widget.setHidden(True)
        self.edit_widget.setHidden(True)
        self.statusbar.setHidden(True)
        self.warning_addexpert_label.setHidden(True)
              
        

    def load_data(self, dir_name: str) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        if not os.path.isdir(os.path.join('.', dir_name)):
            print(f'Нет папки {dir_name} с данными')
            return
        # Загружаем данные
        params = {'dtype': { 'Номер': 'int16', 'Участие': 'int8'}, 'parse_dates': [7], 'date_format': '%d-%b-%y'}
        
        df_ntp = pd.read_csv(os.path.join('.', dir_name, 'Expert.csv'), **params, delimiter=';')
        df_reg = pd.read_csv(os.path.join('.', dir_name, 'Reg_obl_city.csv'), delimiter=';')
        df_grnti = pd.read_csv(os.path.join('.', dir_name, 'grntirub.csv'))
        
        # Расшифровка
        self.dict_grnti = {int(k):v for k,v in zip(df_grnti['Код'].tolist(), df_grnti['Расшифровка'].tolist())}
        df_ntp['Расшифровка'] = df_ntp['ГРНТИ'].str.split(r', ').map(lambda num: ', '.join(dict.fromkeys([self.dict_grnti.get(int(n.split(r'.')[0]), '') for n in num])))
        # Регион
        # TODO: Кастыль
        self.dict_reg = {k:v for k,v in zip(df_reg['Город'].tolist(), df_reg['Регион'].tolist())} 
        df_ntp = pd.merge(df_ntp, df_reg.drop('Округ', axis=1), how='left', on='Город')
        # Округ
        df_ntp = pd.merge(df_ntp.drop('Округ', axis=1), df_reg.drop('Регион', axis=1), how='left', on='Город')
        df_ntp = df_ntp[['Номер', 'ФИО', 'Округ', 'Регион', 'Город', 'ГРНТИ', 'Расшифровка', 'Ключевые слова', 'Участие', 'Дата добавления']]
        
        return df_ntp, df_reg, df_grnti
    
    
    
    def btn_connect(self) -> None:
        self.ntp_show.triggered.connect(lambda: self.show_table('ntp'))
        self.reg_show.triggered.connect(lambda: self.show_table('reg'))
        self.grnti_show.triggered.connect(lambda: self.show_table('grnti'))
        self.close_button.clicked.connect(lambda: self.show_table('empty'))
        
        self.filter_button.clicked.connect(lambda: self.show_filter_widget(False))
        self.filter_close_button.clicked.connect(lambda: self.show_filter_widget(True))
        self.filter_apply_button.clicked.connect(self.apply_filter_widget)
        self.filter_reset_button.clicked.connect(self.reset_filter_widget)
        
        self.add_button.clicked.connect(lambda: self.show_add_widget(False))
        self.addexpert_close_button_.clicked.connect(lambda: self.show_add_widget(True))
        self.addexpert_apply_button.clicked.connect(lambda: self.open_dialog('add'))
        
        self.edit_button.clicked.connect(lambda: self.show_edit_widget(False))
        self.edit_close_button.clicked.connect(lambda: self.show_edit_widget(True))
        self.edit_apply_button.clicked.connect(lambda: self.open_dialog('edit'))
        
        self.delete_button.clicked.connect(lambda: self.open_dialog('delete'))
        
        self.add_expert_button.clicked.connect(lambda: self.open_dialog('group'))
    
    
    
    def keyboard_connect(self) -> None:
        self.ntp_show.setShortcut('Ctrl+1')
        self.reg_show.setShortcut('Ctrl+2')
        self.grnti_show.setShortcut('Ctrl+3')
        self.close_button.setShortcut('Ctrl+w')
        self.filter_close_button.setShortcut('Ctrl+v')
        self.addexpert_close_button_.setShortcut('Ctrl+v')
        self.edit_close_button.setShortcut('Ctrl+v')
        QShortcut(QKeySequence('Ctrl+q'), self).activated.connect(self.app_exit)
        
    
    
    def get_settings(self) -> dict:
        return  {
            'ntp': {
                'df': self.df_ntp.copy(),
                'mode': QTableView.SelectionMode.MultiSelection,
                'behave': QTableView.SelectionBehavior.SelectRows,
                'label': 'Эксперты НТП'
            },
            'reg': {
                'df': self.df_reg.copy(),
                'mode': QTableView.SelectionMode.NoSelection,
                'behave': QTableView.SelectionBehavior.SelectItems,
                'label': 'Справочник по регионам'
            },
            'grnti': {
                'df': self.df_grnti.copy(),
                'mode': QTableView.SelectionMode.NoSelection,
                'behave': QTableView.SelectionBehavior.SelectItems,
                'label': 'Код рубрики (ГРНТИ)'
            }
        }




    # def load_data(self, dir_name: str) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    #     if not os.path.isdir(os.path.join('.', dir_name)):
    #         print(f'Нет папки {dir_name} с данными')
    #         return
        
    #     # Загружаем данные
    #     params = {'dtype': { 'kod': 'int16', 'take_part': 'int8'}, 'parse_dates': [7], 'date_format': '%d-%b-%y'}
        
    #     df_ntp = pd.read_csv(os.path.join('.', dir_name, 'Expert.csv'), **params)
    #     df_reg = pd.read_csv(os.path.join('.', dir_name, 'Reg_obl_city.csv'))
    #     df_grnti = pd.read_csv(os.path.join('.', dir_name, 'grntirub.csv'))
        
    #     # Преобразование значений 
    #     df_ntp['grnti'] = df_ntp['grnti'].str.split(r'; |, |. | ;| ,| .|;|,| ').map(lambda x: ', '.join(x)).str.rstrip('.')
    #     list_key_words = ['Специалист', 'Профессионал', 'Эксперт', 'Научный сотрудник', 'Академик', '', '', '', '']
    #     df_ntp['key_words'] = np.random.choice(list_key_words, df_ntp.shape[0])
        
    #     # Переименование столбцов
    #     df_ntp.columns = ['Номер', 'ФИО', 'Округ', 'Город', 'ГРНТИ', 'Ключевые слова', 'Участие', 'Дата добавления']
    #     df_reg.columns = ['Округ', 'Регион', 'Город']
    #     df_grnti.columns = ['Код', 'Расшифровка']
        
    #     # Меняем индексацию по первичному ключу Номер
    #     # df_ntp = df_ntp.set_index('Номер')
        
    #     return df_ntp, df_reg, df_grnti
    # def save_abc(self):
    #     self.df_ntp.to_csv('./data2/Expert.csv', index=False, encoding="utf-8", date_format='%d-%b-%y')
    #     self.df_reg.to_csv('./data2/Reg_obl_city.csv', index=False, encoding="utf-8", date_format='%d-%b-%y')
    #     self.df_grnti.to_csv('./data2/grntirub.csv', index=False, encoding="utf-8", date_format='%d-%b-%y')