import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_qtagg import FigureCanvas


class PiePlot(FigureCanvas):
    def __init__(self, values):
        self.fig, self.ax = plt.subplots(1, figsize=(10, 10))
        super().__init__(self.fig)

        labels = ['Canela', 'Clavo', 'Uva Pasa', 'Ajo Sal']

        colors = ['#343b47', '#2c313c', '#1f232a', '#838ea2']

        patches, texts, pcts = self.ax.pie(
            values, labels=labels, autopct='%.2f%%', colors=colors,
            wedgeprops={'edgecolor': 'white'})

        self.ax.set_title('Porcentaje de utilidad por producto', color='#fff')

        # For each wedge, set the corresponding text label color to the wedge's
        # face color.
        for i, patch in enumerate(patches):
            texts[i].set_color('#fff')
        plt.setp(pcts, color='white')

        self.ax.set_facecolor('#1f232a')
        self.ax.spines['bottom'].set_color('#1f232a')
        self.ax.spines['top'].set_color('#1f232a')
        self.ax.spines['right'].set_color('#1f232a')
        self.ax.spines['left'].set_color('#1f232a')
        self.ax.tick_params(axis='x', colors='#fff')
        self.ax.tick_params(axis='y', colors='#fff')
        self.fig.set_facecolor('#1f232a')
