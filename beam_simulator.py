from beam_ui import Ui_MainWindow
from PyQt5.QtWidgets import QApplication, QMainWindow
import numpy as np
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import pyqtgraph as pg


class MainWindow(Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.formUniformWaterWave()
    
    def formUniformWaterWave(self):
        """this functon forms the uniform water wave that transmits through the beam from a point source"""
        x = np.linspace(-10, 10, 1000) 
        y = np.linspace(-10, 10, 1000) 
        X, Y = np.meshgrid(x, y) 
        wavelength = 2
        d = wavelength / 4 
        R1 = np.sqrt((X - d)**2 + Y**2) 
        R2 = np.sqrt((X + d)**2 + Y**2) 
        frequency = 1 
        Z1 = np.sin(2 * np.pi * frequency * R1 / wavelength) 
        Z2 = np.sin(2 * np.pi * frequency * R2 / wavelength) 
        Z = Z1 + Z2
        self.WavesGraph.plot_wave(Z)
if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())