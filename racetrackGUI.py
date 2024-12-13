"""
Create a GUI for drawing racetracks.
"""
from game import Game
from environment import BasicEnv
import tkinter as tk
import random
from PIL import Image, ImageDraw, ImageOps, ImageGrab
import numpy as np
import cv2
import math
import time
import threading
from environment import *
from stable_baselines3 import PPO
import torch

app = None

class RacetrackGUI:
    """
    Create a GUI for drawing racetracks.
    """

    def __init__(self, master):
        self.is_game_started = False
        self.is_track_drawn = False
        self.score = 0.0
        self.game = None
        self.master = master
        self.master.title("Racetrack GUI")
        self.master.geometry("500x500")
        self.image = None
        self.track_width = 35
        self.score_text = None
        self.frame_stack = []  # Frame stack for motion
        self.normalized_matrix = np.zeros((50, 50), dtype=np.uint8)
        self.original_frame = None
        self.prev_dist_from_center = 0
        self.prev_x = 0
        self.prev_y = 0
        self.latest_action = 0
        self.prev_val = 1
        self.temp_count  = 0
        self.state = np.zeros((50, 50, 4), dtype=np.uint8)


        # Initialize drawing state and boundaries
        self.drawing = False
        self.last_x, self.last_y = None, None
        self.min_x, self.min_y = None, None
        self.max_x, self.max_y = None, None

        # Create a canvas for drawing
        self.canvas = tk.Canvas(self.master, width=500, height=500, bg="white")
        self.canvas.pack(fill="both", expand=True)  # Make the canvas fill the window
        # self.train_button = tk.Button(self.master, text="Start Training", command=self.start_training)
        # self.train_button.pack(pady=10)  # Add some padding to separate the button from the canvas

        # Bind mouse events to the canvas
        self.canvas.bind("<Button-1>", self.start_draw)
        self.canvas.bind("<B1-Motion>", self.draw)
        self.canvas.bind("<ButtonRelease-1>", self.stop_draw)

        # Bind keyboard events to the game
        self.master.bind("<space>", self.run_game)
        self.master.bind("<Left>", self.change_direction_left)
        self.master.bind("<Right>", self.change_direction_right)


    def perform_action(self, action):
        if action == 0:
            self.press_left()
        elif action == 1:
            self.press_right()
        else:
            self.go_straight()
        self.update_game()


    def press_left(self):
        self.latest_action = 0
        self.master.event_generate("<KeyPress>", keysym="Left")

    def press_right(self):
        self.latest_action = 1
        self.master.event_generate("<KeyPress>", keysym="Right")


    def go_straight(self):
        self.latest_action = 2


    def  update_matrix(self):
        self.normalized_matrix[self.prev_x][self.prev_y] = self.original_frame[self.prev_x][self.prev_y]
        x = int(self.game.car.position[0])
        y = int(self.game.car.position[1])
        x //= 10
        y //= 10
        self.prev_x = x
        self.prev_y = y
        self.normalized_matrix[x][y] = 0
        # img = Image.fromarray((self.normalized_matrix).astype(np.uint8))  # Assumes frames are normalized [0, 1]
        # img.save(os.path.join('./', f"frame_{self.temp_count}.png"))
        self.temp_count += 1

    def get_canvas_as_matrix_init(self):
        """
        Convert the canvas content to an OpenCV-compatible NumPy array (matrix).
        """
        # Save canvas content to a PostScript file
        ps_filename = "canvas_output.eps"
        self.canvas.postscript(file=ps_filename, colormode="gray")
        print("saved image")
        # Convert the PostScript file to an image
        img = Image.open(ps_filename).convert("L")
        img = img.resize((50, 50), Image.Resampling.LANCZOS)
        # Convert the image to a NumPy array
        matrix = np.array(img, dtype=np.uint8)
        print("in init, size is", matrix.size)
        # matrix.resize(500, 500)

        # Display matrix details
        self.normalized_matrix = matrix
        img = Image.fromarray((self.normalized_matrix).astype(np.uint8))  # Assumes frames are normalized [0, 1]
        img.save(os.path.join('./', f"initial.png"))
        return self.normalized_matrix
        # return matrix

    def stack_frames(self, new_frame, stack_size=4):
        """
        Stack frames to include motion information.
        """
        # Initialize the stack with the first frame if empty
        if len(self.frame_stack) == 0:
            self.frame_stack = [np.copy(new_frame)] * stack_size

        # Add the new frame to the stack
        self.frame_stack.append(np.copy(new_frame))

        # Keep only the last `stack_size` frames
        self.frame_stack = self.frame_stack[-stack_size:]

        # Stack frames along a new axis (channels)
        return np.stack(self.frame_stack, axis=-1)

    def start_draw(self, event):
        """
        Start drawing on the canvas.
        """

        self.drawing = True
        self.last_x, self.last_y = event.x, event.y
        self.min_x, self.min_y = event.x, event.y
        self.max_x, self.max_y = event.x, event.y

    def starting_car_coordinates(self):
        # car_x = (self.min_x + self.max_x) / 2
        # car_y = self.min_y + self.track_width / 2
        car_x = 50
        car_y = 50
        return car_x, car_y

    def draw(self, event):
        """
        Draw on the canvas.
        """

        if self.drawing:
            self.canvas.create_line(
                self.last_x, self.last_y, event.x, event.y, fill="#848484", width=20
            )
            self.last_x, self.last_y = event.x, event.y
            self.min_x = min(self.min_x, event.x)
            self.min_y = min(self.min_y, event.y)
            self.max_x = max(self.max_x, event.x)
            self.max_y = max(self.max_y, event.y)

    def stop_draw(self, event):
        """
        Stop drawing on the canvas.
        """

        self.drawing = False
        if (
            self.min_x is not None
            and self.min_y is not None
            and self.max_x is not None
            and self.max_y is not None
        ):
            self.canvas.delete("all")
        self.canvas.create_oval(
            self.min_x,
            self.min_y,
            self.max_x,
            self.max_y,
            outline="#848484",
            width=self.track_width,
            tags='track_1'
        )
        self.canvas.create_oval(
            self.min_x,
            self.min_y,
            self.max_x,
            self.max_y,
            outline="#848484",
            width=self.track_width,
            tags='track_2'
        )

        # self.canvas.create_oval(
        #     self.min_x,
        #     self.min_y,
        #     self.max_x,
        #     self.max_y,
        #     outline="#848484",
        #     width=self.track_width,
        #     tags='track_1'
        # )
        # self.canvas.create_line(
        #     self.min_x,
        #     self.min_y,
        #     self.max_x,
        #     self.max_y,
        #     # outline="#848484",
        #     width=self.track_width + 100,
        #     fill="gray",
        #     tags='track_2'
        # )
        # self.canvas.create_line(
        #     self.min_x,
        #     self.min_y,
        #     self.max_x,
        #     self.max_y,
        #     # outline="#848484",
        #     width=self.track_width + 100,
        #     fill="gray",
        #     tags='track_1'
        # )

        # Calculate the dimensions for the inner oval
        shrink_factor = self.track_width * 0.50 # Adjust shrink factor as needed
        inner_min_x = self.min_x + shrink_factor
        inner_min_y = self.min_y + shrink_factor
        inner_max_x = self.max_x - shrink_factor
        inner_max_y = self.max_y - shrink_factor

        # Draw the inner oval
        self.canvas.create_oval(
            inner_min_x,
            inner_min_y,
            inner_max_x,
            inner_max_y,
            fill="pink",
            tags='inner_track'
        )
        self.is_track_drawn = True
        
        # matrix = self.get_canvas_as_matrix()
        # print(matrix.tolist())

    def draw_score(self):
        """
        Display the score on the canvas.
        """
        if self.score_text:
            self.canvas.delete(self.score_text)  # Remove the previous score text
        self.score_text = self.canvas.create_text(
            10, 10,  # Position of the text (top-left corner)
            anchor="nw",  # Align text to top-left
            text=f"Score: {self.score:.1f}",
            font=("Arial", 16),
            fill="black",
            tags="score"
        )


    def update_score(self):
        """
        Check for collisions between the car and the racetrack, and updates score
        """
        # Get the car's current bounding box
        car_id = self.canvas.find_withtag("car")[0]
        track_id = self.canvas.find_withtag("track_1")[0]
        car_bbox = self.canvas.bbox(car_id)  # (x1, y1, x2, y2)
        track_bbox = self.canvas.bbox(track_id)

        car_center = ((car_bbox[0]+car_bbox[2])/2, (car_bbox[1]+car_bbox[3])/2)
        track_center = ((track_bbox[0]+track_bbox[2])/2, (track_bbox[1]+track_bbox[3])/2)
        # print(car_center, track_center)
        distance_from_center = math.dist(car_center, track_center)

        # Find overlapping items
        overlapping_items = self.canvas.find_overlapping(*car_bbox)
        if (len(overlapping_items) == 4):
            # on track
            self.score += 0.4
            if (self.latest_action == 2):
                self.score += 0.1
        elif len(overlapping_items) == 2:
            if self.prev_dist_from_center < distance_from_center:
                self.score += 0.01
            else:
                self.score -= 0.50
        else:
            if self.prev_dist_from_center > distance_from_center:
                self.score += 0.01
            else:
                self.score -= 0.50

        self.prev_dist_from_center = distance_from_center
        self.draw_score()


    def run_game(self, event=None):
        """
        Start the game simulation when space is pressed.
        """

        if self.is_game_started:
            return

        self.is_game_started = True
        try:
            self.game = Game()
            car_x, car_y = self.starting_car_coordinates()
            self.game.car.position = (car_x, car_y)

            # Define car dimensions for redrawing
            self.car_width = 15
            self.car_height = 10
            # Start updating the game
            # self.update_game()
            # train_model(app)
            train_thread = threading.Thread(target=train_model, args=(app, ))
            train_thread.start()
        except Exception as e:
            print(f"Error starting the game: {e}")


    def update_game(self):
        """
        Update the game state and redraw the car.
        """
        try:
            # Update the car's position in the game logic
            self.game.car.move()
            new_x, new_y = self.game.car.position

            # Clear previous car position
            self.canvas.delete("car")
            self.canvas.delete("car_hood")
            
            # # Calculate the rotated rectangle corners
            car_width = self.car_width
            car_height = self.car_height
            orientation = self.game.car.orientation
            corners = self.get_rotated_rectangle(new_x, new_y, car_width, car_height, orientation)
            hood_corners = self.get_hood_corners(new_x, new_y, car_width, car_height, orientation)


            # # Draw the rotated rectangle as a polygon
            self.canvas.create_polygon(corners, fill="red", outline="black", tags="car")
            self.canvas.create_polygon(hood_corners, fill="black", outline="black", tags="car_hood")

            # Update the score
            self.update_score()
            self.update_matrix()
            self.state = self.stack_frames(self.normalized_matrix)
            # Schedule the next update
            # self.master.after(25, self.update_game)  # ~40 FPS
        except Exception as e:
            print(f"Error updating the game: {e}")

    def change_direction_left(self, event):
        """
        Change the car's direction to the left.
        """
        if hasattr(self, 'game') and hasattr(self.game, 'car'):
            self.game.car.change_direction('left')

    def change_direction_right(self, event):
        """
        Change the car's direction to the right.
        """
        if hasattr(self, 'game') and hasattr(self.game, 'car'):
            self.game.car.change_direction('right')

    def get_rotated_rectangle(self, cx, cy, width, height, angle):
        """
        Calculate the four corners of a rotated rectangle.

        :param cx: Center x-coordinate
        :param cy: Center y-coordinate
        :param width: Width of the rectangle
        :param height: Height of the rectangle
        :param angle: Rotation angle in degrees
        :return: List of points for the rotated rectangle [x1, y1, x2, y2, ...]
        """
        # Convert angle to radians
        radians = math.radians(angle)

        # Half-dimensions
        dx = width / 2
        dy = height / 2

        # Define unrotated rectangle corners relative to center
        corners = [
            (-dx, -dy),  # Top-left
            (dx, -dy),   # Top-right
            (dx, dy),    # Bottom-right
            (-dx, dy),   # Bottom-left
        ]

        # Apply rotation matrix to each corner
        rotated_corners = []
        for x, y in corners:
            rotated_x = x * math.cos(radians) - y * math.sin(radians) + cx
            rotated_y = x * math.sin(radians) + y * math.cos(radians) + cy
            rotated_corners.extend([rotated_x, rotated_y])

        return rotated_corners

    def get_hood_corners(self, car_x, car_y, car_width, car_height, orientation):
        """
        Calculate the corners of the car's hood.

        :param car_x: Car's x-coordinate
        :param car_y: Car's y-coordinate
        :param car_width: Car's width
        :param car_height: Car's height
        :param orientation: Car's orientation angle in degrees
        :return: List of points for the hood's rotated rectangle [x1, y1, x2, y2, ...]
        """
        hood_width = car_width * 0.4  # Hood is 40% of car width
        hood_height = car_height * 0.8  # Hood is 80% of car height

        # Offset hood position along the orientation angle
        offset_x = (car_height / 2 + hood_height / 2) * math.cos(math.radians(orientation))
        offset_y = (car_height / 2 + hood_height / 2) * math.sin(math.radians(orientation))

        hood_center_x = car_x + offset_x
        hood_center_y = car_y + offset_y

        # Get the rotated rectangle for the hood
        return self.get_rotated_rectangle(hood_center_x, hood_center_y, hood_width, hood_height, orientation)

    def reset_car_position(self):
        # if self.game != None:
        #     self.game.car.reset_car_position()
        # else:
        #     print("nope, none")
        self.normalized_matrix = np.copy(self.original_frame)
        self.game.car.reset_car_position()
 
