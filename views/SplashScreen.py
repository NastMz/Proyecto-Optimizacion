# ==> SPLASHSCREEN WINDOW
from PyQt5 import QtCore
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QGraphicsDropShadowEffect, QMainWindow

from views.MainWindow import MainWindow
from views.ui_splash_screen import Ui_SplashScreen

# GLOBALS
counter = 0
jumper = 1


class SplashScreen(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.main = None
        self.ui = Ui_SplashScreen()
        self.ui.setupUi(self)

        # ==> SET INITIAL PROGRESS BAR TO (0) ZERO
        self.progress_bar_value(0)

        # ==> REMOVE STANDARD TITLE BAR
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)  # Remove title bar
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)  # Set background to transparent

        # ==> APPLY DROP SHADOW EFFECT
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(20)
        self.shadow.setXOffset(0)
        self.shadow.setYOffset(0)
        self.shadow.setColor(QColor(0, 0, 0, 120))
        self.ui.circularBg.setGraphicsEffect(self.shadow)

        # QTIMER ==> START
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.progress)
        # TIMER IN MILLISECONDS
        self.timer.start(10)

        # SHOW ==> MAIN WINDOW
        ########################################################################
        self.show()
        # ==> END ##

    # DEF TO LOANDING
    ########################################################################
    def progress(self):
        global counter
        global jumper
        value = counter

        # HTML TEXT PERCENTAGE
        html_text = """<p><span style=" font-size:68pt;">{VALUE}</span><span style=" font-size:58pt; vertical-align:super;">%</span></p>"""

        # REPLACE VALUE
        new_html = html_text.replace("{VALUE}", str(jumper))

        if value > jumper:
            # APPLY NEW PERCENTAGE TEXT
            self.ui.labelPercentage.setText(new_html)
            jumper += 1

        # SET VALUE TO PROGRESS BAR
        # fix max value error if > than 100

        self.progress_bar_value(value)

        # CLOSE SPLASH SCREE AND OPEN APP
        if counter > 100:
            # STOP TIMER
            self.timer.stop()

            # SHOW MAIN WINDOW
            self.main = MainWindow()
            self.main.show()

            # CLOSE SPLASH SCREEN
            self.close()

        # INCREASE COUNTER
        counter += 0.5

    # DEF PROGRESS BAR VALUE
    ########################################################################
    def progress_bar_value(self, value):

        # PROGRESSBAR STYLESHEET BASE
        style_sheet = """
        QFrame{
        	border-radius: 150px;
        	background-color: qconicalgradient(cx:0.5, cy:0.5, angle:90, stop:{STOP_1} #343b47, stop:{STOP_2} #838ea2);
        }
        """

        # GET PROGRESS BAR VALUE, CONVERT TO FLOAT AND INVERT VALUES
        # stop works of 1.000 to 0.000
        progress = (100 - value) / 100.0

        # GET NEW VALUES
        stop_1 = str(progress - 0.001)
        stop_2 = str(progress)

        # SET VALUES TO NEW STYLESHEET
        new_stylesheet = style_sheet.replace("{STOP_1}", stop_1).replace("{STOP_2}", stop_2)

        # APPLY STYLESHEET WITH NEW VALUES
        self.ui.circularProgress.setStyleSheet(new_stylesheet)
