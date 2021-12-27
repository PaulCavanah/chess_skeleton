from PyQt5 import QtCore, QtWidgets

class ClickableLabel(QtWidgets.QLabel) :
    #clicked = QtCore.pyqtSignal()
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent #GUI
        self.FEN_index = None

    """def mouseReleaseEvent(self, QMouseEvent):
        if QMouseEvent.button() == Qt.LeftButton :
            self.clicked.emit()
            #The transition between these lines of code is at least 0.7s and prevents single presses from triggering connection
            #self.clicked.connect() #lambda or an explicit function"""

    def color(self, color, init = False) :
        if init == True :
            self.natural_color = color
            self.setStyleSheet((f"background-image: url('images/{color}_square.png');"))
        else :
            if color == "white" :
                self.setStyleSheet("background-image: url('images/white_square.png');")
            elif color == "black" :
                self.setStyleSheet("background-image: url('images/black_square.png');")
            elif color == "green" :
                self.setStyleSheet("background-image: url('images/green.png');")
            elif color == "red" :
                self.setStyleSheet("background-image: url('images/red.png');")