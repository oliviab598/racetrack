import tkinter as tk


class RacetrackGUI:
    """
    Create a GUI for drawing racetracks.
    """

    def __init__(self, master):
        self.master = master
        self.master.title("Racetrack GUI")
        self.master.geometry("500x500")

        # Create a canvas for drawing
        self.canvas = tk.Canvas(
            self.master, width=500, height=500, bg="white", cursor="crosshair"
        )
        self.canvas.pack()

        # Create a frame for the buttons
        self.button_frame = tk.Frame(self.master)
        self.button_frame.pack(pady=10)

        # Create the clear button
        self.clear_button = tk.Button(
            self.button_frame,
            text="Clear",
            command=self.clear_racetrack,
            bg="red",
            fg="white",
        )
        self.clear_button.pack(side=tk.LEFT, padx=5)

        # Create the solidify button
        self.solidify_button = tk.Button(
            self.button_frame,
            text="Solidify",
            command=self.solidify_racetrack,
            bg="green",
            fg="white",
        )
        self.solidify_button.pack(side=tk.LEFT, padx=5)

        # Hide the buttons initially
        self.button_frame.pack_forget()

        # Initialize drawing state and boundaries
        self.drawing = False
        self.last_x, self.last_y = None, None
        self.min_x, self.min_y = None, None
        self.max_x, self.max_y = None, None
        self.solidified = False

        # Bind mouse events to the canvas
        self.canvas.bind("<Button-1>", self.start_draw)
        self.canvas.bind("<B1-Motion>", self.draw)
        self.canvas.bind("<ButtonRelease-1>", self.stop_draw)

        # Show the initial message
        print("Showing initial message")
        self.show_message("Use the cursor to draw the racetrack", 4000)

    def show_message(self, message, duration):
        """
        Show a message on the canvas for a short period of time.
        """
        print(f"Creating message: {message}")
        self.message_id = self.canvas.create_text(
            250, 250, text=message, fill="black", font=("Helvetica", 24, "bold")
        )
        self.master.after(duration, self.canvas.delete, self.message_id)

    def start_draw(self, event):
        """
        Start drawing on the canvas.
        """
        if not self.solidified:
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

            # Show the buttons when the user stops drawing
            print("Showing buttons")
            self.button_frame.pack(pady=10)

    def clear_racetrack(self):
        """
        Clear the racetrack and allow drawing again.
        """
        self.canvas.delete("all")
        self.solidified = False
        self.button_frame.pack_forget()

    def solidify_racetrack(self):
        """
        Solidify the racetrack and prevent further drawing.
        """
        self.solidified = True
        self.button_frame.pack_forget()


if __name__ == "__main__":
    root = tk.Tk()
    app = RacetrackGUI(root)
    root.mainloop()
