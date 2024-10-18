import os, subprocess, sys
for name in ('exit', 'Dialog_confirm', 'Dialog_comboBox', 'Dialog_lineEdit'):
    if not os.path.isfile(f'{name}.py'):
        match sys.platform:
            case 'darwin': subprocess.run(f'pyuic6 -o {name}.py -x {name}.ui'.split())
            case _: subprocess.run(f'python -m PyQt6.uic.pyuic -o {name}.py -x {name}.ui'.split())       

from _add import Add_Row
from _edit import Edit_Row
from _base import Base_Class, Ui_Dialog_confirm, Ui_Dialog_lineEdit, Ui_Dialog_comboBox
from _table import Table_Methods
from _filter import Filter_table
from _delete import Delete_rows
from _experts import Experts

from PyQt6.QtWidgets import QApplication

import pandas as pd

pd.set_option('future.no_silent_downcasting', True)

# - контроль и восстановление целостности исходных баз данных системы;
# Done
# - добавление/редактирование информации об эксперте в базу данных, верификация вновь поступивших данных, обеспечение целостности данных;
# Done
# - контроль возможного повторного занесения данных об эксперте;
# Done
# - фильтрация информации в базе данных по указанной фамилии
# и/или федеральному округу
# и/или субъекту федерации
# и/или городу
# и/или рубрике
# и/или коду ГРНТИ
# и/или ключевым словам области интересов;
# фиксация отобранного подмножества в поименованную экспертную группу;
# Done
# - просмотр записей выбранной группы кандидатов на включение в состав экспертной группы
# с возможностью простановки/снятия отметок о принятии решения о включении кандидата в экспертную группу;
# фиксация результата в экспертной группе;

# - просмотр записей исходной базы данных с возможностью простановки отметок об отборе эксперта в качестве кандидата на включение/добавление в экспертную группу,
# перенос сведений об отобранных кандидатах в выбранную экспертную группу;

# - утверждение экспертной группы без возможности дальнейшей корректировки состава с увеличением на 1 числа участий в экспертизах в основной базе данных;

# - формирование документов: таблица со списком сформированной поименованной экспертной группы,
# содержащей столбцы: порядковый номер, фамилия И.О., регион, город, код ГРНТИ; карточка эксперта.

class Ui_MainWindow2(Edit_Row, Add_Row, Table_Methods, Filter_table, Delete_rows, Experts):

    def __init__(self):
        # Загружаем данные и всякие переменные
        Base_Class.__init__(self)
        
        # Отобразить пустую страницу
        self.start_position()
        # Подключаем сигнал нажатия кнопки к методу
        self.btn_connect()
        # Привязка клавиш
        self.keyboard_connect()
        # Работа со слоями
        self.layers()
        
        # Скрыть предупреждение
        Delete_rows.__init__(self)
        # Заполнить поля в Добавить
        Add_Row.__init__(self)
        # Заполнить поля в Фильтр
        Filter_table.__init__(self)
        # Заполнить поля в Редактировать
        Edit_Row.__init__(self)
        # Подготовка к Сотрировке
        Table_Methods.__init__(self)
        
        # Отображение "Эксперты НТП"
        self.show_table('ntp')
        
        from PyQt6.QtGui import QShortcut, QKeySequence
        QShortcut(QKeySequence('Ctrl+4'), self).activated.connect(self.groups_show)
   
    def open_dialog(self, string):
        func_before = {
            'add'   : self.before_add_widget,
            'edit'  : self.before_edit_widget,
            'delete': self.before_delete_widget,
            'new_group' : self.before_group_widget
            # 'choose_group' : self.before_group_widget 
        }
        dialog_ui = {
            'add'   : Ui_Dialog_confirm,
            'edit'  : Ui_Dialog_confirm,
            'delete': Ui_Dialog_confirm,
            'new_group' : Ui_Dialog_lineEdit
            # 'choose_group' : Ui_Dialog_comboBox 
        }
        func_after = {
            'add'   : self.apply_add_widget,
            'edit'  : self.apply_edit_widget,
            'delete': self.apply_delete_widget,
            'new_group' : self.save_group_widget
            # 'choose_group' : self.load_group_widget 
        }
        if not func_before[string]():
            return
        dialog = dialog_ui[string](string)
        result = dialog.exec()  # Запускаем диалоговое окно и ожидаем результата
        match result:
            case 1: func_after[string]()
            case 0: return 

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ui = Ui_MainWindow2()
    ui.show()
    sys.exit(app.exec())