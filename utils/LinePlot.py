import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvas


class LinePlot(FigureCanvas):
    def __init__(self, series):
        self.fig, self.ax = plt.subplots(1, figsize=(10, 10))
        super().__init__(self.fig)

        plt.plot(series['Value'], marker='o', color='#838ea2')
        plt.ylabel('Utilidad', color='#fff')
        plt.title('Histórico Simulaciones', color='#fff')

        self.ax.set_facecolor('#1f232a')
        self.ax.spines['bottom'].set_color('#1f232a')
        self.ax.spines['top'].set_color('#1f232a')
        self.ax.spines['right'].set_color('#1f232a')
        self.ax.spines['left'].set_color('#1f232a')
        self.ax.tick_params(axis='x', colors='#fff')
        self.ax.tick_params(axis='y', colors='#fff')
        self.fig.set_facecolor('#1f232a')
