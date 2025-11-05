import tkinter as tk
from tkinter import ttk
import binomial_tree as bt

class TreeVisualizer:
	def __init__(self, root, tree: bt.BinomialTree):
		self.canvas = None
		self.root = root
		self.tree = tree
		self.setup_ui()

	def setup_ui(self):
		control_frame = ttk.Frame(self.root, padding="10")
		control_frame.pack(side=tk.TOP, fill=tk.X)

		self.canvas = tk.Canvas(self.root, bg='white', width=1200, height=600)
		self.canvas.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

	def draw_tree(self):
		self.canvas.delete("all")
		if not self.tree:
			return

		x_spacing = 1200 // (self.tree.steps + 1)
		y_spacing = 500 // (self.tree.steps + 1)

		node_positions = {}

		for step in range(len(self.tree.prices)):
			for node in range(len(self.tree.prices[step])):
				x = (step + 1) * x_spacing
				y = 300 + (node - step/2) * y_spacing

				node_positions[(step, node)] = (x, y)
				
				color = 'red' if self.tree.prices[step][node] > self.tree.K else 'green'
				self.canvas.create_oval(x-15, y-15, x+15, y+15, fill=color, outline='black', width=2)
				self.canvas.create_text(x, y, text=f"{self.tree.prices[step][node]:.1f}", font=("Arial", 8))

				if step > 0:
					if node > 0:
						parent_x, parent_y = node_positions[(step-1, node-1)]
						self.canvas.create_line(parent_x, parent_y, x, y, fill='blue', width=1)
					if node < step:
						parent_x, parent_y = node_positions[(step-1, node)]
						self.canvas.create_line(parent_x, parent_y, x, y, fill='blue', width=1)
	def update_display():
		self.draw_tree()