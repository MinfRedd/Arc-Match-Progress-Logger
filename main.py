import tkinter as tk
import threading

from ui import build_ui
from tray import setup_tray
from hotkeys import start_hotkey_listener, unregister_hotkey
from detector import MatchDetector
from logic import initialize
import os
import subprocess

# checking for arc
import os
import subprocess


def launch_arc_if_not_running():
    try:
        result = subprocess.run(
            ["tasklist"],
            capture_output=True,
            text=True
        )

        process_list = result.stdout.lower()

        if "pioneergame.exe" in process_list:
            print("[INFO] ARC Raiders already running.")
            return

        print("[INFO] Launching ARC Raiders via Steam...")
        os.startfile("steam://rungameid/1808500")

    except Exception as e:
        print("[ERROR] Failed to launch ARC Raiders:", e)
def main():
    root = tk.Tk()

    # Auto-launch ARC if needed
    root.after(800, launch_arc_if_not_running)
    
    root.title("ARC Match Logger")

    # Start minimized so Windows registers it without visible flash
    root.iconify()

    # After short delay, fully withdraw
    root.after(150, root.withdraw)

    # Let window register with Windows first
    # root.after(200, root.withdraw)


    # ----------------------------
    # WINDOW STATE CONTROL
    # ----------------------------

    is_visible = False

    def show_window():
        nonlocal is_visible

        root.deiconify()
        root.lift()
        root.focus_force()
        cost_entry.focus_set()

        is_visible = True

    def hide_window():
        nonlocal is_visible

        # IMPORTANT:
        # Minimize first so OBS registers state change
        root.iconify()

        # Then fully withdraw after small delay
        root.after(120, root.withdraw)

        is_visible = False

    def toggle_window():
        if is_visible:
            hide_window()
        else:
            show_window()
            
    cost_entry, loot_entry, kills_entry, stats_text = build_ui(root, toggle_window)

    # ----------------------------
    # CLEAN SHUTDOWN
    # ----------------------------

    def shutdown():
        unregister_hotkey()
        detector.stop()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", shutdown)
    root.bind("<Control-Shift-Q>", lambda e: shutdown())
    root.bind("<Escape>", lambda e: toggle_window())

    # ----------------------------
    # HOTKEY LISTENER THREAD
    # ----------------------------

    threading.Thread(
        target=lambda: start_hotkey_listener(root, toggle_window),
        daemon=True
    ).start()

    # ----------------------------
    # SYSTEM TRAY THREAD
    # ----------------------------

    threading.Thread(
        target=lambda: setup_tray(show_window, shutdown),
        daemon=True
    ).start()

    # ----------------------------
    # DETECTOR CALLBACK
    # ----------------------------

    def detector_callback(state):
        if state == "show_app":

            cost_snapshot, value_snapshot = detector.get_snapshots()

            def safe_ui_update():
                if cost_snapshot is not None:
                    cost_entry.delete(0, "end")
                    cost_entry.insert(0, str(cost_snapshot))

                if value_snapshot is not None:
                    loot_entry.delete(0, "end")
                    loot_entry.insert(0, str(value_snapshot))

                show_window()

            root.after(0, safe_ui_update)

    def is_app_visible():
        return is_visible

    # ----------------------------
    # DETECTOR SETUP
    # ----------------------------

    detector = MatchDetector(
        detector_callback,
        is_app_visible
    )

    initialize(root, detector)

    detector.start()

    cost_entry.focus_set()

    root.mainloop()


if __name__ == "__main__":
    main()