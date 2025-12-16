import tkinter as tk
from tkinter import ttk
from binomial_tree import BinomialTree
from tree_visualizer import TreeVisualizer


class ConfigWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Configuration de l'Arbre Binomial")
        self.root.geometry("450x400")
        
        # Centrer la fenêtre
        self.center_window()
        
        # Créer le menu
        self.create_menu()
   
    def center_window(self):
        """Centre la fenêtre sur l'écran"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
   
    def create_menu(self):
        """Crée l'interface du menu de configuration"""
        # Frame principal avec un titre
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Titre
        title_label = ttk.Label(
            main_frame, 
            text="Paramètres de l'Option",
            font=("Arial", 14, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Frame pour les paramètres
        self.menu_frame = ttk.Frame(main_frame)
        self.menu_frame.grid(row=1, column=0, columnspan=2)
      
        # Prix initial
        ttk.Label(self.menu_frame, text="Prix initial S₀ :").grid(
            row=0, column=0, sticky="e", padx=5, pady=5
        )
        self.S0_var = tk.DoubleVar(value=150)
        ttk.Entry(self.menu_frame, textvariable=self.S0_var, width=15).grid(
            row=0, column=1, pady=5
        )
        
        # Strike
        ttk.Label(self.menu_frame, text="Strike K :").grid(
            row=1, column=0, sticky="e", padx=5, pady=5
        )
        self.K_var = tk.DoubleVar(value=140)
        ttk.Entry(self.menu_frame, textvariable=self.K_var, width=15).grid(
            row=1, column=1, pady=5
        )
        
        # Durée
        ttk.Label(self.menu_frame, text="Durée (années) T :").grid(
            row=2, column=0, sticky="e", padx=5, pady=5
        )
        self.T_var = tk.DoubleVar(value=0.5)
        ttk.Entry(self.menu_frame, textvariable=self.T_var, width=15).grid(
            row=2, column=1, pady=5
        )
        
        # Volatilité
        ttk.Label(self.menu_frame, text="Volatilité σ :").grid(
            row=3, column=0, sticky="e", padx=5, pady=5
        )
        self.sigma_var = tk.DoubleVar(value=0.25)
        ttk.Entry(self.menu_frame, textvariable=self.sigma_var, width=15).grid(
            row=3, column=1, pady=5
        )
       
        # Taux d'intérêt
        ttk.Label(self.menu_frame, text="Taux d'intérêt r :").grid(
            row=4, column=0, sticky="e", padx=5, pady=5
        )
        self.r_var = tk.DoubleVar(value=0.04)
        ttk.Entry(self.menu_frame, textvariable=self.r_var, width=15).grid(
            row=4, column=1, pady=5
        )
        
        # Nombre d'étapes
        ttk.Label(self.menu_frame, text="Nombre d'étapes :").grid(
            row=5, column=0, sticky="e", padx=5, pady=5
        )
        self.steps_var = tk.IntVar(value=10)
        ttk.Entry(self.menu_frame, textvariable=self.steps_var, width=15).grid(
            row=5, column=1, pady=5
        )
       
        # Type d'option
        ttk.Label(self.menu_frame, text="Type d'option :").grid(
            row=6, column=0, sticky="e", padx=5, pady=5
        )
        self.option_type_var = tk.StringVar(value="call")
        option_combo = ttk.Combobox(
            self.menu_frame, 
            textvariable=self.option_type_var, 
            values=["call", "put"], 
            state="readonly",
            width=13
        )
        option_combo.grid(row=6, column=1, pady=5)
        
        # Bouton de création
        create_btn = ttk.Button(
            main_frame, 
            text="Créer l'Arbre", 
            command=self.create_tree
        )
        create_btn.grid(row=2, column=0, columnspan=2, pady=20)
        
        # Style pour le bouton (optionnel)
        style = ttk.Style()
        style.configure('TButton', padding=6)
    
    def create_tree(self):
        """Crée l'arbre binomial et ouvre la fenêtre de visualisation"""
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
        
        # Gérer la fermeture de la fenêtre
        self.viewer_window.protocol("WM_DELETE_WINDOW", lambda: self.on_viewer_close())
        
        # # Bouton retour
        # btn_frame = ttk.Frame(self.viewer_window)
        # btn_frame.pack(pady=10)
        
        # ttk.Button(
        #     btn_frame, 
        #     text="← Retour au Menu", 
        #     command=self.return_to_menu
        # ).pack()
        
        # Créer le visualiseur
        self.visualizer = TreeVisualizer(self.viewer_window, tree)
   
    def on_viewer_close(self, viewer_window=None):
        if hasattr(self, 'viewer_window'):
            self.viewer_window.destroy()
        self.root.deiconify()


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
