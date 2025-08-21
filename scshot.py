import io
from datetime import datetime
from pathlib import Path
import threading
import tkinter as tk
from tkinter import messagebox

import mss
from PIL import Image
import win32clipboard
import winsound
import keyboard

# Kaydedilecek klasör
SAVE_DIR = Path(r"place to save")
SAVE_DIR.mkdir(parents=True, exist_ok=True)

current_hotkey = None
waiting_for_key = False

def copy_image_to_clipboard(img: Image.Image):
    output = io.BytesIO()
    img.convert("RGB").save(output, "BMP")
    data = output.getvalue()[14:]
    output.close()
    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
    win32clipboard.CloseClipboard()

def take_screenshot():
    ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filepath = SAVE_DIR / f"screenshot_{ts}.jpeg"

    with mss.mss() as sct:
        monitor = sct.monitors[0]
        img = sct.grab(monitor)
        # Pillow Image oluştur
        img_pil = Image.frombytes("RGB", img.size, img.rgb)
        # JPEG olarak kaydet
        img_pil.save(filepath, format="JPEG", quality=90)

        # Panoya kopyala
        copy_image_to_clipboard(img_pil)

    try:
        winsound.Beep(1200, 120)
    except:
        pass

    print(f"[✓] Saved and copied: {filepath}")

def on_key(event):
    global current_hotkey, waiting_for_key
    if waiting_for_key:
        current_hotkey = event.scan_code
        waiting_for_key = False
        messagebox.showinfo("Hotkey Set", f"Screenshot key set: {event.name}")
    elif current_hotkey and event.scan_code == current_hotkey:
        take_screenshot()

def listen_keyboard():
    keyboard.hook(on_key)
    keyboard.wait()

def start_gui():
    global waiting_for_key
    root = tk.Tk()
    root.title("Screenshot Tool")
    root.geometry("300x150")

    label = tk.Label(root, text="Click 'Set Hotkey' then press any key:")
    label.pack(pady=10)

    def set_key():
        global waiting_for_key
        waiting_for_key = True
        messagebox.showinfo("Key Binding", "Press any key to set as screenshot key...")

    btn = tk.Button(root, text="Set Hotkey", command=set_key)
    btn.pack(pady=20)

    root.mainloop()

if __name__ == "__main__":
    threading.Thread(target=listen_keyboard, daemon=True).start()
    start_gui()
