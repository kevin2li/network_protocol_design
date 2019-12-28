import random
import socket
import sys
import threading
import time
import traceback
from datetime import datetime
from PyQt5.QtWidgets import QApplication, QWidget, QMessageBox
from client.client_qt import Ui_Form
from protocol import HEMSProtocol

'''
FLAG:   0  --> 初始化
        1  --> 正常
        2  --> 暂停
        -1 --> 关闭
'''
class Client_Win(QWidget, Ui_Form):
    def __init__(self):
        super(Client_Win, self).__init__()
        self.setupUi(self)
        self.lineEdit.setFocus()
        self.FLAG = 0
        self.addr = '127.0.0.1'
        self.port = 8023
        self.device = None
        self.state = "off"
        self.id = 1001
        self.interval = 1
        self.min = 200
        self.max = 210
        self.show()

    def send(self, conn_socket):
        try:
            while True:
                if self.FLAG == 1:
                    message = {
                        "type": "data",
                        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "power": self.min + random.random()*(self.max - self.min),
                        "id": self.id,
                        "sn": self.device,
                        "state": self.state
                    }
                    packet = HEMSProtocol(**message)
                    conn_socket.sendall(packet.serilize())
                    time.sleep(self.interval)
                elif self.FLAG == -1:
                    self.FLAG = 0
                    break
            conn_socket.shutdown(2)
            conn_socket.close()
        except ConnectionAbortedError:
            # traceback.print_exc()
            QMessageBox.information(self, '提示', '对不起，连接被抛弃')

    def listen(self, conn_socket):
        try:
            while True:
                data = conn_socket.recv(1024)
                data = HEMSProtocol.unserilize(data)
                print(data)
                control_msg = data['body']
                if control_msg['command'] == 'pause':
                    self.btn.setText("启动")
                    self.FLAG = 0
                elif control_msg['command'] == 'resume':
                    self.btn.setText("停止")
                    self.FLAG = 1
                elif control_msg['command'] == 'stop':
                    self.btn.setText("启动")
                    self.FLAG = -1
                elif control_msg['command'] == 'setInterval':
                    self.interval = float(control_msg['value'])

        except ConnectionAbortedError:
            print("ConnectionAbortedError")

    def openClient(self):
        if self.btn.text() == "启动":
            self.state = 'on'
            if self.FLAG == 0:
                try:
                    self.addr = self.lineEdit.text()
                    self.port = int(self.lineEdit_2.text())
                    self.interval = float(self.lineEdit_3.text())
                    self.device = self.lineEdit_4.text()
                    self.id = self.lineEdit_7.text()
                    self.min = float(self.lineEdit_5.text())
                    self.max = float(self.lineEdit_6.text())
                except Exception:
                    traceback.print_exc()
                    QMessageBox.information(self, '提示', '对不起，输入有误， 请检查')
                try:
                    conn_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    conn_socket.connect((self.addr, self.port))

                    threading.Thread(target=self.send, args=(conn_socket,), daemon=True).start()
                    threading.Thread(target=self.listen, args=(conn_socket, ), daemon=True).start()
                except ConnectionRefusedError:
                    traceback.print_exc()
                    QMessageBox.information(self, '提示', '对不起，连接被拒绝')

                self.btn.setText("停止")
                self.FLAG = 1
            else:
                self.FLAG = -1
                self.btn.setText("停止")
        elif self.btn.text() == "停止":
            self.state = 'off'
            self.FLAG = -1
            self.btn.setText("启动")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = Client_Win()
    win.show()
    sys.exit(app.exec_())