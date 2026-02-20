import cv2
import numpy as np
import mss
import time
import os
import pytesseract
import re
from datetime import datetime
import threading


class MatchDetector:

    def __init__(self, callback, is_app_visible_callback):
        self.callback = callback
        self.is_app_visible = is_app_visible_callback
        self.running = False
        self.cooldown_until = 0

        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        ASSETS_DIR = os.path.join(BASE_DIR, "assets")

        self.THRESHOLD = 0.78
        self.CHECK_INTERVAL = 0.5

        SCREEN_WIDTH = 1920
        SCREEN_HEIGHT = 1080

        self.REGIONS = {
            "top_left": (0, 0, int(SCREEN_WIDTH * 0.75), SCREEN_HEIGHT // 2),
            "top_right": (SCREEN_WIDTH // 2, 0, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2),
            "top_middle": (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT),
            "bottom_right": (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2),
        }

        self.TEMPLATES = {
            "currency_icon": ("currency_icon.png", "top_left"),
            "end_round_findings": ("end_round_findings.png", "top_right"),
            "end_round_template2": ("end_round_template2.png", "top_right"),
            "knocked_out_by": ("knocked_out_by.png", "top_right"),
            "ready_up": ("ready_up.png", "bottom_right"),
            "ready": ("ready.png", "top_middle"),
            "show_app": ("show_app_raider.png", "top_right"),
        }

        self.loaded_templates = {}

        for name, (filename, region_name) in self.TEMPLATES.items():
            path = os.path.join(ASSETS_DIR, filename)

            if not os.path.exists(path):
                print(f"[ERROR] Missing asset: {path}")
                continue

            img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
            if img is None:
                print(f"[ERROR] Failed to load: {filename}")
                continue

            self.loaded_templates[name] = {
                "image": img,
                "region": region_name
            }

        print(f"[INIT] Loaded {len(self.loaded_templates)} templates")

        self.previous_state = {}
        self.previous_currency = None

        self.loadout_cost_snapshot = None
        self.loadout_value_snapshot = None

        self.findings_snapshot_taken = False

    def start(self):
        self.running = True
        threading.Thread(target=self._run, daemon=True).start()

    def stop(self):
        self.running = False

    def trigger_cooldown(self, seconds):
        self.cooldown_until = time.time() + seconds

    def get_snapshots(self):
        return self.loadout_cost_snapshot, self.loadout_value_snapshot

    def grab_region(self, sct, region_tuple):
        x, y, w, h = region_tuple
        monitor = {"left": x, "top": y, "width": w, "height": h}
        screenshot = np.array(sct.grab(monitor))
        gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
        return gray

    def match_template(self, screen_img, template_img, template_name=None):

        READY_THRESHOLD = 0.75

        if template_name == "ready":

            best_conf = 0
            best_loc = (0, 0)

            for scale in np.linspace(0.8, 1.2, 9):
                resized = cv2.resize(template_img, None, fx=scale, fy=scale, interpolation=cv2.INTER_LINEAR)

                if resized.shape[0] > screen_img.shape[0] or resized.shape[1] > screen_img.shape[1]:
                    continue

                result = cv2.matchTemplate(screen_img, resized, cv2.TM_CCOEFF_NORMED)
                _, max_val, _, max_loc = cv2.minMaxLoc(result)

                if max_val > best_conf:
                    best_conf = max_val
                    best_loc = max_loc

            detected = best_conf >= READY_THRESHOLD
            return detected, best_conf, best_loc

        result = cv2.matchTemplate(screen_img, template_img, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)
        return max_val >= self.THRESHOLD, max_val, max_loc

    def extract_currency_from_icon(self, screen_img, icon_template):
        detected, _, icon_loc = self.match_template(screen_img, icon_template)

        if not detected:
            return None

        icon_h, icon_w = icon_template.shape
        x, y = icon_loc

        crop_x1 = x + icon_w
        crop_x2 = min(screen_img.shape[1], crop_x1 + 450)

        crop_y1 = max(0, y - 15)
        crop_y2 = min(screen_img.shape[0], y + icon_h + 25)

        crop = screen_img[crop_y1:crop_y2, crop_x1:crop_x2]

        if crop.size == 0:
            return None

        # Increase scaling for better thin digit recognition
        crop = cv2.resize(crop, None, fx=3.0, fy=3.0, interpolation=cv2.INTER_CUBIC)

        # Use adaptive threshold (better for thin 1's)
        crop = cv2.adaptiveThreshold(
            crop,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            31,
            2
        )

        text = pytesseract.image_to_string(
            crop,
            config="--psm 7 -c tessedit_char_whitelist=0123456789,"
        )

        cleaned = re.sub(r"[^\d]", "", text)

        if cleaned:
            return int(cleaned)

        return None

    def detect_findings_text(self, sct):
        region = self.REGIONS["top_right"]
        img = self.grab_region(sct, region)
        text = pytesseract.image_to_string(img)
        return "FINDINGS" in text.upper()

    def detect_raider_text(self, sct):
        region = self.REGIONS["top_right"]
        img = self.grab_region(sct, region)
        text = pytesseract.image_to_string(img)
        return "RAIDER" in text.upper()

    def _run(self):
        with mss.mss() as sct:
            print("[STARTED] Detector running...\n")

            while self.running:

                if time.time() < self.cooldown_until:
                    time.sleep(0.2)
                    continue

                current_state = {}

                for name, data in self.loaded_templates.items():
                    region = self.REGIONS[data["region"]]
                    screen_img = self.grab_region(sct, region)

                    detected, confidence, location = self.match_template(
                        screen_img,
                        data["image"],
                        template_name=name
                    )

                    current_state[name] = detected

                if current_state != self.previous_state:
                    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] STATE CHANGE")
                    for name in current_state:
                        if self.previous_state.get(name) != current_state[name]:
                            status = "DETECTED" if current_state[name] else "LOST"
                            print(f"  - {name}: {status}")

                if current_state.get("ready", False) and not self.previous_state.get("ready", False):
                    if self.previous_currency is not None:
                        cost = self.previous_currency
                        if cost == 100:
                            print("[INFO] Free kit detected (100). Adjusting cost to 0.")
                            cost = 0
                        self.loadout_cost_snapshot = cost
                        print(f"\n[SNAPSHOT] LOADOUT COST LOCKED: {self.loadout_cost_snapshot}")

                if (
                    current_state.get("currency_icon", False)
                    and current_state.get("end_round_findings", False)
                    and self.detect_findings_text(sct)
                    and self.loadout_cost_snapshot is not None
                ):
                    if not self.findings_snapshot_taken:

                        top_left_img = self.grab_region(sct, self.REGIONS["top_left"])
                        currency_now = self.extract_currency_from_icon(
                            top_left_img,
                            self.loaded_templates["currency_icon"]["image"]
                        )

                        if currency_now is not None:
                            self.loadout_value_snapshot = currency_now

                            print("\n================ RUN SNAPSHOT ================")
                            print(f"LOADOUT COST  : {self.loadout_cost_snapshot}")
                            print(f"LOADOUT VALUE : {self.loadout_value_snapshot}")
                            print(f"PROFIT        : {self.loadout_value_snapshot - self.loadout_cost_snapshot}")
                            print("==============================================\n")

                            self.findings_snapshot_taken = True

                if not current_state.get("end_round_findings", False):
                    self.findings_snapshot_taken = False

                if (
                    current_state.get("show_app", False)
                    and not self.previous_state.get("show_app", False)
                ):
                    if self.callback:
                        self.callback("show_app")

                top_left_img = self.grab_region(sct, self.REGIONS["top_left"])
                currency = self.extract_currency_from_icon(
                    top_left_img,
                    self.loaded_templates["currency_icon"]["image"]
                )

                if currency is not None and currency != self.previous_currency:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] LOADOUT VALUE: {currency}")
                    self.previous_currency = currency

                self.previous_state = current_state.copy()
                time.sleep(self.CHECK_INTERVAL)