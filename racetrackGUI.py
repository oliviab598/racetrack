"""
Create a GUI for drawing racetracks. 
"""

import tkinter as tk
import random
from PIL import Image, ImageDraw, ImageOps, ImageGrab
import numpy as np
import cv2


class RacetrackGUI:
    """
    Create a GUI for drawing racetracks.
    """

    def __init__(self, master):
        self.master = master
        self.master.title("Racetrack GUI")
        self.master.geometry("500x500")
        self.image = None

        # Create a canvas for drawing
        self.canvas = tk.Canvas(self.master, width=500, height=500, bg="white")
        self.canvas.pack()

        # Initialize drawing state and boundaries
        self.drawing = False
        self.last_x, self.last_y = None, None
        self.min_x, self.min_y = None, None
        self.max_x, self.max_y = None, None

        # Bind mouse events to the canvas
        self.canvas.bind("<Button-1>", self.start_draw)
        self.canvas.bind("<B1-Motion>", self.draw)
        self.canvas.bind("<ButtonRelease-1>", self.stop_draw)

    def get_canvas_as_2d_list(canvas):
        # Save the canvas content to a PostScript file
        ps_filename = "canvas_output.ps"
        canvas.postscript(file=ps_filename, colormode='color')

        # Open the PostScript file and convert it to an image
        img = Image.open(ps_filename)
        img = img.convert("RGB")  # Ensure RGB mode

        # Extract pixel values as a 2D list
        pixels = img.load()
        width, height = img.size

        # Create a 2D list of pixel values
        pixel_values = [[pixels[x, y] for x in range(width)] for y in range(height)]

        return pixel_values
    
    
    def get_canvas_as_matrix(self):
        """
        Convert the canvas content to an OpenCV-compatible NumPy array (matrix).
        """
        # Save canvas content to a PostScript file
        ps_filename = "canvas_output.eps"
        self.canvas.postscript(file=ps_filename, colormode="gray")

        # Convert the PostScript file to an image
        img = Image.open(ps_filename).convert("RGB")

        # Convert the image to a NumPy array
        matrix = np.array(img)

        # Display matrix details
        print(f"Canvas converted to matrix with shape: {matrix.shape}")

        # Save the matrix as a PNG file using OpenCV
        cv2.imwrite("racetrack_matrix.png", cv2.cvtColor(matrix, cv2.COLOR_RGB2BGR))
        print("Matrix saved as racetrack_matrix.png")

        return matrix
    
    def start_draw(self, event):
        """
        Start drawing on the canvas.
        """

        self.drawing = True
        self.last_x, self.last_y = event.x, event.y
        self.min_x, self.min_y = event.x, event.y
        self.max_x, self.max_y = event.x, event.y

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
        track_width = 20
        self.canvas.create_oval(
            self.min_x,
            self.min_y,
            self.max_x,
            self.max_y,
            outline="#848484",
            width=track_width,
        )

        # Calculate the position for the car on the top center of the track
        car_x = (self.min_x + self.max_x) / 2  # Center x of the oval
        car_y = self.min_y + track_width / 2

        # Draw the car as a small rectangle centered at (car_x, car_y) on the track
        car_width, car_height = 15, 10  # Car size
        self.canvas.create_rectangle(
            car_x - car_width / 2,
            car_y - car_height / 2,
            car_x + car_width / 2,
            car_y + car_height / 2,
            fill="red",
        )

        matrix = self.get_canvas_as_matrix()
        print(matrix.tolist())




if __name__ == "__main__":
    root = tk.Tk()
    app = RacetrackGUI(root)

    root.mainloop()
