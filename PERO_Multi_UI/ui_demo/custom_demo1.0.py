import sys
import threading
import time
import sqlite3

import serial
import serial.tools.list_ports as port_list
from PyQt5 import QtCore, QtTest
from PyQt5.QtCore import QSize, QBasicTimer, QObject, Qt
from PyQt5.QtGui import QIcon, QMovie
from PyQt5.QtWidgets import *


conn = sqlite3.connect('../set_db/pero_database.db')
cur = conn.cursor()

# serial 포트 설정
def connect_serial(serial_port):
    time.sleep(2)
    ser_conn = serial.Serial(
        port=serial_port,
        baudrate=115200,
    )
    return ser_conn


# 각 serial data가 제대로 들어왔는지 확인
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
            # 현재 연결된 usb serial 장치 중 JLink=DK보드의 포트번호를 찾기
            ports = list(port_list.comports())
            for p in ports:
                # JLink란 이름을 가진 COM 포트 번호를 찾아서 저장
                if "JLink" in str(p):
                    serial_port = str(p).split(" ")[0]

            if serial_port == "":
                # DK보드가 연결되지 않은 상태이다
                f = open("../set_db/serial_data.txt", "w")
                f.write("disconnect")
                f.close()
                raise NotImplementedError
            else:
                # DK보드가 연결되었으므로 serial data를 읽어온다
                ser = connect_serial(serial_port)

                while True:
                    # serial data를 읽을 수 있다면 리스트형식으로 저장
                    if ser.readable():
                        res = ser.readline()
                        serial_data = res.decode().split("\n")
                        serial_data = serial_data[0].split(",")

                        errchk = [isNumber(t) for t in serial_data]

                        if errchk == [True, True, True, True, True, True, True, True, True, True]:
                            intlist_flag = 'True'
                        else:
                            intlist_flag = 'False'

                    if len(serial_data) == 10 and intlist_flag == 'True':
                        # 하나의 리스트를 한줄로 덮어써서 txt 파일에 저장
                        vstr = ""
                        for i in serial_data:
                            vstr = vstr + str(i) + ","
                        vstr = vstr.rstrip(",")
                        f = open("../set_db/serial_data.txt", "w")
                        f.writelines(vstr)
                        print(vstr)
                        f.close()
                    else:
                        ser.close()
                        f = open("../set_db/serial_data.txt", "w")
                        f.write("data_error")
                        f.close()
                        raise NotImplementedError
    except NotImplementedError:
        pass

########################################################################################################
# setting window


