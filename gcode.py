from enum import Enum
from time import sleep

import mecode
import numpy as np
import serial
from mecode.printer import Printer
from skimage.io import imread


class Status(Enum):
    IDLE = "Ожидание запуска"
    PREPARING = "Подготовка к запуску"
    MOVING = "Перемещение на позицию"
    WATERING = "Полив цветка"
    PLANTING = "Посадка цветка"
    DOCKING = "Возвращение на базу"


class GCode:
    def __init__(self):
        self.printer = Printer()
        self._progress = 0
        self.pixels = ([], [])
        self.connected = False
        self._history = [(0, 0, 0)]
        self.status = Status.IDLE
        self._image = None
        self.g = mecode.G(setup=False, direct_write=True, direct_write_mode='serial')

    @property
    def image(self):
        return self._image if self.status is not Status.IDLE else None

    @image.setter
    def image(self, value):
        self._image = value

    def connect(self, com):
        self.status = Status.PREPARING
        ser = serial.Serial(com, baudrate=250000)
        self.printer.connect(ser)
        self.printer.start()
        sleep(1)
        self.g._p = self.printer
        self.write("M400", wait=True)
        sleep(1)
        self.connected = True
        # self.write("M92 X407.3 Y407.3")
        self.write("M300 S5000 P280")
        self.write("M117 Flowers!!!")
        self.write("M75")

    # def plot(self):
    #     fig = plt.figure()
    #     ax = fig.gca(projection='3d')
    #     history = np.array(self._history)
    #     x, y, z = history[:, 0], history[:, 1], history[:, 2]
    #
    #     ax.plot(x, y, z)
    #     plt.show()

    def kill(self):
        self.printer.s.write(b"M112\r\n")
        self.status = Status.IDLE
        self.disconnect()

    def done(self):
        self.write("M77")
        self.status = Status.IDLE

    def disconnect(self):
        self.printer.disconnect()
        self.connected = False
        self.status = Status.IDLE

    def plant(self):
        prev_status = self.status
        self.status = Status.PLANTING
        self.move(z=-10, relative=True)
        self.g.dwell(1000)
        self.move(z=10, relative=True)
        self.start_pump()
        self.g.dwell(1000)
        self.stop_pump()
        self.status = prev_status

    def start_pump(self, power=255):
        self.write("M106 S" + str(power))

    def stop_pump(self):
        self.write("M107")

    @property
    def progress(self):
        return self._progress

    @progress.setter
    def progress(self, value):
        self._progress = value
        self.write("M73 P" + str(self._progress))

    def feedrate(self, feedrate=4000):
        self.move(feedrate=feedrate)

    def parse_image(self, file, com=None):
        if not self.connected:
            self.connect(com)
        image = imread(file)
        colors = np.unique(image.reshape(-1, image.shape[2]), axis=0)
        print_size = (1000, 950)  # in mm

        width = image.shape[0]
        height = image.shape[1]
        padding_x = print_size[0] / (width+1)
        padding_y = print_size[1] / (height+1)

        total_pixels = width * height
        self.pixels = ([], [])
        i = 0
        for color in colors:
            print("using "+str(color))
            if color[3] < 255:
                print("got transparent color, ignoring")
                continue
            self.status = Status.MOVING
            self.move(x=0, y=0, feedrate=4000)
            coords = np.dstack(np.where(np.all(image == color, axis=2)))
            for x, y in coords[0]:
                self.pixels[0].append(int(x))
                self.pixels[1].append(int(y))
                self.progress = round(i / total_pixels * 100)
                real_x = (x + 1) * padding_x
                real_y = (y + 1) * padding_y
                self.move(real_x, real_y, relative=False)
                self.dwell(1)
                i += 1
        self.progress = 100
        self.move(0, 0)
        self.done()

    def write(self, command, wait=True):
        return self.g.write(command, resp_needed=wait)

    def wait(self):
        return self.write("M400", wait=True)

    def dwell(self, seconds):
        return self.write("G4 S"+str(seconds))

    def move(self, x=None, y=None, z=None, relative=False, feedrate=None):
        if relative:
            self.write("G91")
        else:
            self.write("G90")

        prev = self._history[len(self._history)-1]
        coords = (x if x is not None else prev[0],
                  y if y is not None else prev[1],
                  z if z is not None else prev[2])
        self._history.append(coords)
        self.write("G0" + (" X" + str(round(x, 2)) if x is not None else "")
                   + (" Y" + str(round(y, 2)) if y is not None else "")
                   + (" Z" + str(round(z, 2)) if z is not None else "")
                   + (" F" + str(min(4000, feedrate)) if feedrate is not None else ""))


if __name__ == '__main__':
    gc = GCode()
    gc.connect("/dev/ttyUSB0")
    gc.move(y=-100)
    gc.wait()
    # for i in range(100):
    #     gc.move(round(1000*random.random(), 2), round(950*random.random(), 2), feedrate=4000)
    #     gc.move(0, 0, feedrate=4000)
    #     gc.write("M400")

    # gc.write("G0 F4000")
    # gc.write("G2 I20 J20")
    # gc.move(x=0, y=40, relative=True)
    # gc.write("G2 I20 J20")
    # gc.write("G2 R80 Y0 X100")
    # gc.move(x=-10, y=0, relative=True)
    # gc.move(x=0, y=10, relative=True)
    # gc.move(x=0, y=-20, relative=True)
    # gc.move(x=0, y=10, relative=True)
    # gc.move(x=10, y=0, relative=True)
    # gc.write("G2 R80 Y0 X-100")
    # gc.move(x=0, y=-40, relative=True)
    # gc.parse_image("./temp_images/converted_unnamed.jpg.png")
    # gc.wait()
    # gc.plot()

