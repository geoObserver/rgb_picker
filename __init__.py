def classFactory(iface):
    from .rgb_picker import RGBColorPickerPlugin
    return RGBColorPickerPlugin(iface)
