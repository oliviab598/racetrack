from gymnasium import Env 
from gymnasium import spaces 
import random 
import numpy as np 
from PIL import Image
import os
import cv2

class BasicEnv(Env):
    def __init__(self, app):
        super().__init__()
        # new_frame = app.get_canvas_as_matrix()
        # self.state = app.stack_frames(new_frame)
        self.state = np.zeros((50, 50, 10), dtype=np.uint8)
        self.app = app
        self.total_calls_to_step = 0
        if app.game == None:
            self.car_position = None
        else:
            self.car_position = app.game.car.position
        self.observation_space = spaces.Box(
            0, 255, (50, 50, 10), dtype=np.uint8 # Grayscale image
        )
        self.action_space = spaces.Discrete(3)  # Assume 0 = left, 1 = right, 2 = none

    def step(self, action):
        done = False 
        prev_cumulative_reward = self.app.score
        self.total_calls_to_step += 1
        self.app.perform_action(action)
        self.state = self.app.state
        # new_frame = self.app.get_canvas_as_matrix()
        # Use stack size of 4
        # self.state = self.app.stack_frames(new_frame)
        
        new_cumulative_reward = self.app.score
        # obs, reward, terminated, truncated, info
        # print("reward is ", new_cumulative_reward - prev_cumulative_reward)

        return self.state, new_cumulative_reward - prev_cumulative_reward, False, False, {}
    
    def reset(self, seed=12345):
        return self.state, {}
    
    def randomize(self):
        print("Randomizing car position")
        self.app.reset_car_position()
    
    def render(self, mode="human"):
        pass

    def close(self):
        pass

    def check_done(self):
        return False