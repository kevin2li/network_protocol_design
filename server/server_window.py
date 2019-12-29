import socket
import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QInputDialog, QLineEdit
import pandas as pd
from matplotlib import pyplot as plt
import os
import threading
from protocol import HEMSProtocol
from server.server_qt import Ui_MainWindow


class Server_Win(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(Server_Win, self).__init__()
        self.setupUi(self)
        self.HOST = '127.0.0.1'
        self.PORT = 8023
        self.FLAG = True
        self.currentDevice = None
        self.control_msg = None
        self.updateImage("blank.png")
        self.show()

    def updateImage(self, filename="blank.png"):
        self.img_label.setStyleSheet(f"QLabel{{border-image: url({filename});}}")
        self.img_label.show()

    def control(self):
        if self.pushButton_15.text() == '暂停':
            self.pushButton_15.setText("继续")
            self.control_msg = {
                "command": "pause"
            }
        elif self.pushButton_15.text() == '继续':
            self.pushButton_15.setText("暂停")
            self.control_msg = {
                "command": "resume"
            }

    def changeDevice(self):
        item = self.listWidget.currentItem()
        self.currentDevice = item.text()
        print(item.text())

    def setInterval(self):
        text, ret = QInputDialog.getText(self, "输入", "请输入间隔值:", QLineEdit.Normal, "")
        if ret and text != '':
            self.control_msg = {
                "command": "setInterval",
                "value": text
            }

    def listen(self):
        self.HOST = self.lineEdit_2.text()
        self.PORT = int(self.lineEdit.text())
        if self.pushButton_5.text() == '启动':
            self.FLAG = True
            listen_thread = threading.Thread(target=self._listen, args=(), daemon=True)
            listen_thread.start()
            self.label_4.setText("监听中")
            self.pushButton_5.setText("关闭")
        else:
            self.FLAG = False
            self.label_4.setText("关闭")
            self.pushButton_5.setText("启动")

    def _listen(self):
        print("Listening...")
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.HOST, self.PORT))
            s.listen(5)
            while self.FLAG:
                conn, addr = s.accept()
                print("connected by ", addr)
                if not self.currentDevice:
                    self.listWidget.clear()
                    self.currentDevice = str(addr)
                    self.listWidget.addItem(str(addr))
                    self.listWidget.setCurrentRow(0)
                else:
                    self.listWidget.addItem(str(addr))
                threading.Thread(target=self.handleClientRequest, args=(conn, addr)).start()
                threading.Thread(target=self.send, args=(conn, addr)).start()
            self.listWidget.clear()

    def handleClientRequest(self, conn, addr):
        while self.FLAG:
            data = conn.recv(1024)
            if len(data) > 0:
                packet = HEMSProtocol.unserilize(data)
                print(packet)
                message = packet['body']
                if self.currentDevice == str(addr):
                    self.label_6.setText(f"{message['power']:.2f}w")
                    self.label_2.setText(str(message['sn']))
                filename = f"{message['sn']}.csv"
                if not os.path.exists(filename):
                    df = pd.DataFrame(columns=['id', 'time', 'power', 'sn', 'state'])
                    df.to_csv(f"{message['sn']}.csv")
                df = pd.read_csv(filename, index_col=0)
                df = df.append(pd.Series(
                    [message['id'], message['time'], message['power'], message['sn'],
                     message['state']], index=df.columns), ignore_index=True)

                csv_path = f"{message['sn']}.csv"
                df.to_csv(csv_path)
                if self.currentDevice == str(addr):
                    self.plot(csv_path)
                    self.updateImage(f"{message['sn']}.png")
            else:
                break
        conn.close()

    def send(self, conn_socket, addr):
        while True:
            if self.currentDevice == str(addr):
                if self.control_msg:
                    packet = HEMSProtocol(type="control", **self.control_msg)
                    conn_socket.sendall(packet.serilize())
                    self.control_msg = None

    def plot(self, csv_path):
        df = pd.read_csv(csv_path, index_col=0)
        y = df['power'][-30:]
        fig, ax = plt.subplots()
        ax.plot(y, "b-")
        plt.ylabel("power")
        fig.savefig(f"{df.sn.iloc[0]}.png")
        plt.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = Server_Win()
    win.show()
    sys.exit(app.exec_())
