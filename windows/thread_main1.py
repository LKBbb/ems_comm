# PyQt5 템플릿 소스
import sys
from PyQt5 import uic
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *


class MyApp(QWidget) :
    def __init__(self) :
        super(MyApp, self).__init__()
        self.initUI()


    def initUI(self) :
        uic.loadUi('./windows/ui/threadtask.ui', self)
        self.btnStart.clicked.connect(self.btnStartClicked)
        self.show()

    def btnStartClicked(self) :
        self.pgbTask.setRange(0, 9999)
        for i in range(0, 10000) :
            print(f'출력 > {i}')
            self.pgbTask.setValue(i)
            self.txbLog.append(f'출력 > {i}')



if __name__ == '__main__' :
    app = QApplication(sys.argv)
    win = MyApp()
    app.exec_()
