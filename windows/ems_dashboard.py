# EMS 대시보드
# pyrcc5 dashboard.qrc -o dashboard_rc.py
# pip install PyMySQL
# py -3.10 -m pip install pyqtgraph
# py -3.10 -m pip install pyqtchart
from PyQt5 import uic
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import sys
from numpy import append
import requests
import json
import dashboard_rc # 리소스 py파일 추가
import paho.mqtt.client as mqtt
import time
import pymysql
import datetime as dt
from PyQt5.QtChart import *



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
    isTempAlarmed = False # 알람여부
    isHumidAlarmed = False # 알람여부
    tempData = humidData = None
    idx = 0
    
    def __init__(self) :
        super(MyApp, self).__init__()
        self.initUI()
        self.showTime()
        self.showWeather()
        self.initThread()
        self.initChart()
    
    def initChart(self) :
        # self.viewLimit = 128 # chart에 그릴 갯수 제한
        self.tempData = self.humidData = QLineSeries()

        # axisX = QDateTimeAxis()
        # axisX.setFormat('HH:mm:ss')
        # axisX.setTickCount(5)
        # dt = QDateTime.currentDateTime()
        # axisX.setRange(dt, dt.addSecs(self.viewLimit))

        # axisY = QValueAxis
        self.iotChart = QChart()
        # self.iotChart.addAxis(axisX, Qt.AlignBottom)
        # self.iotChart.addAxis(axisY, Qt.AlignLeft)
        # self.tempData.attachAxis(axisX)
        # self.humidData.attachAxis(axisX)
        self.iotChart.addSeries(self.tempData)
        # self.iotChart.addSeries(self.humidData)
        self.iotChart.layout().setContentsMargins(5, 5, 5, 5)
        self.dataView.setChart(self.iotChart)
        self.dataView.setRenderHint(QPainter.Antialiasing)
        
    #     self.iotData = QLineSeries()
    #     self.iotData.append(0, 10)
    #     self.iotData.append(1, 20)
    #     self.iotData.append(2, 15)
    #     self.iotData.append(3, 22)

    #     self.iotChart = QChart()
    #     self.iotChart.addSeries(self.iotData)
    #     self.dataView.setChart(self.iotChart)


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
        # 5. 이상기온 알람
        # 6. txbLog 로그 출력
        # 7. Chart 데이터 추가
        dev_id = data['DEV_ID']
        temp = data['TEMP']
        humid = data['HUMID']
        self.lblTempTitle.setText(f'{dev_id} Temperature')
        self.lblHumidTitle.setText(f'{dev_id} Humidity')
        self.lblCurrentTemp.setText(f'{temp:.1f}')
        self.lblCurrentHumid.setText(f'{humid:.0f}')
        # self.txbLog.append(json.dumps(data))
        if temp >= 30.0 :
            self.lblTempAlarm.setText(f'{dev_id} 이상기온감지')
            self.btnTempAlarm.setEnabled(True)
            self.btnTempStop.setEnabled(False)
            if self.isTempAlarmed == False :
                QMessageBox.warning(self, '경고', f'{dev_id}에서 이상 기온 감지!!!')
                self.isTempAlarmed = True
        elif temp <= 26.0 :
            self.lblTempAlarm.setText(f'{dev_id} 정상기온')
            self.isTempAlarmed = False
            self.btnTempAlarm.setDisabled(True)
            self.btnTempStop.setDisabled(False)
        if humid >= 85.0 :
            self.lblHumidAlarm.setText(f'{dev_id} 이상습도감지')
            self.btnTempAlarm.setEnabled(True)
            self.btnTempStop.setEnabled(False)
            if self.isHumidAlarmed == False :
                QMessageBox.warning(self, '경고', f'{dev_id}에서 이상 습도 감지!!!')
                self.isHumidAlarmed = True
        elif temp < 65.0 :
            self.lblHumidAlarm.setText(f'{dev_id} 정상습도')
            self.isHumidAlarmed = False
            self.btnHumidAlarm.setDisabled(True)
            self.btnHumidStop.setDisabled(False)

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
        self.tempData = self.humidData = QLineSeries()
        uic.loadUi('./windows/ui/dashboard.ui', self)
        self.setWindowIcon(QIcon('iot_64.png'))
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
        self.btnTempAlarm.setDisabled(True)
        self.btnTempStop.setDisabled(True)
        self.btnHumidAlarm.setDisabled(True)
        self.btnHumidStop.setDisabled(True)

        # Widget Signal 정의
        self.btnTempAlarm.clicked.connect(self.btnTempAlarmClicked)
        self.btnTempStop.clicked.connect(self.btnTempStopClicked)
        self.btnHumidAlarm.clicked.connect(self.btnHumidAlarmClicked)
        self.btnHumidStop.clicked.connect(self.btnHumidStopClicked)
        self.show()

    def btnTempStopClicked (self) :
        QMessageBox.information(self, '정상', '에어컨 중지')
        self.client = mqtt.Client(client_id = 'Controller')
        self.client.connect(broker_url, 1883)
        curr = dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        origin_data = {'DEV_ID' : 'CONTROL', 'CURR_DT' : curr,
                       'TYPE' : 'AIRCON', 'STAT' : 'OFF'}
        pub_data = json.dumps(origin_data)
        self.client.publish(topic = 'ems/rasp/control/', payload = pub_data)
        print('AIRCON OFF Published')
        self.insertAlarmData('CONTROL', curr, 'AIRCON', 'OFF')

    def btnHumidStopClicked(self) :
        QMessageBox.information(self, '정상', '제습기 중지')
        self.client = mqtt.Client(client_id = 'Controller')
        self.client.connect(broker_url, 1883)
        curr = dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        origin_data = {'DEV_ID' : 'CONTROL', 'CURR_DT' : curr,
                       'TYPE' : 'HUMID', 'STAT' : 'OFF'}
        pub_data = json.dumps(origin_data)
        self.client.publish(topic = 'ems/rasp/control/', payload = pub_data)
        print('Dehumidufier Off Published')
        self.insertAlarmData('CONTROL', curr, 'HUMID', 'OFF')


    def btnTempAlarmClicked(self) :
        QMessageBox.information(self, '알람', '이상온도로 에어컨 가동')
        self.client = mqtt.Client(client_id = 'Controller')
        self.client.connect(broker_url, 1883)
        curr = dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        origin_data = {'DEV_ID' : 'CONTROL', 'CURR_DT' : curr,
                       'TYPE' : 'AIRCON', 'STAT' : 'ON'}
        pub_data = json.dumps(origin_data)
        self.client.publish(topic = 'ems/rasp/control/', payload = pub_data)
        print('AIRCON On Published')
        self.insertAlarmData('CONTROL', curr, 'AIRCON', 'ON')


    def btnHumidAlarmClicked(self) :
        QMessageBox.information(self, '알람', '이상습도로 제습기 가동')
        self.client = mqtt.Client(client_id = 'Controller')
        self.client.connect(broker_url, 1883)
        curr = dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        origin_data = {'DEV_ID' : 'CONTROL', 'CURR_DT' : curr,
                       'TYPE' : 'HUMID', 'STAT' : 'ON'}
        pub_data = json.dumps(origin_data)
        self.client.publish(topic = 'ems/rasp/control/', payload = pub_data)
        print('Dehumidufier On Published')
        self.insertAlarmData('CONTROL', curr, 'HUMID', 'ON')


    # 이상상태, 정상상태 DB저장함수   
    def insertAlarmData(self, dev_id, curr_dt, types, stat) :
        self.conn = pymysql.connect(host = '127.0.0.1', user = 'bms',
                                    password = '1234', db = 'bms',
                                    charset = 'euckr') 
        query = '''INSERT INTO ems_alarm
		                (dev_id, curr_dt, type, stat)
                    VALUES
                        (%s, %s, %s, %s)'''
        with self.conn :
            with self.conn.cursor() as cur :
                cur.execute(query, (dev_id, curr_dt, types, stat))
                self.conn.commit()
                print('Alarm Inserted!')
        # chart 업데이트
        self.updateChart(curr_dt, temp, humid)

    def updateChart(self, curr_dt, temp, humid) :
        self.tempData = append(self.idx, temp)
        self.humidData = append(self.idx, humid)

        self.iotChart
        pass

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