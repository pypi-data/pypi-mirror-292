import os
import sys
import tkinter as tk
from tkinter import ttk
import pyautogui
import threading
import time
from pynput import keyboard
from pynput import mouse
from ttkthemes import ThemedStyle


class AutoClicker:

    def __init__(self, master):
        self.master = master
        self.master.title("Seraphelis Clicker")
        self.master.geometry("400x550")

        self.clicking = False
        self.click_thread = None
        self.hotkey = None
        self.listener = None
        self.click_positions = []

        self.create_widgets()

    def create_widgets(self):
        # Interval input
        interval_frame = ttk.Frame(self.master)
        interval_frame.pack(pady=10)

        ttk.Label(interval_frame, text="Interval:").grid(row=0, column=0, padx=5)

        self.minutes_entry = ttk.Entry(interval_frame, width=5)
        self.minutes_entry.grid(row=0, column=1)
        self.minutes_entry.insert(0, "0")
        ttk.Label(interval_frame, text="min").grid(row=0, column=2, padx=2)

        self.seconds_entry = ttk.Entry(interval_frame, width=5)
        self.seconds_entry.grid(row=0, column=3)
        self.seconds_entry.insert(0, "1")
        ttk.Label(interval_frame, text="sec").grid(row=0, column=4, padx=2)

        self.milliseconds_entry = ttk.Entry(interval_frame, width=5)
        self.milliseconds_entry.grid(row=0, column=5)
        self.milliseconds_entry.insert(0, "0")
        ttk.Label(interval_frame, text="ms").grid(row=0, column=6, padx=2)

        # Click position selection
        position_frame = ttk.Frame(self.master)
        position_frame.pack(pady=10)

        self.position_var = tk.StringVar(value="current")
        ttk.Radiobutton(position_frame, text="Click at current position", variable=self.position_var,
                        value="current").grid(row=0, column=0, columnspan=2, sticky="w")
        ttk.Radiobutton(position_frame, text="Click at fixed positions", variable=self.position_var,
                        value="fixed").grid(row=1, column=0, columnspan=2, sticky="w")

        self.select_position_button = ttk.Button(position_frame, text="Add Position", command=self.select_position)
        self.select_position_button.grid(row=2, column=0, pady=5)

        self.clear_positions_button = ttk.Button(position_frame, text="Clear All", command=self.clear_positions)
        self.clear_positions_button.grid(row=2, column=1, pady=5, padx=5)

        self.positions_listbox = tk.Listbox(position_frame, height=5, width=30)
        self.positions_listbox.grid(row=3, column=0, columnspan=2, pady=5)

        self.delete_position_button = ttk.Button(position_frame, text="Delete Selected",
                                                 command=self.delete_selected_position)
        self.delete_position_button.grid(row=4, column=0, columnspan=2, pady=5)

        # Hotkey selection
        ttk.Label(self.master, text="Select Hotkey:").pack(pady=5)
        self.hotkey_var = tk.StringVar()
        self.hotkey_combo = ttk.Combobox(self.master, textvariable=self.hotkey_var,
                                         values=["Ctrl+F1", "Ctrl+F2", "Ctrl+F3", "Ctrl+F4", "Ctrl+F5"])
        self.hotkey_combo.pack(pady=5)
        self.hotkey_combo.set("Ctrl+F2")  # Default value

        # Apply hotkey button
        self.apply_button = ttk.Button(self.master, text="Apply Hotkey", command=self.apply_hotkey)
        self.apply_button.pack(pady=5)

        # Start/Stop button
        self.toggle_button = ttk.Button(self.master, text="Start", command=self.toggle_clicking)
        self.toggle_button.pack(pady=10)

        # Status label
        self.status_label = ttk.Label(self.master, text="Status: Stopped")
        self.status_label.pack(pady=5)

    def select_position(self):
        self.master.iconify()
        self.status_label.config(text="Click on the desired position...")
        mouse_listener = mouse.Listener(on_click=self.on_click)
        mouse_listener.start()

    def on_click(self, x, y, button, pressed):
        if pressed and button == mouse.Button.left:
            self.click_positions.append((x, y))
            self.update_positions_listbox()
            self.master.deiconify()
            self.status_label.config(text=f"Added position: ({x}, {y})")
            return False  # Stop the listener

    def update_positions_listbox(self):
        self.positions_listbox.delete(0, tk.END)
        for i, pos in enumerate(self.click_positions, 1):
            self.positions_listbox.insert(tk.END, f"{i}. ({pos[0]}, {pos[1]})")

    def clear_positions(self):
        self.click_positions.clear()
        self.update_positions_listbox()
        self.status_label.config(text="Cleared all positions")

    def delete_selected_position(self):
        try:
            selected_index = self.positions_listbox.curselection()[0]
            del self.click_positions[selected_index]
            self.update_positions_listbox()
            self.status_label.config(text=f"Deleted position {selected_index + 1}")
        except IndexError:
            self.status_label.config(text="No position selected")

    def apply_hotkey(self):
        if self.listener:
            self.listener.stop()

        selected_hotkey = self.hotkey_var.get()
        key = selected_hotkey.split("+")[1].lower()
        self.hotkey = f'<ctrl>+<{key}>'

        self.listener = keyboard.GlobalHotKeys({
            self.hotkey: self.toggle_clicking
        })
        self.listener.start()

        self.toggle_button.config(text=f"Start ({selected_hotkey})")
        self.status_label.config(text=f"Hotkey set to {selected_hotkey}")

    def toggle_clicking(self):
        if self.clicking:
            self.stop_clicking()
        else:
            self.start_clicking()

    def start_clicking(self):
        try:
            minutes = int(self.minutes_entry.get())
            seconds = int(self.seconds_entry.get())
            milliseconds = int(self.milliseconds_entry.get())

            total_seconds = minutes * 60 + seconds + milliseconds / 1000

            if total_seconds <= 0:
                raise ValueError("Interval must be positive")

            self.clicking = True
            self.toggle_button.config(text=f"Stop ({self.hotkey_var.get()})")
            self.status_label.config(text="Status: Running")
            self.click_thread = threading.Thread(target=self.auto_click, args=(total_seconds,))
            self.click_thread.start()
        except ValueError as e:
            self.status_label.config(text=f"Error: {str(e)}")

    def stop_clicking(self):
        self.clicking = False
        self.toggle_button.config(text=f"Start ({self.hotkey_var.get()})")
        self.status_label.config(text="Status: Stopped")

    def auto_click(self, interval):
        while self.clicking:
            if self.position_var.get() == "fixed" and self.click_positions:
                for position in self.click_positions:
                    if not self.clicking:
                        break
                    pyautogui.click(position[0], position[1])
                    time.sleep(interval)
            else:
                pyautogui.click()
                time.sleep(interval)

    def on_closing(self):
        self.clicking = False
        if self.listener:
            self.listener.stop()
        self.master.destroy()


def main():
    root = tk.Tk()

    # Get the directory of the script
    if getattr(sys, 'frozen', False):
        # If the application is run as a bundle, use the sys._MEIPASS
        bundle_dir = sys._MEIPASS
    else:
        # Otherwise, use the current directory
        bundle_dir = os.path.dirname(os.path.abspath(__file__))

    icon_path = os.path.join(bundle_dir, "resources", "Seraphelis-nobg.png")

    if os.path.exists(icon_path):
        icon = tk.PhotoImage(file=icon_path)
        root.iconphoto(True, icon)
    else:
        print(f"Warning: Icon file not found at {icon_path}")

    style = ThemedStyle(root)
    style.set_theme("yaru")
    app = AutoClicker(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()