import sys, random
from PyQt6.QtGui import *
from PyQt6.QtCore import Qt, QTimer, QSize, QPoint, QRect
from PyQt6.QtGui import QMouseEvent, QResizeEvent
from PyQt6.QtWidgets import *
from PyQt6.QtWidgets import QWidget
import sounddevice as sd
import numpy as np

class ResizeMixin():
    # Those that use this mixin must have a min & max height and width

    RECT_SIZE = 40
    CURSORS = {
        "ULEFT": Qt.CursorShape.SizeFDiagCursor,
        "URIGHT": Qt.CursorShape.SizeBDiagCursor,
        "BLEFT": Qt.CursorShape.SizeBDiagCursor,
        "BRIGHT": Qt.CursorShape.SizeFDiagCursor
    }

    def __init__(self):
        self.setCorners()
        self.hoverArea = None
        self.startCood = None
        self.isDragResize = False
        self.startGeom = self.geometry()
    
    def centerRect(self, x, y):
        return QRect(x - self.RECT_SIZE // 2, y - self.RECT_SIZE // 2, self.RECT_SIZE, self.RECT_SIZE)


    def setCorners(self):
        rect = self.rect()
        self.corners = {
            "ULEFT": self.centerRect(rect.topLeft().x(), rect.topLeft().y()),
            "URIGHT": self.centerRect(rect.x() + rect.width(), rect.y()),
            "BLEFT": self.centerRect(rect.x(), rect.y() + rect.height()),
            "BRIGHT": self.centerRect(rect.x() + rect.width(), rect.y() + rect.height())
        }
    
    def checkDragResize(self, e):
        position = e.position().toPoint()
        for corner, rect in self.corners.items():
            if (rect.contains(position)):
                self.setCursor(self.CURSORS[corner])
                self.hoverArea = corner
                return True
        self.unsetCursor()
        self.hoverArea = None
        return False
           
    def dragResize(self, e):
        xSign = 1
        ySign = 1
        if (self.hoverArea == "BLEFT" or self.hoverArea == "ULEFT"):
            xSign = -1
        if (self.hoverArea == "ULEFT" or self.hoverArea == "URIGHT"):
            ySign = -1
        difference = e.globalPosition().toPoint() - self.startCood
        
        newWidth = self.startGeom.width() + xSign * difference.x()
        newHeight = self.startGeom.height() + ySign * difference.y()

        newWidth = max(self.MIN_WIDTH, min(self.MAX_WIDTH, newWidth))
        newHeight = max(self.MIN_HEIGHT, min(self.MAX_HEIGHT, newHeight))

        self.setFixedSize(newWidth, newHeight)
        if (self.hoverArea == "BRIGHT"):
            self.move(self.startGeom.x(), self.startGeom.y())
            # self.setGeometry(self.startGeom.x(), self.startGeom.y(), newWidth, newHeight)
        elif (self.hoverArea == "BLEFT"):
            self.move(self.startGeom.x() + self.startGeom.width() - newWidth, self.startGeom.y())
            
            # self.setGeometry(self.startGeom.x() + self.startGeom.width() - newWidth, self.startGeom.y(), newWidth, newHeight)
        elif (self.hoverArea == "URIGHT"):
            self.move(self.startGeom.x(), self.startGeom.y() + self.startGeom.height() - newHeight)
            # self.setGeometry(self.startGeom.x(), self.startGeom.y() + self.startGeom.height() - newHeight, newWidth, newHeight)
        elif (self.hoverArea == "ULEFT"):
            self.move(self.startGeom.x() + self.startGeom.width() - newWidth, self.startGeom.y() + self.startGeom.height() - newHeight)
            # self.setGeometry(self.startGeom.x() + self.startGeom.width() - newWidth, self.startGeom.y() + self.startGeom.height() - newHeight, newWidth, newHeight)
        

    def startDragResize(self, e):
        if (self.hoverArea is None):
            return False
        self.isDragResize = True
        self.startCood = e.globalPosition().toPoint()
        self.startGeom = self.geometry()
        return True

    def stopDragResize(self, e):
        if (self.isDragResize == True):
            self.isDragResize = False
            self.hoverArea = None
            self.unsetCursor()

class Pet(QWidget, ResizeMixin):
    MIN_WIDTH = 200
    MIN_HEIGHT = 150
    MAX_WIDTH = 400
    MAX_HEIGHT = 400
    
    def __init__(self, parent):
        super().__init__(parent)
        self.name = "HelloWorld"
        self.setLayout(self.createLayout())
        self.setMouseTracking(True)

        # set the geometry for resize
        self.setFixedSize(200, 150)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        self.updateGeometry()

        self.move(120, 120)
        
    def terminate(self):
        self.deleteLater()

    def createLayout(self):
        # invisible box around everything, using a 3 x 3 grid, with the main tab in the center
        widg_central = QWidget()
        widg_central.setMouseTracking(True)
        lay_central = QGridLayout()
        lay_central.setSpacing(0)
        lay_central.setContentsMargins(0,0,0,0)
        # central main tab
        lay_main = QVBoxLayout()
        lay_main.addWidget(self.createBar())
        lay_main.setSpacing(0)
        lay_main.setContentsMargins(0,0,0,0)
        stuff = QLabel("Stuff")
        stuff.setStyleSheet("""
                    border-image: url(border/white_border_highres.png) 9 12 12 9 stretch;
                    border-width: 9 9 12 9;
                    border-top: none;
        """)
        stuff.setMouseTracking(True)
        lay_main.addWidget(stuff)
        lay_main.setStretch(0, 0)
        lay_main.setStretch(1, 1)
        
        widg_central.setLayout(lay_main)
        lay_central.addWidget(widg_central, 0, 0)
        feet = QLabel()
        feet.setPixmap(QPixmap("btn/feet.png"))
        feet2 = QLabel()
        feet2.setPixmap(QPixmap("btn/feet.png"))
        layout = QHBoxLayout()
        layout.addStretch(5)
        layout.addWidget(feet)
        layout.addStretch(7)
        layout.addWidget(feet2)
        layout.addStretch(5)
        lay_central.addLayout(layout, 1, 0)
        return lay_central

    def createBar(self):
        lay_bar = QHBoxLayout()
        lay_bar.setContentsMargins(18,0,18,0)

        self.lab_title = QLabel(self.name)
        self.lab_title.setFixedSize(100, 36)
        btn_size = 36
        btn_maximize = QPushButton()
        btn_maximize.setFixedSize(btn_size, btn_size)
        btn_maximize.clicked.connect(sys.exit)
        btn_maximize.setStyleSheet("""
            QPushButton{
                    border-image: url(btn/btn_maximize1.png);
                }

            QPushButton:hover{
                    border-image: url(btn/btn_maximize2.png);
                }
        """)

        lay_bar.addWidget(self.lab_title)
        lay_bar.addStretch()
        lay_bar.addWidget(btn_maximize)

        bar = QWidget()
        bar.setLayout(lay_bar)
        bar.setObjectName("bar")
        bar.adjustSize()
        bar.setFixedHeight(60)
        bar.setMouseTracking(True)
        bar.setStyleSheet("""
            #bar{
                    border-image: url(border/purple_border_highres.png) 9 12 12 9 stretch;
                    border-width: 9 9 12 9;
                    border-bottom: none;
                }
        """)
        return bar

    def mouseMoveEvent(self, e):
        if (self.isDragResize == False):
            if not self.checkDragResize(e):
                super().mouseMoveEvent(e)
        else:
            self.dragResize(e)

    def mousePressEvent(self, e: QMouseEvent | None) -> None:
        if (e is not None):
            if not self.startDragResize(e):
                super().mousePressEvent(e)

    def mouseReleaseEvent(self, e: QMouseEvent | None) -> None:
        if (e is not None):
            self.stopDragResize(e)
            super().mouseReleaseEvent(e)

    def resizeEvent(self, e: QResizeEvent | None) -> None:
        self.setCorners()
        super().resizeEvent(e)

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
        
        self.pet = Pet(self.canvas)
        self.pet.show()
        
    def addNewPet(self):
        pet = Pet(self.canvas)
        pet.show()

    def exitProgram(self):
        sys.exit()
app = QApplication(sys.argv)

window = MainWindow()

window.show()
screen = QApplication.primaryScreen()
screen_geometry = screen.geometry()
app.exec()

