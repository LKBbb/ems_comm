# MQTT Pub/Sub App
from http import client
from threading import Thread, Timer
import time
import paho.mqtt.client as mqtt
import json
import datetime as dt
import adafruit_dht as dht
import board

SENSOR = dht.DHT11(board.D4)

class publisher(Thread) :
    def __init__(self) :
        Thread.__init__(self)
        self.host = '192.168.0.13'
        self.port = 1883
        print('Publisher Thread 시작')
        self.client = mqtt.Client(client_id = 'EMS04')

    def run(self) :
        self.client.connect(self.host, self.port)
        self.publish_data_auto()

    def publish_data_auto(self) :
        t = SENSOR.temperature
        h = SENSOR.humidity
        curr = dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        origin_data = {'DEV_ID' : 'EMS04', 'CURR_DT' : curr,
                    'TEMP' : t, 'HUMID' : h}
        pub_data = json.dumps(origin_data)
        self.client.publish(topic = 'ems/rasp/data/', payload = pub_data)
        print('Published')
        Timer(3.0, self.publish_data_auto).start()
        

class subscriber(Thread) :
    def __init__(self) :
        Thread.__init__(self)
        self.host = '127.0.0.1'
        self.port = 1883
        print('subscriber Thread 시작')
        self.client = mqtt.Client(client_id = 'EMS004')

    def onConnect(self, mpttc, obj, flags, rc) :
        print(f'sub : connected with rc > {rc}')

    def onMessage(self, mqttc, obj, msg) :
        rcv_msg = str(msg.payload.decode('UTF-8'))
        print(f'{msg.topic} / {rcv_msg}')
        time.sleep(2.0)


    def run(self) :
        self.client.on_connect = self.onConnect
        self.client.on_message = self.onMessage
        self.client.connect(self.host, self.port)
        self.client.subscribe(topic = 'ems/rasp/data/')
        self.client.loop_forever()


if __name__ == '__main__' :
    thPub = publisher()
    thSub = subscriber()
    thPub.start()
    thSub.start()