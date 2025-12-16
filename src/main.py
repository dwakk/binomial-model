import tkinter as tk
from config_window import ConfigWindow

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Binomial Tree Pricing Model")
    root.geometry("450x450")

    app = ConfigWindow(root)

    root.mainloop()

