import cv2
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

print("All Ok!")



class App:
    def __init__(self, window, window_title):
        self.window = window
        self.window.title(window_title)
        self.selected_image_path = None  # Instance variable to store the selected image path

        # Set the window size to a specific width and height
        # Set the window size to fit the screen
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        self.window.geometry(f"{screen_width}x{screen_height}")

        # Image width and height
        self.image_width = 348
        self.image_height = 464

        self.canvas_image = tk.Canvas(window, width=screen_width // 2, height=screen_height)
        self.canvas_image.pack(side=tk.RIGHT)

        # Create a new canvas for live video feed
        self.canvas_live = tk.Canvas(window, width=screen_width // 2, height=screen_height)
        self.canvas_live.pack(side=tk.LEFT)

        # Create a Canvas widget
        # self.canvas = tk.Canvas(window, width=800, height=600)
        # self.canvas.pack()

        # Create a button that calls open_file_dialog with the canvas as a parameter
        self.btn_open_image = tk.Button(window, text="Open Image", width=20, command=self.open_file_dialog)
        self.btn_open_image.pack(padx=10, pady=10)
        self.btn_open_image.place(x=10, y=screen_height-300)

        self.lbl_avg_temp = tk.Label(window, text = "AAA")
        self.lbl_avg_temp.pack(padx=10, pady=10)
        self.lbl_avg_temp.place(x=screen_width//2, y=screen_height-300)


        # Button to capture a snapshot
        self.btn_snapshot = tk.Button(window, text="Take Snapshot", width=20, command=self.capture_snapshot)
        self.btn_snapshot.pack(padx=10, pady=10)
        self.btn_snapshot.place(x=300, y=screen_height-300)

        # Initialize other variables or widgets as needed...
        self.major_axis_min = 30
        self.major_axis_max = 100
        self.minor_axis_min = 30
        self.minor_axis_max = 100

        self.len_of_contours = 20

        self.vid = cv2.VideoCapture(0)  # Use the default camera
        self.update()

    def open_file_dialog(self):
        file_path = filedialog.askopenfilename(title="Select an Image", filetypes=[("Image files", "*.png;*.jpg;*.jpeg")])
        if file_path:
            self.selected_image_path = file_path  # Store the selected image path
            # Read the image from the selected path
            frame = cv2.imread(self.selected_image_path, cv2.IMREAD_GRAYSCALE)
            self.process_image(frame)

    # Function to detect manhole cover using Canny and ellipse fitting
    def detect_manhole_cover(self, frame):
        # If the image is grayscale, no need to convert
        if len(frame.shape) == 2:
            gray = frame
            print(" image format2")
        elif len(frame.shape) == 3:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            frame = gray
            print("image format3")

        else:
            print("Error: Unsupported image format")
            return frame

        # Apply GaussianBlur to reduce noise and improve edge detection
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)

        # Apply Canny edge detection
        edges = cv2.Canny(blurred, 30, 150)

        # Find contours in the edged image
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Iterate through contours and fit ellipses
        for contour in contours:
            if len(contour) >= self.len_of_contours:
                ellipse = cv2.fitEllipse(contour)

                # Draw ellipse on the frame
                cv2.ellipse(frame, ellipse, (0, 255, 0), 2)

                # Extract ellipse parameters
                (x, y), (major_axis, minor_axis), angle = ellipse

                # print("ellipse parameters (x, y), (major_axis, minor_axis), angle", (x, y), (major_axis, minor_axis), angle)

                axes = (major_axis, minor_axis)
                (major_axis, minor_axis) = sorted(axes)

                # print
                print("ellipse parameters (x, y), (major_axis, minor_axis), angle", (x, y), (major_axis, minor_axis), angle)

                # Draw major axis, minor axis, center, and angle on the image
                cv2.line(frame, (int(x), int(y)), (int(x + 0.5 * major_axis * np.cos(np.radians(angle))),
                                                int(y + 0.5 * major_axis * np.sin(np.radians(angle)))), 128, 1)
                cv2.line(frame, (int(x), int(y)), (int(x - 0.5 * minor_axis * np.sin(np.radians(angle))),
                                                int(y + 0.5 * minor_axis * np.cos(np.radians(angle)))), 128, 1)
                cv2.circle(frame, (int(x), int(y)), 5, 128, -1)

                # Assuming the manhole cover is a certain size, you can set a threshold
                if (major_axis > self.major_axis_min and major_axis < self.major_axis_max) \
                    and (minor_axis > self.minor_axis_min and minor_axis < self.minor_axis_max):

                    # process temperature
                    # Define the rotated rectangle bounding the ellipse
                    rect = ((x, y), (major_axis, minor_axis), angle)

                    # Create a mask based on the rotated rectangle
                    mask = np.zeros_like(frame)
                    cv2.ellipse(mask, rect, 255, thickness=-1)  # Thickness -1 fills the ellipse

                    # Calculate the average pixel value within the ellipse region
                    # avg_temperature = np.mean(frame[mask != 0])
                    avg_temperature = np.mean((frame[mask != 0]/ (255) * (130 - 50)) + 50)
                    # min_temperature = np.min(frame[mask != 0])
                    min_temperature = np.min((frame[mask != 0]/ (255) * (130 - 50)) + 50)

                    # max_temperature = np.max(frame[mask != 0])
                    max_temperature = np.max((frame[mask != 0]/ (255) * (130 - 50)) + 50)                    

                    # Print the average pixel value
                    print("Average, min, max Pixel Value within Ellipse:", avg_temperature, min_temperature, max_temperature)
                    self.lbl_avg_temp.config(text='Avg. Temp: ' + str(avg_temperature))


                    # Display the image with the fitted ellipse and information
                    # cv2.ellipse(frame, rect, (255,0,0), thickness=-1)
                    # cv2.imshow("Fitted Ellipse", frame)
                    cv2.imshow("Masked Image", mask)

                    # ellipse_region = cv2.bitwise_and(frame, frame, mask=mask)
                    ellipse_region = cv2.bitwise_and(frame, frame, mask=mask)
                    
                    cv2.imshow("ROI", ellipse_region)
               
                    cv2.waitKey(1)
                    # cv2.destroyAllWindows()

                    # ellipse_pixels = ((frame[mask != 0]/ (255) * (130 - 50)) + 50)
                    # print("Pixel values in the ellipse region", ellipse_pixels)
                    # # Plot the pixel values
                    # plt.plot(ellipse_pixels)
                    # plt.xlabel('Pixel Index')
                    # plt.ylabel('Pixel Value')
                    # plt.title('Pixel Values within Ellipse Region')
                    # plt.show()

                    return frame


        return None

    def process_image(self, frame):
        print(" Size of the image: ", frame.shape[:2])
        self.image_width = frame.shape[0] 
        self.image_height = frame.shape[1]
        print("Process Image - width, height", self.image_width, self.image_height)

        if frame is not None:
            # Detect manhole cover
            frame = cv2.resize(frame, (480, 640)) # redundant
            processed_frame = self.detect_manhole_cover(frame)

            # Save the processed frame with a timestamp in the file name
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            file_name = f"snapshot_{timestamp}.png"
            cv2.imwrite(file_name, processed_frame)  # Save the snapshot as an image file

            # Convert the processed frame to ImageTk format
            photo = ImageTk.PhotoImage(image=Image.fromarray(processed_frame))

            # Display the processed frame in the canvas
            self.canvas_image.create_image(0, 0, image=photo, anchor=tk.NW)
            self.canvas_image.photo = photo
        else:
            print("Error: Unable to read the image")

    def capture_snapshot(self):
        ret, frame = self.vid.read()
        if ret:
            # Resize the frame to fit the canvas
            frame = cv2.resize(frame, (self.image_height, self.image_width))
            # cv2.imwrite("snapshot.png", frame)  # Save the snapshot as an image file
            # self.selected_image_path = "snapshot.png"
            self.process_image(frame)

    def update(self):
        ret, frame = self.vid.read()
        # print(" Size of the image: ", frame.shape[:2])
        # self.image_width = frame.shape[0]
        # self.image_height = frame.shape[1]
        # print("Video Frame: width, height", self.image_width, self.image_height)

        if ret:
            # Resize the frame to fit the canvas
            # frame = cv2.resize(frame, (self.image_height, self.image_width))
            frame = cv2.resize(frame, (480, 640))
            # print("Video Frame: width, height", frame.shape[:2])
            frame= cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Display the live video feed on the canvas
            photo_live = ImageTk.PhotoImage(image=Image.fromarray(frame))
            self.canvas_live.create_image(0, 0, image=photo_live, anchor=tk.NW)
            self.canvas_live.photo = photo_live

            # Process the frame and detect manhole cover
            # self.detect_manhole_cover

            self.window.after(10, self.update)  # Schedule the update after 10 milliseconds

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root, "Manhole Cover Detection with Image")
    root.mainloop()