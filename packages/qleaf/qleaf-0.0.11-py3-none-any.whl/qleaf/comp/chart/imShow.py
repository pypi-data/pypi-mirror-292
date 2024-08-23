# Copyright (C) 2023 Jaehak Lee
import numpy as np
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from ...core.abstract_comp import AbstractComp

class ImShowComp(AbstractComp):
    scrolled = Signal(object)
    mouse_moved = Signal(object)
    mouse_pressed = Signal(object)
    mouse_released = Signal(object)

    def initUI(self):
        self.canvas = FigureCanvasQTAgg(Figure(layout="constrained"))
        self.canvas.mpl_connect('scroll_event', self.scrolled.emit)
        self.canvas.mpl_connect('motion_notify_event', self.mouse_moved.emit)
        self.canvas.mpl_connect('button_press_event', self.mouse_pressed.emit)
        self.canvas.mpl_connect('button_release_event', self.mouse_released.emit)
        self.layout().addWidget(self.canvas)
    
    def updateUI(self):
        data = self.props["data"].get()

        self.canvas.figure.clf()

        len_data = len(data.keys())
        if len_data == 0:
            return
        plots = []
        cols = int(np.ceil(np.sqrt(len_data)))
        rows = int(np.ceil(len_data / cols))
        for i, data_name in enumerate(data.keys()):
            plot = self.canvas.figure.add_subplot(rows, cols, i+1)
            tensor = data[data_name]["data"]
            if len(tensor.shape) == 4:
                tensor = tensor.mean(axis=2).mean(axis=2).real
            elif len(tensor.shape) == 3:
                tensor = tensor.mean(axis=2).real
            elif len(tensor.shape) == 2:
                tensor = tensor.real
            else:
                raise ValueError("Invalid tensor shape")
            plot.imshow(tensor)
            plot.set_title(data_name)
            plots.append(plot)

        self.canvas.draw()




