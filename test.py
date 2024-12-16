

import numpy as np
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from numpy import Array
class FieldPlotWidget(QWidget):
    def init(self, parent=None):
        super().init(parent)
        self.setup_ui()
        self.color = np.random.rand(3,)
        
    def setup_ui(self):
        layout = QVBoxLayout()
        self.figure = Figure(figsize=(12, 8))
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.ax_field = self.figure.add_subplot(111)
        self.figure.tight_layout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)
        
    def update_plot(self, arrays:list[Array],extent = [-6, 6, 0, 10]):
        if len(arrays) == 0:
            #remove plot
            self.ax_field.clear()
            self.figure.clear()
            self.canvas.draw()
            return
        x = np.linspace(-6, 6, 200)
        y = np.linspace(0, 10, 200)
        field = arrays[0].calculate_field(x,y)
        for i, array in enumerate(arrays[1:], 1):
            field += array.calculate_field(x,y)

        self.ax_field.clear()
        self.figure.clear()
        self.ax = self.figure.add_subplot(111)

        im = self.ax.imshow(field, extent=extent, aspect='equal', 
                    cmap='jet', origin='lower')
        self.figure.colorbar(im)
        self.ax.set_xlabel('x (m)')
        self.ax.set_ylabel('y (m)')
        self.canvas.draw()