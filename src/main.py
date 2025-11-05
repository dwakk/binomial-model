import binomial_tree as bt
import tree_visualizer as tv
import tkinter as tk

class MainApp:
	def __init__(self, root):
		self.root = root
		self.tree = bt.BinomialTree(S0=100, K=105, T=1.0, r=0.05, sigma=0.2, steps=5)
		self.visualizer = tv.TreeVisualizer(root, self.tree)

	def run(self):
		self.visualizer.draw_tree()


if __name__ == "__main__":
    root = tk.Tk()
    app = MainApp(root)
    app.run()
    root.mainloop()