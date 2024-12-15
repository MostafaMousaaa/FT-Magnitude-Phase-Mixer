from beam_ui import Ui_MainWindow
from PyQt5.QtWidgets import QApplication, QMainWindow
import numpy as np
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import pyqtgraph as pg
"""TODO : 
    1. Add Spacing functionality
    2. Add Frequency functionality
    3. Add Amplitude functionality
    4. Add Phase functionality
    5. Add Transmitter number functionality
    6. Add circular transmitter position functionality
    """

class MainWindow(Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.num_transmitters = 1
        self.formUniformWaterWave()
        self.connections()
    
    def connections(self):
        self.increaseNumButton.clicked.connect(self.increaseNumTransmitters)
        self.decreaseNumButton.clicked.connect(self.decreaseNumTransmitters)
    
    def increaseNumTransmitters(self):
        self.num_transmitters += 1
        self.formUniformWaterWave()
    
    def decreaseNumTransmitters(self):
        if self.num_transmitters > 1:
            self.num_transmitters -= 1
            self.formUniformWaterWave()
        else:
            print("Warning, must have at least one transmitter")

    
    def formUniformWaterWave(self):
        """this functon forms the uniform water wave that transmits through the beam from a point source"""
        x = np.linspace(-5, 5, 1000) 
        y = np.linspace(-5, 5, 1000) 
        X, Y = np.meshgrid(x, y) 
        Z = np.zeros_like(X)
        wavelength = 1
        frequency = 100
        sources_positions = np.array([])
        if self.num_transmitters < 1:
            print("Warning, must have at least one transmitter")
        else:
            for i in range(self.num_transmitters):
                # Calculate the x-coordinate of the current source 
                # (evenly spaced along x-axis)
                source_x = -((self.num_transmitters - 1)/2)*wavelength/4 + i * wavelength / 4
                sources_positions = np.append(sources_positions, [source_x])

                # Distance of the current point source from every point on the grid
                R = np.sqrt((X - source_x)**2 + Y**2)

                # Calculate the wave due to the current source
                Zi = np.sin(2 * np.pi * frequency * R / wavelength)
                # reduce the amplitude inversely proportional to the distance
                Zi = Zi / (R+1)
                # Add the individual wave to the total
                Z += Zi
        self.WavesGraph.plot_wave(sources_positions,Z)
if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())