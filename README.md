# ARC Match Logger

Desktop overlay match logger for ARC Raiders.

This tool uses OCR and template detection to automatically capture loadout cost and match results, then logs data to Google Sheets while tracking session statistics locally.

---

## ✨ Features

- OCR-based loadout cost detection
- Automatic match snapshot detection
- Steam auto-launch integration
- Google Sheets logging
- Session statistics tracking
- Global hotkey toggle (Ctrl + Shift + X)
- System tray support

---

## 🛠 Requirements

- Windows 10 / 11
- Python 3.10+
- Tesseract OCR installed and added to PATH
- Steam installed
- ARC Raiders installed

---

## 📦 Installation

1. Download or clone this repository.

2. Install dependencies:

   pip install -r requirements.txt

3. Create a Google Service Account and download `credentials.json`.

4. Set a Windows environment variable:

   KEYS_DIR = path_to_your_keys_folder

   (The folder should contain: credentials/credentials.json)

5. Run the application:

   python main.py

---

## 🔐 Security

- Google credentials are NOT stored in this repository.
- Credentials are loaded from an environment variable (`KEYS_DIR`).
- No API keys or private keys are included in source code.

---

## 📄 License

This project is licensed under the MIT License.
