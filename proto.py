import sys, random
from PyQt6.QtGui import *
from PyQt6.QtCore import Qt, QTimer, QSize, QPoint, QRect
from PyQt6.QtGui import QContextMenuEvent, QMouseEvent, QResizeEvent
from PyQt6.QtWidgets import *
from PyQt6.QtWidgets import QWidget
import sounddevice as sd
import numpy as np

PBAR_BTN_SIZE = 36
PBAR_HEIGHT = 60
PBAR_NAME = "Hello World"
PBODY_HEIGHT = 100
PBODY_WIDTH = 120

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


class PBar(QFrame):
    def __init__(self, parent, name, height, btn_size):
        super().__init__(parent)
        self.setMouseTracking(True)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        self.setFixedHeight(height)
        self.updateGeometry()
        layout = QHBoxLayout()

        # !!! Change this
        layout.setContentsMargins(18,0,18,0)

        # content
        self.name = QLabel(name, self)
        self.name.setMouseTracking(True)
        self.name.setFixedHeight(btn_size)
        self.button = PSquareButton(self, btn_size)

        layout.addWidget(self.name)
        layout.addWidget(self.button)
        self.setLayout(layout)

    def setName(self, name):
        self.name.setText(name)

    def setHeight(self, height):
        self.setFixedHeight(height)

    def setButtonSize(self, btn_size):
        self.button.setSize(btn_size)

class PSquareButton(QPushButton):
    def __init__(self, parent, btn_size):
        super().__init__(parent)
        self.setMouseTracking(True)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.setFixedSize(btn_size, btn_size)
        self.updateGeometry()
    
    def setSize(self, btn_size):
        self.setFixedSize(btn_size, btn_size)
        
class PContent(QFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.setMouseTracking(True)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        self.updateGeometry()

        self.setLayout(QVBoxLayout())

    def addContent(self, item):
        layout = self.layout()
        if (layout is not None):
            layout.addWidget(item)
    
    def contentAt(self, index):
        layout = self.layout()
        if (layout is not None):
            return layout.takeAt(index)
        
    def removeContent(self, id = -1):
        layout = self.layout()
        if (layout is not None):
            if (id == -1):
                id = layout.count() - 1
            itemToRemove = self.contentAt(id)
            if (itemToRemove is not None): 
                layout.removeItem(itemToRemove)
    
class PBody(QFrame):
    def __init__(self, parent, pbody_width, pbody_height, pbar_name, pbar_height, pbar_btn_size) -> None:
        super().__init__(parent)
        self.setMouseTracking(True)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.setFixedSize(pbody_width, pbody_height)
        self.updateGeometry()

        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0,0,0,0)

        self.bar = PBar(self, pbar_name, pbar_height, pbar_btn_size)
        self.content = PContent(self)

        layout.addWidget(self.bar)
        layout.addWidget(self.content)
        self.setLayout(layout)

        self.setContextMenuPolicy(Qt.ContextMenuPolicy.DefaultContextMenu)
        kill = QAction("Kill", self)
        kill.triggered.connect(self.terminate)
        self.trayMenu = QMenu()
        self.trayMenu.addAction(kill)

    def contextMenuEvent(self, e: QContextMenuEvent | None) -> None:
        if (e):
            self.trayMenu.exec(e.globalPos())

    def terminate(self):
        self.deleteLater()

