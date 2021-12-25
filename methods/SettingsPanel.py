import os
import re
import json
from PyQt5 import QtCore, QtGui, QtWidgets
from methods.windows.settings import *

# Окно с настройками клиента
class SettingPanel(QtWidgets.QWidget):
    def __init__(self, parent=None, signal=None):
        super().__init__(parent, QtCore.Qt.Window)
        self.setting = Ui_Form()
        self.setting.setupUi(self)
        self.setWindowModality(2)

        # Сигнал для возврата в интерфейс
        self.signal = signal

        # Отключает границы окна программы
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.center()

        # Обработчики кнопок
        self.setting.pushButton_7.clicked.connect(lambda: self.close())
        self.setting.pushButton_6.clicked.connect(self.save_config)

        # Подгружает конфиг если он уже есть
        if os.path.exists(os.path.join("data", "config.json")):
            with open(os.path.join("data", "config.json")) as file:
                data = json.load(file)
                self.setting.lineEdit_4.setText(data['nick'])
                self.setting.lineEdit_2.setText(data['server_ip'])
                self.setting.lineEdit_3.setText(data['server_port'])

    # Перетаскивание окна
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

    # Сохранить конфиг
    def save_config(self):
        nick = self.setting.lineEdit_4.text()
        server_ip = self.setting.lineEdit_2.text()
        server_port = self.setting.lineEdit_3.text()
        regular_ip = "\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}"

        # Обновляем поля, для того чтобы пользователь видел какие из них правильные
        self.setting.lineEdit_2.setStyleSheet("border-radius: 7px;")
        self.setting.lineEdit_3.setStyleSheet("border-radius: 7px;")
        self.setting.lineEdit_4.setStyleSheet("border-radius: 7px;")

        # Проверяет корректность ввода
        if len(nick) >= 3 and len(nick) <= 20:
            if not re.match(regular_ip, self.setting.lineEdit_2.text()) is None:
                if server_port.isdecimal() and int(server_port) <= 65535:

                    # Если конфига ещё нет
                    if not os.path.exists(os.path.join("data", "config.json")):
                        with open(os.path.join("data", "config.json"), "w") as file:
                            data = {"nick": nick, "server_ip": server_ip, "server_port": server_port}
                            json.dump(data, file, indent=6)

                    # Если конфиг есть, перезаписывает его
                    else:
                        with open(os.path.join("data", "config.json"), "w") as file:
                            data = {"nick": nick, "server_ip": server_ip, "server_port": server_port}
                            json.dump(data, file, indent=6)

                    # Закрывает окно с настройками
                    self.close()
                    self.signal.emit(['update_config'])
                #Ошибки
                else:
                    self.setting.lineEdit_3.setStyleSheet("border: 2px solid red; border-radius: 7px;")
                    self.setting.lineEdit_3.setText("Проверьте правильность ввода SERVER_PORT")
            else:
                self.setting.lineEdit_2.setStyleSheet("border: 2px solid red; border-radius: 7px;")
                self.setting.lineEdit_2.setText("Проверьте правильность ввода SERVER_IP")
        else:
            self.setting.lineEdit_4.setStyleSheet("border: 2px solid red; border-radius: 7px;")
            self.setting.lineEdit_4.setText("Слишком длинный либо слишком короткий ник")
