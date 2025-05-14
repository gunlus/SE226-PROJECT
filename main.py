import tkinter as tk
from gui import AppGUI

if __name__ == "__main__":
    root = tk.Tk()
    root.title("PDA-226: IMDb AI Movie Companion")
    app = AppGUI(root)
    root.mainloop()

