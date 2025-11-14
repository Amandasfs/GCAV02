# File: app/main.py
import tkinter as tk
from gca_app import GCAApp

def main():
    root = tk.Tk()
    app = GCAApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
