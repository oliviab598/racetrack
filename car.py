

## Defining our car

class car:
    #Constructor
    def __init__(self, orientation, VELOCITY=5, HEIGHT = 10, WIDTH = 15):
        self.orientation = orientation ## angle with x-axis
        self.VELOCITY = VELOCITY ## pixels/sec
        self.HEIGHT = HEIGHT
        self.WIDTH = WIDTH
    #
    def change_direction(self, orientation): ## Think of whether or not to include steering left/right
        self.orientation = orientation

    


    

