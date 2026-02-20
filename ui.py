import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from logic import submit, update_stats_display
import os


def build_ui(root, toggle_window):
    root.title("ARC Match Logger")

    window_width = 900
    window_height = 400

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    center_x = int((screen_width / 2) - (window_width / 2))
    center_y = int((screen_height / 2) - (window_height / 2))

    root.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")
    root.resizable(False, False)
    root.attributes("-topmost", True)

    # ================= BACKGROUND =================

    canvas = tk.Canvas(root, highlightthickness=0)
    canvas.pack(fill="both", expand=True)

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    ASSETS_DIR = os.path.join(BASE_DIR, "assets")
    bg_path = os.path.join(ASSETS_DIR, "background_origin.png")

    bg_image = Image.open(bg_path)
    bg_image = bg_image.resize((window_width, window_height), Image.LANCZOS)

    bg_photo = ImageTk.PhotoImage(bg_image)
    canvas.bg_photo = bg_photo
    canvas.create_image(0, 0, image=bg_photo, anchor="nw")

    # ================= STYLES =================

    style = ttk.Style()
    style.theme_use("clam")

    neon = "#05fa40"

        # ================= VALIDATION =================

    # ================= STRICT MONEY VALIDATION =================

    def validate_money_input(new_value):
        if new_value == "":
            return True  # allow clearing

        suffixes = "kmbKMB"

        # Count suffix letters
        suffix_count = sum(1 for c in new_value if c in suffixes)

        # Only 1 suffix allowed
        if suffix_count > 1:
            root.bell()
            return False

        # If there's a suffix, it must be the LAST character
        if suffix_count == 1:
            if new_value[-1] not in suffixes:
                root.bell()
                return False

        # Everything except last char must be digits
        if new_value[-1] in suffixes:
            number_part = new_value[:-1]
        else:
            number_part = new_value

        if not number_part.isdigit():
            root.bell()
            return False

        return True

    validate_cmd = root.register(validate_money_input)

    style.configure(
        "Green.TCombobox",
        fieldbackground="#0d0d0d",
        background="#0d0d0d",
        foreground=neon,
        arrowcolor=neon,
        bordercolor=neon
    )
    # Force foreground again for safety

    style.configure("Green.TCombobox", foreground=neon)

    # THIS PART FIXES THE INVISIBLE TEXT
    style.map(
        "Green.TCombobox",
        fieldbackground=[("readonly", "#0d0d0d")],
        foreground=[("readonly", neon)],
        selectforeground=[("readonly", neon)],
        selectbackground=[("readonly", "#0d0d0d")]
    )

    font_label = ("Segoe UI", 18)
    font_entry = ("Segoe UI", 14)

    # ================= STROKE TEXT =================

    def create_stroke_text(x, y, text, font, anchor="w", stroke=4):
        for dx in range(-stroke, stroke + 1):
            for dy in range(-stroke, stroke + 1):
                if dx != 0 or dy != 0:
                    canvas.create_text(
                        x + dx, y + dy,
                        text=text,
                        fill="black",
                        font=font,
                        anchor=anchor
                    )

        return canvas.create_text(
            x, y,
            text=text,
            fill=neon,
            font=font,
            anchor=anchor
        )

    def create_label(x, y, text):
        create_stroke_text(x, y, text, font_label, anchor="w", stroke=4)

    # ================= ENTRY WITH PROPER BORDER =================

    def create_bordered_entry(x, y, validate_money=False):
        border_frame = tk.Frame(
            root,
            bg=neon,
            highlightthickness=0
        )

        entry_kwargs = {
            "font": font_entry,
            "justify": "left",
            "bg": "#0d0d0d",
            "fg": neon,
            "insertbackground": neon,
            "relief": "flat",
            "bd": 0,
            "width": 20
        }

        if validate_money:
            entry_kwargs["validate"] = "key"
            entry_kwargs["validatecommand"] = (validate_cmd, "%P")

        entry = tk.Entry(border_frame, **entry_kwargs)

        entry.pack(padx=3, pady=3)
        canvas.create_window(x, y, window=border_frame, anchor="w")

        return entry

    # ================= LEFT COLUMN =================

    left_x = 80

    create_label(left_x, 60, "Loadout Cost")
    cost_entry = create_bordered_entry(left_x, 95, validate_money=True)

    create_label(left_x, 145, "Loadout Value")
    loot_entry = create_bordered_entry(left_x, 180, validate_money=True)

    create_label(left_x, 230, "Notes")
    notes_entry = create_bordered_entry(left_x, 265)

    # ================= RIGHT COLUMN =================

    right_x = 520

    create_label(right_x, 60, "Weapon")

    weapon_var = tk.StringVar()

    combo_border = tk.Frame(
        root,
        bg=neon,
        highlightthickness=0
    )
    # combo box stuff
    # combo box stuff
    weapon_dropdown = ttk.Combobox(
        combo_border,
        textvariable=weapon_var,
        state="readonly",
        values=[
            "Choose Gun",
            "rattler", "stitcher", "ferro", "kettle",
            "bobcat", "tempest", "anvil", "venator",
            "renegade", "burletta", "toro"
        ],
        width=18,
        font=font_entry,
        style="Green.TCombobox"
    )
    # Force internal entry foreground
    weapon_dropdown.configure(foreground=neon)
    weapon_dropdown.pack(padx=3, pady=3)
    canvas.create_window(right_x, 95, window=combo_border, anchor="w")

    # Select first item properly
    print("Value:", weapon_dropdown.get())


    create_label(right_x, 145, "Kills")
    kills_entry = create_bordered_entry(right_x, 180)

    # ================= INITIATED FIGHT =================

    fight_var = tk.BooleanVar()

    fight_checkbox = tk.Checkbutton(
        root,
        variable=fight_var,
        bg="#0d0d0d",
        activebackground="#0d0d0d",
        selectcolor="#0d0d0d",
        fg=neon,
        activeforeground=neon,
        relief="flat",
        bd=0,
        highlightthickness=0
    )

    # Checkbox aligned with Kills input
    canvas.create_window(
        right_x,
        230,
        window=fight_checkbox,
        anchor="w"
    )
    root.after(10, lambda: weapon_dropdown.current(0))
    # Force Tkinter to calculate checkbox width
    root.update_idletasks()

    checkbox_width = fight_checkbox.winfo_width()
    gap = 36  # small space between box and text

    create_stroke_text(
        right_x + checkbox_width + gap,
        230,
        "Initiated Fight?",
        ("Segoe UI", 18, "bold"),
        anchor="w",
        stroke=3
    )

    # ================= CENTER STATS =================

    stats_text = tk.StringVar()
    stats_items = []

    def draw_stats_text(text):
        for item in stats_items:
            canvas.delete(item)
        stats_items.clear()

        x = 300
        y = 30
        stroke = 4
        stroke_color = "black"

        for dx in range(-stroke, stroke + 1):
            for dy in range(-stroke, stroke + 1):
                if dx != 0 or dy != 0:
                    item = canvas.create_text(
                        x + dx, y + dy,
                        text=text,
                        fill=stroke_color,
                        font=("Consolas", 18, "bold"),
                        anchor="nw"
                    )
                    stats_items.append(item)

        main_item = canvas.create_text(
            x, y,
            text=text,
            fill=neon,
            font=("Consolas", 18, "bold"),
            anchor="nw"
        )
        stats_items.append(main_item)

    def update_canvas_stats(*args):
        draw_stats_text(stats_text.get())

    stats_text.trace_add("write", update_canvas_stats)

    # ================= BUTTONS =================

    button_font = ("Segoe UI", 14, "bold")

    def create_bordered_button(x, y, text, command):
        border_frame = tk.Frame(
            root,
            bg=neon,
            highlightthickness=0
        )

        btn = tk.Button(
            border_frame,
            text=text,
            command=command,
            bg="#101010",
            fg=neon,
            activebackground="#101010",
            activeforeground=neon,
            relief="flat",
            bd=0,
            width=10,
            font=button_font
        )

        btn.pack(padx=3, pady=3)
        canvas.create_window(x, y, window=border_frame, anchor="w")

        return btn

    hide_btn = create_bordered_button(520, 330, "Hide", toggle_window)

    submit_btn = create_bordered_button(
        650, 330,
        "Submit",
        lambda: submit(
            cost_entry, loot_entry, kills_entry,
            weapon_dropdown, notes_entry,
            fight_var, stats_text
        )
    )

    update_stats_display(stats_text)

    return cost_entry, loot_entry, kills_entry, stats_text