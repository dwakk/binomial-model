import tkinter as tk
from tkinter import ttk
import math
from scipy.stats import norm

class BinomialTree:
	def __init__(self, S0, K, T, r, sigma, steps, option_type, max_steps=30):
		self.S0 = S0
		self.K = K
		self.T = T
		self.r = r
		self.sigma = sigma
		self.steps = steps
		self.option_type = option_type
		self.max_steps = max_steps
		self.calculate_tree_parameters()
		self.calculate_prices()
		self.calculate_option_prices()
		self.find_most_likely_path()

	def calculate_prices(self):
		self.prices = []
		for step in range(self.steps + 1):
			step_prices = []
			for j in range(step + 1):
				price = self.S0 * (self.u ** (step - j)) * (self.d ** j)
				step_prices.append(price)
			self.prices.append(step_prices)

	def calculate_tree_parameters(self):
		if self.steps > 0:
			dt = self.T / self.steps
			self.u = math.exp(self.sigma * math.sqrt(dt))
			self.d = 1 / self.u
			self.p = (math.exp(self.r * dt) - self.d) / (self.u - self.d)
			self.discount = math.exp(-self.r * dt)
		else:
			self.u = 1.0
			self.d = 1.0
			self.p = 0.5
			self.discount = 1.0

	def calculate_option_prices(self):
		self.option_values = [[0] * (i+1) for i in range(self.steps + 1)]

		for i in range(self.steps + 1):
			stock_price = self.prices[self.steps][i]
			if self.option_type == "call":
				self.option_values[self.steps][i] = max(0, stock_price - self.K)
			elif self.option_type == "put":
				self.option_values[self.steps][i] = max(0, self.K - stock_price)

		for step in reversed(range(self.steps)):
			for i in range(step + 1):
				self.option_values[step][i] = (self.p * self.option_values[step+1][i] + (1 - self.p) * self.option_values[step+1][i+1]) * self.discount

		self.option_price = self.option_values[0][0]

	def find_most_likely_path(self):
		probs = [[0] * (i+1) for i in range(self.steps + 1)]
		probs[0][0] = 1.0

		for step in range(1, self.steps+1):
			for node in range(step + 1):
				prob = 0
				if node < step:
					prob += probs[step-1][node] * self.p
				if node > 0:
					prob += probs[step-1][node-1] * (1 - self.p)
				probs[step][node] = prob

		path = []
		current_node = probs[self.steps].index(max(probs[self.steps]))
		path.append(current_node)

		for step in reversed(range(1, self.steps+1)):
			prob_from_up = 0
			prob_from_down = 0

			if current_node < step:
				prob_from_up = probs[step-1][current_node] * self.p
			if current_node > 0:
				prob_from_down = probs[step-1][current_node-1] * (1 - self.p)

			if prob_from_up > prob_from_down:
				current_node = current_node
			else:
				current_node -= 1

			path.append(current_node)
		
		self.most_likely_path = list(reversed(path))


	def black_scholes_price(self):
		if self.option_type == "call":
			d1 = (math.log(self.S0 / self.K) + (self.r + self.sigma**2 / 2) * self.T) / (self.sigma * math.sqrt(self.T))
			d2 = d1 - self.sigma * math.sqrt(self.T)
			return self.S0 * norm.cdf(d1) - self.K * math.exp(-self.r * self.T) * norm.cdf(d2)
		else:
			d1 = (math.log(self.S0 / self.K) + (self.r + self.sigma**2 / 2) * self.T) / (self.sigma * math.sqrt(self.T))
			d2 = d1 - self.sigma * math.sqrt(self.T)
			return self.K * math.exp(-self.r * self.T) * norm.cdf(-d2) - self.S0 * norm.cdf(-d1)
