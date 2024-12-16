from beam_ui import Ui_MainWindow
from PyQt5.QtWidgets import QApplication, QMainWindow
import numpy as np
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
"""TODO : 
    1. Add Spacing functionality
    2. Add Frequency functionality
    3. Add Amplitude functionality
    4. Add Phase functionality
    5. Add Transmitter number functionality
    6. Add circular transmitter position functionality
    """

class Transmitter:
    def __init__(self, x = 0, y = 0, amplitude = 1, frequency = 1000, phase = 0):
        self.x = x
        self.y = y
        self.amplitude = amplitude
        self.frequency = frequency
        self.phase = phase

class MainWindow(Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.transmitters = [Transmitter()]
        self.num_transmitters = 1
        self.speed = 343
        self.spacing = 1
        self.curvature = 0
        self.x = np.linspace(-6, 6, 200)
        self.y = np.linspace(0, 10, 200)
        self.connections()
        self.formUniformWaterWave()
    
    def connections(self):
        self.increaseNumButton.clicked.connect(self.increaseNumTransmitters)
        self.decreaseNumButton.clicked.connect(self.decreaseNumTransmitters)
    
    def increaseNumTransmitters(self):
        self.num_transmitters += 1
        self.transmitters.append(Transmitter())
        self.formUniformWaterWave()
    
    def decreaseNumTransmitters(self):
        if self.num_transmitters > 1:
            self.num_transmitters -= 1
            self.transmitters.pop()
            self.formUniformWaterWave()
        else:
            print("Warning, must have at least one transmitter")

    
    def formUniformWaterWave(self):
        """this functon forms the uniform sound wave that transmits through the beam from a point source"""
        
        field = np.zeros((len(self.x), len(self.y)), dtype=complex)
        for transmitter in self.transmitters:
            k = 2 * np.pi * transmitter.frequency / self.speed
            wavelength = self.speed / transmitter.frequency
            tr_field = np.zeros_like(field)
            for n in range(self.num_transmitters):
                x_offset = (n - (self.num_transmitters - 1) / 2) * self.spacing*wavelength
                y_offset = self.curvature * x_offset**2
                X, Y = np.meshgrid(self.x  - x_offset, self.y - y_offset)
                r = np.sqrt(X**2 + Y**2)
                phase = k*r + n*k*self.spacing*wavelength
                tr_field += transmitter.amplitude * np.exp(-1j*phase)
            field += tr_field/r
        self.WavesGraph.plot_wave(20*np.log10(np.abs(field)))

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())