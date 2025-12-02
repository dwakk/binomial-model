import tkinter as tk
from tkinter import ttk
from binomial_tree import BinomialTree
from tree_visualizer import TreeVisualizer

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Configuration de l'Arbre Binomial")
        self.create_menu()

    # ---------------- MENU ----------------
    def create_menu(self):
        self.menu_frame = ttk.Frame(self.root, padding=20)
        self.menu_frame.pack()

        # Prix initial
        ttk.Label(self.menu_frame, text="Prix initial S0 :").grid(row=0, column=0, sticky="e")
        self.S0_var = tk.DoubleVar(value=150)
        ttk.Entry(self.menu_frame, textvariable=self.S0_var).grid(row=0, column=1)

        # Strike
        ttk.Label(self.menu_frame, text="Strike K :").grid(row=1, column=0, sticky="e")
        self.K_var = tk.DoubleVar(value=140)
        ttk.Entry(self.menu_frame, textvariable=self.K_var).grid(row=1, column=1)

        # Durée
        ttk.Label(self.menu_frame, text="Durée (années) T :").grid(row=2, column=0, sticky="e")
        self.T_var = tk.DoubleVar(value=0.5)
        ttk.Entry(self.menu_frame, textvariable=self.T_var).grid(row=2, column=1)

        # Volatilité
        ttk.Label(self.menu_frame, text="Volatilité σ :").grid(row=3, column=0, sticky="e")
        self.sigma_var = tk.DoubleVar(value=0.25)
        ttk.Entry(self.menu_frame, textvariable=self.sigma_var).grid(row=3, column=1)

        # Taux
        ttk.Label(self.menu_frame, text="Taux d’intérêt r :").grid(row=4, column=0, sticky="e")
        self.r_var = tk.DoubleVar(value=0.04)
        ttk.Entry(self.menu_frame, textvariable=self.r_var).grid(row=4, column=1)

        # Étapes
        ttk.Label(self.menu_frame, text="Nombre d'étapes :").grid(row=5, column=0, sticky="e")
        self.steps_var = tk.IntVar(value=10)
        ttk.Entry(self.menu_frame, textvariable=self.steps_var).grid(row=5, column=1)

        # Type d’option
        ttk.Label(self.menu_frame, text="Type d’option :").grid(row=6, column=0, sticky="e")
        self.option_type_var = tk.StringVar(value="call")
        ttk.Combobox(self.menu_frame, textvariable=self.option_type_var, values=["call", "put"], state="readonly").grid(row=6, column=1)

        # Bouton pour créer l'arbre
        ttk.Button(self.menu_frame, text="Créer l'Arbre", command=self.create_tree).grid(row=7, column=0, columnspan=2, pady=10)

    # ---------------- CRÉER ARBRE ----------------
    def create_tree(self):
        # Masquer la fenêtre principale
        self.root.withdraw()

        # Créer l'arbre binomial
        tree = BinomialTree(
            S0=self.S0_var.get(),
            K=self.K_var.get(),
            T=self.T_var.get(),
            r=self.r_var.get(),
            sigma=self.sigma_var.get(),
            steps=self.steps_var.get(),
            option_type=self.option_type_var.get(),
            max_steps=50
        )

        # Créer la fenêtre de visualisation
        self.viewer_window = tk.Toplevel(self.root)
        self.viewer_window.title("Visualisation de l'Arbre Binomial")
        self.viewer_window.geometry("1200x800")

        # Bouton Retour
        ttk.Button(self.viewer_window, text="Retour", command=self.return_to_menu).pack(pady=10)

        # Lancer le visualizer
        self.visualizer = TreeVisualizer(self.viewer_window, tree)

    # ---------------- RETOUR AU MENU ----------------
    def return_to_menu(self):
        self.viewer_window.destroy()
        self.root.deiconify()

# ---------------- MAIN ----------------
if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()

