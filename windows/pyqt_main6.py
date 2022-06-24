## QPushButton

import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

class MyApp(QWidget) :

    def __init__(self)  -> None :
       super().__init__()
       self.initUI() # 내가 만들 UI 초기화 함수

    def initUI(self) :
        self.setWindowTitle("QPush Button")
        self.setGeometry(810, 390, 300, 300)
        self.setWindowIcon(QIcon('./windows/images/lion.png'))

        btn1 = QPushButton('Hello',self)
        # btn1.setEnabled(True)
        btn1.clicked.connect(self.btn1_click) # 시그널

        # btn1.setGeometry(50,100,100,40)
        # QHBoxLayout, QVBoxLayout, QGridLayout
        
        vbox = QGridLayout(self)
        vbox.addWidget(btn1)
        
        self.show()

    def btn1_click(self) :
        QMessageBox.about(self, 'greeting', 'Hi, everyone~')
        

if __name__ == "__main__" :
    app = QApplication(sys.argv)
    wnd = MyApp()
    
    app.exec_()