import tkinter as tk
from tkinter import ttk, messagebox
import pyautogui
import threading
import time

class AutoClickerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AutoClicker")

        self.window_label = ttk.Label(root, text="Select Window:")
        self.window_label.grid(row=0, column=0, padx=5, pady=5)

        self.window_listbox = tk.Listbox(root, width=50, height=10)
        self.window_listbox.grid(row=1, column=0, padx=5, pady=5)

        self.update_windows_button = ttk.Button(root, text="Update Windows List", command=self.update_window_list)
        self.update_windows_button.grid(row=2, column=0, padx=5, pady=5)

        self.select_window_button = ttk.Button(root, text="Select", command=self.select_window)
        self.select_window_button.grid(row=3, column=0, padx=5, pady=5)

        self.interval_label = ttk.Label(root, text="Interval (seconds):")
        self.interval_label.grid(row=4, column=0, padx=5, pady=5)

        self.interval_entry = ttk.Entry(root)
        self.interval_entry.grid(row=5, column=0, padx=5, pady=5)

        self.start_button = ttk.Button(root, text="Start Clicking", command=self.start_clicking)
        self.start_button.grid(row=6, column=0, padx=5, pady=5)

        self.stop_button = ttk.Button(root, text="Stop Clicking", command=self.stop_clicking)
        self.stop_button.grid(row=7, column=0, padx=5, pady=5)

        self.clicking = False
        self.click_thread = None
        self.interval = 0.5  # Интервал по умолчанию

        self.update_window_list()

        # Привязываем функцию toggle_clicking к нажатию F6
        self.root.bind('<F6>', self.toggle_clicking)

    def update_window_list(self):
        self.window_listbox.delete(0, tk.END)
        windows = ["Window 1", "Window 2", "Window 3"]  # Пример списка окон, замените на реальный список
        for win in windows:
            self.window_listbox.insert(tk.END, win)

    def select_window(self):
        selected_index = self.window_listbox.curselection()
        if not selected_index:
            messagebox.showerror("Error", "Please select a window")
            return

        window_title = self.window_listbox.get(selected_index)
        messagebox.showinfo("Window Selected", f"Selected window: {window_title}")

    def start_clicking(self):
        if self.clicking:
            messagebox.showinfo("Info", "AutoClicker is already running.")
            return

        interval = self.interval_entry.get()
        try:
            self.interval = float(interval)
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid interval")
            return

        self.clicking = True
        self.click_thread = threading.Thread(target=self.auto_click)
        self.click_thread.start()

    def stop_clicking(self):
        self.clicking = False
        if self.click_thread:
            self.click_thread.join()
            messagebox.showinfo("Info", "AutoClicker stopped.")

    def auto_click(self):
        while self.clicking:
            pyautogui.click()
            time.sleep(self.interval)

    def toggle_clicking(self, event=None):
        if self.clicking:
            self.stop_clicking()
        else:
            self.start_clicking()

if __name__ == "__main__":
    root = tk.Tk()
    app = AutoClickerApp(root)
    root.mainloop()