class PBase(QFrame):
    def __init__(self, parent, pbase_padding, pbody_width, pbody_height, pbar_name, pbar_height, pbar_btn_size) -> None:
        super().__init__(parent)
        self.states = {"dragging" : Dragging(self)}
        self.state = None
        self.hoverArea = None

        self.setMouseTracking(True)
        self.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        self.updateGeometry()

        layout = QGridLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0,0,0,0)

        self.body = PBody(self, pbody_width, pbody_height, pbar_name, pbar_height, pbar_btn_size)
        self.body.trayMenu.clear()
        kill = QAction("Kill", self)
        kill.triggered.connect(sys.exit)
        self.body.trayMenu.addAction(kill)
        
        layout.addWidget(self.body, 1, 1)
        layout.setRowMinimumHeight(0, pbase_padding)
        layout.setRowMinimumHeight(2, pbase_padding)
        layout.setColumnMinimumWidth(0, pbase_padding)
        layout.setColumnMinimumWidth(2, pbase_padding)

        self.setLayout(layout)
        self.adjustSize()
        print(self.body.pos(), self.pos())
        print(self.b_width(), self.b_height())

    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton and self.body.underMouse():
            self.state =  self.states["dragging"]
            self.state.startDrag(e)

    def mouseMoveEvent(self, e):
        if (isinstance(self.state, Dragging)):
            self.state.continueDrag(e)

    def mouseReleaseEvent(self, e):
        if (isinstance(self.state, Dragging)):
            self.state.deactivate()
        
    def terminate(self):
        self.deleteLater()

    def b_height(self):
        return self.body.height()
    
    def b_width(self):
        return self.body.width()
    
    def difference(self):
        return self.mapToGlobal(self.body.pos()) - self.pos()
    
    def LEFTBOUND(self):
        return -self.difference().x()

    def RIGHTBOUND(self):
        if (screen_geometry != None):
            return screen_geometry.width()  - self.b_width()  - self.difference().x()
        return 0

    def FLOOR(self):
        if (screen_geometry != None):
            return screen_geometry.height()  - self.b_height() - self.difference().y()
        return 0
    
    def CEILING(self):
        return -self.difference().x()
    
    def globalBodyGeom(self):
        bodyCood = self.body.pos()
        globalLeft = self.mapToParent(bodyCood) 
        return QRect(globalLeft, self.body.size())
    
    def activateState(self, state):
        self.state = self.states[state]
        self.state.initialize()
    
    def walk(self, x, y):
        x += self.x()
        y += self.y()

        difference = self.mapToGlobal(self.body.pos()) - self.pos()

        x = max(self.LEFTBOUND(), min(x, self.RIGHTBOUND()))
        y = max(self.CEILING(), min(y, self.FLOOR()))
        self.move(x, y)

    def setPadding(self, pbase_padding):
        layout = self.layout()
        if (layout and isinstance(layout, QGridLayout)):
            layout.setRowMinimumHeight(0, pbase_padding)
            layout.setRowMinimumHeight(2, pbase_padding)
            layout.setColumnMinimumWidth(0, pbase_padding)
            layout.setColumnMinimumWidth(2, pbase_padding)

class PMinimized(PBase):
    def __init__(self, parent, pbase_padding, pbody_width, pbody_height, pbar_name, pbar_height, pbar_btn_size): 
        super().__init__(parent, pbase_padding, pbody_width, pbody_height, pbar_name, pbar_height, pbar_btn_size)
        minimizedStates = {"falling" : Falling(self), "walking" : Walking(self), "standing" : Standing(self), "climbing" : Climbing(self), "hanging" : Hanging(self)}
        self.states.update(minimizedStates)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updatePet)
        self.timer.start(70)
    
    def updatePet(self):
        if (self.state == None):
            # determine what state to transition to
            # pet is at floor:
            choices = []
            weights = []
            if (self.y() == self.FLOOR()):
                choices += ["walking", "standing"]
                weights += [3, 3]
                # if (sound.music):
                #     choices += []
                #     weights += [1]
            elif (self.y() == self.CEILING()):
                choices += ["hanging"]
                weights += [5]
            if (self.x() == self.LEFTBOUND() or self.x() == self.RIGHTBOUND()):
                choices += ["climbing"]
                weights += [5]
            if (self.y() < self.FLOOR() and self.y() >= self.CEILING()):
                choices += ["falling"]
                weights += [2]
            
            state = random.choices(choices, weights = weights, k = 1)
            self.state = self.states[state[0]]
            self.state.initialize()
            self.state.activate()

        else:
            self.state.activate()

    def mousePressEvent(self, e):
        if (self.body.underMouse()):
            self.activateState("standing")
        super().mousePressEvent(e)
    