class TreeVisualizer:
    def __init__(self, root, tree: BinomialTree):
        self.canvas = None
        self.root = root
        self.tree = tree
        
        # Variables pour le zoom et panning
        self.zoom_factor = 1.0
        self.pan_offset_x = 0
        self.pan_offset_y = 0
        self.is_panning = False
        self.last_pan_x = 0
        self.last_pan_y = 0
        
        self.setup_ui()
        self.root.after(100, self.draw_tree)

    def setup_ui(self):
        style = ttk.Style()
        style.theme_use("clam")

        control_frame = ttk.Frame(self.root, padding=15)
        control_frame.pack(side=tk.TOP, fill=tk.X)

        for col in range(4):  # 4 colonnes maintenant
            control_frame.columnconfigure(col, weight=1)

        def add_param(parent, label, var, from_, to_, row, col, increment=0.01):
            block = ttk.LabelFrame(parent, text=label, padding=10)
            block.grid(row=row, column=col, sticky="ew", padx=10, pady=5)
            block.columnconfigure(1, weight=1)

            spin = ttk.Spinbox(
                block, from_=from_, to=to_,
                textvariable=var,
                increment=increment,
                width=6,
                justify="center",
                command=self.on_param_change
            )
            spin.grid(row=0, column=0, padx=(0,5))

            scale = ttk.Scale(
                block,
                from_=from_,
                to=to_,
                variable=var,
                command=self.on_param_change,
                length=150
            )
            scale.grid(row=0, column=1, sticky="ew")

        self.s0_var = tk.DoubleVar(value=self.tree.S0)
        self.k_var = tk.DoubleVar(value=self.tree.K)
        self.steps_var = tk.IntVar(value=self.tree.steps)
        self.r_var = tk.DoubleVar(value=self.tree.r)
        self.sigma_var = tk.DoubleVar(value=self.tree.sigma)
        self.T_var = tk.DoubleVar(value=self.tree.T)

        add_param(control_frame, "S0", self.s0_var, 20, 200, row=0, col=0, increment=1)
        add_param(control_frame, "Strike K", self.k_var, 20, 200, row=0, col=1, increment=1)
        add_param(control_frame, "Steps", self.steps_var, 2, 50, row=0, col=2, increment=1)

        add_param(control_frame, "Rate r", self.r_var, 0.01, 0.2, row=1, col=0, increment=0.005)
        add_param(control_frame, "Vol σ", self.sigma_var, 0.01, 0.5, row=1, col=1, increment=0.005)
        add_param(control_frame, "Time T", self.T_var, 0.05, 3, row=1, col=2, increment=0.05)

        # CONTROLES DE ZOOM
        zoom_frame = ttk.LabelFrame(control_frame, text="Navigation", padding=10)
        zoom_frame.grid(row=0, column=3, rowspan=2, sticky="nsew", padx=10, pady=5)
        
        ttk.Button(zoom_frame, text="Zoom -", command=self.zoom_out, width=8).grid(row=0, column=0, padx=2, pady=2)
        ttk.Button(zoom_frame, text="Reset", command=self.zoom_reset, width=8).grid(row=0, column=1, padx=2, pady=2)
        ttk.Button(zoom_frame, text="Zoom +", command=self.zoom_in, width=8).grid(row=1, column=0, padx=2, pady=2)
        ttk.Button(zoom_frame, text="Center", command=self.zoom_center, width=8).grid(row=1, column=1, padx=2, pady=2)
        
        self.zoom_label = ttk.Label(zoom_frame, text="100%", font=("Arial", 10, "bold"))
        self.zoom_label.grid(row=2, column=0, columnspan=2, pady=5)

        self.canvas = tk.Canvas(self.root, bg='white')
        self.canvas.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        
        # LIENS DES EVENEMENTS
        self.canvas.bind("<Configure>", self.on_resize)
        self.canvas.bind("<MouseWheel>", self.on_mousewheel)
        self.canvas.bind("<Button-4>", self.on_mousewheel)
        self.canvas.bind("<Button-5>", self.on_mousewheel)
        self.canvas.bind("<ButtonPress-1>", self.on_pan_start)
        self.canvas.bind("<B1-Motion>", self.on_pan_move)
        self.canvas.bind("<ButtonRelease-1>", self.on_pan_end)
        
        # RACCOURCIS CLAVIER
        self.root.bind("<Control-plus>", lambda e: self.zoom_in())
        self.root.bind("<Control-equal>", lambda e: self.zoom_in())  # Pour certains layouts
        self.root.bind("<Control-minus>", lambda e: self.zoom_out())
        self.root.bind("<Control-0>", lambda e: self.zoom_reset())
        self.root.bind("<Left>", lambda e: self.pan_key(30, 0))
        self.root.bind("<Right>", lambda e: self.pan_key(-30, 0))
        self.root.bind("<Up>", lambda e: self.pan_key(0, 30))
        self.root.bind("<Down>", lambda e: self.pan_key(0, -30))
        
        self.canvas.config(cursor="fleur")
        self.update_zoom_label()

    # METHODES DE ZOOM
    def zoom_in(self):
        """Zoom +"""
        old_zoom = self.zoom_factor
        self.zoom_factor = min(5.0, self.zoom_factor * 1.2)
        self._apply_zoom_center(old_zoom)

    def zoom_out(self):
        """Zoom -"""
        old_zoom = self.zoom_factor
        self.zoom_factor = max(0.1, self.zoom_factor / 1.2)
        self._apply_zoom_center(old_zoom)

    def zoom_reset(self):
        """Reset complet"""
        self.zoom_factor = 1.0
        self.pan_offset_x = 0
        self.pan_offset_y = 0
        self.draw_tree()
        self.update_zoom_label()

    def zoom_center(self):
        """Centre la vue"""
        self.pan_offset_x = 0
        self.pan_offset_y = 0
        self.draw_tree()

    def _apply_zoom_center(self, old_zoom):
        """Applique le zoom au centre"""
        if old_zoom != self.zoom_factor:
            self.draw_tree()
            self.update_zoom_label()

    def update_zoom_label(self):
        """Met à jour l'affichage du zoom"""
        percentage = int(self.zoom_factor * 100)
        self.zoom_label.config(text=f"{percentage}%")

    def pan_key(self, dx, dy):
        """Navigation au clavier"""
        self.pan_offset_x += dx
        self.pan_offset_y += dy
        self.draw_tree()

    # METHODES EXISTANTES (gardez votre code)
    def on_mousewheel(self, event):
        zoom_speed = 0.1
        old_zoom = self.zoom_factor
        
        if event.delta > 0 or event.num == 4:
            self.zoom_factor *= (1 + zoom_speed)
        else:
            self.zoom_factor *= (1 - zoom_speed)
        
        self.zoom_factor = max(0.1, min(5.0, self.zoom_factor))
        
        if old_zoom != self.zoom_factor:
            mouse_x = event.x
            mouse_y = event.y
            scale_change = self.zoom_factor / old_zoom
            self.pan_offset_x = mouse_x - (mouse_x - self.pan_offset_x) * scale_change
            self.pan_offset_y = mouse_y - (mouse_y - self.pan_offset_y) * scale_change
            self.draw_tree()
            self.update_zoom_label()

    def on_pan_start(self, event):
        self.is_panning = True
        self.last_pan_x = event.x
        self.last_pan_y = event.y
        self.canvas.config(cursor="hand2")

    def on_pan_move(self, event):
        if self.is_panning:
            dx = event.x - self.last_pan_x
            dy = event.y - self.last_pan_y
            self.pan_offset_x += dx
            self.pan_offset_y += dy
            self.last_pan_x = event.x
            self.last_pan_y = event.y
            self.draw_tree()

    def on_pan_end(self, event):
        self.is_panning = False
        self.canvas.config(cursor="fleur")

    def draw_tree(self):
        # [Votre méthode draw_tree existante...]
        if not hasattr(self, 'canvas') or not self.canvas:
            return
            
        self.canvas.delete("all")
        self.canvas.update_idletasks()
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if canvas_width <= 10 or canvas_height <= 10:
            return

        if not self.tree or not hasattr(self.tree, 'prices') or not self.tree.prices:
            return

        base_x_spacing = max(80, canvas_width // (self.tree.steps + 2))
        base_y_spacing = max(60, canvas_height // (self.tree.steps + 2))
        
        x_spacing = base_x_spacing * self.zoom_factor
        y_spacing = base_y_spacing * self.zoom_factor
        node_radius = min(20, base_x_spacing // 4, base_y_spacing // 4) * self.zoom_factor

        node_positions = {}

        try:
            for step in range(len(self.tree.prices)):
                for node in range(len(self.tree.prices[step])):
                    base_x = (step + 1) * base_x_spacing
                    base_y = canvas_height // 2 + (node - step/2) * base_y_spacing
                    
                    x = base_x * self.zoom_factor + self.pan_offset_x
                    y = base_y * self.zoom_factor + self.pan_offset_y

                    y = max(node_radius + 5, min(canvas_height - node_radius - 5, y))
                    
                    node_positions[(step, node)] = (x, y)
                    
                    color = 'red' if self.tree.prices[step][node] > self.tree.K else 'green'
                    self.canvas.create_oval(x-node_radius, y-node_radius, x+node_radius, y+node_radius, 
                                          fill=color, outline='black', width=1)
                    self.canvas.create_text(x, y, text=f"{self.tree.prices[step][node]:.1f}", 
                                          font=("Arial", max(6, int(node_radius // 3))))

            for step in range(1, len(self.tree.prices)):
                for node in range(len(self.tree.prices[step])):
                    x, y = node_positions[(step, node)]
                    
                    if node < step:
                        parent_x, parent_y = node_positions[(step-1, node)]
                        self.canvas.create_line(parent_x, parent_y, x, y, fill='blue', width=1)
                    
                    if node > 0:
                        parent_x, parent_y = node_positions[(step-1, node-1)]
                        self.canvas.create_line(parent_x, parent_y, x, y, fill='blue', width=1)
                        
        except Exception as e:
            print(f"Erreur dessin: {e}")

    def on_param_change(self, event=None):
        self.zoom_factor = 1.0
        self.pan_offset_x = 0
        self.pan_offset_y = 0
        
        try:
            self.steps_var.set(int(round(self.steps_var.get())))
            self.tree = BinomialTree(
                S0=max(1, self.s0_var.get()),
                K=max(1, self.k_var.get()),
                T=max(0.05, self.T_var.get()),
                r=max(0.001, self.r_var.get()),
                sigma=max(0.01, self.sigma_var.get()),
                steps=max(1, self.steps_var.get()),
				option_type=self.option_type_var.get()
            )
            self.draw_tree()
            self.update_zoom_label()
        except:
            self.root.after(100, self.draw_tree)

    def on_resize(self, event=None):
        if hasattr(self, '_resize_after'):
            self.root.after_cancel(self._resize_after)
        self._resize_after = self.root.after(200, self.draw_tree)


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Binomial Tree Pricing Model")
    root.geometry("1200x800")
    
    tree = BinomialTree(S0=100, K=105, T=1.0, r=0.05, sigma=0.2, steps=5, option_type="call", max_steps=50)
    visualizer = TreeVisualizer(root, tree)
    
    root.mainloop()