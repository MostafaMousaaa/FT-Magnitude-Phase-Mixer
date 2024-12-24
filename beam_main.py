from PySide6 import QtWidgets
import sys
from beamUI import Ui_MainWindow
from beamUI import BeamformingCalculator
import numpy as np


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
class Transmitter:
    def __init__(self, x = 0, y = 0, amplitude = 1, frequency = 1000, phase = 0):
        self.x = x
        self.y = y
        self.amplitude = amplitude
        self.frequency = frequency
        self.phase = phase

class Window(Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.x = np.linspace(-6, 6, 200)
        self.y = np.linspace(0, 10, 200)
        self.transmitters = [Transmitter()]
        self.speed = 343
        self.rotation = 0
        self.field = None
        self.calculator = BeamformingCalculator()
                
        self  .steeringAngleSpin.valueChanged.connect(self.update_pattern)
        self  .spacingSpin.valueChanged.connect(self.update_pattern)
        self  .curvedCheckBox.stateChanged.connect(self.update_pattern)
        self  .radiusSlider.valueChanged.connect(self.update_pattern)
        self  .increaseNumButton.clicked.connect(self.increase_elements)
        self  .decreaseNumButton.clicked.connect(self.decrease_elements)
        self  .magnitudeSpin.valueChanged.connect(self.update_element)
        self  .frequencySpin.valueChanged.connect(self.update_element)
        self  .phaseShiftSpin.valueChanged.connect(self.update_element)
        self  .selectTransmitterComboBox.currentIndexChanged.connect(self.update_element_display)

        self.update_pattern()
        # Initialize transmitter selection
        self  .transmitterNumLCD.display(self.calculator.num_elements)
        self.update_transmitter_combo()
        self.update_waves()
        
        
        
        
        
        
        
    def update_pattern(self):
        print("Debug: Updating beam pattern")
        print(f"Steering: {self  .steeringAngleSpin.value()}")
        print(f"Spacing: {self  .spacingSpin.value()}")
        print(f"Curved: {self  .curvedCheckBox.isChecked()}")
        print(f"Radius: {self  .radiusSlider.value()}")
        
        # Update calculator parameters
        self.calculator.steering_angle = self  .steeringAngleSpin.value()
        
        # Fix spacing calculation: divide by 100 to convert to wavelengths
        self.calculator.spacing = self  .spacingSpin.value() / 100.0  # Convert to wavelengths
        print(f"Actual spacing: {self.calculator.spacing} wavelengths")  # Debug print
        
        self.calculator.is_curved = self  .curvedCheckBox.isChecked()
        self.calculator.radius = self  .radiusSlider.value() / 100
        
        # Calculate and update pattern
        angles, magnitudes = self.calculator.calculate_beam_pattern()
        self.BeamPatternGraph.update_beam_pattern(angles, magnitudes)
        self.update_waves()
        
    def update_element(self):
        index = self  .selectTransmitterComboBox.currentIndex()
        freq = self  .frequencySpin.value()
        phase = self  .phaseShiftSpin.value()
        # Fix: Scale magnitude to 0-1 range
        magnitude = self  .magnitudeSpin.value() / 100.0
        
        print(f"Updating element {index} with:")
        print(f"Frequency: {freq}")
        print(f"Phase: {phase}")
        print(f"Magnitude: {magnitude}")
        
        self.calculator.update_element(index, freq, phase, magnitude)
        self.update_waves()
        
    def update_waves(self):
        
        # Debug print
        print("Updating waves with:")
        print(f"Amplitudes: {self.calculator.amplitudes}")
        print(f"Phases: {self.calculator.phases}")
        print(f"Frequencies: {self.calculator.frequencies}")
        self.formBeam()
        
    def update_transmitter_combo(self):
        self  .selectTransmitterComboBox.clear()
        for i in range(self.calculator.num_elements):
            self  .selectTransmitterComboBox.addItem(f"Transmitter {i+1}")
            
    def update_element_display(self):
        index = self  .selectTransmitterComboBox.currentIndex()
        if index >= 0 and index < len(self.calculator.frequencies):
            self  .frequencySpin.setValue(self.calculator.frequencies[index])
            self  .phaseShiftSpin.setValue(self.calculator.phases[index])
            self  .magnitudeSpin.setValue(self.calculator.amplitudes[index] * 100)
    
    def increase_elements(self):
        self.calculator.num_elements += 1
        self.transmitters.append(Transmitter())
        self  .transmitterNumLCD.display(self.calculator.num_elements)
        self.update_transmitter_combo()
        self.update_pattern()
        self.update_waves()
        
    def decrease_elements(self):
        if self.calculator.num_elements > 1:
            self.calculator.num_elements -= 1
            self.transmitters.pop()
            self  .transmitterNumLCD.display(self.calculator.num_elements)
            self.update_transmitter_combo()
            self.update_pattern()
            self.update_waves()

    def formBeam(self):
        """this functon forms the sound waves that transmit from point sources"""
        
        field = np.zeros((len(self.x), len(self.y)), dtype=complex)
        for transmitter in self.transmitters:
            k = 2 * np.pi * transmitter.frequency / self.speed
            wavelength = self.speed / transmitter.frequency
            tr_field = np.zeros_like(field)
            for n in range(self.calculator.num_elements):
                x_offset = (n - (self.calculator.num_elements - 1) / 2) * self.calculator.spacing*wavelength
                y_offset = self.calculator.radius * x_offset**2
                rotation = np.radians(self.rotation)
                x_n = x_offset*np.cos(rotation) - y_offset*np.sin(rotation)
                y_n = x_offset*np.sin(rotation) + y_offset*np.cos(rotation)
                X, Y = np.meshgrid(self.x  - x_n, self.y - y_n)
                r = np.sqrt(X**2 + Y**2)
                steering_angle = np.radians(self.calculator.steering_angle)
                phase = k*r + n*k*self.calculator.spacing*wavelength*np.sin(steering_angle)+ transmitter.phase
                tr_field += transmitter.amplitude * np.exp(-1j*phase)
            field += tr_field/r**2
        self.field = 20*np.log10(np.abs(field))
        self.WavesGraph.plot_wave(self.field)
def main(): 
    app = QtWidgets.QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()