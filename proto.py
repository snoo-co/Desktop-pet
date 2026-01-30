import sys, random
from PyQt6.QtGui import *
from PyQt6.QtCore import Qt, QTimer, QSize, QPoint, QRect
from PyQt6.QtGui import QMouseEvent, QResizeEvent
from PyQt6.QtWidgets import *
from PyQt6.QtWidgets import QWidget
import sounddevice as sd
import numpy as np

class PBar(QWidget):
    def __init__(self, parent, btn_size = 36, name = "Untitled", height = 60):
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
        # self.lab_title.setFixedSize(100, 36)
        self.button = PSquareButton(self, btn_size)

        layout.addChildWidget(self.name)
        layout.addStretch()
        layout.addChildWidget(self.button)
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
        
class PContent(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.setMouseTracking(True)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        self.updateGeometry()

        self.setLayout(QVBoxLayout())

    def addContent(self, item):
        layout = self.layout()
        if (layout is not None):
            if (isinstance(item,QWidget)):
                layout.addChildWidget(item)
            elif (isinstance(item, QLayout)):
                layout.addChildLayout(item)

    
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
    
class PBody(QWidget):
    def __init__(self, parent) -> None:
        super().__init__(parent)
        self.bar = PBar(self)
        self.content = PContent(self)
        