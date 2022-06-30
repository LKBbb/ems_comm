# PyQt5 템플릿 소스
import sys
from PyQt5 import uic
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *


class MyApp(QWidget) :
    closeSignal = pyqtSignal() # CustomSignal
    def __init__(self) :
        super(MyApp, self).__init__()
        self.initUI()


    def initUI(self) :
        self.setWindowTitle('Close Demo')
        self.resize(300,300)

        self.btnClose = QPushButton('close',self)
        self.btnClose.clicked.connect(self.btnCloseClicked)
        self.closeSignal.connect(self.onClose)
        self.show()

    def onClose(self) :
        self.close()

    def btnCloseClicked(self) :
        self.closeSignal.emit()


if __name__ == '__main__' :
    app = QApplication(sys.argv)
    win = MyApp()
    app.exec_()
