import common as c

class Predictor:
	def __init__(self):
		self.data = []
		self.last_pred = c.WIN_X
		self.pred = 0

	def predict(self, left_data, right_data):
		print("Right data:", right_data)

		pred_paddle_pos = c.WIN_X * max(right_data)/800

		# Stop small gitters
		if ( abs(pred_paddle_pos-self.last_pred/c.WIN_X > 0.1) ):
			# We have made a big change, so its worth updating the position
			self.pred = pred_paddle_pos

		self.last_pred = pred_paddle_pos
		return self.pred