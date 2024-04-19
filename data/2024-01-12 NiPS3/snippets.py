def get_position(stepper=stepper):
   return np.array([stepper.get_position(i) for i in stepper.axes()])

def set_position(pos, stepper=stepper):
    for i,p in zip(stepper.axes(), pos):
        stepper.move_absolute(i, p)


"""	
image capture settingsfor first temp:
Gain: 	260
Number:	4
flake 1-2:
	exposure:	1/4s
flake 3:
	exposure:	1/5s

"""