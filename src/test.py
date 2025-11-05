import tkinter as tk
from tkinter import ttk
import math

class BinomialTreeVisualizer:
    def __init__(self, root):
        self.root = root
        self.root.title("Binomial Tree Pricing Model")
        self.root.geometry("1200x800")
        
        # Variables de test
        self.S0 = 100
        self.K = 105
        self.T = 1.0
        self.r = 0.05
        self.sigma = 0.2
        self.steps = 5
        
        self.setup_ui()
        self.draw_test_tree()
    
    def setup_ui(self):
        # Frame de contrôle
        control_frame = ttk.Frame(self.root, padding="10")
        control_frame.pack(side=tk.TOP, fill=tk.X)
        
        # Curseurs pour les paramètres
        ttk.Label(control_frame, text="S0:").grid(row=0, column=0)
        self.s0_var = tk.DoubleVar(value=self.S0)
        ttk.Scale(control_frame, from_=50, to=150, variable=self.s0_var, 
                 command=self.on_parameter_change).grid(row=0, column=1)
        
        ttk.Label(control_frame, text="K:").grid(row=1, column=0)
        self.k_var = tk.DoubleVar(value=self.K)
        ttk.Scale(control_frame, from_=50, to=150, variable=self.k_var,
                 command=self.on_parameter_change).grid(row=1, column=1)
        
        ttk.Label(control_frame, text="Steps:").grid(row=2, column=0)
        self.steps_var = tk.IntVar(value=self.steps)
        ttk.Scale(control_frame, from_=2, to=20, variable=self.steps_var,
                 command=self.on_parameter_change).grid(row=2, column=1)
        
        # Canvas pour l'arbre
        self.canvas = tk.Canvas(self.root, bg='white', width=1200, height=600)
        self.canvas.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
    
    def calculate_tree_parameters(self):
        """Calcule u, d, p pour l'arbre"""
        dt = self.T / self.steps
        self.u = math.exp(self.sigma * math.sqrt(dt))
        self.d = 1 / self.u
        self.p = (math.exp(self.r * dt) - self.d) / (self.u - self.d)
    
    def generate_price_tree(self):
        """Génère les prix de l'arbre binomial"""
        self.prices = []
        for step in range(self.steps + 1):
            step_prices = []
            for j in range(step + 1):
                price = self.S0 * (self.u ** (step - j)) * (self.d ** j)
                step_prices.append(price)
            self.prices.append(step_prices)
    
    def draw_test_tree(self):
        """Dessine un arbre de test simplifié"""
        self.calculate_tree_parameters()
        self.generate_price_tree()
        self.canvas.delete("all")
        
        # Paramètres de dessin
        x_spacing = 1200 // (self.steps + 1)
        y_spacing = 500 // (self.steps + 1)
        
        nodes = {}  # Stocke les positions des nœuds
        
        # Dessine les nœuds et les liens
        for step in range(self.steps + 1):
            for node in range(step + 1):
                x = (step + 1) * x_spacing
                y = 300 + (node - step/2) * y_spacing
                
                # Stocke la position
                nodes[(step, node)] = (x, y)
                
                # Détermine la couleur (rouge si prix > K)
                color = 'red' if self.prices[step][node] > self.K else 'green'
                
                # Dessine le nœud
                self.canvas.create_oval(x-15, y-15, x+15, y+15, 
                                      fill=color, outline='black', width=2)
                
                # Texte du prix
                self.canvas.create_text(x, y, text=f"{self.prices[step][node]:.1f}", 
                                      font=('Arial', 8))
                
                # Dessine les liens avec les nœuds parents
                if step > 0:
                    if node > 0:  # Lien avec parent down
                        parent_x, parent_y = nodes[(step-1, node-1)]
                        self.canvas.create_line(parent_x, parent_y, x, y, 
                                              fill='blue', width=1)
                    if node < step:  # Lien avec parent up  
                        parent_x, parent_y = nodes[(step-1, node)]
                        self.canvas.create_line(parent_x, parent_y, x, y,
                                              fill='blue', width=1)
        
        # Ligne de seuil
        self.canvas.create_line(0, 300, 1200, 300, fill='orange', width=2, dash=(4,2))
        self.canvas.create_text(50, 300, text=f"K={self.K}", fill='orange')
    
    def on_parameter_change(self, event=None):
        """Met à jour l'arbre quand les paramètres changent"""
        self.S0 = self.s0_var.get()
        self.K = self.k_var.get()
        self.steps = self.steps_var.get()
        self.draw_test_tree()

if __name__ == "__main__":
    root = tk.Tk()
    app = BinomialTreeVisualizer(root)
    root.mainloop()