class stackedFrame(QWidget):
    # window 위젯을 스위치시키기 위한 시그널
    switch_window = QtCore.pyqtSignal()

    def __init__(self):
        QWidget.__init__(self)
        self.initUI()

    def initUI(self):
        # process bar step
        self.timer = QBasicTimer()
        # index
        self.index = 0
        self.step = 0
        self.q_where = []

        # stack에 삽입할 위젯들을 생성
        self.start = QWidget()
        self.stack1 = QWidget()
        self.stack2 = QWidget()
        self.stack3 = QWidget()
        self.serial = QWidget()
        self.set_use = QWidget()

        # 각 stack 위젯에 배치할 객체들과 메서드를 갖는 함수 생성
        self.startLoading()
        self.qestion1()
        self.qestion2()
        self.qestion3()
        self.serial_init()
        self.setLoading()

        # StackWidget에 각 위젯들 삽입
        self.Stack = QStackedWidget(self)
        self.Stack.addWidget(self.start)
        self.Stack.addWidget(self.stack1)
        self.Stack.addWidget(self.stack2)
        self.Stack.addWidget(self.stack3)
        self.Stack.addWidget(self.serial)
        self.Stack.addWidget(self.set_use)

        vbox = QVBoxLayout(self)
        vbox.addWidget(self.Stack)

        self.setLayout(vbox)
        self.setGeometry(400, 200, 800, 400)
        self.setFixedSize(800, 400)
        self.setWindowTitle('setting window')
        self.setStyleSheet("background-color: white")
        self.center()

    # 중앙 위치
    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    # 처음 시작 로딩 위젯
    def startLoading(self):
        loading = QLabel()
        movie = QMovie("../img/loading.gif")
        loading.setMovie(movie)
        movie.start()

        layout = QFormLayout()
        layout.addRow(QLabel())
        layout.addRow(loading)
        layout.addRow(QLabel())

        # timer만큼 지난 후 다음 위젯으로
        self.timer.start(30, self)
        # 함수를 start 위젯에  set
        self.start.setLayout(layout)

    # 사용자의 type을 분류하기 위한 질문 위젯1
    def qestion1(self):
        testBtn = QPushButton(self)
        testBtn.setText("next")
        testBtn.clicked.connect(self.display)

        self.q1_ans1 = QRadioButton("오른손")
        self.q1_ans2 = QRadioButton("왼손")
        self.q1_ans3 = QRadioButton("양손")

        layout = QFormLayout()
        layout.addRow("주로 어떤 손을 사용하시나요?", QLabel())
        layout.addRow(QLabel())
        layout.addRow(self.q1_ans1)
        layout.addRow(self.q1_ans2)
        layout.addRow(self.q1_ans3)
        layout.addRow(QLabel())
        layout.addRow(QLabel())
        layout.addRow(QLabel())
        layout.addRow(QLabel())
        layout.addRow(testBtn)
        layout.setLabelAlignment(Qt.AlignCenter)
        layout.setFormAlignment(Qt.AlignBottom)
        self.stack1.setLayout(layout)

    # 사용자의 type을 분류하기 위한 질문 위젯2
    def qestion2(self):
        testBtn = QPushButton(self)
        testBtn.setText("next")
        testBtn.clicked.connect(self.display)

        self.q2_ans1 = QRadioButton("문서 프로그램")
        self.q2_ans2 = QRadioButton("웹 브라우저")
        self.q2_ans3 = QRadioButton("게임")
        self.q2_ans4 = QRadioButton("몰라")
        self.q2_ans5 = QRadioButton("전반적으로 다")

        layout = QFormLayout()
        layout.addRow("주로 어떤 프로그램에 사용하실 것 같나요?", QLabel())
        layout.addRow(QLabel())
        layout.addRow(self.q2_ans1)
        layout.addRow(self.q2_ans2)
        layout.addRow(self.q2_ans3)
        layout.addRow(self.q2_ans4)
        layout.addRow(self.q2_ans5)
        layout.addRow(QLabel())
        layout.addRow(testBtn)
        layout.setLabelAlignment(Qt.AlignCenter)
        layout.setFormAlignment(Qt.AlignBottom)

        self.stack2.setLayout(layout)

    # 사용자의 type을 분류하기 위한 질문 위젯3
    def qestion3(self):
        testBtn = QPushButton(self)
        testBtn.setText("next")
        testBtn.clicked.connect(self.display)

        icon_ci = QIcon("../img/circle.png")
        self.circle = QRadioButton()
        self.circle.setIcon(icon_ci)
        self.circle.setIconSize(QSize(150, 40))
        icon_rl = QIcon("../img/left_right.png")
        self.linear_rl = QRadioButton()
        self.linear_rl.setIcon(icon_rl)
        self.linear_rl.setIconSize(QSize(150, 40))
        icon_ud = QIcon("../img/up_down")
        self.linear_ud = QRadioButton()
        self.linear_ud.setIcon(icon_ud)
        self.linear_ud.setIconSize(QSize(150, 40))
        icon_cu = QIcon("../img/curve")
        self.curve = QRadioButton()
        self.curve.setIcon(icon_cu)
        self.curve.setIconSize(QSize(150, 40))

        layout = QFormLayout()
        layout.addRow("문서를 저장한다면 어떤 제스처를 사용하고 싶은가요?", QLabel())
        layout.addRow(QLabel())
        layout.addRow(self.circle)
        layout.addRow(self.linear_rl)
        layout.addRow(self.linear_ud)
        layout.addRow(self.curve)
        layout.addRow(testBtn)
        layout.setLabelAlignment(Qt.AlignCenter)
        layout.setFormAlignment(Qt.AlignBottom)

        self.stack3.setLayout(layout)

    # 터치 커스텀을 위한 위젯
    def serial_init(self):
        t = threading.Thread(target=loop_listen, daemon=True)
        t.start()

        testBtn = QPushButton(self)
        testBtn.setText("next")
        testBtn.clicked.connect(self.display)

        # comment
        self.comment = QLabel("엄지 손가락을 대주세요")

        # touch panel
        panel_1 = QLabel(self)
        panel_1.setStyleSheet("background-color: red")
        panel_2 = QLabel(self)
        panel_2.setStyleSheet("background-color: red")
        panel_3 = QLabel(self)
        panel_3.setStyleSheet("background-color: red")
        panel_4 = QLabel(self)
        panel_4.setStyleSheet("background-color: red")
        panel_5 = QLabel(self)
        panel_5.setStyleSheet("background-color: red")
        panel_6 = QLabel(self)
        panel_6.setStyleSheet("background-color: red")
        panel_7 = QLabel(self)
        panel_7.setStyleSheet("background-color: red")
        panel_8 = QLabel(self)
        panel_8.setStyleSheet("background-color: red")
        panel_9 = QLabel(self)
        panel_9.setStyleSheet("background-color: red")
        panel_10 = QLabel(self)
        panel_10.setStyleSheet("background-color: red")

        layout = QFormLayout()
        layout.addRow(self.comment)
        layout.addRow(QLabel())
        hbox = QHBoxLayout()
        hbox.addWidget(panel_1)
        hbox.addWidget(panel_2)
        hbox.addWidget(panel_3)
        hbox.addWidget(panel_4)
        hbox.addWidget(panel_5)
        hbox.addWidget(panel_6)
        hbox.addWidget(panel_7)
        hbox.addWidget(panel_8)
        hbox.addWidget(panel_9)
        hbox.addWidget(panel_10)
        layout.addRow(hbox)
        layout.addRow(QLabel())
        layout.addRow(testBtn)
        layout.setFormAlignment(Qt.AlignBottom)

        self.serial.setLayout(layout)

    # 최종 setting을 위한 딜레이 위젯
    def setLoading(self):
        self.pbar = QProgressBar(self)

        layout = QFormLayout()
        layout.addRow(QLabel())
        layout.addRow(self.pbar)
        layout.addRow(QLabel())
        layout.setFormAlignment(Qt.AlignCenter)

        self.set_use.setLayout(layout)

    ####################################################
    # EVENT

    def display(self):
        # 첫번째 질문 페이지
        if self.index == 1:
            if self.q1_ans1.isChecked():
                self.q_where.append("1")
                self.index = self.index + 1
                self.Stack.setCurrentIndex(self.index)
            elif self.q1_ans2.isChecked():
                self.q_where.append("2")
                self.index = self.index + 1
                self.Stack.setCurrentIndex(self.index)
            elif self.q1_ans3.isChecked():
                self.q_where.append("3")
                self.index = self.index + 1
                self.Stack.setCurrentIndex(self.index)
            else:
                reply = QMessageBox.question(self, 'Wait!', "질문에 답을 선택해주세요!", QMessageBox.Ok)
        elif self.index == 2:
            if self.q2_ans1.isChecked():
                self.q_where.append("1")
                self.index = self.index + 1
                self.Stack.setCurrentIndex(self.index)
            elif self.q2_ans2.isChecked():
                self.q_where.append("2")
                self.index = self.index + 1
                self.Stack.setCurrentIndex(self.index)
            elif self.q2_ans3.isChecked():
                self.q_where.append("3")
                self.index = self.index + 1
                self.Stack.setCurrentIndex(self.index)
            elif self.q2_ans4.isChecked():
                self.q_where.append("4")
                self.index = self.index + 1
                self.Stack.setCurrentIndex(self.index)
            elif self.q2_ans5.isChecked():
                self.q_where.append("5")
                self.index = self.index + 1
                self.Stack.setCurrentIndex(self.index)
            else:
                reply = QMessageBox.question(self, 'Wait!', "질문에 답을 선택해주세요!", QMessageBox.Ok)
        elif self.index == 3:
            if self.circle.isChecked():
                self.q_where.append("1")
                self.index = self.index + 1
                self.Stack.setCurrentIndex(self.index)
            elif self.linear_rl.isChecked():
                self.q_where.append("2")
                self.index = self.index + 1
                self.Stack.setCurrentIndex(self.index)
            elif self.linear_ud.isChecked():
                self.q_where.append("3")
                self.index = self.index + 1
                self.Stack.setCurrentIndex(self.index)
            elif self.curve.isChecked():
                self.q_where.append("4")
                self.index = self.index + 1
                self.Stack.setCurrentIndex(self.index)
            else:
                reply = QMessageBox.question(self, 'Wait!', "질문에 답을 선택해주세요!", QMessageBox.Ok)
            print(self.q_where)
            # 질문에 대한 답으로 사용자의 타입을 DB에서 찾기
            cur.execute("select userType from type_question where question1 =%s and question2 =%s and question3 =%s" %(self.q_where[0], self.q_where[1], self.q_where[2]))
            row = cur.fetchall()
            type = row[0][0]
            print(type)  # type :사용자의 타입
        # serial page: 마지막 setting 페이지 전에 process bar를 0으로 초기화
        elif self.index == 4:
            self.step = 0
            self.index = self.index + 1
            self.Stack.setCurrentIndex(self.index)
        # setting이 끝나면 setting 페이지 close
        elif self.index >= 5:
            self.close()

    def timerEvent(self, e):
        # process bar의 value를 step을 set
        if self.step < 100:
            self.step = self.step + 1
            self.pbar.setValue(self.step)
        # step이 100이 넘어갔을 때
        elif self.step >= 100:
            # 첫번째 위젯이라면 다음 페이지로 이동
            if self.index == 0:
                self.index = self.index + 1
                self.Stack.setCurrentIndex(self.index)
            # 마지막 setting 페이지라면 timer를 멈추고 다음 윈도우를 띄움
            elif self.index == 5:
                self.timer.stop()
                self.switch_window.emit()
            self.timer.swap(self.timer)
            return


