from PySide6 import QtWidgets, QtCore
import sys
from beamUI import Ui_MainWindow
from beamUI import BeamformingCalculator
from beamUI import WavesGraph , PolarChartWidget
import numpy as np
from PySide6.QtCharts import QLineSeries, QValueAxis, QPolarChart
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter
from PySide6.QtCharts import QChart, QPolarChart, QChartView, QValueAxis, QLineSeries, QPolarChart
from PySide6.QtGui import QPainter
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import Qt 


# class PolarChartWidget(QWidget):
#     def __init__(self, parent=None):
#         super().__init__(parent)
#         self.chart = QPolarChart()
#         self.chart.legend().hide()
        
#         # Setup axes
#         self.angular_axis = QValueAxis()
#         self.angular_axis.setRange(-180, 180)
#         self.angular_axis.setLabelFormat("%.1f°")
        
#         self.radial_axis = QValueAxis()
#         self.radial_axis.setRange(0, 1)
#         self.radial_axis.setLabelFormat("%.2f")
        
#         # Fix: Use QPolarChart.PolarOrientation enum values
#         self.chart.addAxis(self.angular_axis, QPolarChart.PolarOrientationAngular)
#         self.chart.addAxis(self.radial_axis, QPolarChart.PolarOrientationRadial)
        
#         # Setup chart view
#         self.chartView = QChartView(self.chart)
#         self.chartView.setRenderHint(QPainter.Antialiasing)
        
#         # Layout
#         layout = QVBoxLayout(self)
#         layout.addWidget(self.chartView)
        
#     def update_beam_pattern(self, angles, magnitudes):
#         # Clear existing series
#         for series in self.chart.series():
#             self.chart.removeSeries(series)
            
#         # Create new series
#         series = QLineSeries()
        
#         # Add data points
#         for angle, magnitude in zip(angles, magnitudes):
#             series.append(angle, magnitude)
            
#         # Add series to chart
#         self.chart.addSeries(series)
#         series.attachAxis(self.angular_axis)
#         series.attachAxis(self.radial_axis)

# class WavesGraph(QWidget):
#     def __init__(self, parent: QWidget = None):
#         super().__init__(parent)
        
#         # Create matplotlib figure
#         self.figure = Figure(figsize=(6, 4))
#         self.canvas = FigureCanvas(self.figure)
#         self.ax = self.figure.add_subplot(111)
        
#         # Setup layout
#         layout = QVBoxLayout(self)
#         layout.addWidget(self.canvas)
        
#     def update_waves(self, time, amplitudes, phases, frequencies):
#         self.ax.clear()
#         colors = ['#81A1C1', '#A3BE8C', '#EBCB8B', '#BF616A', '#B48EAD']
        
#         for i, (amp, phase, freq) in enumerate(zip(amplitudes, phases, frequencies)):
#             y = amp * np.sin(2*np.pi*freq*time + np.deg2rad(phase))
#             self.ax.plot(time, y, color=colors[i % len(colors)], 
#                         label=f'Element {i+1}')
        
#         self.ax.set_xlabel('Time')
#         self.ax.set_ylabel('Amplitude')
#         self.ax.grid(True)
#         self.ax.legend()
#         self.canvas.draw()

# class BeamformingCalculator:
#     def __init__(self):
#         self.num_elements = 1
#         self.frequencies = [10]  # Default frequency
#         self.phases = [0]       # Default phase
#         self.amplitudes = [1]   # Default amplitude
#         self.spacing = 0.5      # Default spacing in wavelengths
#         self.steering_angle = 0
#         self.is_curved = False
#         self.radius = 1
        
#     def calculate_beam_pattern(self):
#         angles = np.linspace(-180, 180, 361)  # Changed range
#         k = 2 * np.pi
#         array_factor = np.zeros_like(angles, dtype=complex)
        
#         if not self.is_curved:
#             for n in range(self.num_elements):
#                 # Apply individual element characteristics
#                 phase_shift = self.phases[n % len(self.phases)]
#                 amplitude = self.amplitudes[n % len(self.amplitudes)]
#                 phase = k * self.spacing * n * np.sin(np.deg2rad(angles - self.steering_angle))
#                 array_factor += amplitude * np.exp(1j * (phase + np.deg2rad(phase_shift)))
#         else:
#             theta = np.linspace(-np.pi/4, np.pi/4, self.num_elements)
#             for n, th in enumerate(theta):
#                 amplitude = self.amplitudes[n % len(self.amplitudes)]
#                 phase_shift = self.phases[n % len(self.phases)]
#                 x = self.radius * np.cos(th)
#                 y = self.radius * np.sin(th)
#                 phase = k * (x * np.sin(np.deg2rad(angles)) + y * np.cos(np.deg2rad(angles)))
#                 array_factor += amplitude * np.exp(1j * (phase + np.deg2rad(phase_shift)))
                
#         magnitudes = np.abs(array_factor) / self.num_elements
#         return angles, magnitudes

#     def update_element(self, index, freq, phase, magnitude):
#         while len(self.frequencies) <= index:
#             self.frequencies.append(10)
#             self.phases.append(0)
#             self.amplitudes.append(1)
            
