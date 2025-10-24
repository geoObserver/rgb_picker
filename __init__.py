# rgb_color_picker/__init__.py
# -*- coding: utf-8 -*-

def classFactory(iface):
    # Qt6 Module explizit importieren bevor das Plugin geladen wird
    from PyQt6 import QtWidgets, QtGui, QtCore
    from .main import RGBColorPickerPlugin
    return RGBColorPickerPlugin(iface)