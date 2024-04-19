def get_position(stepper=stepper):
   return np.array([stepper.get_position(i) for i in stepper.axes()])

def set_position(pos, stepper=stepper):
   for i,p in zip(stepper.axes(), pos):
      stepper.move_absolute(i, p)

from numpy import array

flakes = {
   1: array([-0.371562, -0.028984, -1.127265]),
   2: array([-0.088671, -0.019375, -1.122421]),
   3: array([-0.167499,  0.028828, -1.116015]),
   4: array([ 0.998828,  1.491796, -1.094921]),
   5: array([ 0.962343,  1.452187, -1.094687]),
   6: array([ 0.955078,  1.451874, -1.093984]),
   7: array([ 1.039218,  1.12039 , -1.09789 ])
 }