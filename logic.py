# logic.py

from logger import log_match

# These will be injected from main.py
root_window = None
detector_instance = None

session = {
    "matches": 0,
    "extracts": 0,
    "deaths": 0,
    "profit": 0.0,
    "kills": 0
}


def initialize(root, detector):
    global root_window, detector_instance
    root_window = root
    detector_instance = detector


def parse_value(value: str) -> float:
    try:
        value = value.strip().lower()
        if value == "":
            return 0.0

        multiplier = 1

        if value.endswith("k"):
            multiplier = 1000
            value = value[:-1]
        elif value.endswith("m"):
            multiplier = 1000000
            value = value[:-1]
        elif value.endswith("b"):
            multiplier = 1000000000
            value = value[:-1]

        return float(value) * multiplier
    except:
        return 0.0


def update_stats_display(stats_text):
    matches = session["matches"]
    extracts = session["extracts"]
    deaths = session["deaths"]
    profit = session["profit"]
    kills = session["kills"]

    winrate = (extracts / matches * 100) if matches else 0

    stats_text.set(
        f"Matches: {matches}\n\n"
        f"Extracts: {extracts}\n\n"
        f"Deaths: {deaths}\n\n"
        f"Win Rate: {winrate:.1f}%\n\n"
        f"Total Profit: {profit:,.0f}\n\n"
        f"Total Kills: {kills}"
    )


def reset_session(stats_text):
    session["matches"] = 0
    session["extracts"] = 0
    session["deaths"] = 0
    session["profit"] = 0.0
    session["kills"] = 0
    update_stats_display(stats_text)


def submit(cost_entry, loot_entry, kills_entry,
           weapon_entry, notes_entry, fight_var, stats_text):

    cost = parse_value(cost_entry.get())
    loot_value = parse_value(loot_entry.get())
    kills = int(parse_value(kills_entry.get()))

    profit = loot_value - cost

    weapon = weapon_entry.get().strip() or "Unknown"
    notes = notes_entry.get().strip()
    initiated_fight = "Y" if fight_var.get() else "N"

    died = loot_value == 0

    session["matches"] += 1
    session["profit"] += profit
    session["kills"] += kills

    if died:
        session["deaths"] += 1
    else:
        session["extracts"] += 1

    update_stats_display(stats_text)

    log_match(cost, loot_value, kills, weapon, initiated_fight, notes)

    # CLEAR FIELDS
    cost_entry.delete(0, "end")
    loot_entry.delete(0, "end")
    kills_entry.delete(0, "end")
    weapon_entry.delete(0, "end")
    notes_entry.delete(0, "end")
    fight_var.set(False)

    cost_entry.focus_set()

    # ==========================
    # NEW BEHAVIOR (WHAT WE ADDED)
    # ==========================

    # Hide the window
    if root_window is not None:
        root_window.state("iconic")
        root_window.update()

    # Trigger 30 second cooldown
    if detector_instance is not None:
        detector_instance.trigger_cooldown(30)
