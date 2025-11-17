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

		self.profit_values = [[0] * (i+1) for i in range(self.steps + 1)]
		for step in range(self.steps + 1):
			for node in range(step + 1):
				self.profit_values[step][node] = self.option_values[step][node] - self.option_price

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
		self.most_likely_payoff = self.option_values[self.steps][probs[self.steps].index(max(probs[self.steps]))]
		self.most_likely_prob = probs[self.steps][probs[self.steps].index(max(probs[self.steps]))]
		self.most_likely_profit = self.profit_values[self.steps][probs[self.steps].index(max(probs[self.steps]))]
	
	def black_scholes_price(self):
		if self.option_type == "call":
			d1 = (math.log(self.S0 / self.K) + (self.r + self.sigma**2 / 2) * self.T) / (self.sigma * math.sqrt(self.T))
			d2 = d1 - self.sigma * math.sqrt(self.T)
			return self.S0 * norm.cdf(d1) - self.K * math.exp(-self.r * self.T) * norm.cdf(d2)
		else:
			d1 = (math.log(self.S0 / self.K) + (self.r + self.sigma**2 / 2) * self.T) / (self.sigma * math.sqrt(self.T))
			d2 = d1 - self.sigma * math.sqrt(self.T)
			return self.K * math.exp(-self.r * self.T) * norm.cdf(-d2) - self.S0 * norm.cdf(-d1)