def train_model(app):
    app.get_canvas_as_matrix_init()
    app.original_frame = np.copy(app.normalized_matrix)
    # Calculate the position for the car on the top center of the track
    car_x, car_y = app.starting_car_coordinates()

    # Draw the car as a small rectangle centered at (car_x, car_y) on the track
    car_width, car_height = 15, 10  # Car size
    app.canvas.create_rectangle(
        car_x - car_width / 2,
        car_y - car_height / 2,
        car_x + car_width / 2,
        car_y + car_height / 2,
        fill="red",
        tags="car"
    )
    app.canvas.create_rectangle(
        car_x - car_width / 2,
        car_y - car_height / 2,
        car_x + car_width / 4,
        car_y + car_height / 2,
        fill="black",
        tags="car"
    )
    print("training...")
    # Check if GPU is available and set the device accordingly
    device = "cuda" if torch.cuda.is_available() else "cpu"
    # Move the model to GPU explicitly
    print(f"Training on device: {device}")

    # Define the RL model
    model = PPO("CnnPolicy", env, verbose=1, device=device)

    # Train the model
    timesteps_per_episode = 3000000
    num_episodes = 1
    for episode in range(num_episodes):
        model.learn(total_timesteps=timesteps_per_episode)
        env.randomize()

    # Save the model
    model.save("basic_env_model")

    # Load the model and test
    model = PPO.load("basic_env_model", env=env)

    obs = env.reset()
    for _ in range(10000):  # Run for 100 steps
        vec_env = model.get_env()
        obs = vec_env.reset()
        action, _ = model.predict(obs)
        obs, reward, done, _, _ = env.step(action)
        print(f"Action: {action}, Reward: {reward}")


root = tk.Tk()
app = RacetrackGUI(root)
from stable_baselines3.common.env_checker import check_env
env = BasicEnv(app)
check_env(env)


if __name__ == "__main__":
    root.mainloop()