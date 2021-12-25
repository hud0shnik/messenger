import time
import pickle
from cryptography.fernet import Fernet
from PyQt5 import QtCore, QtGui, QtWidgets
from methods.windows.settings import *

# Мониторинг входящих сообщений
class message_monitor(QtCore.QThread):
    mysignal = QtCore.pyqtSignal(list)
    server_socket = None
    symmetric_key = None

    def __init__(self, parent=None):
        QtCore.QThread.__init__(self, parent)

    def run(self):
        print(f'server_socket: {self.server_socket}')

        while True:
            if self.server_socket != None:
                message = self.server_socket.recv(1024)
                pickle_dec = pickle.loads(message)

                # Если это запрос на заполнение ключей
                # ["SERVER_OK", "MESSAGE", "KEY"]
                if pickle_dec[0] == "SERVER_OK":
                    self.symmetric_key = pickle_dec[-1]
                    self.cipher = Fernet(self.symmetric_key) 
                    self.mysignal.emit(pickle_dec)

                # Обработка сообщений от других пользователей
                # ['ENCRYPT_MESSAGE', self.nick, message_text.encode()]
                elif pickle_dec[0] == "ENCRYPT_MESSAGE":
                    decrypted_text = self.cipher.decrypt(pickle_dec[-1]).decode()
                    decrypted_payload = ["ENCRYPT_MESSAGE", pickle_dec[1], pickle_dec[2], decrypted_text]
                    self.mysignal.emit(decrypted_payload)

            time.sleep(2)

    # Отправить зашифрованное сообщение на сервер
    def send_encrypt(self, data_list):
        # ['ENCRYPT_MESSAGE', self.nick, message_text.encode()]
        if data_list[0] == "ENCRYPT_MESSAGE":
            encrypted_message = self.cipher.encrypt(data_list[-1])
            pickle_payload = ['ENCRYPT_MESSAGE', data_list[1], data_list[2], encrypted_message]
            self.server_socket.send(pickle.dumps(pickle_payload))

        # Если клиент разорвал соединение
        # ['EXIT', f'{self.nick}', 'вышел из чата!']
        elif data_list[0] == "EXIT":
            encrypted_message = self.cipher.encrypt(data_list[-1])
            pickle_payload = ['EXIT', data_list[1], encrypted_message]
            self.server_socket.send(pickle.dumps(pickle_payload))
