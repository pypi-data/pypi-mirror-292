import tkinter as tk
from tkinter import ttk

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Blum Crypto Clicker")
        self.root.configure(bg="black")
        self.root.geometry("300x200")

        self.label = ttk.Label(root, text="Blum Crypto Clicker", foreground="white", background="black")
        self.label.pack(pady=10)

        self.start_button = ttk.Button(root, text="Start Clicker", command=self.start_clicker)
        self.start_button.pack(pady=5)

        self.stop_button = ttk.Button(root, text="Stop Clicker", command=self.stop_clicker)
        self.stop_button.pack(pady=5)

        self.clicker = None

    def start_clicker(self):
        from main import ImageClicker
        self.clicker = ImageClicker()
        self.clicker.start()

    def stop_clicker(self):
        if self.clicker:
            self.clicker.stop()

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
