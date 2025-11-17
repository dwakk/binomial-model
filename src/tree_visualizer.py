import tkinter as tk
from tkinter import ttk
from binomial_tree import BinomialTree
from tooltip import Tooltip

class TreeVisualizer:
	def __init__(self, root, tree: BinomialTree):
		self.canvas = None
		self.root = root
		self.tree = tree

		self.zoom_factor = 1.0
		self.pan_offset_x = 0
		self.pan_offset_y = 0
		self.is_panning = False
		self.last_pan_x = 0
		self.last_pan_y = 0

		self.option_type_var = tk.StringVar(value=self.tree.option_type)
		self.show_stock_var = tk.BooleanVar(value=False)
		self.show_most_likely_path_var = tk.BooleanVar(value=False)
		self.show_profits_var = tk.BooleanVar(value=False)

		self.setup_ui()
		self.update_price_display()
		self.root.after(100, self.draw_tree)

	def setup_ui(self):
		style = ttk.Style()
		style.theme_use("clam")

		style.configure("TScale",
			background="#F9F9F9",
			troughcolor="#E6E6E6",
			sliderrelief="flat",
			troughrelief="flat",
			sliderthickness=16
		)

		control_frame = ttk.Frame(self.root, padding=15)
		control_frame.pack(side=tk.TOP, fill=tk.X)

		for col in range(5):  
			control_frame.columnconfigure(col, weight=1)

		def add_param(parent, label, var, from_, to_, row, col, increment=0.01, tooltip_text=""):
			block = ttk.LabelFrame(parent, text=label, padding=10)
			block.grid(row=row, column=col, sticky="ew", padx=10, pady=5)
			block.columnconfigure(1, weight=1)

			spin = ttk.Spinbox(block, from_=from_, to=to_, textvariable=var, increment=increment, width=6, justify="center", command=self.on_param_change)
			spin.grid(row=0, column=0, padx=(0,5))

			scale = ttk.Scale(block,from_=from_,to=to_,variable=var,command=self.on_param_change,length=150)
			scale.grid(row=0, column=1, sticky="ew")

			icon_container = ttk.Frame(block)
			icon_container.grid(row=0, column=2, padx=(5.0))

			info_label = ttk.Label(icon_container, text="?", cursor="question_arrow", font=("Arial", 10, "bold"), foreground="blue")
			info_label.grid(row=0, column=2, padx=(5.0))
			if tooltip_text:
				Tooltip(info_label, tooltip_text)

		self.s0_var = tk.DoubleVar(value=self.tree.S0)
		self.k_var = tk.DoubleVar(value=self.tree.K)
		self.steps_var = tk.IntVar(value=self.tree.steps)
		self.r_var = tk.DoubleVar(value=self.tree.r)
		self.sigma_var = tk.DoubleVar(value=self.tree.sigma)
		self.T_var = tk.DoubleVar(value=self.tree.T)

		tooltips = {
			"S0": "Initial price of the underlying asset.\nUsually ranges from 50 to 150",
			"K": "Strike price of the option.\nTypical ranges are 50 to 200",
			"Steps": "Number of steps in the binomial tree.\nThe more steps, the more accurate the price will be, but the longer it will take to compute",
			"r": "Annual interest rate of the underlying asset.\nUsually ranges from 1 to 10% (0.01 to 0.1)",
			"σ": "Annual volatility of the underlying asset.\nTypical ranges are 10% to 50% (0.1 to 0.5)",
			"T": "Time to maturity of the option in years.\n1.0 = 1 year, 0.5 = 6 months, etc."
		}

		add_param(control_frame, "Initial Price S0", self.s0_var, 20, 200, row=0, col=0, increment=1, tooltip_text=tooltips["S0"])
		add_param(control_frame, "Strike Price K", self.k_var, 20, 200, row=0, col=1, increment=1, tooltip_text=tooltips["K"])
		add_param(control_frame, "Steps", self.steps_var, 2, self.tree.max_steps, row=0, col=2, increment=1, tooltip_text=tooltips["Steps"])
		add_param(control_frame, "Interest Rate r", self.r_var, 0.01, 0.2, row=1, col=0, increment=0.005, tooltip_text=tooltips["r"])
		add_param(control_frame, "Volatility σ", self.sigma_var, 0.01, 0.5, row=1, col=1, increment=0.005, tooltip_text=tooltips["σ"])
		add_param(control_frame, "Maturity T", self.T_var, 0.05, 3, row=1, col=2, increment=0.05, tooltip_text=tooltips["T"])

		option_frame = ttk.LabelFrame(control_frame, text="Option Type", padding=10)
		option_frame.grid(row=0, column=3, rowspan=2, sticky="nsew", padx=10, pady=5)

		ttk.Radiobutton(option_frame, text="Call option", variable=self.option_type_var, value="call", command=self.on_param_change).grid(row=0, column=0, sticky="w")
		ttk.Radiobutton(option_frame, text="Put option", variable=self.option_type_var, value="put", command=self.on_param_change).grid(row=1, column=0, sticky="w")

		display_frame = ttk.LabelFrame(control_frame, text="Display", padding=10)
		display_frame.grid(row=0, column=4, rowspan=2, sticky="nsew", padx=10, pady=5)

		ttk.Checkbutton(display_frame, text="Show stock prices", variable=self.show_stock_var, command=self.draw_tree).grid(row=0, column=0, sticky="w")
		ttk.Checkbutton(display_frame, text="Show most likely path", variable=self.show_most_likely_path_var, command=self.draw_tree).grid(row=1, column=0, sticky="w")
		ttk.Checkbutton(display_frame, text="Show profits", variable=self.show_profits_var, command=self.draw_tree).grid(row=2, column=0, sticky="w")
		ttk.Button(display_frame, text="Plot convergence", command=self.open_plot_window).grid(row=3, column=0, sticky="w")

		self.price_label = ttk.Label(control_frame, text="Option price: ", font=("Arial", 12, "bold"))
		self.price_label.grid(row=2, column=0, columnspan=3, pady=5, sticky="w")

		self.payoff_label = ttk.Label(control_frame, text="Estimated payoff at T: ", font=("Arial", 12, "bold"))
		self.payoff_label.grid(row=3, column=0, columnspan=3, pady=5, sticky="w")

		zoom_frame = ttk.LabelFrame(control_frame, text="Navigation", padding=10)
		zoom_frame.grid(row=0, column=5, rowspan=2, sticky="nsew", padx=10, pady=5)

		ttk.Button(zoom_frame, text="Zoom -", command=self.zoom_out, width=8).grid(row=0, column=0, padx=2, pady=2)
		ttk.Button(zoom_frame, text="Reset", command=self.zoom_reset, width=8).grid(row=0, column=1, padx=2, pady=2)
		ttk.Button(zoom_frame, text="Zoom +", command=self.zoom_in, width=8).grid(row=1, column=0, padx=2, pady=2)
		ttk.Button(zoom_frame, text="Center", command=self.zoom_center, width=8).grid(row=1, column=1, padx=2, pady=2)

		self.zoom_label = ttk.Label(zoom_frame, text="100%", font=("Arial", 10, "bold"))
		self.zoom_label.grid(row=2, column=0, columnspan=2, pady=5)

		self.canvas = tk.Canvas(self.root, bg='white')
		self.canvas.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

		self.canvas.bind("<Configure>", self.on_resize)
		self.canvas.bind("<ButtonPress-1>", self.on_pan_start)
		self.canvas.bind("<B1-Motion>", self.on_pan_move)
		self.canvas.bind("<ButtonRelease-1>", self.on_pan_end)

		self.root.bind("<Control-plus>", lambda e: self.zoom_in())
		self.root.bind("<Control-equal>", lambda e: self.zoom_in())
		self.root.bind("<Control-minus>", lambda e: self.zoom_out())
		self.root.bind("<Control-0>", lambda e: self.zoom_reset())
		self.root.bind("<Left>", lambda e: self.pan_key(30, 0))
		self.root.bind("<Right>", lambda e: self.pan_key(-30, 0))
		self.root.bind("<Up>", lambda e: self.pan_key(0, 30))
		self.root.bind("<Down>", lambda e: self.pan_key(0, -30))

		self.canvas.config(cursor="fleur")
		self.update_zoom_label()

	def on_color_change(self):
		pass

	def zoom_out(self):
		old_zoom = self.zoom_factor
		self.zoom_factor = max(0.1, self.zoom_factor / 1.2)
		self._apply_zoom_center(old_zoom)

	def zoom_in(self):
		old_zoom = self.zoom_factor
		self.zoom_factor = min(5.0, self.zoom_factor * 1.2)
		self._apply_zoom_center(old_zoom)

	def zoom_reset(self):
		self.zoom_factor = 1.0
		self.pan_offset_x = 0
		self.pan_offset_y = 0
		self.draw_tree()
		self.update_zoom_label()

	def zoom_center(self):
		self.pan_offset_x = 0
		self.pan_offset_y = 0
		self.draw_tree()

	def _apply_zoom_center(self, old_zoom):
		if old_zoom != self.zoom_factor:
			self.draw_tree()
			self.update_zoom_label()

	def update_zoom_label(self):
		self.zoom_label.config(text=f"{int(self.zoom_factor * 100)}%")

	def pan_key(self, dx, dy):
		self.pan_offset_x += dx
		self.pan_offset_y += dy
		self.draw_tree()

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
		if not self.canvas:
			return
		self.canvas.delete("all")

		self.canvas.update_idletasks()
		canvas_width = self.canvas.winfo_width()
		canvas_height = self.canvas.winfo_height()

		if canvas_width <= 10 or canvas_height <= 10:
			return

		if not self.tree:
			return

		base_x_spacing = max(80, canvas_width // (self.tree.steps + 2))
		base_y_spacing = max(60, canvas_height // (self.tree.steps + 2))

		x_spacing = base_x_spacing * self.zoom_factor
		y_spacing = base_y_spacing * self.zoom_factor
		node_radius = min(20, base_x_spacing // 4, base_y_spacing // 4) * self.zoom_factor

		node_positions = {}

		for step in range(len(self.tree.option_values)):
			for node in range(len(self.tree.option_values[step])):
				base_x = (step + 1) * base_x_spacing
				base_y = canvas_height // 2 + (node - step/2) * base_y_spacing

				x = base_x * self.zoom_factor + self.pan_offset_x
				y = base_y * self.zoom_factor + self.pan_offset_y

				y = max(node_radius + 5, min(canvas_height - node_radius - 5, y))

				node_positions[(step, node)] = (x, y)

				option_value = self.tree.option_values[step][node]
				if self.option_type_var.get() == "call":
					color = 'lightgreen' if option_value > 0 else 'lightcoral'
				else:
					color = 'lightblue' if option_value > 0 else 'lightcoral'

				if self.show_profits_var.get():
					profit = self.tree.profit_values[step][node]
					if profit > 0:
						color = 'lightgreen' if self.option_type_var.get() == "call" else 'lightblue'
					else:
						color = 'lightcoral'

				self.canvas.create_oval(x - node_radius, y - node_radius, x + node_radius, y + node_radius, fill=color, outline='black', width=1)
				
				if self.show_profits_var.get():
					self.canvas.create_text(x, y, text=f"{profit:.2f}", font=("Arial", int(max(9, (node_radius // 3))*self.zoom_factor)), fill='black')
				else:
					self.canvas.create_text(x, y, text=f"{option_value:.2f}", font=("Arial", int(max(9, (node_radius // 3))*self.zoom_factor)), fill='black')

				if self.show_stock_var.get():
					stock_price = self.tree.prices[step][node]
					self.canvas.create_text(x, y + node_radius + 12, text=f"{stock_price:.1f}", font=("Arial", int(max(8, (node_radius // 4))*self.zoom_factor)), fill='black')

		for step in range(1, len(self.tree.prices)):
			for node in range(len(self.tree.prices[step])):
				x, y = node_positions[(step, node)]

				if node < step:
					parent_x, parent_y = node_positions[(step - 1, node)]
					self.canvas.create_line(parent_x, parent_y, x, y, fill="blue", width=1)

				if node > 0:
					parent_x, parent_y = node_positions[(step - 1, node - 1)]
					self.canvas.create_line(parent_x, parent_y, x, y, fill="blue", width=1)

		if self.show_most_likely_path_var.get():
			most_likely_path = self.tree.most_likely_path
			for step in range(1, len(most_likely_path)):
				prev_node = most_likely_path[step-1]
				current_node = most_likely_path[step]
				x1, y1 = node_positions[(step-1, prev_node)]
				x2, y2 = node_positions[(step, current_node)]
				self.canvas.create_line(x1, y1, x2, y2, fill="green", width=4)

	def on_param_change(self, event=None):
		current_params = (self.steps_var.set(int(round(self.steps_var.get()))),
		self.s0_var.set(int(round(self.s0_var.get()))),
		self.k_var.set(int(round(self.k_var.get()))),
		self.r_var.set(round(self.r_var.get(), 3)),
		self.sigma_var.set(round(self.sigma_var.get(), 3)),
		self.T_var.set(round(self.T_var.get(), 2)))

		self.tree = BinomialTree(
			S0=max(1, self.s0_var.get()),
			K=max(1, self.k_var.get()),
			T=max(0.05, self.T_var.get()),
			r=max(0.001, self.r_var.get()),
			sigma=max(0.01, self.sigma_var.get()),
			steps=max(1, self.steps_var.get()),
			option_type=self.option_type_var.get(),
			max_steps=self.tree.max_steps
		)

		self.update_price_display()
		self.draw_tree()

	def update_price_display(self):
		self.price_label.config(text=f"Option price: {self.tree.option_price:.2f}")
		self.payoff_label.config(text=f"Estimated payoff at T: {self.tree.most_likely_payoff:.2f} with probability {self.tree.most_likely_prob * 100:.2f}%")

	def on_resize(self, event):
		if hasattr(self, '_resize_after'):
			self.root.after_cancel(self._resize_after)
		self._resize_after = self.root.after(200, self.draw_tree)

	def open_plot_window(self):
		from convergence_plot import ConvergencePlot
		tree_params = {
			'S0': self.tree.S0,
			'K': self.tree.K,
			'T': self.tree.T,
			'r': self.tree.r,
			'sigma': self.tree.sigma,
			'option_type': self.tree.option_type
		}

		self.convergence_plot = ConvergencePlot(self.root, tree_params)