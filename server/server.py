import time
import json
import pickle
import socket
import base64
import threading
from cryptography.fernet import Fernet


class Server:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.all_client = []
        self.symmetric_key = None

        # Запускает прослушивание соединений
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.ip, self.port))
        self.server.listen(0)
        threading.Thread(target=self.connect_handler).start()
        print('Server is OK')

    # Обработка входящих соединений
    def connect_handler(self):
        while True:
            client, address = self.server.accept()
            if client not in self.all_client:
                self.all_client.append(client)

                # Отправляет запрос на успешное подключение + раздает ключи
                self.get_key()
                payload = ['SERVER_OK', "Успешное подключение!", self.symmetric_key]
                client.send(pickle.dumps(payload))
                threading.Thread(target=self.message_handler, args=(client,)).start()

            time.sleep(2)

    # Обрабатывает отправленный текст
    def message_handler(self, client_socket):
        while True:
            try:
                message = client_socket.recv(1024)
                pickle_dec = pickle.loads(message)
                print(pickle_dec)
            except:
                self.all_client.remove(client_socket)
                break

            # Отправляет зашифрованное сообщение юзерам
            if pickle_dec[0] == "ENCRYPT_MESSAGE":
                for client in self.all_client:
                    if client != client_socket:
                        client.send(message)

            # Если клиент отправил запрос на дисконнект
            elif pickle_dec[0] == "EXIT":
                print('=' * 50)
                print('=' * 50)
                self.all_client.remove(client_socket)
                break

            time.sleep(1)

    # Генератор ключа шифрования
    def get_key(self) -> None:
        if self.symmetric_key is None:
            self.symmetric_key = Fernet.generate_key()


if __name__ == "__main__":
    myserver = Server('127.0.0.1', 5555)