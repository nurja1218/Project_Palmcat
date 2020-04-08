import sys
import threading
import time

import serial
import serial.tools.list_ports as port_list
from PyQt5 import QtCore
from PyQt5.QtCore import QObject, pyqtSignal, QThread
from PyQt5.QtWidgets import *


def connect_serial(serial_port):
    ser_conn = serial.Serial(
        port=serial_port,
        baudrate=115200,
    )
    return ser_conn


def isNumber(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def loop_listen():
    try:
        while True:
            time.sleep(0.1)
            serial_port = ""
            ports = list(port_list.comports())
            for p in ports:
                if "JLink" in str(p):
                    serial_port = str(p).split(" ")[0]
            print(serial_port)

            # serial_port = "COM3"

            if serial_port == "":
                f = open("./serial_data.txt", "w")
                f.write("disconnect")
                f.close()
                raise NotImplementedError
            else:
                ser = connect_serial(serial_port)

                while True:
                    if ser.readable():
                        # gyro_axis = ['100', '100', '0']  # 자이로 축값
                        res = ser.readline()
                        res_decode = res.decode("utf-8")
                        line_split = res_decode.replace("\x00", "")
                        serial_data = line_split.split("\n")
                        serial_data = serial_data[0].split(",")
                        # serial_data = gyro_axis + serial_data
                        errchk = [isNumber(t) for t in serial_data]

                        if errchk == [True, True, True, True, True, True, True, True, True, True, True, True, True]:
                            intlist_flag = 'True'
                        else:
                            intlist_flag = 'False'

                    if len(serial_data) == 13 and intlist_flag == 'True':
                        ######################################
                        # 하나의 리스트를 한줄로 덮어써서 txt파일에 저장
                        vstr = ""
                        for i in serial_data:
                            vstr = vstr + str(i) + ","
                        vstr = vstr.rstrip(",")
                        f = open("./serial_data.txt", "w")
                        f.writelines(vstr)
                        # print(vstr)
                        f.close()
                    else:
                        ##################################
                        ser.close()
                        f = open("./serial_data.txt", "w")
                        f.write("data_error")
                        f.close()
                        raise NotImplementedError
    except NotImplementedError:
        pass


class dataTrans(QObject):
    trans_data = pyqtSignal()


class vrFrame(QWidget):

    def __init__(self):
        QWidget.__init__(self)

        self.initUI()

    def initUI(self):
        self.label1_1 = QLabel()
        self.label1_2 = QLabel()
        self.label1_3 = QLabel()
        self.label1_4 = QLabel()
        self.label1_5 = QLabel()
        self.label2_1 = QLabel()
        self.label2_2 = QLabel()
        self.label2_3 = QLabel()
        self.label2_4 = QLabel()
        self.label2_5 = QLabel()
        self.label3_1 = QLabel()
        self.label3_2 = QLabel()
        self.label3_3 = QLabel()
        self.label3_4 = QLabel()
        self.label3_5 = QLabel()
        self.label4_1 = QLabel()
        self.label4_2 = QLabel()
        self.label4_3 = QLabel()
        self.label4_4 = QLabel()
        self.label4_5 = QLabel()
        self.label5_1 = QLabel()
        self.label5_2 = QLabel()
        self.label5_3 = QLabel()
        self.label5_4 = QLabel()
        self.label5_5 = QLabel()

        hbox1 = QHBoxLayout()
        hbox2 = QHBoxLayout()
        hbox3 = QHBoxLayout()
        hbox4 = QHBoxLayout()
        hbox5 = QHBoxLayout()
        vbox = QVBoxLayout()

        hbox1.addWidget(self.label1_1)
        hbox1.addWidget(self.label1_2)
        hbox1.addWidget(self.label1_3)
        hbox1.addWidget(self.label1_4)
        hbox1.addWidget(self.label1_5)
        hbox2.addWidget(self.label2_1)
        hbox2.addWidget(self.label2_2)
        hbox2.addWidget(self.label2_3)
        hbox2.addWidget(self.label2_4)
        hbox2.addWidget(self.label2_5)
        hbox3.addWidget(self.label3_1)
        hbox3.addWidget(self.label3_2)
        hbox3.addWidget(self.label3_3)
        hbox3.addWidget(self.label3_4)
        hbox3.addWidget(self.label3_5)
        hbox4.addWidget(self.label4_1)
        hbox4.addWidget(self.label4_2)
        hbox4.addWidget(self.label4_3)
        hbox4.addWidget(self.label4_4)
        hbox4.addWidget(self.label4_5)
        hbox5.addWidget(self.label5_1)
        hbox5.addWidget(self.label5_2)
        hbox5.addWidget(self.label5_3)
        hbox5.addWidget(self.label5_4)
        hbox5.addWidget(self.label5_5)

        vbox.addLayout(hbox1)
        vbox.addLayout(hbox2)
        vbox.addLayout(hbox3)
        vbox.addLayout(hbox4)
        vbox.addLayout(hbox5)

        self.labels = {"1,1": self.label1_1, "1,2": self.label1_2, "1,3": self.label1_3,
                       "1,4": self.label1_4, "1,5": self.label1_5, "2,1": self.label2_1,
                       "2,2": self.label2_2, "2,3": self.label2_3, "2,4": self.label2_4,
                       "2,5": self.label2_5, "3,1": self.label3_1, "3,2": self.label3_2,
                       "3,3": self.label3_3, "3,4": self.label3_4, "3,5": self.label3_5,
                       "4,1": self.label4_1, "4,2": self.label4_2, "4,3": self.label4_3,
                       "4,4": self.label4_4, "4,5": self.label4_5, "5,1": self.label5_1,
                       "5,2": self.label5_2, "5,3": self.label5_3, "5,4": self.label5_4,
                       "5,5": self.label5_5}

        # 초기값
        self.base_yaw = None
        self.base_pitch = None

        # 누적 yaw, pitch를 담을 변수
        self.meta_yaw = 0
        self.meta_pitch = 0

        self.label3_3.setStyleSheet("background-color: white")

        self.watcher = QtCore.QFileSystemWatcher(self)
        self.watcher.addPath("./serial_data.txt")
        self.watcher.fileChanged.connect(self.label_change)

        self.setLayout(vbox)
        self.setWindowTitle('VR demo')

    # yaw값의 조건에 따라 label에 색을 칠해주는 함수
    def pitch_module(self, lst=[], yaw=str):
        if self.meta_pitch < lst[0]:
            key_s = "5," + yaw
            for i in range(25):
                if list(self.labels.keys())[i] == key_s:
                    if self.hit:
                        self.labels[key_s].setStyleSheet("background-color: red")
                    else:
                        self.labels[key_s].setStyleSheet("background-color: green")
                else:
                    list(self.labels.values())[i].setStyleSheet("")
        # (4, 1)
        elif lst[0] <= self.meta_pitch < lst[1]:
            key_s = "4," + yaw
            for i in range(25):
                if list(self.labels.keys())[i] == key_s:
                    if self.hit:
                        self.labels[key_s].setStyleSheet("background-color: red")
                    else:
                        self.labels[key_s].setStyleSheet("background-color: green")
                else:
                    list(self.labels.values())[i].setStyleSheet("")
        # (3, 1)
        elif lst[1] <= self.meta_pitch < lst[2]:
            key_s = "3," + yaw
            for i in range(25):
                if list(self.labels.keys())[i] == key_s:
                    if self.hit:
                        self.labels[key_s].setStyleSheet("background-color: red")
                    else:
                        self.labels[key_s].setStyleSheet("background-color: green")
                else:
                    list(self.labels.values())[i].setStyleSheet("")
        # (2, 1)
        elif lst[2] <= self.meta_pitch < lst[3]:
            key_s = "2," + yaw
            for i in range(25):
                if list(self.labels.keys())[i] == key_s:
                    if self.hit:
                        self.labels[key_s].setStyleSheet("background-color: red")
                    else:
                        self.labels[key_s].setStyleSheet("background-color: green")
                else:
                    list(self.labels.values())[i].setStyleSheet("")
        # (1, 1)
        elif self.meta_pitch >= lst[3]:
            key_s = "1," + yaw
            for i in range(25):
                if list(self.labels.keys())[i] == key_s:
                    if self.hit:
                        self.labels[key_s].setStyleSheet("background-color: red")
                    else:
                        self.labels[key_s].setStyleSheet("background-color: green")
                else:
                    list(self.labels.values())[i].setStyleSheet("")

    def label_change(self, path):
        with open(path, 'r') as f:
            text_data = f.read()

        serial_txt = text_data.split(",")
        serial_txt = list(map(float, serial_txt))

        # yaw, pitch축으 값을 변수에 저장
        self.yaw = serial_txt[2]
        self.pitch = serial_txt[0]
        self.delta_yaw = 0.0
        self.delta_pitch = 0.0
        if serial_txt[3] == 1.0:
            self.meta_yaw = 0.0
            self.meta_pitch = 0.0
        else:
            # 기준값이 설정되지 않았다면 초기값을 기준값으로 저장
            if self.base_yaw is None:
                self.base_yaw = serial_txt[2]
                # delta_yaw : 현재값에 기준값을 뺀 상대값
                self.delta_yaw = (self.yaw - self.base_yaw)*11
            else:
                self.delta_yaw = (self.yaw - self.base_yaw)*11
                self.base_yaw = self.yaw

            self.meta_yaw = self.meta_yaw + self.delta_yaw

            if self.base_pitch is None:
                self.base_pitch = serial_txt[0]
                # delta_pitch : 현재값에 기준값을 뺀 상대값
                self.delta_pitch = (self.pitch - self.base_pitch)*9
            else:
                self.delta_pitch = (self.pitch - self.base_pitch)*9
                self.base_pitch = self.pitch
            self.meta_pitch = self.meta_pitch + self.delta_pitch

        print(serial_txt)
        print("meta yaw: " + str(self.meta_yaw) + " meta pitch: " + str(self.meta_pitch))

        sum = 0.0
        hit = False
        # 터치패널에 손가락을 모두 뗐을때 hit!
        for i in range(4, 10):
            sum = sum + serial_txt[i]
            if sum == 0.0:
                self.hit = False
            else:
                self.hit = True
        # yaw와 pitch의 구간 범위
        self.yaw_range = [500.0, 200.0, -200.0, -500.0]
        self.pitch_range = [-350.0, -150.0, 200.0, 450.0]
#####################################################################
        # 2차원 평면이므로 2개의 축을 사용
        # 행렬로 치면 (a, 1)
        if self.meta_yaw > self.yaw_range[0]:
            self.pitch_module(self.pitch_range, "1")
        # (a, 2)
        elif self.yaw_range[1] <= self.meta_yaw < self.yaw_range[0]:
            self.pitch_module(self.pitch_range, "2")
        # (a, 3)
        elif self.yaw_range[2] <= self.meta_yaw < self.yaw_range[1]:
            self.pitch_module(self.pitch_range, "3")
        # (a, 4)
        elif self.yaw_range[3] <= self.meta_yaw < self.yaw_range[2]:
            self.pitch_module(self.pitch_range, "4")
        # (a, 5)
        elif self.meta_yaw < self.yaw_range[3]:
            self.pitch_module(self.pitch_range, "5")
#######################################################################


class Controller:
    # 마찬가지 위젯 변경 시그널
    switch_window = QtCore.pyqtSignal()

    def __init__(self):
        pass

    def show_main(self):
        self.main_window = vrFrame()
        self.main_window.show()
        # self.main_window.showMaximized()
        # self.main_window.showFullScreen()


def main():
    t = threading.Thread(target=loop_listen, daemon=True)
    t.start()
    app = QApplication(sys.argv)
    controller = Controller()
    controller.show_main()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