########################################################################################################
# pero window

# right list의 각 item을 구성할 class
class itemWidget(QWidget):

    def __init__(self, app_command, touch, gesture, db_id):
        QWidget.__init__(self)

        self.line_layout = QHBoxLayout(self)

        self.line_check = QCheckBox()
        self.app_function = QLabel()
        # label을 영역을 채우도록 expanding 시킴
        self.app_function.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.app_function.setText(app_command)
        self.touch = QLabel()
        self.touch.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.touch.setText(touch)
        self.gesture = QLabel()
        self.gesture.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.gesture.setText(gesture)
        self.modify_btn = QPushButton()
        self.modify_btn.setText("🖊")
        self.modify_btn.setObjectName(db_id)

        self.line_layout.addWidget(self.line_check)
        self.line_layout.addWidget(self.app_function)
        self.line_layout.addWidget(self.touch)
        self.line_layout.addWidget(self.gesture)
        self.line_layout.addWidget(self.modify_btn)
        self.line_layout.setAlignment(Qt.AlignCenter)
        self.line_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.line_layout)


########################################################################
# 메인 pero 위젯
class peroWindow(QWidget):
    switch_window = QtCore.pyqtSignal(str, str)

    def __init__(self):
        QWidget.__init__(self)

        self.leftlist = QListWidget()
        self.rightlist = QListWidget()
        self.rightlist.setStyleSheet("border: 1px solid gray;")
        # right list 위젯의 버튼과 체크박스를 담을 리스트
        self.gest_checkBox = []
        self.modify_btns = []

        # 현재 DB에 있는 application 종류를 조회
        apps = cur.execute("SELECT DISTINCT application FROM user_gesture")
        apps = apps.fetchall()
        for i in range(len(apps)):
            self.leftlist.insertItem(i, "%d. " % (i + 1) + apps[i][0])

        self.select_app = QLabel()
        # 첫번째 Application
        self.select_app.setText(apps[0][0])
        self.select_app.setObjectName(apps[0][0])

        # 첫번째 application의 데이터를 조회
        self.rightWidgetSet(apps[0][0])

        self.gest_blank = QLabel()
        self.gest_blank.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.gest_delBtn = QPushButton()
        self.gest_delBtn.setText("-")
        self.gest_delBtn.clicked.connect(lambda: self.gestDelBtn(self.select_app.objectName()))
        self.app_addBtn = QPushButton()
        self.app_addBtn.setText("+")
        self.app_addBtn.clicked.connect(lambda: self.appAddBtn(self.select_app.objectName()))
        self.app_delBtn = QPushButton()
        self.app_delBtn.setText("-")
        self.app_delBtn.clicked.connect(lambda: self.appDelBtn(self.select_app.objectName()))
        self.app_blank = QLabel()
        self.app_blank.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        # hbox_bottom.addWidget(self.gest_btn, alignment=Qt.AlignBottom)

        hbox = QHBoxLayout(self)

        vbox_l = QVBoxLayout(self)
        vbox_l.addWidget(self.leftlist)
        v_hbox_l = QHBoxLayout(self)
        v_hbox_l.addWidget(self.app_addBtn)
        v_hbox_l.addWidget(self.app_delBtn)
        v_hbox_l.addWidget(self.app_blank)
        vbox_l.addLayout(v_hbox_l)

        vbox_r = QVBoxLayout(self)
        vbox_r.addWidget(self.select_app)
        vbox_r.addWidget(self.rightlist)
        v_hbox_r = QHBoxLayout(self)
        v_hbox_r.addWidget(self.gest_blank)
        v_hbox_r.addWidget(self.gest_delBtn)
        vbox_r.addLayout(v_hbox_r)

        hbox.addLayout(vbox_l)
        hbox.addLayout(vbox_r)

        self.peroMenuBar = QMenuBar()
        menubar = self.peroMenuBar.addMenu("&Help")
        exitAction = QAction('Exit', self)
        exitAction.triggered.connect(qApp.quit)
        menubar.addAction(exitAction)

        self.leftlist.setCurrentRow(0)
        self.leftlist.currentRowChanged.connect(lambda: self.display(apps))

        self.setLayout(hbox)
        self.setFixedSize(800, 400)
        self.center()
        self.setStyleSheet("background-color: white")
        self.setWindowTitle('pero window')
        # self.show()

    ########################################################################
    # 중앙 위치
    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    ########################################################################
    # right list 위젯 구성 함수
    def rightWidgetSet(self, c_app):
        self.gest_checkBox.clear()
        self.modify_btns.clear()
        self.rightlist.clear()
        cur.execute("SELECT command_name, touch_fin, gesture, id FROM user_gesture WHERE application = '%s'" % c_app)
        app_data = cur.fetchall()
        self.select_app.setText(c_app)
        self.select_app.setObjectName(c_app)

        for data in app_data:
            item = QListWidgetItem(self.rightlist)
            self.custom_item = itemWidget(data[0], data[1], data[2], data[3])
            self.modify_btns.append(self.custom_item.modify_btn)
            self.gest_checkBox.append(self.custom_item.line_check)
            self.custom_item.setStyleSheet("border: 0px solid")
            self.rightlist.setItemWidget(item, self.custom_item)
            self.rightlist.addItem(item)

        for i in range(len(self.modify_btns)):
            self.modify_btns[i].clicked.connect(lambda: self.modifyBtnClick(c_app))

    #############################
    # event
    def display(self, apps):
        for i in range(len(apps)):
            if self.leftlist.currentRow() == i:
                self.rightWidgetSet(apps[i][0])

    # pencle button
    def modifyBtnClick(self, c_app):
        # 현재 클릭한 버튼의 객체
        sender = self.sender()
        # 현재클릭한 버튼의 objectName
        # sender.objectName() = id : 이 값을 기준으로 db를 update하여 페이지를 수정한다.
        cur.execute("SELECT gesture FROM user_gesture WHERE id = '%s'" % sender.objectName())
        c_ges = cur.fetchall()
        print(c_ges[0][0])
        # 버튼을 클릭하면 signal 발생
        self.switch_window.emit(sender.objectName(), c_ges[0][0])

    def gestDelBtn(self, c_app):
        print(c_app)
        # 체크된 각 item과 그 DB의 id를 확인
        for i in range(len(self.gest_checkBox)):
            if self.gest_checkBox[i].isChecked():
                print(self.modify_btns[i].objectName())
                print(self.rightlist.item(i))
        # DB에서 체크된 튜플의 gesture와 touch를 delete한다.

        # rightlist clear한 후 다시 db 조회해서 띄운다
        self.rightlist.clear()
        self.rightWidgetSet(c_app)

    def appAddBtn(self, c_app):
        # 적용할 application을 조회한 후 추가 하도록
        # rightlist clear한 후 다시 db 조회해서 띄운다
        self.rightlist.clear()
        self.rightWidgetSet(c_app)

    def appDelBtn(self, c_app):
        print(c_app)
        # 체크된 각 item과 그 DB의 id를 확인
        for i in range(len(self.gest_checkBox)):
            if self.gest_checkBox[i].isChecked():
                print(self.modify_btns[i].objectName())
                print(self.rightlist.item(i))

        # rightlist clear한 후 다시 db 조회해서 띄운다
        self.rightlist.clear()
        self.rightWidgetSet(c_app)


