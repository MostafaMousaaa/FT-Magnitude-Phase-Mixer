import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSlider, QSpinBox, QDoubleSpinBox
from PyQt5.QtCore import Qt
from functools import partial
from PyQt5.QtCore import QThread, pyqtSignal

class Transmitter:
    def __init__(self, frequency, amplitude):
        self.frequency = frequency
        self.amplitude = amplitude

class WavesGraph(QWidget):
    def __init__(self, x, y):
        super().__init__()
        self.x = x
        self.y = y
        self.figure, self.ax = plt.subplots(figsize=(6, 5), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        layout = QVBoxLayout(self)
        layout.addWidget(self.canvas)
        self.figure.patch.set_facecolor('#2E3440')
        self.ax.set_facecolor('#2E3440')
        self.ax.tick_params(colors='white')
        self.ax.spines['bottom'].set_color('white')
        self.ax.spines['top'].set_color('white')
        self.ax.spines['right'].set_color('white')
        self.ax.spines['left'].set_color('white')

    def plot_wave(self, z):
        self.ax.clear()
        extent = [self.x[0], self.x[-1], self.y[0], self.y[-1]]  # Updated extent
        im = self.ax.imshow(z, extent=extent, aspect='equal',
                            cmap='jet', origin='lower')
        self.ax.set_xlabel('x (m)', color='white')
        self.ax.set_ylabel('y (m)', color='white')
        self.ax.axis('off')
        self.canvas.draw()

class PhasedArrayUnit:
    def __init__(self, x, y, num_transmitters, spacing, curvature, speed, transmitters):
        self.x = x
        self.y = y
        self.num_transmitters = num_transmitters
        self.spacing = spacing
        self.curvature = curvature
        self.speed = speed
        self.transmitters = transmitters
        self.beam_angle = 0
        self.delay_shift = 0

    def form_uniform_water_wave(self, steering_angle=0, delay_shift=0):
        field = np.zeros((len(self.x), len(self.y)), dtype=complex)
        k = 2 * np.pi * self.transmitters[0].frequency / self.speed
        wavelength = self.speed / self.transmitters[0].frequency

        for transmitter in self.transmitters:
            tr_field = np.zeros_like(field)
            for n in range(self.num_transmitters):
                x_offset = (n - (self.num_transmitters - 1) / 2) * self.spacing * wavelength
                y_offset = self.curvature * x_offset**2
                X, Y = np.meshgrid(self.x, self.y)
                r = np.sqrt((X - x_offset) ** 2 + (Y - y_offset) ** 2) + 1e-8

                # Steered phase calculation
                theta = np.deg2rad(steering_angle)
                steered_phase = k * x_offset * np.sin(theta)
                phase = k * r + n * k * self.spacing * wavelength + steered_phase + delay_shift
                tr_field += transmitter.amplitude * np.exp(-1j * phase)
            field += tr_field / r
        return field

class App(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Phased Array Simulator")
        self.setGeometry(100, 100, 1200, 800)

        self.x = np.linspace(-6, 6, 200)
        self.y = np.linspace(0, 10, 200)
        self.speed = 1500  # speed of sound in water

        self.array_units = []
        self.setup_ui()

        self.update_plot()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        control_layout = QHBoxLayout()

        # Array Units Configuration
        self.num_array_units_spinbox = QSpinBox()
        self.num_array_units_spinbox.setMinimum(1)
        self.num_array_units_spinbox.setValue(1)
        self.num_array_units_spinbox.valueChanged.connect(self.update_array_units)

        control_layout.addWidget(QLabel("Number of Array Units:"))
        control_layout.addWidget(self.num_array_units_spinbox)

        # Global Parameters (Speed and Steer)
        speed_label = QLabel("Speed (m/s):")
        self.speed_spinbox = QDoubleSpinBox()
        self.speed_spinbox.setDecimals(0)
        self.speed_spinbox.setMinimum(1000)
        self.speed_spinbox.setMaximum(2000)
        self.speed_spinbox.setValue(1500)
        self.speed_spinbox.valueChanged.connect(self.update_speed)

        steer_label = QLabel("Steering Angle (\u00b0):")
        self.steer_slider = QSlider(Qt.Horizontal)
        self.steer_slider.setMinimum(-90)
        self.steer_slider.setMaximum(90)
        self.steer_slider.setValue(0)
        self.steer_slider.valueChanged.connect(self.update_plot)

        control_layout.addWidget(speed_label)
        control_layout.addWidget(self.speed_spinbox)
        control_layout.addWidget(steer_label)
        control_layout.addWidget(self.steer_slider)

        # Unit Controls
        self.unit_controls_layout = QVBoxLayout()
        self.unit_controls_widget = QWidget()
        self.unit_controls_widget.setLayout(self.unit_controls_layout)

        # WavesGraph
        self.wave_graph = WavesGraph(self.x, self.y)

        main_layout.addLayout(control_layout)
        main_layout.addWidget(self.unit_controls_widget)
        main_layout.addWidget(self.wave_graph)

    def update_array_units(self):
        num_units = self.num_array_units_spinbox.value()
        while len(self.array_units) < num_units:
            self.add_array_unit()
        while len(self.array_units) > num_units:
            self.remove_array_unit()
        self.update_unit_controls()
        self.update_plot()

    def add_array_unit(self):
        # Default unit parameters
        num_transmitters = 10
        spacing = 0.5
        curvature = 0.0
        frequency = 500000
        amplitude = 1
        transmitters = [Transmitter(frequency, amplitude)]

        new_unit = PhasedArrayUnit(self.x, self.y, num_transmitters, spacing, curvature, self.speed, transmitters)
        self.array_units.append(new_unit)

    def remove_array_unit(self):
        if self.array_units:
            self.array_units.pop()

    def update_speed(self):
        self.speed = self.speed_spinbox.value()
        for array_unit in self.array_units:
            array_unit.speed = self.speed
        self.update_plot()

    def update_unit_controls(self):
        # Clear existing controls
        while self.unit_controls_layout.count():
            item = self.unit_controls_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        # Add new controls for each array
        for unit_index, unit in enumerate(self.array_units):

            unit_layout = QVBoxLayout()
            unit_layout.addWidget(QLabel(f"<b>Unit {unit_index + 1} Controls</b>", alignment=Qt.AlignCenter))

            # Number of Transmitters
            transmitters_layout = QHBoxLayout()
            transmitters_label = QLabel("Number of Transmitters:")
            transmitters_spinbox = QSpinBox()
            transmitters_spinbox.setMinimum(1)
            transmitters_spinbox.setMaximum(50)
            transmitters_spinbox.setValue(unit.num_transmitters)
            transmitters_spinbox.valueChanged.connect(partial(self.update_unit_parameter, unit, 'num_transmitters'))
            transmitters_layout.addWidget(transmitters_label)
            transmitters_layout.addWidget(transmitters_spinbox)

            # Spacing
            spacing_layout = QHBoxLayout()
            spacing_label = QLabel("Spacing (wavelength):")
            spacing_spinbox = QDoubleSpinBox()
            spacing_spinbox.setMinimum(0.1)
            spacing_spinbox.setMaximum(5)
            spacing_spinbox.setValue(unit.spacing)
            spacing_spinbox.setSingleStep(0.1)
            spacing_spinbox.valueChanged.connect(partial(self.update_unit_parameter, unit, 'spacing'))
            spacing_layout.addWidget(spacing_label)
            spacing_layout.addWidget(spacing_spinbox)

            # Curvature
            curvature_layout = QHBoxLayout()
            curvature_label = QLabel("Curvature:")
            curvature_spinbox = QDoubleSpinBox()
            curvature_spinbox.setMinimum(-0.01)
            curvature_spinbox.setMaximum(0.01)
            curvature_spinbox.setValue(unit.curvature)
            curvature_spinbox.setSingleStep(0.001)
            curvature_spinbox.valueChanged.connect(partial(self.update_unit_parameter, unit, 'curvature'))
            curvature_layout.addWidget(curvature_label)
            curvature_layout.addWidget(curvature_spinbox)

            # Delay/Shift Slider
            delay_layout = QHBoxLayout()
            delay_label = QLabel("Delay Shift (radians):")
            delay_slider = QSlider(Qt.Horizontal)
            delay_slider.setMinimum(-30)
            delay_slider.setMaximum(30)
            delay_slider.setValue(0)
            delay_slider.valueChanged.connect(partial(self.update_unit_parameter, unit, 'delay_shift'))
            delay_layout.addWidget(delay_label)
            delay_layout.addWidget(delay_slider)

            # Frequency Control
            frequency_layout = QHBoxLayout()
            frequency_label = QLabel("Frequency (Hz):")
            frequency_spinbox = QDoubleSpinBox()
            frequency_spinbox.setMinimum(10000)
            frequency_spinbox.setMaximum(1000000)
            frequency_spinbox.setValue(unit.transmitters[0].frequency)
            frequency_spinbox.setSingleStep(10000)
            frequency_spinbox.valueChanged.connect(partial(self.update_unit_frequency, unit))
            frequency_layout.addWidget(frequency_label)
            frequency_layout.addWidget(frequency_spinbox)

            unit_layout.addLayout(transmitters_layout)
            unit_layout.addLayout(spacing_layout)
            unit_layout.addLayout(curvature_layout)
            unit_layout.addLayout(delay_layout)
            unit_layout.addLayout(frequency_layout)

            self.unit_controls_layout.addLayout(unit_layout)

    def update_unit_parameter(self, unit, parameter, value):
        setattr(unit, parameter, value)
        self.update_plot()

    def update_unit_frequency(self, unit, frequency):
        unit.transmitters[0].frequency = frequency
        self.update_plot()

    def update_plot(self):
        combined_field = np.zeros((len(self.x), len(self.y)), dtype=complex)
        for unit in self.array_units:
            steering_angle = self.steer_slider.value()
            field = unit.form_uniform_water_wave(steering_angle, unit.delay_shift)
            combined_field += field
        self.wave_graph.plot_wave(20 * np.log10(np.abs(combined_field)+ 1e-8))

if __name__ == '__main__':
    app = QApplication([])
    window = App()
    window.show()
    app.exec_()
