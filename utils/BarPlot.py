import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_qtagg import FigureCanvas


class BarPlot(FigureCanvas):
    def __init__(self, solution):
        self.fig, self.ax = plt.subplots(1, figsize=(10, 10))
        super().__init__(self.fig)
        # y = solution
        # labels = ["Canela", "Clavo", "Uva Pasa", "Ajo Sal"]

        # self.ax.axis('off')
        # self.ax.bar(y, labels=labels)

        objects = ("Canela", "Clavo", "Uva Pasa", "Ajo Sal")
        y_pos = np.arange(len(objects))
        performance = solution

        rects = plt.bar(y_pos, performance, align='center', color='#838ea2')
        plt.xticks(y_pos, objects)
        plt.ylabel('Cantidad', color='#fff')
        plt.title('Ventas necesarias para maximizar utilidad', color='#fff')

        for rect in rects:
            height = rect.get_height()
            self.ax.text(rect.get_x() + rect.get_width() / 2., height-2,
                         '%d' % float(height),
                         ha='center', va='bottom', color='#fff')

        self.ax.set_facecolor('#1f232a')
        self.ax.spines['bottom'].set_color('#1f232a')
        self.ax.spines['top'].set_color('#1f232a')
        self.ax.spines['right'].set_color('#1f232a')
        self.ax.spines['left'].set_color('#1f232a')
        self.ax.tick_params(axis='x', colors='#fff')
        self.ax.tick_params(axis='y', colors='#fff')
        self.fig.set_facecolor('#1f232a')
