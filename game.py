from racetrackGUI import app
import math

## Defining our car
class Game:

    class Car:
        #Constructor
        def __init__(self, orientation, VELOCITY=5, HEIGHT = 10, WIDTH = 15):
            self.orientation = orientation ## angle with x-axis
            self.position = (0,0)
            self.VELOCITY = VELOCITY ## pixels/sec
            self.HEIGHT = HEIGHT
            self.WIDTH = WIDTH
            self.DIRECTION_MULTIPLIER = 2
            self.ORIENTATION_DELTA = 5
        #
        def change_direction(self, action): ## Think of whether or not to include steering left/right
            if action == 'left':
                self.orientation += self.ORIENTATION_DELTA
            elif action == 'right':
                self.orientation -= self.ORIENTATION_DELTA

            if self.orientation < 0:
                self.orientation += 360

            if self.orientation >= 360:
                self.orientation -= 360


        def move(self):
            x_direction = self.DIRECTION_MULTIPLIER * math.cos(self.orientation * (math.pi / 180))
            y_direction = self.DIRECTION_MULTIPLIER * math.sin(self.orientation * (math.pi / 180))

            self.position = (self.position[0] + x_direction, self.position[1] + y_direction)

        


    def __init__(self):
        car = self.Car(0)



    

    

