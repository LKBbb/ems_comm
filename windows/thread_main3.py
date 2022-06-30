# Thread 사용 / CustomSignal 동작
import sys
from PyQt5 import uic
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import time

class Worker(QThread) : # PyQt에서 Thread 사용
    valChangeSignal = pyqtSignal(int)

    def __init__(self, parent) :
        super().__init__(parent)
        self.parent = parent
        self.working = True

    def run(self) : # Thread로 동작할 내용
        while self.working == True :
            for i in range(0, 10000) :
                print(f'출력 > {i}')
                self.valChangeSignal.emit(i)
                time.sleep(0.0001)

class MyApp(QWidget) :
    setValueSignal = pyqtSignal()
    def __init__(self) :
        super(MyApp, self).__init__()
        self.initUI()

    def initUI(self) :
        uic.loadUi('./windows/ui/threadtask.ui', self)
        self.btnStart.clicked.connect(self.btnStartClicked)

        # Worker 클래스가 가지고 있는 valChangeSignal 설정
        self.th = Worker(self)
        self.th.valChangeSignal.connect(self.updateProgress) # 슬롯정의
        self.show()
    
    @pyqtSlot(int)
    def updateProgress(self, val) :
        self.pgbTask.setValue(val)
        self.txbLog.append(f'출력 > {val}')
        if val == 9999 :
            self.th.working = False        

    @pyqtSlot()
    def btnStartClicked(self) :
        self.pgbTask.setRange(0, 9999)
        self.th.start()
        self.th.working = True

if __name__ == '__main__' :
    app = QApplication(sys.argv)
    win = MyApp()
    app.exec_()
