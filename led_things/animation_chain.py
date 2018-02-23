from animation import Animation

class AnimationChain:
	INFINITE = 0

	animation_chain = None
	repititions = 0
	current_rep	= 0
	current_anim = 0
	done = None

	"""
	to create a chain of animations, first create animations as shown in the animation.py file
	then create a chain like so:
	
	chain = AnimationChain([anim1, anim2, anim3, ...], 3)
	this will create a chain with anim1->anim2->anim3->anim1...
	that will cycle 3 times
	
	specify zero for infinitely repeating
	"""
	def __init__(self, animations=None, repititions=0):
		self.animation_chain = []
		if not animations == None:
			for a in animations:
				self.animation_chain.append(a)

			self.repititions = repititions
			self.current_rep = 0
			self.current_anim = 0

			self.done = False

	# performs an iteration for the animaiton chain
	# returns NONE when the anim is done
	def do_frame(self, delta):
		# check if we are done with the animation
		if self.done:
			return None

		# check if our current animation is done
		if self.animation_chain[self.current_anim].is_animation_done():
			# if done, increment to next anim in chain
			self.current_anim += 1
			
			# if we are at the end of the list...
			if self.current_anim >= len(self.animation_chain):
				# increase our repitition count
				self.current_rep += 1

				# check if we are repeating infinitely (repititions = 0)
				if not self.repititions == AnimationChain.INFINITE:
					# check if we have exceeded our number of repititions
					if self.current_rep > self.repititions:
						self.done = True
						return None

				# reset our current animation
				self.current_anim = 0
				
			# reset the current animation
			self.animation_chain[self.current_anim].reset()

 			# we are at the beginning of the next animation, so return the initial value
			return self.animation_chain[self.current_anim].initial

		# animation is not done, do next frame
		# animation frame returns a tuple of (r,g,b)
		return self.animation_chain[self.current_anim].do_frame(delta)


if __name__ == "__main__":
	print("test of animation chains")

	a1 = Animation(RGB_start=(0,0,0), RGB_end=(255,255,255),duration=1.0)
	a2 = Animation(RGB_start=(255,255,255),RGB_end=(0,0,0),duration=1.0)
	a3 = Animation(RGB_start=(0,0,0),RGB_end=(128,10,50),duration=2.0)
	ac = AnimationChain([a1, a2, a3], 1)

	for frames in range(0, 100):
		print(ac.do_frame(0.25))