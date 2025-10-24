# -*- coding: utf-8 -*-
# RGB Picker Tool (Qt6/QGIS3.34+)

import os
#from qgis.PyQt import QtGui, QtCore, QtWidgets
from PyQt6 import QtGui, QtCore, QtWidgets
from qgis.gui import QgsMapTool
from qgis.utils import iface
from qgis.core import QgsProject, QgsPointXY

plugin_dir = os.path.dirname(__file__)

class RGBPickerTool(QgsMapTool):
    def __init__(self, canvas):
        super().__init__(canvas)
        self.canvas = canvas

    def rgb_to_cmyk(self, r, g, b):
        if (r, g, b) == (0, 0, 0):
            return 0, 0, 0, 100

        r_prime = r / 255.0
        g_prime = g / 255.0
        b_prime = b / 255.0
        k = 1 - max(r_prime, g_prime, b_prime)
        c = (1 - r_prime - k) / (1 - k) if (1 - k) != 0 else 0
        m = (1 - g_prime - k) / (1 - k) if (1 - k) != 0 else 0
        y = (1 - b_prime - k) / (1 - k) if (1 - k) != 0 else 0
        c = int(round(c * 100, 0))
        m = int(round(m * 100, 0))
        y = int(round(y * 100, 0))
        k = int(round(k * 100, 0))
        return c, m, y, k

    def rgb_to_hcv(self, r, g, b):
        color = QtGui.QColor(r, g, b)
        h = color.hueF()
        v = color.valueF()
        s = color.saturationF()
        c = s * v
        return (int(round(h * 100, 0)), int(round(c * 100, 0)), int(round(v * 100, 0)))

    def rgb_to_hsv(self, r, g, b):
        color = QtGui.QColor(r, g, b)
        h = color.hueF()
        s = color.saturationF()
        v = color.valueF()

        if h < 0:
            h_deg = None
        else:
            h_deg = int(round(h * 360.0, 0))
        return (h_deg, int(round(s * 100, 0)), int(round(v * 100, 0)))

    def canvasReleaseEvent(self, event):
        #screen_point = event.pos()
        screen_point = event.position()
        pixel_ratio = self.canvas.devicePixelRatioF()
        physical_x = int(screen_point.x() * pixel_ratio)
        physical_y = int(screen_point.y() * pixel_ratio)
        image = self.canvas.grab().toImage()

        myEPSG = str(QgsProject.instance().crs().authid()).replace("EPSG:", "")

        if 0 <= physical_x < image.width() and 0 <= physical_y < image.height():
            color = QtGui.QColor(image.pixel(physical_x, physical_y))
            r, g, b = color.red(), color.green(), color.blue()
            myHex = f'#{r:02X}{g:02X}{b:02X}'

            # CMYK
            c, m, y, k = self.rgb_to_cmyk(r, g, b)
            myCMYK = f"{c}%,{m}%,{y}%,{k}%"

            # HSV
            h, s, v = self.rgb_to_hsv(r, g, b)
            myHSV = f"{h if h is not None else 'None'}°, {s}%, {v}%"

            # Map-Koordinaten
            #canvas = iface.mapCanvas()
            #map_point = canvas.getCoordinateTransform().toMapCoordinates(QtCore.QPoint(physical_x, physical_y))
            transform = self.canvas.getCoordinateTransform()
            map_point = transform.toMapPoint(physical_x, physical_y)

            # Info-Dialog
            html = (
                f"<strong>Click-Coordinate:</strong>"
                f"<table>"
                f"<tr><td width=50>Pixel:</td><td>x: {physical_x}, y: {physical_y}</td></tr>"
                f"<tr><td>Real:</td><td>x: {round(map_point.x(),3)}, y: {round(map_point.y(),3)}"
                f"<br>(<a href=https://spatialreference.org/ref/epsg/{myEPSG}>EPSG:{myEPSG}</a>)</td></tr>"
                f"</table><br>"
                f"<strong>Color Values:</strong>"
                f"<table>"
                f"<tr><td width=50><a href=https://en.wikipedia.org/wiki/RGB_color_spaces>RGB:</a></td>"
                f"<td width=150>{r}, {g}, {b}  |  {myHex}</td>"
                f"<td width=80 rowspan=4 style='border:2px solid black; background-color:{myHex};'></td></tr>"
                f"<tr><td><a href=https://en.wikipedia.org/wiki/CMYK_color_model>CMYK:</a></td><td>{myCMYK}</td></tr>"
                f"<tr><td><a href=https://en.wikipedia.org/wiki/HSL_and_HSV>HSV:</a></td><td>{myHSV}</td></tr>"
                f"</table><br><br>"
                f'RGB Color Picker v0.3 (Qt6) &nbsp;–&nbsp; <a href="https://geoobserver.de/qgis-plugins/">Other #geoObserver Tools ...</a>'
            )

            QtWidgets.QMessageBox.information(None, "RGB Color Picker by #geoObserver", html)

        else:
            QtWidgets.QMessageBox.warning(None, "Outside", "Clicked outside the visible map.")
