import sys
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, \
      QVBoxLayout, QLabel, QSlider, QPushButton, QWidget, QHBoxLayout
import pyqtgraph as pg

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Beamforming Simulator")
        self.setGeometry(100, 100, 800, 600)
        self.initUI()
        self.connections()

    def initUI(self):
        layout = QVBoxLayout()
        hlayout = QHBoxLayout()
        self.label = QLabel("Beamforming Simulator", self)
        layout.addWidget(self.label)
        self.plotWidget = pg.PlotWidget(self)
        self.slider = QSlider(self)
        hlayout.addWidget(self.slider)
        hlayout.addWidget(self.plotWidget)
        layout.addLayout(hlayout)        
        self.button = QPushButton("Simulate", self)
        layout.addWidget(self.button)
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def connections(self):
        self.button.clicked.connect(self.beamform)

    def beamform(self): 
        x = np.linspace(0, 10, 1000) 
        y = np.linspace(0, 10, 1000) 
        X, Y = np.meshgrid(x, y) 
        wavelength = 2
        d = wavelength / 4 
        R1 = np.sqrt((X - d)**2 + Y**2) 
        R2 = np.sqrt((X + d)**2 + Y**2) 
        frequency = 1 
        Z1 = np.sin(2 * np.pi * frequency * R1 / wavelength) 
        Z2 = np.sin(2 * np.pi * frequency * R2 / wavelength) 
        Z = Z1 + Z2  
        self.plotWidget.clear() 
        img = pg.ImageItem(Z) 
        self.plotWidget.addItem(img)
        emitters = np.array([[-d, 0], [d, 0]]) 
        scatter = pg.ScatterPlotItem(pos=emitters, pen=pg.mkPen(None), brush=pg.mkBrush('r'), size=10) 
        self.plotWidget.addItem(scatter)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
