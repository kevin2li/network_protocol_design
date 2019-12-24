import json
import socket
import sys
from PyQt5.QtWidgets import QMainWindow, QApplication
import pandas as pd
from matplotlib import pyplot as plt
import os
import threading

from server.server_qt import Ui_MainWindow


class Server_Win(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(Server_Win, self).__init__()
        self.setupUi(self)
        self.HOST = '127.0.0.1'
        self.PORT = 8023
        self.FLAG = True
        self.updateImage("blank.png")
        self.show()

    def updateImage(self, filename="blank.png"):
        self.img_label.setStyleSheet(f"QLabel{{border-image: url({filename});}}")
        self.img_label.show()

    def control(self):
        pass

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
                threading.Thread(target=self.handleClientRequest, args=(conn,)).start()

    def handleClientRequest(self, conn):
        while self.FLAG:
            data = conn.recv(1024)
            if len(data) > 0:
                print(data)
                message = json.loads(data.decode('utf-8'))
                self.label_6.setText(f"{message['power']:.2f}w")
                self.label_2.setText(str(message['sn']))
                filename = f"{message['sn']}.csv"
                if not os.path.exists(filename):
                    df = pd.DataFrame(columns=['id', 'type', 'time', 'power', 'sn', 'state'])
                    df.to_csv(f"{message['sn']}.csv")
                df = pd.read_csv(filename, index_col=0)
                df = df.append(pd.Series(
                    [message['id'], message['type'], message['time'], message['power'], message['sn'],
                     message['state']], index=df.columns), ignore_index=True)

                csv_path = f"{message['sn']}.csv"
                df.to_csv(csv_path)
                self.plot(csv_path)
                self.updateImage(f"{message['sn']}.png")
            else:
                conn.close()
                break
        conn.close()

    def plot(self, csv_path):
        df = pd.read_csv(csv_path, index_col=0)
        y = df['power'][-30:]
        plt.plot(y, "b-")
        plt.ylabel("power")
        plt.ylim(990, 1020)
        plt.savefig(f"{df.sn.iloc[0]}.png")
        plt.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = Server_Win()
    win.show()
    sys.exit(app.exec_())
