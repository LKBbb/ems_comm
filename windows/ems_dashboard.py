# EMS 대시보드
# pyrcc5 dashboard.qrc -o dashboard_rc.py
# pip install PyMySQL
from socket import AI_PASSIVE
import string
from PyQt5 import uic
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import sys
import requests
import json
import dashboard_rc # 리소스 py파일 추가
import paho.mqtt.client as mqtt
import time
import pymysql

apikey = '4a8801006868cc69e65350b6be9b2138'
broker_url = '127.0.0.1' # 로컬에 MQTT Broker가 같이 설치되어 있으므로 127.0.0.1

class Worker(QThread) :
    sigStatus = pyqtSignal(str) # 연결상태 시그널, 부모클래스 MyApp 전달됨
    sigMessage = pyqtSignal(dict) #MQTT Subscribe Signal, MyApp 전달 (딕셔너리형)
    def __init__(self, parent) :
        super().__init__(parent)
        self.parent = parent
        self.host = broker_url
        self.port = 1883
        self.client = mqtt.Client(client_id = 'Dashboard')

    def onConnect(self, mqttc, obj, flags, rc) :
        try :
            print(f'Connected with result code > {rc}')
            self.sigStatus.emit('SUCCEED') # MyApp으로 메세지 전달
        except Exception as e :
            print(f'error > {e.args}')
            self.sigStatus.emit('FAILED')

    def onMessage(self, mqttc, obj, msg) :
        rcv_msg = str(msg.payload.decode('UTF-8'))
        # print(f'{msg.topic} / {rcv_msg}')
        self.sigMessage.emit(json.loads(rcv_msg))
        time.sleep(2.0)

    def mqttloop(self) :
        self.client.loop()
        print('MQTT Client loop')

    def run(self) :
        self.client.on_connect = self.onConnect
        self.client.on_message = self.onMessage
        self.client.connect(self.host, self.port)
        self.client.subscribe(topic = 'ems/rasp/data/')
        self.client.loop_forever()

class MyApp(QMainWindow) :
    
    def __init__(self) :
        super(MyApp, self).__init__()
        self.initUI()
        self.showTime()
        self.showWeather()
        self.initThread()


    def initThread(self) :
        self.myThread = Worker(parent = self)
        self.myThread.sigStatus.connect(self.updateStatus)
        self.myThread.start()
        self.myThread.sigMessage.connect(self.updateMessages)


    @pyqtSlot(dict)
    def updateMessages(self, data) :
        # 1. 딕셔너리 분해
        # 2. Label에 Devide 명칭 Update
        # 3. 온습도 label에 현재 온습도 업데이트
        # 4. MySQL DB에 입력
        dev_id = data['DEV_ID']
        temp = data['TEMP']
        humid = data['HUMID']
        self.lblTempTitle.setText(f'{dev_id} Temperature')
        self.lblHumidTitle.setText(f'{dev_id} Humidity')
        self.lblCurrentTemp.setText(f'{temp:.1f}')
        self.lblCurrentHumid.setText(f'{humid:.0f}')

        # DB입력
        self.conn = pymysql.connect(host = '127.0.0.1', user = 'bms',
                                    password = '1234', db = 'bms',
                                    charset = 'euckr') 
        curr_dt = data['CURR_DT']
        query = '''INSERT INTO ems_data
		                (dev_id, curr_dt, temp, humid)
                    VALUES
                        (%s, %s, %s, %s)'''
        with self.conn :
            with self.conn.cursor() as cur :
                cur.execute(query, (dev_id, curr_dt, temp, humid))
                self.conn.commit()
                print('DB Inserted!')


    @pyqtSlot(str)
    def updateStatus(self, stat) :
        if stat == 'SUCCEED' :
            self.lblStatus.setText('Connected!')
            self.connFrame.setStyleSheet(
                'background-image:url(:/green);'
                'background-repeat:no-repeat;'
                'border:none;'
        )
        else :
            self.lblStatus.setText('Disconnected!')
            self.connFrame.setStyleSheet(
                'background-image:url(:/red);'
                'background-repeat:no-repeat;'
                'border:none;'
        )     


    def showWeather(self) :
        url = 'https://api.openweathermap.org/data/2.5/weather' \
              f'?q=seoul&appid={apikey}'\
              '&lang=kr&units=metric'
        result = requests.get(url)
        result = json.loads(result.text)
        weather = result['weather'][0]['main'].lower()
        self.weatherFrame.setStyleSheet(
            (
                f'background-image: url(:/{weather});'
                'background-repeat:no-repeat;'
                'border:none;'
            )
        )


    def showTime(self) :
        today = QDateTime.currentDateTime()
        currDate = today.date()
        currTime = today.time()
        currDay = today.toString('dddd')

        self.lblDate.setText(currDate.toString('yyyy-MM-dd'))
        self.lblDay.setText(currDay)
        self.lblTime.setText(currTime.toString('HH:mm'))
        
        if today.time().hour() >= 5 and today.time().hour() < 12 :
            self.lblGreeting.setText('Good Morning!')
        elif today.time().hour() >= 12 and today.time().hour() < 18 :
            self.lblGreeting.setText('Good Afternoon!')
        elif today.time().hour() >= 18 or today.time().hour() < 5:
            self.lblGreeting.setText('Good Evening!')


    def initUI(self) :
        uic.loadUi('./windows/ui/dashboard.ui', self)
        self.setWindowIcon(QIcon('iot_64.png'))
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
        # Widget Signal 정의
        self.btnTempAlarm.clicked.connect(self.btnTempAlarmClicked)
        self.btnHumidAlarm.clicked.connect(self.btnHumidAlarmClicked)
        self.show()
    
    def btnTempAlarmClicked(self) :
        QMessageBox.information(self, '알람', '이상온도로 냉방 가동')

    def btnHumidAlarmClicked(self) :
        QMessageBox.information(self, '알람', '이상습도로 제습 가동')





    def closeEvent(self, signal) : 
        ans = QMessageBox.question(self, '종료', '정말 종료하시겠습니까?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if ans == QMessageBox.Yes :
            signal.accept()
        else :
            signal.ignore()
if __name__ == '__main__' :
    app = QApplication(sys.argv)
    win = MyApp()
    app.exec_()    