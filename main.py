import os
import sys
import time
import json
import socket
from PyQt5 import QtCore, QtGui, QtWidgets
from des import *

from methods.SettingsPanel import *
from methods.ConnectThreadMonitor import *

# Интерфейс программы и обработчик событий
class Client(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Отключает границы окна программы
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.center()

        # Обработчики кнопок
        self.ui.pushButton.clicked.connect(self.send_message)
        self.ui.pushButton_2.clicked.connect(self.connect_to_server)
        self.ui.pushButton_3.clicked.connect(lambda: self.close())
        self.ui.pushButton_4.clicked.connect(lambda: self.ui.listWidget.clear())
        self.ui.pushButton_7.clicked.connect(self.setting_panel)
        # Объект класса для обработки соединений 
        self.connect_monitor = message_monitor()
        self.connect_monitor.mysignal.connect(self.signal_handler)

        # Данные из конфига
        self.nick = None
        self.ip = None
        self.port = None
        self.connect_status = False

    # Реализует перетаскивание окна
    # -/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/
    def center(self):
        qr = self.frameGeometry()
        cp = QtWidgets.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
    def mousePressEvent(self, event):
        self.oldPos = event.globalPos()
    def mouseMoveEvent(self, event):
        try:
            delta = QtCore.QPoint(event.globalPos() - self.oldPos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.oldPos = event.globalPos()
        except AttributeError:
            pass    
    # -/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/

    # Открыть окно для настройки клиента
    def setting_panel(self):
        setting_win = SettingPanel(self, self.connect_monitor.mysignal)
        setting_win.show()

    # Обновление конфигов юзеров в real-time
    def update_config(self):
        if os.path.exists(os.path.join("data", "config.json")):
            with open(os.path.join("data", "config.json")) as file:
                data = json.load(file)
                self.nick = data['nick']
                self.ip = data['server_ip']
                self.port = int(data['server_port'])

    # Обработчик сигналов
    def signal_handler(self, value: list):
        # Обновление конфига
        if value[0] == "update_config":
            self.update_config()

        # Обновление ключа шифрования
        elif value[0] == "SERVER_OK":
            self.connect_status = True
            item = QtWidgets.QListWidgetItem()
            item.setTextAlignment(QtCore.Qt.AlignHCenter)
            item.setText(f"SERVER: {value[1]}\n")
            self.ui.listWidget.addItem(item)
            print(value)

        # Обработка сообщений других юзеров
        elif value[0] == "ENCRYPT_MESSAGE":
            item = QtWidgets.QListWidgetItem()
            item.setTextAlignment(QtCore.Qt.AlignRight)

            item.setText(f"{value[1]}:\n{value[-1]}")
            self.ui.listWidget.addItem(item)
            print(value)

    # Отправка сообщений на сервер
    def send_message(self):
        if self.connect_status:
            message_text = self.ui.lineEdit.text()
            
            # Если поле с текстом не пустое шифрует сообщение и передаёт на сервер
            if len(message_text) > 0:
                payload = ['ENCRYPT_MESSAGE', self.nick, message_text.encode()]
                print(payload)
                self.connect_monitor.send_encrypt(payload)

                # Добавляет свое сообщение в ListWidget
                item = QtWidgets.QListWidgetItem()
                item.setTextAlignment(QtCore.Qt.AlignLeft)
                size = QtCore.QSize(45, 45)

                item.setText(f"{self.nick} (ВЫ):\n{message_text}")
                self.ui.listWidget.addItem(item)

        else:
            message = "Проверьте соединение с сервером"
            QtWidgets.QMessageBox.about(self, "Оповещение", message)

    # Покдлючение к серверу
    def connect_to_server(self):
        # Обновляет конфиг
        self.update_config()    
        #Если с никнеймом всё ок, блокирует кнопки и запускает мониторинг сообщений 
        if self.nick != None:
            try:
                self.btn_locker(self.ui.pushButton_2, True)
                self.btn_locker(self.ui.pushButton_7, True)
                self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.client.connect((self.ip, self.port))
                self.connect_monitor.server_socket = self.client
                self.connect_monitor.start()
            # Ошибки
            except Exception as err:
                message = "Ошибка соединения с сервером.\nПроверьте правильность ввода данных"
                QtWidgets.QMessageBox.about(self, "Оповещение", message)
        else:   
            message = "Для начала заполните данные во вкладке 'Настройки'"
            QtWidgets.QMessageBox.about(self, "Оповещение", message)

    # Блокировщик кнопок
    def btn_locker(self, btn: object, lock_status: bool) -> None:
        default_style = """
        QPushButton{
            color: white;
            background-color: #618685;
        }
        QPushButton:hover{
            background-color: #618685;
        }      
        QPushButton:pressed{
            background-color: #618685;
        }
        """

        lock_style = """
        color: #9EA2AB;
        background-color: #618685;
        """
        if lock_style:
            btn.setDisabled(True)
            btn.setStyleSheet(lock_style)
        else:
            btn.setDisabled(False)
            btn.setStyleSheet(default_style)

    # Обработчик события на выход
    def closeEvent(self, value: QtGui.QCloseEvent) -> None:
        try:
            payload = ['EXIT', f'{self.nick}', 'вышел из чата!'.encode()]
            self.connect_monitor.send_encrypt(payload); self.hide()
            time.sleep(3); self.client.close()
            self.close()
        except Exception as err:
            print(err)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    myapp = Client()
    myapp.show()
    sys.exit(app.exec_())