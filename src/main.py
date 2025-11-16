from binomial_tree import BinomialTree
from tree_visualizer import TreeVisualizer
import tkinter as tk


if __name__ == "__main__":
	root = tk.Tk()
	root.title("Binomial Tree Pricing Model")
	root.geometry("1200x800")
	
	tree = BinomialTree(S0=150, K=140, T=0.5, r=0.04, sigma=0.25, steps=10, option_type="call", max_steps=50)
	visualizer = TreeVisualizer(root, tree)
	
	root.mainloop()