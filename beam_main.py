from PySide6 import QtWidgets
import sys
from beamUI import Ui_MainWindow
from beamUI import BeamformingCalculator
import numpy as np


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
        self.steeringAngleSpin.valueChanged.connect(self.update_pattern)
        self.spacingSpin.valueChanged.connect(self.update_pattern)
        self.curvedCheckBox.stateChanged.connect(self.update_pattern)
        self.radiusSlider.valueChanged.connect(self.update_pattern)
        self.increaseNumButton.clicked.connect(self.increase_elements)
        self.decreaseNumButton.clicked.connect(self.decrease_elements)
        self.magnitudeSpin.valueChanged.connect(self.update_element)
        self.frequencySpin.valueChanged.connect(self.update_element)
        self.phaseShiftSpin.valueChanged.connect(self.update_element)
        self.selectTransmitterComboBox.currentIndexChanged.connect(self.update_element_display)
        self.update_pattern()
        self.transmitterNumLCD.display(self.calculator.num_elements)
        self.update_transmitter_combo()
        self.update_waves()
        
        
    def update_pattern(self):
        print("Debug: Updating beam pattern")
        print(f"Steering: {self.steeringAngleSpin.value()}")
        print(f"Spacing: {self.spacingSpin.value()}")
        print(f"Curved: {self.curvedCheckBox.isChecked()}")
        print(f"Radius: {self.radiusSlider.value()}")
        self.calculator.steering_angle = self.steeringAngleSpin.value()
        self.calculator.spacing = self.spacingSpin.value() / 100.0
        print(f"Actual spacing: {self.calculator.spacing} wavelengths") 
        self.calculator.is_curved = self.curvedCheckBox.isChecked()
        self.calculator.radius = self.radiusSlider.value() / 100
        angles, magnitudes = self.calculator.calculate_beam_pattern()
        self.BeamPatternGraph.update_beam_pattern(angles, magnitudes)
        self.update_waves()
        
    def update_element(self):
        index = self.selectTransmitterComboBox.currentIndex()
        freq = self.frequencySpin.value()
        phase = self.phaseShiftSpin.value()
        magnitude = self.magnitudeSpin.value() / 100.0
        self.transmitters[index].amplitude = magnitude
        self.transmitters[index].frequency = freq
        self.transmitters[index].phase = phase
        print(f"Updating element {index} with:")
        print(f"Frequency: {freq}")
        print(f"Phase: {phase}")
        print(f"Magnitude: {magnitude}")
        self.calculator.update_element(index, freq, phase, magnitude)
        self.update_waves()
        
    def update_waves(self):
        print("Updating waves with:")
        print(f"Amplitudes: {self.calculator.amplitudes}")
        print(f"Phases: {self.calculator.phases}")
        print(f"Frequencies: {self.calculator.frequencies}")
        self.formBeam()
        
    def update_transmitter_combo(self):
        self.selectTransmitterComboBox.clear()
        for i in range(self.calculator.num_elements):
            self.selectTransmitterComboBox.addItem(f"Transmitter {i+1}")
            
    def update_element_display(self):
        index = self.selectTransmitterComboBox.currentIndex()
        if index >= 0 and index < len(self.calculator.frequencies):
            self.frequencySpin.setValue(self.calculator.frequencies[index])
            self.phaseShiftSpin.setValue(self.calculator.phases[index])
            self.magnitudeSpin.setValue(self.calculator.amplitudes[index] * 100)
    
    def increase_elements(self):
        self.calculator.num_elements += 1
        self.transmitters.append(Transmitter())
        self.transmitterNumLCD.display(self.calculator.num_elements)
        self.update_transmitter_combo()
        self.update_pattern()
        self.update_waves()
        
    def decrease_elements(self):
        if self.calculator.num_elements > 1:
            self.calculator.num_elements -= 1
            self.transmitters.pop()
            self.transmitterNumLCD.display(self.calculator.num_elements)
            self.update_transmitter_combo()
            self.update_pattern()
            self.update_waves()

    def formBeam(self):        
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