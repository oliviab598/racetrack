import math
import random

CANVAS_HEIGHT = 500
CANVAS_WIDTH = 500

## Defining our car
class Game:

    class Car:
        #Constructor
        def __init__(self, orientation, VELOCITY=2, HEIGHT = 10, WIDTH = 15):
            self.orientation = orientation ## angle with x-axis
            self.position = (0,0)
            self.VELOCITY = VELOCITY ## pixels/sec
            self.HEIGHT = HEIGHT
            self.WIDTH = WIDTH
            self.DIRECTION_MULTIPLIER = 2
            self.ORIENTATION_DELTA = 15


        def change_direction(self, action): ## Think of whether or not to include steering left/right
            if action == 'right':
                self.orientation += self.ORIENTATION_DELTA
            elif action == 'left':
                self.orientation -= self.ORIENTATION_DELTA

            if self.orientation < 0:
                self.orientation += 360

            if self.orientation >= 360:
                self.orientation -= 360


        def move(self):
            x_direction = self.DIRECTION_MULTIPLIER * math.cos(self.orientation * (math.pi / 180))
            y_direction = self.DIRECTION_MULTIPLIER * math.sin(self.orientation * (math.pi / 180))
            new_x, new_y = self.position[0] + x_direction, self.position[1] + y_direction
            new_x %= CANVAS_WIDTH
            new_y %= CANVAS_HEIGHT
            self.position = (new_x, new_y)

        def reset_car_position(self):
            self.position = (random.randrange(499), random.randrange(499))


    def __init__(self):
        self.car = self.Car(0)



    

    

