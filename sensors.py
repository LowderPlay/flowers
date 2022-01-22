import json
import threading
import serial


class Sensors:
    def __init__(self):
        self.serial = serial.Serial('/dev/ttyAMA1', 115200)
        self.thread = threading.Thread(target=self.readline, args=())
        self.thread.start()

        self._humidity_calibration = (120, 670)  # min, max

        self.ground_temperature = None
        self._ground_humidity = None
        self.air_temperature = None
        self.air_humidity = None

    @property
    def ground_humidity(self):
        return round((self._ground_humidity - self._humidity_calibration[0]) / \
               (self._humidity_calibration[1] - self._humidity_calibration[0]), 2) * 100

    def readline(self):
        while self.serial.is_open:
            data = json.loads(self.serial.readline())
            self.ground_temperature = round(data.get("gnd").get("temp"), 2)
            self._ground_humidity = data.get("gnd").get("hum")
            self.air_temperature = round(data.get("air").get("temp"), 2)
            self.air_humidity = data.get("air").get("hum")

    def close(self):
        self.serial.close()


if __name__ == '__main__':
    sensors = Sensors()