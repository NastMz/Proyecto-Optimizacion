from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, QPropertyAnimation
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QMainWindow, QGraphicsDropShadowEffect

#######################################################
# IMPORT GUI FILE
#######################################################
from GUI.ui_interface import Ui_MainWindow


#######################################################
# MAIN WINDOW CLASS
#######################################################
class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.animation = None
        self.clickPosition = None
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.dragPos = None

        self.ui.minimizeBtn.clicked.connect(lambda: self.showMinimized())
        self.ui.closeBtn.clicked.connect(lambda: self.close())

        # REMOVE TITLE BAR
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setWindowOpacity(1)

        # SIZE GRIP
        self.gripSize = 10
        self.grip = QtWidgets.QSizeGrip(self)
        self.grip.resize(self.gripSize, self.gripSize)

        # DROP SHADOW EFFECT
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(20)
        self.shadow.setXOffset(0)

        self.shadow.setYOffset(0)
        self.shadow.setColor(QColor(0, 0, 0, 60))
        self.ui.dropShadowFrame.setGraphicsEffect(self.shadow)

        # MOVE WINDOW
        self.ui.headerContainer.mouseMoveEvent = self.move_window

        # TITLE BAR
        self.ui.minimizeBtn.clicked.connect(self.minimize_window)
        self.ui.restoreBtn.clicked.connect(self.restore_window)
        self.ui.maximizeBtn.clicked.connect(self.maximize_window)
        self.ui.closeBtn.clicked.connect(lambda: self.close())

        self.ui.restoreBtn.hide()

        # SIDEBAR
        self.ui.menuBtn.clicked.connect(self.toggle_menu)

        self.ui.settingsBtn.clicked.connect(lambda: self.toggle_submenu(0, 0))
        self.ui.infoBtn.clicked.connect(lambda: self.toggle_submenu(1, 1))
        self.ui.helpBtn.clicked.connect(lambda: self.toggle_submenu(2, 2))
        self.ui.closeSubMenuBtn.clicked.connect(lambda: self.toggle_submenu())

        self.ui.userBtn.clicked.connect(lambda: self.toggle_right_menu(0, 0))
        self.ui.moreBtn.clicked.connect(lambda: self.toggle_right_menu(1, 1))
        self.ui.closeRightMenuBtn.clicked.connect(lambda: self.toggle_right_menu())

        # SHOW WINDOW
        self.show()

    def minimize_window(self):
        self.showMinimized()

    def restore_window(self):
        self.showNormal()
        self.ui.restoreBtn.hide()
        self.ui.maximizeBtn.show()

    def maximize_window(self):
        self.showMaximized()
        self.ui.maximizeBtn.hide()
        self.ui.restoreBtn.show()

    def toggle_menu(self, index):
        width = self.ui.leftMenuContainer.width()
        self.animation = QPropertyAnimation(self.ui.leftMenuContainer, b'maximumWidth')
        default = 50
        if width == default:
            extend = 120
        else:
            extend = default
        self.animation.setDuration(300)
        self.animation.setStartValue(width)
        self.animation.setEndValue(extend)
        self.animation.setEasingCurve(QtCore.QEasingCurve.InOutQuart)
        self.animation.start()
        
    def toggle_submenu(self, btn=None, index=None):
        width = self.ui.centerMenuContainer.width()
        self.animation = QPropertyAnimation(self.ui.centerMenuContainer, b'maximumWidth')
        default = 0
        if width == default or width == 200 and self.ui.stackedWidget.currentIndex() != btn and btn is not None:
            extend = 200
        else:
            extend = default
        self.animation.setDuration(300)
        self.animation.setStartValue(width)
        self.animation.setEndValue(extend)
        self.animation.setEasingCurve(QtCore.QEasingCurve.InOutQuart)
        self.animation.start()
        if index is not None:
            self.ui.stackedWidget.setCurrentIndex(index)

    def toggle_right_menu(self, btn=None, index=None):
        width = self.ui.rightMenuContainer.width()
        self.animation = QPropertyAnimation(self.ui.rightMenuContainer, b'maximumWidth')
        default = 0
        if width == default or width == 200 and self.ui.stackedWidget_2.currentIndex() != btn and btn is not None:
            extend = 200
        else:
            extend = default
        self.animation.setDuration(300)
        self.animation.setStartValue(width)
        self.animation.setEndValue(extend)
        self.animation.setEasingCurve(QtCore.QEasingCurve.InOutQuart)
        self.animation.start()
        if index is not None:
            self.ui.stackedWidget_2.setCurrentIndex(index)

    #######################################################
    # SIZE GRIP
    #######################################################
    def resizeEvent(self, event):
        rect = self.rect()
        self.grip.move(rect.right() - self.gripSize, rect.bottom() - self.gripSize)

    #######################################################
    # MOVE WINDOW
    #######################################################
    def mousePressEvent(self, event):
        self.clickPosition = event.globalPos()

    def move_window(self, event):
        if not self.isMaximized() and event.buttons() == Qt.LeftButton:
            self.move(self.pos() + event.globalPos() - self.clickPosition)
            self.clickPosition = event.globalPos()
            event.accept()

        if event.globalPos().y() <= 20:
            self.showMaximized()
        else:
            self.showNormal()
