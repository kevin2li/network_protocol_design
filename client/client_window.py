import json
import random
import socket
import sys
import threading
import time
import traceback
from datetime import datetime

from PyQt5.QtWidgets import QApplication, QWidget, QMessageBox

from client.client_qt import Ui_Form


class Client_Win(QWidget, Ui_Form):
    def __init__(self):
        super(Client_Win, self).__init__()
        self.setupUi(self)
        self.lineEdit.setFocus()
        self.FLAG = True
        self.addr = '127.0.0.1'
        self.port = 8023
        self.device = 'ABC'
        self.interval = 1
        self.show()

    def send(self, conn_socket, interval=1, device='ABC'):
        id = 0
        try:
            while self.FLAG:
                id += 1
                message = {
                    "type": "data",
                    "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "power": 1000 + random.random()*10,
                    "id": id,
                    "sn": device,
                    "state": "on"
                }
                print(json.dumps(message))
                conn_socket.sendall(json.dumps(message).encode('utf-8'))
                time.sleep(interval)
            conn_socket.close()
        except ConnectionAbortedError:
            traceback.print_exc()
            QMessageBox.information(self, '提示', '对不起，连接被抛弃')
            sys.exit(1)
        except Exception:
            traceback.print_exc()

    def openClient(self):
        if self.btn.text() == "启动":
            self.FLAG = True
            try:
                self.addr = self.lineEdit.text()
                self.port = int(self.lineEdit_2.text())
                self.interval = float(self.lineEdit_3.text())
                self.device = self.lineEdit_4.text()
            except Exception as e:
                traceback.print_exc()
                QMessageBox.information(self, '提示', '对不起，输入有误， 请检查')
            try:
                conn_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                conn_socket.connect((self.addr, self.port))
                threading.Thread(target=self.send, args=(conn_socket, self.interval, self.device)).start()
            except ConnectionRefusedError as e:
                traceback.print_exc()
                QMessageBox.information(self, '提示', '对不起，连接被拒绝')

            self.btn.setText("停止")
        else:
            self.FLAG = False
            self.btn.setText("启动")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = Client_Win()
    win.show()
    sys.exit(app.exec_())