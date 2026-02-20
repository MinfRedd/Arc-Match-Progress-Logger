import gspread
from gspread.utils import ValueInputOption
from google.oauth2.service_account import Credentials
from datetime import datetime
import os


# -----------------------------
# GOOGLE AUTH SETUP
# -----------------------------

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

keys_dir = os.environ.get("KEYS_DIR")

if not keys_dir:
    raise RuntimeError("KEYS_DIR environment variable not set.")

cred_path = os.path.join(keys_dir, "credentials", "credentials.json")

if not os.path.exists(cred_path):
    raise FileNotFoundError(f"Credentials file not found at: {cred_path}")

creds = Credentials.from_service_account_file(
    cred_path,
    scopes=SCOPES
)

client = gspread.authorize(creds)

SPREADSHEET_ID = "1VlU4IgJjKn9-k7MJB7a-mexiE9QkY8jNah54mg6EiS4"

spreadsheet = client.open_by_key(SPREADSHEET_ID)
sheet = spreadsheet.sheet1

print("Connected to spreadsheet:", spreadsheet.url)


# -----------------------------
# LOG MATCH FUNCTION
# -----------------------------

def log_match(cost, loot_value, kills, weapon, initiated_fight, notes):
    try:
        # Only check columns A–H starting from row 2
        data = sheet.get("A2:H")

        next_row = 2

        for i, row in enumerate(data):
            # If row is empty OR all cells are empty
            if not row or all(cell == "" for cell in row):
                next_row = i + 2
                break
        else:
            next_row = len(data) + 2

        raid_number = next_row - 1

        row_data = [
            raid_number,
            weapon,
            cost,
            kills,
            loot_value,
            "",  # Reserved column (F)
            initiated_fight,
            notes
        ]

        sheet.update(
            range_name=f"A{next_row}:H{next_row}",
            values=[row_data],
            value_input_option=ValueInputOption.user_entered
        )

        print(f"[{datetime.now().strftime('%H:%M:%S')}] Match logged.")
        print("Written to row:", next_row)

    except Exception as e:
        print("Failed to log match:", e)


# -----------------------------
# OPTIONAL TEST CALL
# (Delete this block if not needed)
# -----------------------------
if __name__ == "__main__":
    log_match(
        cost=50000,
        loot_value=120000,
        kills=3,
        weapon="AK-74",
        initiated_fight="Yes",
        notes="Test entry"
    )
