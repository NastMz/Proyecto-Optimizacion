import copy

import pandas as pd
from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, QPropertyAnimation
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QMainWindow, QGraphicsDropShadowEffect, QTableWidgetItem, QHeaderView

from Core.Analysis import Analysis
from Core.Board import Board
from Core.Simplex import Simplex
from utils.BarPlot import BarPlot
from utils.LinePlot import LinePlot
#######################################################
# IMPORT views FILE
#######################################################
from views.ui_interface import Ui_MainWindow


#######################################################
# MAIN WINDOW CLASS
#######################################################
def clean_boards(boards):
    for board in boards:
        for row in range(len(board)):
            row_content = copy.deepcopy(board[row])
            index = None
            for item in row_content:
                if type(item) == list:
                    index = row_content.index(item)
                    break
            if index is not None:
                line = row_content[index]
                after = row_content[index + 1:]
                row_content = row_content[:index]
                row_content += line
                row_content += after
            board[row] = row_content


class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.animation = None
        self.clickPosition = None
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.dragPos = None

        self.board = Board(
            variables=['X1', 'X2', 'X3', 'X4', 'S1', 'S2', 'S3', 'S4', 'S5', 'S6', 'S7', 'S8', 'S9', 'S10', 'S11',
                       'S12', 'A1',
                       'A2', 'A3', 'A4', 'CR'],
            solution_variables=['S1', 'S2', 'S3', 'S4', 'S5', 'S6', 'S7', 'S8', 'A1', 'A2', 'A3', 'A4'],
            solution_coefficients=[0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1],
            function_coefficients=[1918, 1158, 896, 1868, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            restrictions_coefficients=[
                [12, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 19051],
                [0, 10, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 22680],
                [0, 0, 50, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 10000],
                [0, 0, 0, 60, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3780],
                [1421, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 750000],
                [0, 858, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 325000],
                [0, 0, 664, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 325000],
                [0, 0, 0, 1384, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 600000],
                [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, 0, 0, 0, 1, 0, 0, 0, 10],
                [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, 0, 0, 0, 1, 0, 0, 10],
                [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, 0, 0, 0, 1, 0, 4],
                [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, 0, 0, 0, 1, 6]
            ],
            function_phase_one_coefficients=[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1]
        )

        self.boards_phase_one, self.boards_phase_two = Simplex().simplex_two_phases(self.board)

        clean_boards(self.boards_phase_one)
        clean_boards(self.boards_phase_two)

        # GET OPTIMAL VALUES
        self.analysis = Analysis()

        self.optimal_values = self.analysis.solution.get_values(self.analysis.get_var_list())
        self.optimal_profit = self.analysis.solution.get_objective_value()
        self.dual_prices = self.analysis.get_dual_price()

        # Defne Data

        self.timeseries_data = {
            'Name': ['Actual'],

            'Value': [self.optimal_profit]
        }

        # Create dataframe

        self.dataframe = pd.DataFrame(self.timeseries_data, columns=['Name', 'Value'])

        # Setting the Date as index

        self.dataframe = self.dataframe.set_index("Name")

        self.ui.verticalLayout_23.addWidget(LinePlot(self.dataframe))

        # WINDOW BUTTONS
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
        self.ui.stackedWidget_3.setCurrentIndex(0)

        self.ui.menuBtn.clicked.connect(self.toggle_menu)

        self.ui.homeBtn.clicked.connect(lambda: self.set_page(0))
        self.ui.analisisBtn.clicked.connect(lambda: self.set_page(1))
        self.ui.reportBtn.clicked.connect(lambda: self.set_page(2))
        self.ui.simplexBtn.clicked.connect(lambda: self.set_page(3))

        # FILL SIMPLEX BOARDS
        self.set_table(self.boards_phase_one)
        self.set_table(self.boards_phase_two)

        self.ui.pushButton_2.setEnabled(False)
        self.ui.pushButton_3.clicked.connect(lambda: self.set_board(direction=1))
        self.ui.pushButton_2.clicked.connect(lambda: self.set_board(direction=0))

        # FILL MAIN INFO
        self.set_values()
        self.draw_pie_chart()

        # FILL ANALYSIS OPTIONS
        self.fill_combobox()

        self.ui.options.currentIndexChanged.connect(lambda: self.on_combobox_change())
        self.ui.items.currentIndexChanged.connect(lambda: self.on_combobox_change())

        self.on_combobox_change()

        self.ui.simulateBtn.clicked.connect(lambda: self.simulate())

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

    def set_page(self, index):
        self.ui.stackedWidget_3.setCurrentIndex(index)
        selected_style = "background-color: #1f232a;"

        unselected_style = "background-color: #16191d;"

        if index == 0:
            self.ui.homeBtn.setStyleSheet(selected_style)
            self.ui.analisisBtn.setStyleSheet(unselected_style)
            self.ui.reportBtn.setStyleSheet(unselected_style)
            self.ui.simplexBtn.setStyleSheet(unselected_style)
        elif index == 1:
            self.ui.homeBtn.setStyleSheet(unselected_style)
            self.ui.analisisBtn.setStyleSheet(selected_style)
            self.ui.reportBtn.setStyleSheet(unselected_style)
            self.ui.simplexBtn.setStyleSheet(unselected_style)
        elif index == 2:
            self.ui.homeBtn.setStyleSheet(unselected_style)
            self.ui.analisisBtn.setStyleSheet(unselected_style)
            self.ui.reportBtn.setStyleSheet(selected_style)
            self.ui.simplexBtn.setStyleSheet(unselected_style)
        elif index == 3:
            self.ui.homeBtn.setStyleSheet(unselected_style)
            self.ui.analisisBtn.setStyleSheet(unselected_style)
            self.ui.reportBtn.setStyleSheet(unselected_style)
            self.ui.simplexBtn.setStyleSheet(selected_style)

    def toggle_menu(self):
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

    def set_board(self, direction):
        if direction == 1:
            if self.ui.stackedWidget.currentIndex() < self.ui.stackedWidget.count() - 1:
                self.ui.stackedWidget.setCurrentIndex(self.ui.stackedWidget.currentIndex() + 1)
                self.ui.pushButton_2.setEnabled(True)
            else:
                self.ui.pushButton_3.setEnabled(False)
        elif direction == 0:
            if self.ui.stackedWidget.currentIndex() > 0:
                self.ui.stackedWidget.setCurrentIndex(self.ui.stackedWidget.currentIndex() - 1)
                self.ui.pushButton_3.setEnabled(True)
            else:
                self.ui.pushButton_2.setEnabled(False)

        if self.ui.stackedWidget.currentIndex() < len(self.boards_phase_one):
            self.ui.iteration.setText(str(self.ui.stackedWidget.currentIndex()))
        else:
            self.ui.iteration.setText(str(self.ui.stackedWidget.currentIndex() - len(self.boards_phase_one)))
        if self.ui.stackedWidget.currentIndex() >= len(self.boards_phase_one):
            self.ui.fase.setText('Fase 2')
        else:
            self.ui.fase.setText('Fase 1')

    def set_table(self, board):
        for board in board:
            page = QtWidgets.QWidget()
            vertical_layout = QtWidgets.QVBoxLayout(page)
            simplex_table = QtWidgets.QTableWidget(page)
            simplex_table.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
            simplex_table.setRowCount(len(board))
            simplex_table.setColumnCount(len(board[0]))
            simplex_table.horizontalHeader().setVisible(False)
            simplex_table.verticalHeader().setVisible(False)
            row = 0
            for line in board:
                column = 0
                for item in line:
                    if type(item) == str or type(item) == int:
                        cell = QTableWidgetItem(str(item))
                    else:
                        cell = QTableWidgetItem(str(f'{item:.2f}'))
                    cell.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
                    simplex_table.setItem(row, column, cell)
                    column += 1
                row += 1
            simplex_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
            vertical_layout.addWidget(simplex_table)
            self.ui.stackedWidget.addWidget(page)

    def draw_pie_chart(self):
        self.ui.graphic.addWidget(BarPlot(self.analysis.solution.get_values(self.analysis.get_var_list())))

    def set_values(self):
        self.ui.canelaValue.setText(str(f'$ {1918:.2f}'))
        self.ui.clavoValue.setText(str(f'$ {1158:.2f}'))
        self.ui.uvaValue.setText(str(f'$ {896:.2f}'))
        self.ui.ajoValue.setText(str(f'$ {1868:.2f}'))
        self.ui.profitValue.setText(str(f'$ {self.optimal_profit:.2f}'))

    def fill_combobox(self):
        options = ['Precio de Venta', 'Cantidad Materia Prima', 'Cantidad Presupuesto', 'Cantidad Demanda']
        items = ['Canela', 'Clavo', 'Uva Pasa', 'Ajo Sal']
        for option in options:
            self.ui.options.addItem(option)
        for item in items:
            self.ui.items.addItem(item)

    def on_combobox_change(self):
        values = [
            [1918, 1158, 896, 1868],
            [19051, 22680, 10000, 3780],
            [750000, 325000, 325000, 600000],
            [10, 10, 4, 6]
        ]
        option = self.ui.options.currentIndex()
        item = self.ui.items.currentIndex()
        self.ui.elementValue.setText(str(f'$ {values[option][item]:.2f}'))
        self.ui.newValue.setValue(0)
        if option == 0:
            self.ui.newValue.setMinimum(float(self.analysis.interval_coefficients[item][0]))
            self.ui.newValue.setMaximum(float(self.analysis.interval_coefficients[item][1]))
            self.ui.underLimit.setText(str(f'{self.analysis.interval_coefficients[item][0]:.2f}'))
            self.ui.overLimit.setText(str(f'{self.analysis.interval_coefficients[item][1]:.2f}'))
        elif option == 1:
            self.ui.newValue.setMinimum(float(self.analysis.right_interval[item][0]))
            self.ui.newValue.setMaximum(float(self.analysis.right_interval[item][1]))
            self.ui.underLimit.setText(str(f'{self.analysis.right_interval[item][0]:.2f}'))
            self.ui.overLimit.setText(str(f'{self.analysis.right_interval[item][1]:.2f}'))
        elif option == 2:
            self.ui.newValue.setMinimum(float(self.analysis.right_interval[item + 4][0]))
            self.ui.newValue.setMaximum(float(self.analysis.right_interval[item + 4][1]))
            self.ui.underLimit.setText(str(f'{self.analysis.right_interval[item + 4][0]:.2f}'))
            self.ui.overLimit.setText(str(f'{self.analysis.right_interval[item + 4][1]:.2f}'))
        elif option == 3:
            self.ui.newValue.setMinimum(float(self.analysis.right_interval[item + 8][0]))
            self.ui.newValue.setMaximum(float(self.analysis.right_interval[item + 8][1]))
            self.ui.underLimit.setText(str(f'{self.analysis.right_interval[item + 8][0]:.2f}'))
            self.ui.overLimit.setText(str(f'{self.analysis.right_interval[item + 8][1]:.2f}'))

    def simulate(self):
        option = self.ui.options.currentIndex()
        item = self.ui.items.currentIndex()
        new_value = self.ui.newValue.value()
        new_value = float(new_value)
        analysis = None
        if option == 0:
            if item == 0:
                analysis = Analysis(p_x1=new_value)
            elif item == 1:
                analysis = Analysis(p_x2=new_value)
            elif item == 2:
                analysis = Analysis(p_x3=new_value)
            elif item == 3:
                analysis = Analysis(p_x4=new_value)
        elif option == 1:
            if item == 0:
                analysis = Analysis(pm_x1=new_value)
            elif item == 1:
                analysis = Analysis(pm_x2=new_value)
            elif item == 2:
                analysis = Analysis(pm_x3=new_value)
            elif item == 3:
                analysis = Analysis(pm_x4=new_value)
        elif option == 2:
            if item == 0:
                analysis = Analysis(bill_x1=new_value)
            elif item == 1:
                analysis = Analysis(bill_x2=new_value)
            elif item == 2:
                analysis = Analysis(bill_x3=new_value)
            elif item == 3:
                analysis = Analysis(bill_x4=new_value)
        elif option == 3:
            if item == 0:
                analysis = Analysis(d_x1=new_value)
            elif item == 1:
                analysis = Analysis(d_x2=new_value)
            elif item == 2:
                analysis = Analysis(d_x3=new_value)
            elif item == 3:
                analysis = Analysis(d_x4=new_value)

        optimal_values = analysis.solution.get_values(analysis.get_var_list())
        optimal_profit = analysis.solution.get_objective_value()

        self.timeseries_data['Name'] = self.timeseries_data['Name'] + [f"Simulación {len(self.timeseries_data['Name'])}"]
        self.timeseries_data['Value'] = self.timeseries_data['Value'] + [optimal_profit]
        self.dataframe = pd.DataFrame(self.timeseries_data, columns=['Name', 'Value'])
        self.dataframe = self.dataframe.set_index("Name")

        self.ui.verticalLayout_23.replaceWidget(self.ui.verticalLayout_23.itemAt(0).widget(), LinePlot(self.dataframe))

        self.ui.textEdit.append(
            f"""
                    <h3>Resultados Simulación {len(self.timeseries_data['Name'])}</h3>
                    <hr>
                    <table style="border: 1px solid #fff;">
                      <tr>
                        <th>Actual</th>
                        <th>Simulación</th>
                      </tr>
                      <tr>
                        <td>
                            <strong>Ventas:</strong>
                            <ul>
                                <li><strong>Canela:</strong> {self.optimal_values[0]:.2f} Unidades</li>
                                <li><strong>Clavo: </strong> {self.optimal_values[1]:.2f} Unidades</li>
                                <li><strong>Uva Pasa: </strong> {self.optimal_values[2]:.2f} Unidades</li>
                                <li><strong>Ajo Sal: </strong> {self.optimal_values[3]:.2f} Unidades</li>
                            </ul>
                        </td>
                        <td>
                            <strong>Ventas:</strong>
                            <ul>
                                <li><strong>Canela:</strong> {optimal_values[0]:.2f} Unidades</li>
                                <li><strong>Clavo: </strong> {optimal_values[1]:.2f} Unidades</li>
                                <li><strong>Uva Pasa: </strong> {optimal_values[2]:.2f} Unidades</li>
                                <li><strong>Ajo Sal: </strong> {optimal_values[3]:.2f} Unidades</li>
                            </ul>
                        </td>
                      </tr>
                      <tr>
                        <td>
                            <strong>Utilidad:</strong> {self.optimal_profit:.2f}
                        </td>
                        <td>
                            <strong>Utilidad:</strong> {optimal_profit:.2f}
                        </td>
                      </tr>
                    </table>
                    <br>
                    """
        )
