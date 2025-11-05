import math

class BinomialTree:
	def __init__(self, S0, K, T, r, sigma, steps):
		self.S0 = S0
		self.K = K
		self.T = T
		self.r = r
		self.sigma = sigma
		self.steps = steps
		self.calculate_tree_parameters()
		self.calculate_prices()

	def calculate_prices(self):
		self.prices = []
		for step in range(self.steps + 1):
			step_prices = []
			for j in range(step + 1):
				price = self.S0 * (self.u ** (step - j)) * (self.d ** j)
				step_prices.append(price)
			self.prices.append(step_prices)

	def calculate_tree_parameters(self):
		dt = self.T / self.steps
		self.u = math.exp(self.sigma * math.sqrt(dt))
		self.d = 1 / self.u
		self.p = (math.exp(self.r * dt) - self.d) / (self.u - self.d)