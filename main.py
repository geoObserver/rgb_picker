# -*- coding: utf-8 -*-
import os
#from qgis.PyQt import QtWidgets, QtGui
from PyQt6 import QtWidgets, QtGui
from qgis.core import Qgis
from .color_tool import RGBPickerTool

plugin_dir = os.path.dirname(__file__)

class RGBColorPickerPlugin:
    def __init__(self, iface):
        self.iface = iface
        self.canvas = iface.mapCanvas()
        self.action = None
        self.tool = None
        self.toolbar = None
        self.actions = []

    def initGui(self):
        # Gemeinsame Toolbar suchen oder anlegen
        self.toolbar = self.iface.mainWindow().findChild(QtWidgets.QToolBar, "#geoObserverTools")
        if not self.toolbar:
            self.toolbar = self.iface.addToolBar("#geoObserver Tools")
            self.toolbar.setObjectName("#geoObserverTools")
            self.toolbar.setToolTip("#geoObserver Tools ...")

        # Plugin-Action
        icon_path = os.path.join(plugin_dir, 'logo.png')
        self.action = QtGui.QAction(QtGui.QIcon(icon_path), "RGB Color Picker", self.iface.mainWindow())
        self.action.setCheckable(True)
        self.action.triggered.connect(self.activate_tool)

        self.toolbar.addAction(self.action)
        self.actions.append(self.action)

    def activate_tool(self):
        self.tool = RGBPickerTool(self.canvas)
        self.canvas.setMapTool(self.tool)
        self.iface.messageBar().pushMessage(
            "RGB Color Picker",
            "Click on the map to get RGB-, HEX-, HSV- & CMYK values.",
            level=Qgis.Info
        )

    def unload(self):
        for action in self.actions:
            if self.toolbar:
                self.toolbar.removeAction(action)
        self.actions.clear()
