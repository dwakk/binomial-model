# main.py
import tkinter as tk
from config_window import ConfigWindow  # le menu principal

if __name__ == "__main__":
    # Création de la fenêtre principale pour le menu
    root = tk.Tk()
    root.title("Binomial Tree Pricing Model")
    root.geometry("450x450")  # taille adaptée au menu

    # Lancer le menu
    app = ConfigWindow(root)

    # Boucle principale Tkinter
    root.mainloop()

