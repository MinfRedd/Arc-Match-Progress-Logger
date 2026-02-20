# hotkeys.py

import ctypes
from ctypes import wintypes

MOD_CONTROL = 0x0002
MOD_SHIFT = 0x0004
VK_X = 0x58  # X key
HOTKEY_ID = 1

user32 = ctypes.windll.user32


def start_hotkey_listener(root, toggle_callback):
    if not user32.RegisterHotKey(None, HOTKEY_ID, MOD_CONTROL | MOD_SHIFT, VK_X):
        print("Hotkey registration failed")
        return

    msg = wintypes.MSG()

    while user32.GetMessageW(ctypes.byref(msg), None, 0, 0) != 0:
        if msg.message == 0x0312:  # WM_HOTKEY
            root.after(0, toggle_callback)

    user32.UnregisterHotKey(None, HOTKEY_ID)


def unregister_hotkey():
    try:
        user32.UnregisterHotKey(None, HOTKEY_ID)
    except:
        pass