########################################################################
# gesture modify 클래스
class gestureModify(QWidget):
    switch_window = QtCore.pyqtSignal(str)

    def __init__(self, g_id, c_ges):
        QWidget.__init__(self)
        self.g_id = g_id
        self.c_ges = c_ges
        self.setupUI()

    def setupUI(self):
        self.setWindowTitle('custom gesture')
        self.setFixedSize(500, 300)

        cur.execute("SELECT application, command_name FROM user_gesture WHERE id = '%s'" % self.g_id)
        datas = cur.fetchall()
        gesture = ["linear_up", "linear_down", "사용안함"]

        self.c_command = QLabel()
        self.c_command.setText(datas[0][1])

        self.custom_gesture = QComboBox()
        for i in range(len(gesture)):
            self.custom_gesture.addItem(gesture[i])

        self.button = QPushButton('save')
        self.button.clicked.connect(lambda: self.login(datas[0][0]))
        layout = QGridLayout()
        layout.addWidget(self.c_command, 0, 0)
        layout.addWidget(self.custom_gesture, 0, 2)
        layout.addWidget(QLabel(), 1, 0)
        layout.addWidget(QLabel(), 1, 2)
        layout.addWidget(self.button, 1, 1)

        self.setLayout(layout)

    def login(self, c_app):
        # 기존의 기능에 매핑된 제스처를 삭제
        cur.execute(
            '''UPDATE user_gesture SET
                gesture = CASE WHEN application = "%s" AND gesture = "%s" THEN "" ELSE gesture END;'''
            % (c_app, self.c_ges))
        # 선택한 gesture 세팅
        if self.custom_gesture.currentText() == "사용안함":
            set_ges = ""
        else:
            set_ges = self.custom_gesture.currentText()
            # 선택한 제스처의 기존 설정을 삭제
            cur.execute(
                '''UPDATE user_gesture SET
                    gesture = ""
                    WHERE gesture = "%s" AND application = "%s";'''
                % (set_ges, c_app))
        # 사용자가 설정한대로 gesture 매핑 update
        cur.execute(
            '''UPDATE user_gesture SET
                gesture = "%s"
                WHERE id = "%s";'''
            % (set_ges, self.g_id))

        self.switch_window.emit(c_app)

######################################################################################################


class Controller:

    def __init__(self):
        pass

    def show_main(self):
        # start signal
        self.main_window = stackedFrame()
        self.main_window.switch_window.connect(self.show_pero)
        self.main_window.show()

    def show_pero(self):
        self.pero_main = peroWindow()
        self.pero_main.switch_window.connect(self.gesture_modify)
        self.main_window.close()
        self.pero_main.show()

    def gesture_modify(self, g_id, c_ges):
        self.g_ui_modify = gestureModify(g_id, c_ges)
        self.g_ui_modify.switch_window.connect(self.pero_custom)
        self.g_ui_modify.show()

    def pero_custom(self, m_data):
        self.pero_main.rightWidgetSet(m_data)
        self.g_ui_modify.close()


def main():
    app = QApplication(sys.argv)
    # ex = stackedFrame()
    controller = Controller()
    controller.show_main()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
