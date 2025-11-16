import tkinter as tk
from tkinter import ttk
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from binomial_tree import BinomialTree
import time
from datetime import datetime

class ConvergencePlot:
	def __init__(self, parent, tree_params):
		self.parent = parent
		self.tree_params = tree_params

		self.setup_ui()

	def setup_ui(self):
		self.window = tk.Toplevel(self.parent)
		self.window.title("Convergence Plot")
		self.window.geometry("800x600")

		control_frame = ttk.Frame(self.window, padding=10)
		control_frame.pack(side=tk.TOP, fill=tk.X)

		ttk.Label(control_frame, text="Max steps: ").grid(row=0, column=0, padx=5)
		self.max_steps_var = tk.IntVar(value=100)
		ttk.Spinbox(control_frame, from_=1, to=1000, textvariable=self.max_steps_var, width=5).grid(row=0, column=1, padx=5)

		ttk.Label(control_frame, text="Step size: ").grid(row=0, column=2, padx=5)
		self.step_size_var = tk.IntVar(value=5)
		ttk.Spinbox(control_frame, from_=1, to=100, textvariable=self.step_size_var, width=5).grid(row=0, column=3, padx=5)

		ttk.Button(control_frame, text="Plot", command=self.plot_convergence).grid(row=0, column=4, padx=10)

		ttk.Button(control_frame, text="Export to CSV", command=self.export_data).grid(row=0, column=5, padx=5)

		self.fig = Figure(figsize=(10,6), dpi=100)
		self.ax = self.fig.add_subplot(111)

		self.canvas = FigureCanvasTkAgg(self.fig, master=self.window)
		self.canvas.draw()
		self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)

		self.info_label = ttk.Label(self.window, text="Click on 'Plot' to see the convergence plot")
		self.info_label.pack(side=tk.BOTTOM, pady=10)

	def plot_convergence(self):
		max_steps = self.max_steps_var.get()
		step_size = self.step_size_var.get()
		steps_range = list(range(1, max_steps+1, step_size))

		self.convergence_data = {
			'steps_range': steps_range,
			'binomial_prices': [],
			'bs_prices': [],
			'errors': [],
			'tree_params': self.tree_params.copy(),
			'timestamp': time.time()
		}

		self.info_label.config(text="Calculating...")
		self.window.update()

		start = time.time()

		for steps in steps_range:
			tree = BinomialTree(**self.tree_params, steps=steps)
			option_price = tree.option_price
			bs_price = tree.black_scholes_price()
			self.convergence_data['binomial_prices'].append(option_price)
			self.convergence_data['bs_prices'].append(bs_price)
			self.convergence_data['errors'].append(abs(option_price - bs_price))

		self.ax.clear()
		if hasattr(self, "ax2"):
			self.ax2.remove()

		self.ax2 = self.ax.twinx()

		self.ax.plot(steps_range, self.convergence_data['binomial_prices'], 'b-', label='Binomial price', marker='o', markersize=3)
		self.ax.axhline(y=self.convergence_data['bs_prices'][0], color='r', linestyle='--', label=f'Black-Scholes: {self.convergence_data["bs_prices"][0]:.4f}')

		self.ax2.plot(steps_range, self.convergence_data['errors'], 'g-', linewidth=1, label='Error', alpha=0.7)
		self.ax2.set_ylabel('Error', color='g')
		self.ax2.tick_params(axis='y', labelcolor='g')

		self.ax.set_xlabel("Steps")
		self.ax.set_ylabel("Option price")
		self.ax.set_title("Convergence Plot for the Binomial Tree Pricing Model with Black-Scholes formula")
		self.ax.legend(loc='upper left')
		self.ax.grid(True, alpha=0.3)
		self.ax2.legend(loc='upper right')

		self.fig.tight_layout()
		self.canvas.draw()
		end = time.time()

		self.info_label.config(text=f"Time taken: {end - start:.2f} seconds")

	def export_data(self):
		import csv
		from tkinter import filedialog

		if not self.convergence_data['binomial_prices']:
			self.info_label.config(text="No data to export. Calculate convergence first.")
			return

		filename = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")])

		if filename:
			with open(filename, 'w', newline='') as file:
				writer = csv.writer(file)
				writer.writerow(["# Convergence Analysis - Binomial with Black-Scholes"])
				writer.writerow([f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"])
				writer.writerow([f"# Parameters: S0={self.tree_params['S0']}, K={self.tree_params['K']}, T={self.tree_params['T']}, r={self.tree_params['r']}, sigma={self.tree_params['sigma']}, option_type={self.tree_params['option_type']}"])
				writer.writerow("")
				writer.writerow(['steps', 'binomial_prices', 'bs_prices', 'error', 'relative_error'])
				
				for i, step in enumerate(self.convergence_data['steps_range']):
					binomial = self.convergence_data['binomial_prices'][i]
					bs = self.convergence_data['bs_prices'][i]
					error = self.convergence_data['errors'][i]
					relative_error = error / bs if bs != 0 else 0

					writer.writerow([step, binomial, bs, error, relative_error])

			self.info_label.config(text=f"Data exported to {filename}")