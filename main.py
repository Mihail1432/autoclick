import tkinter as tk
from tkinter import messagebox
import ctypes
import threading
import time
from PIL import ImageGrab, Image, ImageTk

# Определяем константы и функции Windows API
user32 = ctypes.windll.user32

class AutoClickerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AutoClicker")

        self.window_label = tk.Label(root, text="Select Window:")
        self.window_label.pack(padx=5, pady=5)
        self.window_listbox = tk.Listbox(root)
        self.window_listbox.pack(padx=5, pady=5)

        self.update_windows_button = tk.Button(root, text="Update Windows List", command=self.update_window_list)
        self.update_windows_button.pack(padx=5, pady=5)

        self.select_window_button = tk.Button(root, text="Select", command=self.select_window)
        self.select_window_button.pack(padx=5, pady=5)

        self.interval_label = tk.Label(root, text="Interval (seconds):")
        self.interval_label.pack(padx=5, pady=5)
        self.interval_entry = tk.Entry(root)
        self.interval_entry.pack(padx=5, pady=5)

        self.start_button = tk.Button(root, text="Start", command=self.start_clicking)
        self.start_button.pack(padx=5, pady=5)

        self.stop_button = tk.Button(root, text="Stop", command=self.stop_clicking)
        self.stop_button.pack(padx=5, pady=5)

        self.canvas = tk.Canvas(root, width=800, height=600)
        self.canvas.pack(padx=5, pady=5)

        self.selected_window = None
        self.clicking = False
        self.click_thread = None
        self.click_coordinates = None

        self.update_window_list()

    def update_window_list(self):
        self.window_listbox.delete(0, tk.END)
        self.windows = []  # Список для хранения кортежей (hwnd, window_title)
        user32.EnumWindows(self.enum_windows_callback, ctypes.cast(self.windows, ctypes.POINTER(ctypes.py_object)))
        for win in self.windows:
            self.window_listbox.insert(tk.END, win[1])

    def enum_windows_callback(self, hwnd, lParam):
        if user32.IsWindowVisible(hwnd):
            length = user32.GetWindowTextLengthW(hwnd) + 1
            buffer = ctypes.create_unicode_buffer(length)
            user32.GetWindowTextW(hwnd, buffer, length)
            if buffer.value:
                lParam.append((hwnd, buffer.value))
        return True

    def select_window(self):
        try:
            selected_index = self.window_listbox.curselection()
            if not selected_index:
                messagebox.showerror("Error", "Please select a window")
                return

            hwnd = self.windows[selected_index[0]][0]
            self.selected_window = hwnd
            self.update_canvas()
            self.show_selected_window()

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def show_selected_window(self):
        if self.selected_window:
            self.root.withdraw()  # Скрываем главное окно приложения
            self.show_window_in_new_screen(self.selected_window)

    def show_window_in_new_screen(self, hwnd):
        rect = ctypes.wintypes.RECT()
        user32.GetWindowRect(hwnd, ctypes.byref(rect))
        x, y = rect.left, rect.top
        width, height = rect.right - rect.left, rect.bottom - rect.top

        new_window = tk.Toplevel()
        new_window.geometry(f"{width}x{height}+{x}+{y}")
        new_window.title("Selected Window")
        new_window.attributes("-topmost", True)  # Окно поверх всех других

        canvas = tk.Canvas(new_window, width=width, height=height)
        canvas.pack()
        canvas.create_rectangle(0, 0, width, height, outline='blue', width=2)  # Синий контур окна

        def on_click(event):
            # При клике в окне, рисуем синий кружок и сохраняем координаты
            canvas.create_oval(event.x - 5, event.y - 5, event.x + 5, event.y + 5, fill='blue')
            self.click_coordinates = (event.x, event.y)

        def on_enter_press(event):
            # При нажатии Enter, завершаем выбор окна
            new_window.destroy()
            self.root.deiconify()  # Восстанавливаем отображение главного окна

        canvas.bind("<Button-1>", on_click)
        new_window.bind("<Return>", on_enter_press)

    def update_canvas(self):
        # Обновление холста, если выбрано окно
        if self.selected_window:
            self.canvas.delete("all")
            img = self.capture_window()
            if img:
                self.canvas.create_image(0, 0, anchor=tk.NW, image=img)
                self.canvas.image = img  # Сохраняем ссылку на изображение, чтобы оно не удалилось

    def capture_window(self):
        if self.selected_window:
            rect = ctypes.wintypes.RECT()
            user32.GetWindowRect(self.selected_window, ctypes.byref(rect))
            left, top, right, bottom = rect.left, rect.top, rect.right, rect.bottom
            try:
                screenshot = ImageGrab.grab(bbox=(left, top, right, bottom))
                screenshot.thumbnail((800, 600))
                img = ImageTk.PhotoImage(screenshot)
                return img
            except Exception as e:
                print(f"Error capturing window: {e}")
        return None

    def start_clicking(self):
        if not self.selected_window:
            messagebox.showerror("Error", "Please select a window")
            return

        if self.clicking:
            messagebox.showerror("Error", "Clicking is already in progress")
            return

        interval = self.interval_entry.get()
        try:
            interval = float(interval)
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid interval")
            return

        self.clicking = True
        self.click_thread = threading.Thread(target=self.click_in_window_periodically)
        self.click_thread.start()

    def stop_clicking(self):
        self.clicking = False
        if self.click_thread:
            self.click_thread.join()

    def click_in_window_periodically(self):
        while self.clicking:
            if self.click_coordinates:
                x, y = self.click_coordinates
                self.click_in_window(x, y)
            time.sleep(float(self.interval_entry.get()))

    def click_in_window(self, x, y):
        if self.selected_window:
            rect = ctypes.wintypes.RECT()
            user32.GetWindowRect(self.selected_window, ctypes.byref(rect))
            left, top = rect.left, rect.top
            ctypes.windll.user32.SetCursorPos(left + x, top + y)
            ctypes.windll.user32.mouse_event(2, 0, 0, 0, 0)  # left mouse button down
            ctypes.windll.user32.mouse_event(4, 0, 0, 0, 0)  # left mouse button up

    def on_key_press(self, event):
        if event.keysym == 'F6':
            if self.clicking:
                self.stop_clicking()
            else:
                self.start_clicking()

    def run(self):
        self.root.bind("<KeyPress>", self.on_key_press)
        self.root.mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    app = AutoClickerApp(root)
    app.run()
