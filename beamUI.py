# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'beamUI.ui'
##
## Created by: Qt User Interface Compiler version 6.8.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QFrame,
    QGridLayout, QHBoxLayout, QLCDNumber, QLabel,
    QMainWindow, QMenuBar, QPushButton, QSizePolicy,
    QSlider, QSpinBox, QStatusBar, QVBoxLayout,
    QWidget)

# from polarchartwidget import PolarChartWidget
from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import Qt 
from PySide6.QtCharts import QChart, QPolarChart, QChartView, QValueAxis, QLineSeries, QPolarChart
from PySide6.QtGui import QPainter
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

class PolarChartWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.chart = QPolarChart()
        self.chart.legend().hide()
        
        # Setup axes
        self.angular_axis = QValueAxis()
        self.angular_axis.setRange(-180, 180)
        self.angular_axis.setLabelFormat("%.1f°")
        
        self.radial_axis = QValueAxis()
        self.radial_axis.setRange(0, 1)
        self.radial_axis.setLabelFormat("%.2f")
        
        # Fix: Use QPolarChart.PolarOrientation enum values
        angular_orientation = getattr(QPolarChart, 'PolarOrientationAngular', 2)
        radial_orientation = getattr(QPolarChart, 'PolarOrientationRadial', 1)
        
        # Add axes with proper orientation
        self.chart.addAxis(self.angular_axis, angular_orientation)
        self.chart.addAxis(self.radial_axis, radial_orientation)
        
        # Setup chart view
        self.chartView = QChartView(self.chart)
        self.chartView.setRenderHint(QPainter.Antialiasing)
        
        # Layout
        layout = QVBoxLayout(self)
        layout.addWidget(self.chartView)
        
    def update_beam_pattern(self, angles, magnitudes):
        # Clear existing series
        for series in self.chart.series():
            self.chart.removeSeries(series)
            
        # Create new series
        series = QLineSeries()
        
        # Add data points
        for angle, magnitude in zip(angles, magnitudes):
            series.append(angle, magnitude)
            
        # Add series to chart
        self.chart.addSeries(series)
        series.attachAxis(self.angular_axis)
        series.attachAxis(self.radial_axis)
        
        # Add grid lines
        self.angular_axis.setTickCount(13)  # 30-degree steps
        self.radial_axis.setTickCount(6)    # 0.2 steps
        
        # Update series with smoother line
        series = QLineSeries()
        for angle, magnitude in zip(angles, magnitudes):
            series.append(angle, magnitude)
        
        # Close the pattern loop
        series.append(angles[0], magnitudes[0])

class WavesGraph(QWidget):
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        
        # Create matplotlib figure
        self.figure = Figure(figsize=(6, 4))
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        
        # Setup layout
        layout = QVBoxLayout(self)
        layout.addWidget(self.canvas)
        
    def update_waves(self, time, amplitudes, phases, frequencies):
        self.ax.clear()
        colors = ['#81A1C1', '#A3BE8C', '#EBCB8B', '#BF616A', '#B48EAD']
        
        for i, (amp, phase, freq) in enumerate(zip(amplitudes, phases, frequencies)):
            y = amp * np.sin(2*np.pi*freq*time + np.deg2rad(phase))
            self.ax.plot(time, y, color=colors[i % len(colors)], 
                        label=f'Element {i+1}')
        
        self.ax.set_xlabel('Time')
        self.ax.set_ylabel('Amplitude')
        self.ax.grid(True)
        self.ax.legend()
        self.canvas.draw()

