from PyQt6 import QtCore, QtGui, QtWidgets

class TitleBar(QtWidgets.QFrame):
    def __init__(self, MainWindow):
        super().__init__()
        self.setAutoFillBackground(True)
        self.mouseClickPosition = None
        self.MainWidow = MainWindow

    def mousePressEvent(self, event):
        self.mouseClickPosition = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if self.mouseClickPosition is not None:
            delta = event.globalPosition().toPoint() - self.mouseClickPosition
            self.mouseClickPosition = event.globalPosition().toPoint()
            self.MainWidow.move(self.MainWidow.pos() + delta)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.mouseClickPosition = None

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        # 隐藏主窗口的边框
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        # 设置窗口为半透明
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        self.title_bar = TitleBar(self)
        self.setMenuWidget(self.title_bar)
        # Enable mouse tracking to receive mouse move events even when the mouse button is not pressed
        self.setMouseTracking(True)

        # Store the mouse press position
        self.mousePressPosition = None


