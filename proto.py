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
PBODY_HEIGHT = 200
PBODY_WIDTH = 250

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

    def setSize(self, pbody_width, pbody_height):
        self.setFixedSize(pbody_width, pbody_height)

class PBase(QFrame):
    def __init__(self, parent, pbase_padding, pbody_width, pbody_height, pbar_name, pbar_height, pbar_btn_size) -> None:
        super().__init__(parent)
        self.states = {"dragging" : Dragging(self)}
        self.state = None

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
            self.state.initialize(e)

    def mouseMoveEvent(self, e):
        if (isinstance(self.state, Dragging)):
            self.state.activate(e)

    def mouseReleaseEvent(self, e):
        if (isinstance(self.state, Dragging)):
            self.state.deactivate()
        
    def terminate(self):
        self.deleteLater()

    def b_height(self):
        return self.body.height()
    
    def b_width(self):
        return self.body.width()
    
    def walk(self, x, y):
        x += self.x()
        y += self.y()

        difference = self.mapToGlobal(self.body.pos()) - self.pos()

        x = max(-difference.x(), min(x, screen_geometry.width()  - self.b_width() - difference.x()))
        y = max(-difference.y(), min(y, screen_geometry.height() - self.b_height() - difference.y()))
        self.move(x, y)

    def setPadding(self, pbase_padding):
        layout = self.layout()
        if (layout and isinstance(layout, QGridLayout)):
            layout.setRowMinimumHeight(0, pbase_padding)
            layout.setRowMinimumHeight(2, pbase_padding)
            layout.setColumnMinimumWidth(0, pbase_padding)
            layout.setColumnMinimumWidth(2, pbase_padding)

class State:
    def __init__(self, parent: PBase):
        self.parent = parent

    def initialize(self): pass
    def activate(self): pass
    def deactivate(self): pass

class Dragging(State):
    def __init__(self, parent:PBase):
        super().__init__(parent)
        self.mouseCood = None

    def initialize(self, e):
        self.mouseCood = e.position().toPoint()

    def activate(self, e):
        coordinates = self.parent.mapToParent(e.position().toPoint() - self.mouseCood)
        self.parent.walk(coordinates.x() - self.parent.x(), coordinates.y() - self.parent.y())

    def deactivate(self):
        self.mouseCood = None
        self.parent.state = None


    

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
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
        
        # self.pet = PBar(self, PBAR_NAME, PBAR_HEIGHT, PBAR_BTN_SIZE)
        self.pet = PBase(self, 20, PBODY_WIDTH, PBODY_HEIGHT, PBAR_NAME, PBAR_HEIGHT, PBAR_BTN_SIZE)
        # self.pet = PBody(self, PBODY_WIDTH, PBODY_HEIGHT, PBAR_NAME, PBAR_HEIGHT, PBAR_BTN_SIZE)
        self.pet.show()
        
    # def addNewPet(self):
    #     pet = Pet(self.canvas)
    #     pet.show()

    def exitProgram(self):
        sys.exit()
app = QApplication(sys.argv)

window = MainWindow()

window.show()
screen = QApplication.primaryScreen()
screen_geometry = screen.geometry()
with open("style.qss", "r") as qss:
    app.setStyleSheet(qss.read())
app.exec()

