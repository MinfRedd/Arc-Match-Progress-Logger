import pystray
from pystray import MenuItem as item
from PIL import Image, ImageDraw


def create_image():
    image = Image.new("RGB", (64, 64), "#111111")
    draw = ImageDraw.Draw(image)
    draw.rectangle((16, 16, 48, 48), fill="#00ff88")
    return image


def setup_tray(show_callback, shutdown_callback):

    def tray_show(icon=None, item=None):
        show_callback()

    def tray_quit(icon, item):
        icon.stop()
        shutdown_callback()

    icon = pystray.Icon(
        "ARC Match Logger",
        create_image(),
        "ARC Match Logger",
        menu=pystray.Menu(
            item("Show", tray_show),
            item("Quit", tray_quit)
        )
    )

    icon.run()