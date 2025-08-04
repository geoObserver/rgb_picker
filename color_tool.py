from qgis.PyQt.QtGui import QColor
from qgis.PyQt.QtCore import Qt, QPoint
from qgis.PyQt.QtWidgets import QMessageBox
from qgis.gui import QgsMapTool
from qgis.utils import iface
from qgis.core import QgsProject

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
        # QColor erwartet Werte zwischen 0–255
        color = QColor(r, g, b)
        # Farbton und Value direkt aus HSV
        h = color.hueF()       # Hue als float [0.0–1.0]
        v = color.valueF()     # Value als float [0.0–1.0]
        s = color.saturationF()# Saturation als float [0.0–1.0]
        # Chroma als Produkt aus Saturation und Value (gängigste Definition)
        c = s * v
        return (int(round(h * 100, 0)), int(round(c * 100, 0)), int(round(v * 100, 0)))
        
    def rgb_to_hsv(self, r, g, b):
        color = QColor(r, g, b)
        h = color.hueF()         # Hue (Farbton) als float [0.0 - 1.0]
        s = color.saturationF()  # Saturation (Sättigung) als float [0.0 - 1.0]
        v = color.valueF()       # Value (Helligkeit) als float [0.0 - 1.0]
        
        if h < 0:
            h_deg = None  # z. B. bei Grau (kein Farbton vorhanden)
        else:
            h_deg = int(round(h * 360.0,0))
        return (h_deg, int(round(s * 100, 0)), int(round(v * 100, 0)))

    def canvasReleaseEvent(self, event):
        screen_point = event.pos()
        pixel_ratio = self.canvas.devicePixelRatioF()
        physical_x = int(screen_point.x() * pixel_ratio)
        physical_y = int(screen_point.y() * pixel_ratio)
        image = self.canvas.grab().toImage()
        myEPSG = str(QgsProject.instance().crs().authid())
        myEPSG = str(myEPSG).replace('EPSG:','')
        if 0 <= physical_x < image.width() and 0 <= physical_y < image.height():
            color = QColor(image.pixel(int(physical_x), int(physical_y)))
            r = color.red()
            g = color.green()
            b = color.blue()
            myHex = '#{:02X}{:02X}{:02X}'.format(r, g, b)
            myCMYK = self.rgb_to_cmyk(r, g, b)
            myCMYK = str(myCMYK).replace('(','').replace(')','')
            myCMYK = "".join(myCMYK)
            myCMYK = str(myCMYK).replace(',','%,') + '%'
            myHSV = self.rgb_to_hsv(r, g, b)
            myHSV = str(myHSV).replace('(','').replace(')','')
            myHSV = "".join(myHSV)
            myHSV = str(myHSV).replace(',','%,') + '%'
            myHSV = str(myHSV).replace('%','°',1)
            myHSV = str(myHSV).replace('None°','None',1)
            canvas = iface.mapCanvas()
            screen_point = QPoint(physical_x, physical_y)
            map_point = canvas.getCoordinateTransform().toMapCoordinates(screen_point)
            QMessageBox.information(None, "RGB Color Picker by #geoObserver",
                f"<strong>Click-Coordinate:</strong><table><tr><td width=50>Pixel:<td></td>x: {physical_x}, y: {physical_y}</td></tr><tr><td>Real:<td></td>x: {str(round(map_point.x(),3))}, y: {str(round(map_point.y(),3))}<br>(<a href=https://spatialreference.org/ref/epsg/{myEPSG}>EPSG:{myEPSG}</a>)</td></tr></table><br><br><strong>ColorValues:</strong><table><tr><td width=50><a href=https://en.wikipedia.org/wiki/RGB_color_spaces>RGB:</a></td><td width=150>{r}, {g}, {b}  |  {str(myHex)}</td><td width=80 rowspan=4 style='Border:2px solid black; background-color:{str(myHex)}';> </td>" + 
f'</tr><tr><td><a href=https://en.wikipedia.org/wiki/CMYK_color_model>CMYK:</a><td></td>{str(myCMYK)}</td></tr><tr><td><a href=https://en.wikipedia.org/wiki/HSL_and_HSV>HSV:</a></td><td width=100>{str(myHSV)}</td></tr><tr><td><br><a href=https://geoobserver.de/qgis-plugin-rgb_picker>more ...</a></td><td></td></tr></table>')
        else:
            QMessageBox.warning(None, "Outside", "Clicked outside the visible map.")