class PMaximized(PBase):
    MIN_WIDTH = 200
    MIN_HEIGHT = 150
    MAX_WIDTH = 400
    MAX_HEIGHT = 400

    CURSORS = {
        "ULEFT": Qt.CursorShape.SizeFDiagCursor,
        "URIGHT": Qt.CursorShape.SizeBDiagCursor,
        "BLEFT": Qt.CursorShape.SizeBDiagCursor,
        "BRIGHT": Qt.CursorShape.SizeFDiagCursor
    }

    RECT_SIZE = 15

    def __init__(self, parent, pbase_padding, pbody_min_width, pbody_min_height, pbody_max_width, pbody_max_height, pbar_name, pbar_height, pbar_btn_size): 
        super().__init__(parent, pbase_padding, pbody_min_width, pbody_min_height, pbar_name, pbar_height, pbar_btn_size)
        maximizedStates = {"resizing" : Resizing(self, pbody_min_width, pbody_min_height, pbody_max_width, pbody_max_height)}
        self.states.update(maximizedStates)

    def showEvent(self, event):
        self.setCorners()
    
    def centerRect(self, x, y):
        return QRect(x - self.RECT_SIZE // 2, y - self.RECT_SIZE // 2, self.RECT_SIZE, self.RECT_SIZE)

    def setCorners(self):
        rect = self.globalBodyGeom()
        self.corners = {
            "ULEFT": self.centerRect(rect.topLeft().x(), rect.topLeft().y()),
            "URIGHT": self.centerRect(rect.x() + rect.width(), rect.y()),
            "BLEFT": self.centerRect(rect.x(), rect.y() + rect.height()),
            "BRIGHT": self.centerRect(rect.x() + rect.width(), rect.y() + rect.height())
        }

    def walk(self, x, y):
        super().walk(x, y)
        self.setCorners()

    def checkDragResize(self, e):
        position = e.globalPosition().toPoint()
        for corner, rect in self.corners.items():
            if (rect.contains(position)):
                self.setCursor(self.CURSORS[corner])
                self.hoverArea = corner
                return True
        self.unsetCursor()
        self.hoverArea = None
        return False
    
    def mousePressEvent(self, e):
        if (e is not None):
            if not self.startDragResize(e):
                super().mousePressEvent(e)

    def startDragResize(self, e):
        if (self.hoverArea is None):
            return False
        self.state = self.states["resizing"]
        self.state.startResize(e, self.hoverArea)
        return True
    
    def mouseReleaseEvent(self, e: QMouseEvent | None) -> None:
        if (e is not None):
            if (isinstance(self.state, Resizing)):
                self.state.deactivate()
            super().mouseReleaseEvent(e)

    def resizeEvent(self, e: QResizeEvent | None) -> None:
        self.setCorners()
        super().resizeEvent(e)

    def mouseMoveEvent(self, e):
        if (isinstance(self.state, Resizing)):
                self.state.continueResize(e)
        else:
            self.checkDragResize(e)
            super().mouseMoveEvent(e)

    def mouseDoubleClickEvent(self, a0: QMouseEvent | None) -> None:
       pass

class State:
    def __init__(self, parent: PBase):
        self.parent = parent

    def initialize(self): pass
    def activate(self): pass
    def deactivate(self): pass

class Resizing(State):
    def __init__(self, parent:PBase, pbody_min_width, pbody_min_height, pbody_max_width, pbody_max_height):
        super().__init__(parent)
        self.hoverArea = None
        self.startCood = None
        self.startGeom = None
        self.startBodyGeom = None
        self.MIN_WIDTH = pbody_min_width
        self.MIN_HEIGHT = pbody_min_height
        self.MAX_WIDTH = pbody_max_width
        self.MAX_HEIGHT = pbody_max_height

    def startResize(self, e, hoverArea):
        self.startCood = e.globalPosition().toPoint()
        self.startBodyGeom = self.parent.globalBodyGeom()
        self.startGeom = self.parent.geometry()
        self.hoverArea = hoverArea

    def continueResize(self, e):
        xSign = 1
        ySign = 1
        if (self.hoverArea == "BLEFT" or self.hoverArea == "ULEFT"):
            xSign = -1
        if (self.hoverArea == "ULEFT" or self.hoverArea == "URIGHT"):
            ySign = -1
        difference = e.globalPosition().toPoint() - self.startCood
        
        # new width is old width + difference moved by mouse, capped by max & min
        newWidth = self.startBodyGeom.width() + xSign * difference.x()
        newHeight = self.startBodyGeom.height() + ySign * difference.y()

        newWidth = max(self.MIN_WIDTH, min(self.MAX_WIDTH, newWidth))
        newHeight = max(self.MIN_HEIGHT, min(self.MAX_HEIGHT, newHeight))

        self.parent.body.setFixedSize(newWidth, newHeight)
        self.parent.adjustSize()
        if (self.hoverArea == "BRIGHT"):
            self.parent.move(self.startGeom.x(), self.startGeom.y())
        elif (self.hoverArea == "BLEFT"):
            self.parent.move(self.startGeom.x() + self.startBodyGeom.width() - newWidth, self.startGeom.y())
        elif (self.hoverArea == "URIGHT"):
            self.parent.move(self.startGeom.x(), self.startGeom.y() + self.startBodyGeom.height() - newHeight)
        elif (self.hoverArea == "ULEFT"):
            self.parent.move(self.startGeom.x() + self.startBodyGeom.width() - newWidth, self.startGeom.y() + self.startBodyGeom.height() - newHeight)

    def deactivate(self):
        self.hoverArea = None
        self.parent.unsetCursor()
        self.parent.state = None
        self.startCood = None
        self.startBodyGeom = None
        self.startGeom = None
 

class Dragging(State):
    def __init__(self, parent:PBase):
        super().__init__(parent)
        self.mouseCood = None

    def startDrag(self, e):
        self.mouseCood = e.position().toPoint()

    def continueDrag(self, e):
        coordinates = self.parent.mapToParent(e.position().toPoint() - self.mouseCood)
        self.parent.walk(coordinates.x() - self.parent.x(), coordinates.y() - self.parent.y())

    def deactivate(self):
        self.mouseCood = None
        self.parent.state = None

class Falling(State):
    def __init__(self, Pet):
        super().__init__(Pet)
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
    def __init__(self, Pet):
        super().__init__(Pet)
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
    def __init__(self, Pet):
        super().__init__(Pet)
        self.steps = 0

    def initialize(self):
        self.steps = (random.randrange(20, 30))   

    def activate(self):
        if (self.steps == 0):
            self.parent.state = None
        else:
            self.steps -= 1

class Climbing(State):
    def __init__(self, Pet):
        super().__init__(Pet)
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
    def __init__(self, Pet):
        super().__init__(Pet)
    # Change when have sprites

class Pet:
    def __init__(self, parent, pbase_padding, pbody_min_width, pbody_min_height, pbody_max_width, pbody_max_height, pbar_name, pbar_height, pbar_btn_size): 
        self.minimized = PMinimized(parent, pbase_padding, pbody_min_width, pbody_min_height, pbar_name, pbar_height, pbar_btn_size)
        self.minimized.body.bar.button.clicked.connect(self.maximize)
        self.minimized.hideEvent = self.minHide
        self.minimized.showEvent = self.minShow

        self.maximized = PMaximized(parent, pbase_padding, pbody_min_width, pbody_min_height, pbody_max_width, pbody_max_height, pbar_name, pbar_height, pbar_btn_size)
        self.maximized.body.bar.button.clicked.connect(self.minimize)
        self.maximized.showEvent = self.maxShow
        self.minimized.show()


    def maximize(self):
        self.minimized.hide()
        self.maximized.show()

    def minHide(self, a0):
        self.minimized.timer.stop()

    def minShow(self, a0):
        self.minimized.move(self.maximized.pos())
        self.minimized.timer.start()
        self.minimized.activateState("falling")

    def maxShow(self, event):
        self.maximized.move(self.minimized.pos())
        self.maximized.walk(0,0)

    def petPosition(self):
        if self.minimized.isHidden():
            return self.maximized.pos()
        else:
            return self.minimized.pos()


    def minimize(self):
        self.minimized.show()
        self.maximized.hide()


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setMouseTracking(True)
        self.setWindowTitle("Cute Pet")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.showFullScreen()
        
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
        
        # self.pet = PMaximized(self, 20, PBODY_WIDTH, PBODY_HEIGHT, 400, 400, PBAR_NAME, PBAR_HEIGHT, PBAR_BTN_SIZE)
        # self.pet1 = PMinimized(self, 20, PBODY_WIDTH, PBODY_HEIGHT, PBAR_NAME, PBAR_HEIGHT, PBAR_BTN_SIZE)
        # self.pet1.show()
        self.pet = Pet(self, 20, PBODY_WIDTH, PBODY_HEIGHT, 400, 400, PBAR_NAME, PBAR_HEIGHT, PBAR_BTN_SIZE)
        # self.pet.show()
        
    # def addNewPet(self):
    #     pet = Pet(self.canvas)
    #     pet.show()

    def exitProgram(self):
        sys.exit()

screen_geometry = None
app = QApplication(sys.argv)

window = MainWindow()

window.show()
screen = QApplication.primaryScreen()
screen_geometry = screen.geometry()
with open("style.qss", "r") as qss:
    app.setStyleSheet(qss.read())

# sound = SoundEngine()
app.exec()

