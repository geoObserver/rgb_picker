from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction
from qgis.core import Qgis
from .color_tool import RGBPickerTool
import os

plugin_dir = os.path.dirname(__file__)

class RGBColorPickerPlugin:
    def __init__(self, iface):
        self.iface = iface
        self.canvas = iface.mapCanvas()
        self.action = None
        self.tool = None

    def initGui(self):
        icon = os.path.join(os.path.join(plugin_dir, 'logo.png'))
        self.action = QAction(QIcon(icon), "RGB Color Picker", self.iface.mainWindow())
        self.action.setCheckable(True)
        self.action.triggered.connect(self.activate_tool)
        self.iface.addToolBarIcon(self.action)

    def activate_tool(self):
        self.tool = RGBPickerTool(self.canvas)
        self.canvas.setMapTool(self.tool)
        self.iface.messageBar().pushMessage("RGB Color Picker",
            "Click on the map to get RGB-, HEX-, HSV- & CMYK values.", level=Qgis.Info)

    def unload(self):
        self.iface.removeToolBarIcon(self.action)
