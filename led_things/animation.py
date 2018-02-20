


# performs linear interpolation using supplied animation and frame delta
def linear_interpolation(animation, delta):
	#return v0 + t * (v1 - v0)
	animation.total_time += delta
	scale = animation.total_time / animation.duration

	r = int(animation.initial[0] + scale * animation.step[0])
	g = int(animation.initial[1] + scale * animation.step[1])
	b = int(animation.initial[2] + scale * animation.step[2])

	return (r,g,b)



# defines an animation on an RGB value
# 	has initial and ending conditions
# 	amount of time animation should last
# 	interpolation function that varies between 0 and 1

class Animation:
	initial  = (0,0,0)
	end 	 = (0,0,0)
	step 	 = None #[] # BUG list is being shared here, need to make them specific to instance of animation
					# ^ attempted fix, 2/5/18
	
	duration = 0.0
	total_time = 0.0

	interpolation_func = None


	def __init__(self, RGB_start=(0,0,0), RGB_end=(0,0,0), duration=0.0, interpolation_func=linear_interpolation):
		self.initial = RGB_start #(int(RGB_start[0]),int(RGB_start[1]),int(RGB_start[2]))
		self.end = RGB_end #(int(RGB_end[0]),int(RGB_end[1]),int(RGB_end[2]))

		self.step = (self.end[0] - self.initial[0], self.end[1] - self.initial[1], self.end[2] - self.initial[2])
		#self.step.append(self.end[0] - self.initial[0])
		#self.step.append(self.end[1] - self.initial[1])
		#self.step.append(self.end[2] - self.initial[2])

		#print(self.step)

		self.duration = duration
		self.total_time = 0.0

		self.interpolation_func = interpolation_func

	def do_frame(self, delta):
		if not self.is_animation_done():
			return self.interpolation_func(self,delta)
		return self.end

	def is_animation_done(self):
		if self.total_time >= self.duration:
			return True
		return False

	def reset(self):
		self.total_time = 0.0

if __name__ == "__main__":
	print("testing animation")

	a = Animation((255,255,255),(0,0,0), 3.0)
	for i in range(1,100):
		print(a.do_frame(0.1))