#         self.frequencies[index] = freq
#         self.phases[index] = phase
#         self.amplitudes[index] = magnitude


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        # Remove existing graph widgets first
        for i in reversed(range(self.ui.horizontalLayout.count())): 
            self.ui.horizontalLayout.itemAt(i).widget().setParent(None)
        
        # Add graphs in correct order
        self.beam_pattern = PolarChartWidget(self)
        self.waves_graph = WavesGraph(self)
        
        self.ui.horizontalLayout.addWidget(self.beam_pattern)
        self.ui.horizontalLayout.addWidget(self.waves_graph)
        
        # Initialize calculator
        self.calculator = BeamformingCalculator()
        
        # Connect signals
        self.ui.steeringAngleSpin.valueChanged.connect(self.update_pattern)
        self.ui.spacingSpin.valueChanged.connect(self.update_pattern)
        self.ui.curvedCheckBox.stateChanged.connect(self.update_pattern)
        self.ui.radiusSlider.valueChanged.connect(self.update_pattern)
        self.ui.increaseNumButton.clicked.connect(self.increase_elements)
        self.ui.decreaseNumButton.clicked.connect(self.decrease_elements)
        
        # Connect additional signals
        self.ui.magnitudeSpin.valueChanged.connect(self.update_element)
        self.ui.frequencySpin.valueChanged.connect(self.update_element)
        self.ui.phaseShiftSpin.valueChanged.connect(self.update_element)
        
        # Initialize
        self.update_pattern()
        
        # Initialize transmitter selection
        self.ui.transmitterNumLCD.display(self.calculator.num_elements)
        self.update_transmitter_combo()
        
        # Connect combo box signal
        self.ui.selectTransmitterComboBox.currentIndexChanged.connect(self.update_element_display)
        
        # Set initial spacing value and range
        self.ui.spacingSpin.setRange(10, 200)  # Range from 0.1 to 2.0
        self.ui.spacingSpin.setValue(50)        # Default 0.5
        self.ui.spacingSpin.setSingleStep(1)    # Step by 0.01 when converted

        # Set ranges for input controls
        self.ui.steeringAngleSpin.setRange(-90, 90)  # Steering angle ±90°
        self.ui.phaseShiftSpin.setRange(0, 360)      # Phase 0-360°
        self.ui.frequencySpin.setRange(1, 100)       # Frequency range
        self.ui.magnitudeSpin.setRange(0, 100)       # Magnitude 0-100%
        
    def update_pattern(self):
        print("Debug: Updating beam pattern")
        print(f"Steering: {self.ui.steeringAngleSpin.value()}")
        print(f"Spacing: {self.ui.spacingSpin.value()}")
        print(f"Curved: {self.ui.curvedCheckBox.isChecked()}")
        print(f"Radius: {self.ui.radiusSlider.value()}")
        
        # Update calculator parameters
        self.calculator.steering_angle = self.ui.steeringAngleSpin.value()
        
        # Fix spacing calculation: divide by 100 to convert to wavelengths
        self.calculator.spacing = self.ui.spacingSpin.value() / 100.0  # Convert to wavelengths
        print(f"Actual spacing: {self.calculator.spacing} wavelengths")  # Debug print
        
        self.calculator.is_curved = self.ui.curvedCheckBox.isChecked()
        self.calculator.radius = self.ui.radiusSlider.value() / 100
        
        # Calculate and update pattern
        angles, magnitudes = self.calculator.calculate_beam_pattern()
        self.beam_pattern.update_beam_pattern(angles, magnitudes)
        self.update_waves()  # Update both visualizations together
        
    def update_element(self):
        index = self.ui.selectTransmitterComboBox.currentIndex()
        freq = self.ui.frequencySpin.value()
        phase = self.ui.phaseShiftSpin.value()
        # Fix: Scale magnitude to 0-1 range
        magnitude = self.ui.magnitudeSpin.value() / 100.0
        
        print(f"Updating element {index} with:")
        print(f"Frequency: {freq}")
        print(f"Phase: {phase}")
        print(f"Magnitude: {magnitude}")
        
        self.calculator.update_element(index, freq, phase, magnitude)
        self.update_waves()
        
    def update_waves(self):
        time = np.linspace(0, 2, 1000)  # Show 2 periods
        
        # Debug print
        print("Updating waves with:")
        print(f"Amplitudes: {self.calculator.amplitudes}")
        print(f"Phases: {self.calculator.phases}")
        print(f"Frequencies: {self.calculator.frequencies}")
        
        # Fix: Use waves_graph instead of ui.WavesGraph
        self.waves_graph.update_waves(
            time,
            self.calculator.amplitudes,
            self.calculator.phases,
            self.calculator.frequencies
        )
        
    def update_transmitter_combo(self):
        self.ui.selectTransmitterComboBox.clear()
        for i in range(self.calculator.num_elements):
            self.ui.selectTransmitterComboBox.addItem(f"Transmitter {i+1}")
            
    def update_element_display(self):
        index = self.ui.selectTransmitterComboBox.currentIndex()
        if index >= 0 and index < len(self.calculator.frequencies):
            self.ui.frequencySpin.setValue(self.calculator.frequencies[index])
            self.ui.phaseShiftSpin.setValue(self.calculator.phases[index])
            self.ui.magnitudeSpin.setValue(self.calculator.amplitudes[index] * 100)
    
    def increase_elements(self):
        self.calculator.num_elements += 1
        self.ui.transmitterNumLCD.display(self.calculator.num_elements)
        self.update_transmitter_combo()
        self.update_pattern()
        self.update_waves()
        
    def decrease_elements(self):
        if self.calculator.num_elements > 1:
            self.calculator.num_elements -= 1
            self.ui.transmitterNumLCD.display(self.calculator.num_elements)
            self.update_transmitter_combo()
            self.update_pattern()
            self.update_waves()
        
def main():
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()