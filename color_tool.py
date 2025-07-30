from qgis.PyQt.QtGui import QColor
from qgis.PyQt.QtCore import Qt, QPoint
from qgis.PyQt.QtWidgets import QMessageBox
from qgis.gui import QgsMapTool
from qgis.utils import iface

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
        return int(round(c * 100, 0)), int(round(m * 100, 0)), int(round(y * 100, 0)), int(round(k * 100, 0))

    def canvasReleaseEvent(self, event):
        screen_point = event.pos()
        pixel_ratio = self.canvas.devicePixelRatioF()
        physical_x = int(screen_point.x() * pixel_ratio)
        physical_y = int(screen_point.y() * pixel_ratio)
        image = self.canvas.grab().toImage()
        if 0 <= physical_x < image.width() and 0 <= physical_y < image.height():
            color = QColor(image.pixel(int(physical_x), int(physical_y)))
            r = color.red()
            g = color.green()
            b = color.blue()
            myHex = '#{:02X}{:02X}{:02X}'.format(r, g, b)
            myCMYK = self.rgb_to_cmyk(r, g, b)
            myCMYK = str(myCMYK).replace('(','').replace(')','')
            canvas = iface.mapCanvas()
            screen_point = QPoint(physical_x, physical_y)
            map_point = canvas.getCoordinateTransform().toMapCoordinates(screen_point)
            QMessageBox.information(None, "RGB_Picker by #geoObserver",
                f"<strong>Click-Coordinate:</strong><table><tr><td width=50>Pixel:<td></td>x: {physical_x}, y: {physical_y}</td></tr><tr><td>Real:<td></td>x: {str(round(map_point.x(),3))}, y: {str(round(map_point.y(),3))}</td></tr></table><br><br><strong>ColorValues:</strong><table><tr><td width=50>RGB:<td></td>{r}, {g}, {b}</td>" + 
f'</tr><tr><td>HEX:<td></td>{str(myHex)}</td></tr><tr><td>CMYK:<td></td>{str(myCMYK)}</td></tr></table>')
        else:
            QMessageBox.warning(None, "Outside", "Clicked outside the visible map.")
