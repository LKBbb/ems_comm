# New Adafruit Package
# sudo pip install adafruit-circuitpython-dht
# sudo apt install libgpiod2

# + -> 오른쪽 1
# out -> 왼쪽 4
# - -> 오른쪽 3 

import adafruit_dht as dht
import board
import time
 
SENSOR = dht.DHT11(board.D4)

while True :
    try :
        t = SENSOR.temperature
        h = SENSOR.humidity
        print(f'Temp > {t:.1f}`C / Humidity > {h:.1f}%')
    

    except RuntimeError as e:
        print(f'ERROR > {e.args[0]}')
        time.sleep(1.5)

    except Exception as e :
        SENSOR.exit()
        raise e

    time.sleep(1.5)    