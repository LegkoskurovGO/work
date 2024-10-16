from exit import Ui_MainWindow
from confirm_window import Ui_Dialog

from PyQt6 import uic
from PyQt6.QtWidgets import QMainWindow, QDialog, QTableView, QLineEdit
from PyQt6.QtCore import QAbstractTableModel, Qt, QRect, QSettings, QRegularExpression
from PyQt6.QtGui import QShortcut, QKeySequence, QRegularExpressionValidator

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
        
        if string == 'group':
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
        self.regex_grnti = r'^(?:\d{2}(\.(\d{2}(\.(\d{2})?)?)?)?)$'
        self.regex_grntis = r'(?:^\d{2}(\.(\d{2}(\.(\d{2})?)?)?)?(\,\s\d{2}(\.(\d{2}(\.(\d{2})?)?)?)?)?)$'
        # Валидаторы
        self.validator_grnti = QRegularExpressionValidator(QRegularExpression(r'^(?:[\d\.]{2,8})$'))
        self.validator_name = QRegularExpressionValidator(QRegularExpression(r'^(?:[А-ЯЁа-яё\.\s]+)$'))
        self.validator_multi = QRegularExpressionValidator(QRegularExpression(r'^(?:[А-ЯЁа-яё\.\s\,]+)$'))
        # Сохранение изменённых данных
        # self.save_abc()
    
    
    def app_exit(self) -> None: 
        # shutil.rmtree(os.path.realpath(os.path.join('.', 'groups')))
        exit()
    def open_dialog(self, string):
        pass
        
    def start_position(self, btns: bool = False) -> None:
        self.stackedWidget.setCurrentWidget(self.page_1)
        self.addexpert_widget.setHidden(True)
        self.edit_widget.setHidden(True)
        self.filter_widget.setHidden(True)
        self.add_widget.setHidden(btns)
        self.ramka1.setHidden(btns)
        self.ramka2.setHidden(btns)              
            

    def load_data(self, dir_name: str) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        if not os.path.isdir(os.path.join('.', dir_name)):
            print(f'Нет папки {dir_name} с данными')
            return
        # Загружаем данные
        params = {'dtype': { 'Номер': 'int16', 'Участие': 'int8'}, 'parse_dates': [7], 'date_format': '%d-%b-%y'}
        
        df_ntp = pd.read_csv(os.path.join('.', dir_name, 'Expert.csv'), **params)
        df_reg = pd.read_csv(os.path.join('.', dir_name, 'Reg_obl_city.csv'), delimiter=';')
        # df_grnti = pd.read_csv(os.path.join('.', dir_name, 'grntirub.csv'))
        df_grnti = pd.read_csv(os.path.join('.', dir_name, 'grnti-latest.csv'), header=0, usecols=[0,1], names=['Код', 'Расшифровка']).drop_duplicates(keep='first')
        
        # Title case GRNTI
        # df_grnti['Расшифровка'] = df_grnti['Расшифровка'].str.capitalize()
        
        # Расшифровка
        dtypes_grnti = {'level_0_code': str, 'level_1_code': str, 'level_2_code': str, 'level_0_title': str, 'level_1_title': str, 'level_2_title': str}
        df_grnti_all = pd.read_csv(os.path.join('.', dir_name, 'grnti-latest.csv'), dtype=dtypes_grnti)
        dict1 = {k:v for k,v in zip(df_grnti_all.level_0_code.tolist(), df_grnti_all.level_0_title.tolist()) if k != ''}
        dict2 = {k:v for k,v in zip(df_grnti_all.level_1_code.tolist(), df_grnti_all.level_1_title.tolist()) if k != ''}
        dict3 = {k:v for k,v in zip(df_grnti_all.level_2_code.tolist(), df_grnti_all.level_2_title.tolist()) if k != ''}
        self.dict_grnti = dict1 | dict2 | dict3
        df_ntp['Расшифровка'] = df_ntp['ГРНТИ'].str.split(r', ').map(lambda num: ', '.join(dict.fromkeys([a for n in num if (a := self.dict_grnti.get(n, ''))])))
        # Регион
        # TODO: Кастыль
        self.dict_reg = {k:v for k,v in zip(df_reg['Город'].tolist(), df_reg['Регион'].tolist())} 
        df_ntp = pd.merge(df_ntp, df_reg.drop('Округ', axis=1), how='left', on='Город')
        # Округ
        df_ntp = pd.merge(df_ntp.drop('Округ', axis=1), df_reg.drop('Регион', axis=1), how='left', on='Город')
        df_ntp = df_ntp[['Номер', 'ФИО', 'Округ', 'Регион', 'Город', 'ГРНТИ', 'Расшифровка', 'Ключевые слова', 'Участие', 'Дата добавления']]
        
        return df_ntp, df_reg, df_grnti
    
    
    def btn_connect(self) -> None:
        # Меню
        self.ntp_show.triggered.connect(lambda: self.show_table('ntp'))
        self.reg_show.triggered.connect(lambda: self.show_table('reg'))
        self.grnti_show.triggered.connect(lambda: self.show_table('grnti'))
        # Главные кнопки
        self.add_button.clicked.connect(lambda: self.show_add_widget(False))
        self.delete_button.clicked.connect(lambda: self.open_dialog('delete'))
        self.edit_button.clicked.connect(lambda: self.show_edit_widget(False))
        self.add_expert_button.clicked.connect(lambda: self.open_dialog('group'))
        self.filter_button.clicked.connect(lambda: self.show_filter_widget(False))
        # Фильтр
        self.filter_close_button.clicked.connect(lambda: self.show_filter_widget(True))
        self.filter_apply_button.clicked.connect(self.apply_filter_widget)
        self.filter_reset_button.clicked.connect(self.reset_filter_widget)
        # Добавить
        self.addexpert_close_button_.clicked.connect(lambda: self.show_add_widget(True))
        self.addexpert_apply_button.clicked.connect(lambda: self.open_dialog('add'))
        self.addexpert_reset_button.clicked.connect(self.reset_add_widget)
        # Редактировать
        self.edit_close_button.clicked.connect(lambda: self.show_edit_widget(True))
        self.edit_apply_button.clicked.connect(lambda: self.open_dialog('edit'))
        self.edit_reset_button.clicked.connect(lambda: self.show_edit_widget(False))
        # Добавить в экспертную группу
    
    
    def keyboard_connect(self) -> None:
        # Меню
        self.ntp_show.setShortcut('Ctrl+1')
        self.reg_show.setShortcut('Ctrl+2')
        self.grnti_show.setShortcut('Ctrl+3')
        # Close widgets
        self.filter_close_button.setShortcut('escape')
        self.addexpert_close_button_.setShortcut('escape')
        self.edit_close_button.setShortcut('escape')
        # Удалить экспертов
        self.delete_button.setShortcut('backspace')
        self.filter_button.setShortcut('f')
        # QShortcut(QKeySequence('Ctrl+q'), self).activated.connect(self.app_exit)
    
    
    def layers(self) -> None:
        self.init_table.raise_()
        self.init_tablename.raise_()
        self.ramka1.lower()
        self.ramka2.lower()
        self.add_widget.lower()
        self.addexpert_widget.raise_()
        self.edit_widget.raise_()
        self.filter_widget.raise_()
    
    
    def get_settings(self) -> dict:
        return  {
            'ntp': {
                'df': self.df_ntp.copy(),
                'mode': QTableView.SelectionMode.ExtendedSelection,
                'behave': QTableView.SelectionBehavior.SelectRows,
                'label': 'Эксперты НТП'
            },
            'reg': {
                'df': self.df_reg.copy(),
                'mode': QTableView.SelectionMode.ExtendedSelection,
                'behave': QTableView.SelectionBehavior.SelectItems,
                'label': 'Справочник по регионам'
            },
            'grnti': {
                'df': self.df_grnti.copy(),
                'mode': QTableView.SelectionMode.ExtendedSelection,
                'behave': QTableView.SelectionBehavior.SelectItems,
                'label': 'Код рубрики (ГРНТИ)'
            }
        }


    # def save_abc(self):
    #     self.df_ntp.to_csv('./data2/Expert.csv', index=False, encoding="utf-8", date_format='%d-%b-%y')
    #     self.df_reg.to_csv('./data2/Reg_obl_city.csv', index=False, encoding="utf-8", date_format='%d-%b-%y')
    #     self.df_grnti.to_csv('./data2/grntirub.csv', index=False, encoding="utf-8", date_format='%d-%b-%y')