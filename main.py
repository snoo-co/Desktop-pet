import sys, random
from PyQt6.QtGui import QColor, QPalette, QPixmap, QIcon, QAction
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QSystemTrayIcon, QStyle, QMenu, QLabel
import sounddevice as sd
import numpy as np

class Color(QWidget):
    WIDTH = 100
    HEIGHT = 100

    def __init__(self, parent, color):
        super().__init__(parent)

        self.mouseCood = None
        # 0: transition, 1: falling
        self.state = None
        self.isDragged = False
        self.states = [Falling(self), Walking(self), Standing(self), Climbing(self), Hanging(self), Breeding(self), Dancing(self)]

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updatePet)
        self.timer.start(70)
        
        self.setGeometry(129,120,self.WIDTH,self.HEIGHT)
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(color))
        self.setPalette(palette)

        kill = QAction("Kill", self)
        kill.triggered.connect(self.terminate)
        self.trayMenu = QMenu()
        self.trayMenu.addAction(kill)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.DefaultContextMenu)

    def LEFTBOUND(self):
        return 0

    def RIGHTBOUND(self):
        return screen_geometry.width() - self.WIDTH

    def FLOOR(self):
        return screen_geometry.height() - self.HEIGHT
    
    def CEILING(self):
        return 0
    
    # Dragging pet
    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            self.mouseCood = e.position().toPoint()

    def mouseMoveEvent(self, event):
        if self.mouseCood is not None:
            coordinates = self.mapToParent(event.position().toPoint() - self.mouseCood)
            self.walk(coordinates.x() - self.x(), coordinates.y() - self.y())
            self.isDragged = True

    def mouseReleaseEvent(self, event):
        self.mouseCood = None
        if (self.isDragged):
            self.isDragged = False
            self.state = None

    def mouseDoubleClickEvent(self, e):
        self.states[5].activate()

    def contextMenuEvent(self, e):
        self.trayMenu.exec(e.globalPos())
    

    def walk(self, x, y):
        x += self.x()
        y += self.y()
        if (x < self.LEFTBOUND()):
            x = self.LEFTBOUND()
        elif (x > self.RIGHTBOUND()):
            x = self.RIGHTBOUND()
        if (y < self.CEILING()):
            y = self.CEILING()
        elif (y > self.FLOOR()):
            y = self.FLOOR()

        self.move(x, y)

    def updatePet(self):
        if (not self.isDragged):
            if (self.state == None):
                # determine what state to transition to
                # pet is at floor:
                choices = []
                weights = []
                if (self.y() == self.FLOOR()):
                    choices += [1, 2]
                    weights += [3, 3]
                    if (sound.music):
                        choices += [6]
                        weights += [1]
                elif (self.y() == self.CEILING()):
                    choices += [4]
                    weights += [5]
                if (self.x() == self.LEFTBOUND() or self.x() == self.RIGHTBOUND()):
                    choices += [3]
                    weights += [5]
                if (self.y() < self.FLOOR() and self.y() >= self.CEILING()):
                    choices += [0]
                    weights += [2]
                
                state = random.choices(choices, weights = weights, k = 1)
                self.state = self.states[state[0]]
                self.state.initialize()
                self.state.activate()

            else:
                self.state.activate()

    def terminate(self):
        self.deleteLater()


                


# Eating -> get from store or generate -> when drag & overlay, will eat
# Maybe they have stats? Maybe they can talk & stuff
# Sleep
# Pet head
# Clothes
# Breed SEMI OK    
# Dance if music OK
# speech recognition to different commands
# 

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cute Pet")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.showFullScreen()
        
        self.setMouseTracking(True)
        self.canvas = QWidget(self)
        self.setCentralWidget(self.canvas)
        self.trayIcon = QSystemTrayIcon(self)
        self.trayIcon.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_TrashIcon))
        massacre = QAction("Massacre", self)
        massacre.triggered.connect(self.exitProgram)
        trayMenu = QMenu()
        trayMenu.addAction(massacre)

        self.trayIcon.setContextMenu(trayMenu)
        self.trayIcon.show()
        
        self.pet = Color(self.canvas, "red")
        
    def addNewPet(self):
        pet = Color(self.canvas, "blue")
        pet.show()

    def mousePressEvent(self, e):
        pass

    def mouseMoveEvent(self, e):
        pass
    
    def exitProgram(self):
        sys.exit()


class SoundEngine:
    ONTHRESHOLD = 0.01
    OFFTHRESHOLD = 0.00
    def __init__(self):
        self.music = False
        samplerate = 44100

        def callback(indata, frames, time, status):
            if(np.max(np.abs(indata)) > self.ONTHRESHOLD):
                self.music = True
            elif(np.max(np.abs(indata)) < self.ONTHRESHOLD):
                self.music = False
        
        stream = sd.InputStream(samplerate = samplerate, blocksize = 200, channels = 1, dtype = 'float32', callback = callback)
        stream.start()

class State:
        def __init__(self, Color):
            self.parent = Color

        def initialize(self): pass
        def activate(self): pass
    
class Falling(State):
    def __init__(self, Color):
        super().__init__(Color)
        self.yv = 0

    def initialize(self):
        self.yv = 0

    def activate(self):
        self.yv += 10
        if (self.parent.y() + self.yv < self.parent.FLOOR()):
            self.parent.walk(0, self.yv)
        else:
            self.parent.walk(0, self.parent.FLOOR() - self.parent.y())
            self.parent.state = None

class Walking(State):
    def __init__(self, Color):
        super().__init__(Color)
        self.direction = 1
        self.steps = 0

    def initialize(self):
        self.direction = random.choice([-1,1])
        self.steps = (random.randrange(30, 40))   

    def activate(self):
        if (self.steps == 0):
            self.parent.state = None
        else:
            self.steps -= 1
            self.parent.walk(self.direction * 5, 0)

class Standing(State):
    def __init__(self, Color):
        super().__init__(Color)
        self.steps = 0

    def initialize(self):
        self.steps = (random.randrange(20, 30))   

    def activate(self):
        if (self.steps == 0):
            self.parent.state = None
        else:
            self.steps -= 1

class Climbing(State):
    def __init__(self, Color):
        super().__init__(Color)
        self.direction = 1
        self.steps = 0

    def initialize(self):
        self.direction = random.choice([-1,1])
        self.steps = (random.randrange(30, 45))   

    def activate(self):
        if (self.steps == 0):
            self.parent.state = None
        else:
            self.steps -= 1
            self.parent.walk(0, self.direction * 5)

class Hanging(Walking):
    def __init__(self, Color):
        super().__init__(Color)
    # Change when have sprites

class Breeding(State):
    def activate(self):
        window.addNewPet()

class Dancing(State):
    def initialize(self):
        self.steps = (random.randrange(30, 45))   

    def activate(self):
        if (self.steps == 0):
            palette = self.parent.palette()
            palette.setColor(QPalette.ColorRole.Window, QColor("red"))
            self.parent.setPalette(palette)
            self.parent.state = None
        else:
            self.steps -= 1
            palette = self.parent.palette()
            choices = ["blue", "purple", "orange", "green"]
            color = random.choice(choices)
            palette.setColor(QPalette.ColorRole.Window, QColor(color))
            self.parent.setPalette(palette)

app = QApplication(sys.argv)

window = MainWindow()

window.show()
screen = QApplication.primaryScreen()
screen_geometry = screen.geometry()

sound = SoundEngine()
app.exec()

