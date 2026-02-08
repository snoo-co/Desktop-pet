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
        
        
    # def addNewPet(self):
    #     pet = Pet(self.canvas)
    #     pet.show()

    def exitProgram(self):
        sys.exit()

    def mouseMoveEvent(self, e):
        print(e.pos())

app = QApplication(sys.argv)

window = MainWindow()

window.show()
screen = QApplication.primaryScreen()
screen_geometry = screen.geometry()
with open("style.qss", "r") as qss:
    app.setStyleSheet(qss.read())

app.exec()

