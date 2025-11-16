import tkinter as tk
from tkinter import ttk

class Tooltip:
	def __init__(self, widget, text):
		self.widget = widget
		self.text = text
		self.tip_window = None
		self.widget.bind("<Enter>", self.show_tip)
		self.widget.bind("<Leave>", self.hide_tip)

	def show_tip(self, event=None):
		if self.tip_window:
			return
		x, y, _, _ = self.widget.bbox("insert")
		x += self.widget.winfo_rootx() + 25
		y += self.widget.winfo_rooty() + 25

		self.tip_window = tw = tk.Toplevel(self.widget)
		tw.wm_overrideredirect(True)
		tw.wm_geometry(f"+{x}+{y}")
		label = ttk.Label(tw, text=self.text, justify=tk.LEFT, background="#ffffe0", relief=tk.SOLID, borderwidth=1, font=("Arial", 10))
		label.pack()

	def hide_tip(self, event=None):
		if self.tip_window:
			self.tip_window.destroy()
			self.tip_window = None