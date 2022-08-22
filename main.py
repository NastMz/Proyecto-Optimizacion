#######################################################
# IMPORTS
#######################################################
import sys

from PyQt5.QtWidgets import QApplication

from views.SplashScreen import SplashScreen

#######################################################
# EXECUTE APP
#######################################################
if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = SplashScreen()
    window.show()
    sys.exit(app.exec_())