class BeamformingCalculator:
    def __init__(self):
        self.num_elements = 1
        self.frequencies = [10]
        self.phases = [0]
        self.amplitudes = [0.5]  # Start at 50%
        self.spacing = 0.5      # Default spacing in wavelengths
        self.steering_angle = 0
        self.is_curved = False
        self.radius = 1.0
        
    def calculate_beam_pattern(self):
        angles = np.linspace(-180, 180, 361)  # Changed range
        k = 2 * np.pi
        array_factor = np.zeros_like(angles, dtype=complex)
        
        if not self.is_curved:
            for n in range(self.num_elements):
                # Apply individual element characteristics
                phase_shift = self.phases[n % len(self.phases)]
                amplitude = self.amplitudes[n % len(self.amplitudes)]
                phase = k * self.spacing * n * np.sin(np.deg2rad(angles - self.steering_angle))
                array_factor += amplitude * np.exp(1j * (phase + np.deg2rad(phase_shift)))
        else:
            theta = np.linspace(-np.pi/4, np.pi/4, self.num_elements)
            for n, th in enumerate(theta):
                amplitude = self.amplitudes[n % len(self.amplitudes)]
                phase_shift = self.phases[n % len(self.phases)]
                x = self.radius * np.cos(th)
                y = self.radius * np.sin(th)
                phase = k * (x * np.sin(np.deg2rad(angles)) + y * np.cos(np.deg2rad(angles)))
                array_factor += amplitude * np.exp(1j * (phase + np.deg2rad(phase_shift)))
                
        magnitudes = np.abs(array_factor)
        magnitudes = magnitudes / np.max(magnitudes)  # Normalize to max value
        return angles, magnitudes

    def update_element(self, index, freq, phase, magnitude):
        while len(self.frequencies) <= index:
            self.frequencies.append(10)
            self.phases.append(0)
            self.amplitudes.append(1)
            
        self.frequencies[index] = freq
        self.phases[index] = phase
        self.amplitudes[index] = magnitude

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1218, 692)
        MainWindow.setStyleSheet(u"/* General QWidget Style */\n"
"QWidget {\n"
"    background-color: #2E3440;\n"
"    color: #D8DEE9;\n"
"    font-family: \"Segoe UI\", Arial, sans-serif;\n"
"    font-size: 12pt;\n"
"}\n"
"\n"
"/* PushButtons */\n"
"QPushButton {\n"
"    background-color: #4C566A;\n"
"    color: #ECEFF4;\n"
"    border: 1px solid #81A1C1;\n"
"    border-radius: 5px;\n"
"    padding: 5px 15px;\n"
"}\n"
"QPushButton:hover {\n"
"    background-color: #81A1C1;\n"
"}\n"
"QPushButton:pressed {\n"
"    background-color: #5E81AC;\n"
"}\n"
"\n"
"/* SpinBoxes */\n"
"QSpinBox {\n"
"    background-color: #3B4252;\n"
"    color: #ECEFF4;\n"
"    border: 1px solid #81A1C1;\n"
"    border-radius: 3px;\n"
"    padding: 2px;\n"
"}\n"
"QSpinBox::up-button {\n"
"    subcontrol-origin: border;\n"
"    subcontrol-position: top right;\n"
"    width: 12px;\n"
"    border-left: 1px solid #81A1C1;\n"
"}\n"
"QSpinBox::down-button {\n"
"    subcontrol-origin: border;\n"
"    subcontrol-position: bottom right;\n"
"    width: 12px;\n"
"    border-left: 1"
                        "px solid #81A1C1;\n"
"}\n"
"\n"
"/* Horizontal Sliders */\n"
"QSlider::groove:horizontal {\n"
"    border: 1px solid #81A1C1;\n"
"    height: 5px;\n"
"    background: #3B4252;\n"
"}\n"
"QSlider::handle:horizontal {\n"
"    background: #81A1C1;\n"
"    border: 1px solid #5E81AC;\n"
"    width: 15px;\n"
"    margin: -5px 0;\n"
"    border-radius: 5px;\n"
"}\n"
"\n"
"/* Labels */\n"
"QLabel {\n"
"    color: #ECEFF4;\n"
"    font-size: 12pt;\n"
"    font-weight: bold;\n"
"}\n"
"\n"
"/* CheckBoxes */\n"
"QCheckBox {\n"
"    color: #ECEFF4;\n"
"}\n"
"QCheckBox::indicator {\n"
"    width: 15px;\n"
"    height: 15px;\n"
"}\n"
"QCheckBox::indicator:unchecked {\n"
"    border: 1px solid #81A1C1;\n"
"    background-color: #2E3440;\n"
"}\n"
"QCheckBox::indicator:checked {\n"
"    background-color: #81A1C1;\n"
"    border: 1px solid #5E81AC;\n"
"}\n"
"\n"
"/* ComboBoxes */\n"
"QComboBox {\n"
"    background-color: #3B4252;\n"
"    color: #ECEFF4;\n"
"    border: 1px solid #81A1C1;\n"
"    border-radius: 3px;\n"
"    paddin"
                        "g: 3px;\n"
"}\n"
"QComboBox QAbstractItemView {\n"
"    background-color: #3B4252;\n"
"    color: #ECEFF4;\n"
"    border: 1px solid #81A1C1;\n"
"}\n"
"\n"
"/* LCD Number */\n"
"QLCDNumber {\n"
"    background-color: #3B4252;\n"
"    color: #81A1C1;\n"
"    border: 2px solid #81A1C1;\n"
"    border-radius: 5px;\n"
"}\n"
"\n"
"/* QPolarChart */\n"
"QPolarChart {\n"
"    background: transparent;\n"
"}\n"
"QPolarChart > .chart-title {\n"
"    color: #ECEFF4;\n"
"    font-size: 14pt;\n"
"    font-weight: bold;\n"
"}\n"
"QPolarChart > .axis-title {\n"
"    color: #D8DEE9;\n"
"}\n"
"\n"
"/* Scrollbars */\n"
"QScrollBar:horizontal, QScrollBar:vertical {\n"
"    border: none;\n"
"    background: #2E3440;\n"
"    width: 8px;\n"
"    margin: 0px;\n"
"}\n"
"QScrollBar::handle:horizontal, QScrollBar::handle:vertical {\n"
"    background: #4C566A;\n"
"    min-width: 20px;\n"
"    min-height: 20px;\n"
"}\n"
"QScrollBar::add-line, QScrollBar::sub-line {\n"
"    background: none;\n"
"    border: none;\n"
"}\n"
"")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.centralwidget.setStyleSheet(u"")
        self.gridLayout = QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.BeamPatternGraph = PolarChartWidget(self.centralwidget)
        self.BeamPatternGraph.setObjectName(u"BeamPatternGraph")

        self.horizontalLayout.addWidget(self.BeamPatternGraph)

        self.WavesGraph = WavesGraph(self.centralwidget)
        self.WavesGraph.setObjectName(u"WavesGraph")

        self.horizontalLayout.addWidget(self.WavesGraph)


        self.gridLayout.addLayout(self.horizontalLayout, 0, 0, 1, 1)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.verticalLayout_4 = QVBoxLayout()
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.horizontalLayout_11 = QHBoxLayout()
        self.horizontalLayout_11.setObjectName(u"horizontalLayout_11")
        self.label_4 = QLabel(self.centralwidget)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setMaximumSize(QSize(16777215, 100))

        self.horizontalLayout_11.addWidget(self.label_4)

        self.steeringAngleSpin = QSpinBox(self.centralwidget)
        self.steeringAngleSpin.setObjectName(u"steeringAngleSpin")

        self.horizontalLayout_11.addWidget(self.steeringAngleSpin)


        self.verticalLayout_4.addLayout(self.horizontalLayout_11)

        self.horizontalLayout_12 = QHBoxLayout()
        self.horizontalLayout_12.setObjectName(u"horizontalLayout_12")
        self.label_7 = QLabel(self.centralwidget)
        self.label_7.setObjectName(u"label_7")
        self.label_7.setMaximumSize(QSize(16777215, 100))

        self.horizontalLayout_12.addWidget(self.label_7)

        self.spacingSpin = QSpinBox(self.centralwidget)
        self.spacingSpin.setObjectName(u"spacingSpin")

        self.horizontalLayout_12.addWidget(self.spacingSpin)


        self.verticalLayout_4.addLayout(self.horizontalLayout_12)


        self.horizontalLayout_2.addLayout(self.verticalLayout_4)

        self.line = QFrame(self.centralwidget)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.Shape.VLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)

        self.horizontalLayout_2.addWidget(self.line)

        self.verticalLayout_6 = QVBoxLayout()
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.curvedCheckBox = QCheckBox(self.centralwidget)
        self.curvedCheckBox.setObjectName(u"curvedCheckBox")

        self.verticalLayout_6.addWidget(self.curvedCheckBox)

        self.horizontalLayout_10 = QHBoxLayout()
        self.horizontalLayout_10.setObjectName(u"horizontalLayout_10")
        self.label_8 = QLabel(self.centralwidget)
        self.label_8.setObjectName(u"label_8")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_8.sizePolicy().hasHeightForWidth())
        self.label_8.setSizePolicy(sizePolicy)
        self.label_8.setMaximumSize(QSize(100, 100))

        self.horizontalLayout_10.addWidget(self.label_8)

        self.radiusSlider = QSlider(self.centralwidget)
        self.radiusSlider.setObjectName(u"radiusSlider")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.radiusSlider.sizePolicy().hasHeightForWidth())
        self.radiusSlider.setSizePolicy(sizePolicy1)
        self.radiusSlider.setMinimumSize(QSize(100, 0))
        self.radiusSlider.setOrientation(Qt.Horizontal)

        self.horizontalLayout_10.addWidget(self.radiusSlider)


        self.verticalLayout_6.addLayout(self.horizontalLayout_10)


        self.horizontalLayout_2.addLayout(self.verticalLayout_6)

        self.line_2 = QFrame(self.centralwidget)
        self.line_2.setObjectName(u"line_2")
        self.line_2.setFrameShape(QFrame.Shape.VLine)
        self.line_2.setFrameShadow(QFrame.Shadow.Sunken)

        self.horizontalLayout_2.addWidget(self.line_2)

        self.verticalLayout_7 = QVBoxLayout()
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.label_5 = QLabel(self.centralwidget)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setMaximumSize(QSize(16777215, 100))

        self.horizontalLayout_3.addWidget(self.label_5)

        self.selectTransmitterComboBox = QComboBox(self.centralwidget)
        self.selectTransmitterComboBox.setObjectName(u"selectTransmitterComboBox")

        self.horizontalLayout_3.addWidget(self.selectTransmitterComboBox)


        self.verticalLayout_7.addLayout(self.horizontalLayout_3)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalLayout_9 = QHBoxLayout()
        self.horizontalLayout_9.setObjectName(u"horizontalLayout_9")
        self.label_10 = QLabel(self.centralwidget)
        self.label_10.setObjectName(u"label_10")
        self.label_10.setMaximumSize(QSize(16777215, 100))

        self.horizontalLayout_9.addWidget(self.label_10)

        self.magnitudeSpin = QSpinBox(self.centralwidget)
        self.magnitudeSpin.setObjectName(u"magnitudeSpin")

        self.horizontalLayout_9.addWidget(self.magnitudeSpin)

        self.horizontalLayout_8 = QHBoxLayout()
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.label_9 = QLabel(self.centralwidget)
        self.label_9.setObjectName(u"label_9")
        self.label_9.setMaximumSize(QSize(16777215, 100))

        self.horizontalLayout_8.addWidget(self.label_9)

        self.frequencySpin = QSpinBox(self.centralwidget)
        self.frequencySpin.setObjectName(u"frequencySpin")

        self.horizontalLayout_8.addWidget(self.frequencySpin)

        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.label_3 = QLabel(self.centralwidget)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setMaximumSize(QSize(16777215, 100))

        self.horizontalLayout_6.addWidget(self.label_3)

        self.phaseShiftSpin = QSpinBox(self.centralwidget)
        self.phaseShiftSpin.setObjectName(u"phaseShiftSpin")

        self.horizontalLayout_6.addWidget(self.phaseShiftSpin)


        self.horizontalLayout_8.addLayout(self.horizontalLayout_6)


        self.horizontalLayout_9.addLayout(self.horizontalLayout_8)


        self.horizontalLayout_4.addLayout(self.horizontalLayout_9)


        self.verticalLayout_7.addLayout(self.horizontalLayout_4)


        self.horizontalLayout_2.addLayout(self.verticalLayout_7)

        self.line_3 = QFrame(self.centralwidget)
        self.line_3.setObjectName(u"line_3")
        self.line_3.setFrameShape(QFrame.Shape.VLine)
        self.line_3.setFrameShadow(QFrame.Shadow.Sunken)

        self.horizontalLayout_2.addWidget(self.line_3)

        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout_7 = QHBoxLayout()
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.label = QLabel(self.centralwidget)
        self.label.setObjectName(u"label")
        self.label.setMaximumSize(QSize(16777215, 100))

        self.horizontalLayout_7.addWidget(self.label)

        self.transmitterNumLCD = QLCDNumber(self.centralwidget)
        self.transmitterNumLCD.setObjectName(u"transmitterNumLCD")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.transmitterNumLCD.sizePolicy().hasHeightForWidth())
        self.transmitterNumLCD.setSizePolicy(sizePolicy2)
        self.transmitterNumLCD.setMinimumSize(QSize(70, 0))
        self.transmitterNumLCD.setMaximumSize(QSize(5000, 50))

        self.horizontalLayout_7.addWidget(self.transmitterNumLCD)


        self.verticalLayout.addLayout(self.horizontalLayout_7)

        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.decreaseNumButton = QPushButton(self.centralwidget)
        self.decreaseNumButton.setObjectName(u"decreaseNumButton")

        self.horizontalLayout_5.addWidget(self.decreaseNumButton)

        self.increaseNumButton = QPushButton(self.centralwidget)
        self.increaseNumButton.setObjectName(u"increaseNumButton")
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.increaseNumButton.sizePolicy().hasHeightForWidth())
        self.increaseNumButton.setSizePolicy(sizePolicy3)
        self.increaseNumButton.setMaximumSize(QSize(16777215, 16777215))

        self.horizontalLayout_5.addWidget(self.increaseNumButton)


        self.verticalLayout.addLayout(self.horizontalLayout_5)


        self.horizontalLayout_2.addLayout(self.verticalLayout)


        self.gridLayout.addLayout(self.horizontalLayout_2, 1, 0, 1, 1)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1218, 34))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.magnitudeSpin.setRange(0, 100)
        self.magnitudeSpin.setValue(50)
        self.frequencySpin.setRange(1, 100)
        self.frequencySpin.setValue(10)
        self.phaseShiftSpin.setRange(0, 360)
        self.steeringAngleSpin.setRange(-90, 90)
        self.spacingSpin.setRange(10, 200)
        self.spacingSpin.setValue(50)
        self.radiusSlider.setRange(10, 200)
        self.radiusSlider.setValue(100)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.label_4.setText(QCoreApplication.translate("MainWindow", u"Steering Angle", None))
        self.label_7.setText(QCoreApplication.translate("MainWindow", u"Spacing", None))
        self.curvedCheckBox.setText(QCoreApplication.translate("MainWindow", u"Curved", None))
        self.label_8.setText(QCoreApplication.translate("MainWindow", u"Radius", None))
        self.label_5.setText(QCoreApplication.translate("MainWindow", u"         Transmitter", None))
        self.label_10.setText(QCoreApplication.translate("MainWindow", u"Magnitude", None))
        self.label_9.setText(QCoreApplication.translate("MainWindow", u"Frequency", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"Phase Shift", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"Num of transmitters", None))
        self.decreaseNumButton.setText(QCoreApplication.translate("MainWindow", u"Decrease", None))
        self.increaseNumButton.setText(QCoreApplication.translate("MainWindow", u"Increase", None))
    # retranslateUi
