from _add import Add_Row
from _edit import Edit_Row
from _base import Base_Class, Ui_Dialog2
from _table import Table_Methods
from _filter import Filter_table
from _delete import Delete_rows

from PyQt6.QtWidgets import QApplication

import sys
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

# - просмотр записей выбранной группы кандидатов на включение в состав экспертной группы
# с возможностью простановки/снятия отметок о принятии решения о включении кандидата в экспертную группу;
# фиксация результата в экспертной группе;

# - просмотр записей исходной базы данных с возможностью простановки отметок об отборе эксперта в качестве кандидата на включение/добавление в экспертную группу,
# перенос сведений об отобранных кандидатах в выбранную экспертную группу;

# - утверждение экспертной группы без возможности дальнейшей корректировки состава с увеличением на 1 числа участий в экспертизах в основной базе данных;

# - формирование документов: таблица со списком сформированной поименованной экспертной группы,
# содержащей столбцы: порядковый номер, фамилия И.О., регион, город, код ГРНТИ; карточка эксперта.

class Ui_MainWindow2(Edit_Row, Add_Row, Table_Methods, Filter_table, Delete_rows):

    def __init__(self):
        # Загружаем данные и всякие переменные
        Base_Class.__init__(self)
        
        # Отобразить пустую страницу
        self.start_position()
        
        # Подключаем сигнал нажатия кнопки к методу
        self.btn_connect()
        
        # Привязка клавиш
        self.keyboard_connect()
        
        # Заполнить поля в Добавить
        self.fill_add_lineEdit()
        
        # Заполнить поля в Фильтр
        self.fill_filter_lineEdit()
        
        # Заполнить поля в Редактировать
        self.fill_edit_lineEdit()
        
        # Подготовка к Сотрировке
        Table_Methods.__init__(self)
        
    def open_dialog(self, string):
        if string == 'delete' and len(Edit_Row.rows_selected(self)) == 0: return
        dialog = Ui_Dialog2(string)
        result = dialog.exec()  # Запускаем диалоговое окно и ожидаем результата
        func = {
            'add': self.apply_add_widget,
            'edit': self.apply_edit_widget,
            'delete': self.delete_selected_rows
        }
        match result:
            case 1: func[string]()
            case 0: return
    

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ui = Ui_MainWindow2()
    ui.show()
    sys.exit(app.exec())