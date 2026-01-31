import sys, random
from PyQt6.QtGui import *
from PyQt6.QtCore import Qt, QTimer, QSize, QPoint, QRect
from PyQt6.QtGui import QMouseEvent, QResizeEvent
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

class PBase(QFrame):
    def __init__(self, parent, pbase_padding, pbody_width, pbody_height, pbar_name, pbar_height, pbar_btn_size) -> None:
        super().__init__(parent)
        self.setMouseTracking(True)
        self.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        self.updateGeometry()

        layout = QGridLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0,0,0,0)

        self.body = PBody(self, pbody_width, pbody_height, pbar_name, pbar_height, pbar_btn_size)
        
        layout.addWidget(self.body, 1, 1)
        layout.setRowMinimumHeight(0, pbase_padding)
        layout.setRowMinimumHeight(2, pbase_padding)
        layout.setColumnMinimumWidth(0, pbase_padding)
        layout.setColumnMinimumWidth(2, pbase_padding)

        self.setLayout(layout)
        self.adjustSize()

        self.mouseCood = None
        # 0: transition, 1: falling
        self.state = None
        self.isDragged = False

    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            self.mouseCood = e.position().toPoint()

    def mouseMoveEvent(self, event):
        if self.mouseCood is not None:
            coordinates = self.mapToParent(event.position().toPoint() - self.mouseCood)
            self.move(coordinates.x(), coordinates.y())
            self.isDragged = True

    def mouseReleaseEvent(self, event):
        self.mouseCood = None
        if (self.isDragged):
            self.isDragged = False
            self.state = None
        
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

