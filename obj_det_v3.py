import cv2
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
# from gps_v1 import *
import folium
import selenium
from selenium import webdriver
import os

#
from use_roi import get_user_selected_roi

print("All Ok!")



class App:
    def __init__(self, window, window_title):
        self.window = window
        self.window.title(window_title)
        self.selected_image_path = None  # Instance variable to store the selected image path

        # Set the window size to a specific width and height
        # Set the window size to fit the screen
        self.screen_width = self.window.winfo_screenwidth()
        self.screen_height = self.window.winfo_screenheight()
        self.window.geometry(f"{self.screen_width}x{self.screen_height}")

        # Image width and height
        self.image_width = 348
        self.image_height = 464

        # Create a black image to display initially
        self.initial_black_image = np.zeros((640, 480), dtype=np.uint8)

        # Convert the black image to PhotoImage format
        initial_photo = ImageTk.PhotoImage(image=Image.fromarray(self.initial_black_image))

        # Heading and canvas container for the first canvas (self.canvas_image)
        frame_live_feed = tk.Frame(window)
        frame_live_feed.pack(side=tk.LEFT, padx=0, pady=0)  # Adjust padding as needed

        # Heading for the first canvas (self.canvas_image)
        label_live_feed = tk.Label(frame_live_feed, text="Live Feed:", font=("Helvetica", 16), fg="red")
        # label_live_feed.pack(side=tk.LEFT, pady=0)  # Adjust padding as needed
        label_live_feed.grid(row=0, column=0, sticky="w")  # Left-align the label
        
        # Create a new canvas for live video feed
        self.canvas_live = tk.Canvas(frame_live_feed, width=480, height=self.screen_height)
        # self.canvas_live.pack(side=tk.LEFT, pady=50)
        self.canvas_live.grid(row=1, column=0, sticky="w")  # Left-align the canvas

        # Heading and canvas container for the first canvas (self.canvas_image)
        frame_screenshot = tk.Frame(window)
        frame_screenshot.pack(side=tk.LEFT, padx=0, pady=0)  # Adjust padding as needed

        # Heading for the second canvas (self.canvas_live)
        label_screenshot = tk.Label(frame_screenshot, text="Screenshot:", font=("Helvetica", 16), fg="green")
        # label_screenshot.pack(side=tk.LEFT, padx=490)  # Adjust padding as needed
        label_screenshot.grid(row=0, column=0, sticky="w")  # Left-align the label

        self.canvas_image = tk.Canvas(frame_screenshot, width=480, height=self.screen_height)
        # self.canvas_image.pack(side=tk.LEFT, pady=50)
        self.canvas_image.grid(row=1, column=0, sticky="w")  # Left-align the canvas
        
        self.lbl_avg_temp = tk.Label(window, text="Avg. Temperature: ", font=("Helvetica", 14), fg="blue")
        self.lbl_avg_temp.pack(side=tk.LEFT, padx=10, pady=10)
        self.lbl_avg_temp.place(x=480, y=self.screen_height-400)
        # self.lbl_avg_temp.grid(row=2, column=0, sticky="w", columnspan=2)  # Left-align the label

        # Display the black image in the canvas
        self.canvas_image.create_image(0, 0, image=initial_photo, anchor=tk.NW)
        self.canvas_image.photo = initial_photo        

        # Create a Canvas widget for georeferenced map
        self.canvas_map = tk.Canvas(window, width=480, height=640)
        self.canvas_map.pack(side=tk.RIGHT)

        # Initialize a simple map centered on a specific location
        self.map_center = [37.7749, -122.4194]  # San Francisco
        self.map = folium.Map(location=self.map_center, zoom_start=12)

        # Convert the Folium map to an ImageTk format
        # map_img = self.folium_map_to_image(self.map)
        map_img = self.update_map_image()
        self.photo_map = ImageTk.PhotoImage(map_img)

        # Display the map in the canvas
        self.canvas_map.create_image(0, 0, image=self.photo_map, anchor=tk.NW)
        self.canvas_map.photo_map = self.photo_map

        # Create a checkbox for manual detection
        self.manual_det_var = tk.BooleanVar()
        self.chk_manual_det = tk.Checkbutton(window, text="Manual Detection", variable=self.manual_det_var, command=self.toggle_manual_detection)
        self.chk_manual_det.pack(padx=10, pady=10)
        self.chk_manual_det.place(x=10, y=self.screen_height-200)

        # Create a Canvas widget
        # self.canvas = tk.Canvas(window, width=800, height=600)
        # self.canvas.pack()

        # Create a button that calls open_file_dialog with the canvas as a parameter
        self.btn_open_image = tk.Button(window, text="Open Image", width=20, command=self.open_file_dialog)
        self.btn_open_image.pack(padx=10, pady=10)
        self.btn_open_image.place(x=10, y=self.screen_height-300)

        # Button to capture a snapshot
        self.btn_snapshot = tk.Button(window, text="Take Snapshot", width=20, command=self.capture_snapshot)
        self.btn_snapshot.pack(padx=10, pady=10)
        self.btn_snapshot.place(x=300, y=self.screen_height-300)

        # Button to capture a snapshot
        self.btn_email = tk.Button(window, text="Send Email Alert!", width=20, command=self.capture_snapshot)
        self.btn_email.pack(padx=10, pady=10)
        self.btn_email.place(x=500, y=self.screen_height-300)

        # Initialize other variables or widgets as needed...
        self.major_axis_min = 30
        self.major_axis_max = 100
        self.minor_axis_min = 30
        self.minor_axis_max = 100

        self.len_of_contours = 20

        self.RTSP = 'rtsp://169.254.78.161/avc/'
        self.vid = cv2.VideoCapture(self.RTSP)  # Use the default camera
        self.update()

        self.classic_cv_det = False
        self.manual_det = False  # Initialize manual detection as True

    def open_file_dialog(self):
        file_path = filedialog.askopenfilename(title="Select an Image", filetypes=[("Image files", "*.png;*.jpg;*.jpeg")])
        if file_path:
            self.selected_image_path = file_path  # Store the selected image path
            # Read the image from the selected path
            frame = cv2.imread(self.selected_image_path, cv2.IMREAD_GRAYSCALE)
            self.process_image(frame)
    
    def toggle_manual_detection(self):
        # Toggle the value of manual detection based on the checkbox state
        self.manual_det = not self.manual_det

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
            # return frame

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
                # cv2.ellipse(frame, ellipse, (0, 255, 0), 2)

                # Extract ellipse parameters
                (x, y), (major_axis, minor_axis), angle = ellipse

                # print("ellipse parameters (x, y), (major_axis, minor_axis), angle", (x, y), (major_axis, minor_axis), angle)

                axes = (major_axis, minor_axis)
                (major_axis, minor_axis) = sorted(axes)

                # print
                print("ellipse parameters (x, y), (major_axis, minor_axis), angle", (x, y), (major_axis, minor_axis), angle)

                # Draw major axis, minor axis, center, and angle on the image
                # cv2.line(frame, (int(x), int(y)), (int(x + 0.5 * major_axis * np.cos(np.radians(angle))),
                #                                 int(y + 0.5 * major_axis * np.sin(np.radians(angle)))), 128, 1)
                # cv2.line(frame, (int(x), int(y)), (int(x - 0.5 * minor_axis * np.sin(np.radians(angle))),
                #                                 int(y + 0.5 * minor_axis * np.cos(np.radians(angle)))), 128, 1)
                # cv2.circle(frame, (int(x), int(y)), 5, 128, -1)

                # Assuming the manhole cover is a certain size, you can set a threshold
                if (major_axis > self.major_axis_min and major_axis < self.major_axis_max) \
                    and (minor_axis > self.minor_axis_min and minor_axis < self.minor_axis_max):

                    cv2.ellipse(frame, ellipse, (0, 255, 0), 2)

                    # process temperature
                    # Define the rotated rectangle bounding the ellipse
                    rect = ((x, y), (major_axis, minor_axis), angle)

                    # Create a mask based on the rotated rectangle
                    mask = np.zeros_like(frame)
                    cv2.ellipse(mask, rect, 255, thickness=-1)  # Thickness -1 fills the ellipse

                    # Calculate the average pixel value within the ellipse region
                    # avg_temperature = np.mean(frame[mask != 0])
                    avg_temperature = round(np.mean((frame[mask != 0]/ (255) * (130 - 50)) + 50), 2)
                    # min_temperature = np.min(frame[mask != 0])
                    min_temperature = np.min((frame[mask != 0]/ (255) * (130 - 50)) + 50)

                    # max_temperature = np.max(frame[mask != 0])
                    max_temperature = np.max((frame[mask != 0]/ (255) * (130 - 50)) + 50)                    

                    # Print the average pixel value
                    print("Average, min, max Pixel Value within Ellipse:", avg_temperature, min_temperature, max_temperature)
                    self.lbl_avg_temp.config(text='Avg. Temp: ' + str(avg_temperature) + '°F')


                    # Display the image with the fitted ellipse and information
                    # cv2.ellipse(frame, rect, (255,0,0), thickness=-1)
                    # cv2.imshow("Fitted Ellipse", frame)
                    # cv2.imshow("Masked Image", mask)

                    # ellipse_region = cv2.bitwise_and(frame, frame, mask=mask)
                    ellipse_region = cv2.bitwise_and(frame, frame, mask=mask)
                    
                    # cv2.imshow("ROI", ellipse_region)
               
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
            if(self.classic_cv_det == True):
                processed_frame = self.detect_manhole_cover(frame)
            elif(self.manual_det == True):
                processed_frame = self.get_user_selected_roi(frame)
            else:
                processed_frame = self.detect_manhole_cover(frame)


            if processed_frame is not None:
                # Save the processed frame with a timestamp in the file name
                timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                file_name = f"snapshot_{timestamp}.png"
                cv2.imwrite(file_name, processed_frame)  # Save the snapshot as an image file

                # Georeference the data points and display the map
                # data_points = [(37.7749, -122.4194, "San Francisco"),  # Replace with actual GPS coordinates
                #             (34.0522, -118.2437, "Los Angeles"),
                #             (40.7128, -74.0060, "New York")]
                
                data_points = [(38.98582939, -76.937329584, "UMD")]  # Replace with actual GPS coordinates
               
                self.georeference_points_on_map(data_points)

                # Convert the processed frame to ImageTk format
                photo = ImageTk.PhotoImage(image=Image.fromarray(processed_frame))

                # Display the processed frame in the canvas
                self.canvas_image.create_image(0, 0, image=photo, anchor=tk.NW)
                self.canvas_image.photo = photo
            else:
                print("Error: Empty processed Frame")
        else:
            print("Error: Unable to read the image")
        
        # self.move_map()

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
    
    def georeference_points_on_map(self, data_points):
        center_lat = sum(point[0] for point in data_points) / len(data_points)
        center_lon = sum(point[1] for point in data_points) / len(data_points)
        my_map = folium.Map(location=[center_lat, center_lon], zoom_start=12)

        for point in data_points:
            folium.Marker([point[0], point[1]], popup=point[2]).add_to(my_map)

        # my_map.save("georeferenced_map.html")

        # Update the map view in the canvas
        # Load the georeferenced map into the WebView
        # self.canvas_map.load_url("georeferenced_map.html")

    # def show_georeferenced_map(self):
    #     # Load the georeferenced map into the Canvas
    #     geo_map_path = "georeferenced_map.html"
    #     self.canvas_map.delete("all")  # Clear the canvas
    #     self.canvas_map.create_text(400, 300, text="Loading Georeferenced Map...")

    #     try:
    #         map_img = Image.open(geo_map_path)
    #         map_img = ImageTk.PhotoImage(map_img)
    #         self.canvas_map.create_image(0, 0, anchor=tk.NW, image=map_img)
    #         self.canvas_map.map_img = map_img
    #     except Exception as e:
    #         print(f"Error loading georeferenced map: {e}")

    def get_user_selected_roi(self, frame):
        # while True:
        # Capture frame-by-frame
        # ret, frame = video_capture.read()
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

            # Display the frame
            # cv2.imshow('Select ROI', frame)

            # Break the loop on 'ESC' key press
            # key = cv2.waitKey(1) & 0xFF
            # if key == 27:
            #     break

        # Close the video capture window
        # cv2.destroyAllWindows()

        # Allow the user to select the ROI
        roi = cv2.selectROI('Select-ROI', frame, showCrosshair=False)

        # Print the selected ROI coordinates
        print("Selected ROI coordinates:", roi)
        x, y, w, h = roi
        color = (255, 255, 255)
        thickness = 2
        cv2.rectangle(frame, (int(x), int(y)), (int(x + w), int(y + h)), color, thickness)

        # process temperature
        # Define the rotated rectangle bounding the ellipse
        # rect = ((x, y), (major_axis, minor_axis), angle)

        # Create a mask based on the rotated rectangle
        mask = np.zeros_like(frame)
        # cv2.rectangle(mask, rect, 255, thickness=-1)  # Thickness -1 fills the ellipse

        cv2.rectangle(mask, (int(x), int(y)), (int(x + w), int(y + h)), 255, thickness=-1)
        # Calculate the average pixel value within the ellipse region
        # avg_temperature = np.mean(frame[mask != 0])
        avg_temperature = round(np.mean((frame[mask != 0]/ (255) * (130 - 50)) + 50), 2)
        # min_temperature = np.min(frame[mask != 0])
        min_temperature = np.min((frame[mask != 0]/ (255) * (130 - 50)) + 50)

        # max_temperature = np.max(frame[mask != 0])
        max_temperature = np.max((frame[mask != 0]/ (255) * (130 - 50)) + 50)                    

        # Print the average pixel value
        print("Average, min, max Pixel Value within Ellipse:", avg_temperature, min_temperature, max_temperature)
        self.lbl_avg_temp.config(text='Avg. Temp: ' + str(avg_temperature) + '°F')


        cv2.destroyAllWindows()

        return frame

        # Add this method to handle map movement
    def move_map(self):
        # Implement your logic to move the map (this is just a placeholder)
        # For example, you can update self.map_center and regenerate the map image
        new_center = [38.98582939, -76.937329584]  # UMD
        self.map = folium.Map(location=new_center, zoom_start=12)

        # Convert the new Folium map to an ImageTk format
        # map_img = self.folium_map_to_image(self.map)
        map_img = self.update_map_image()
        self.photo_map = ImageTk.PhotoImage(image=map_img)

        # Display the updated map in the canvas
        self.canvas_map.create_image(0, 0, image=self.photo_map, anchor=tk.NW)
        self.canvas_map.photo_map = self.photo_map
    
    # def folium_map_to_image(self, folium_map):
    #     # Save the Folium map as an HTML file
    #     html_path = "temp_map.html"
    #     folium_map.save(html_path)

    #     # Open the saved HTML file and save it as an image using a web browser
    #     browser = folium._tmp_browse.get()
    #     browser.get(f"file://{html_path}")
    #     browser.save_screenshot("temp_map.png")

    #     # Close the browser and load the saved image
    #     browser.quit()
    #     map_img = Image.open("temp_map.png")

    #     return map_img
    
    def update_map_image(self):
        # Save the map as an HTML file
        map_html_path = "temp_map.html"
        self.map.save(map_html_path)

        # Use Selenium to open the HTML file and save a screenshot
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--headless")  # Run Chrome in headless mode (no window)

        # Use Selenium to open the HTML file and save a screenshot
        browser = webdriver.Chrome(options=chrome_options)  # You need to have the ChromeDriver executable in your PATH
        browser.get(f"file:///{os.path.abspath(map_html_path)}")
        browser.save_screenshot("temp_map.png")
        browser.quit()

        # Open the saved screenshot and convert it to a PIL Image
        map_img = Image.open("temp_map.png")

        # Resize the image as needed
        map_img = map_img.resize((int(self.screen_width // 2), 600), Image.LANCZOS)

        # Use ImageTk.PhotoImage to create an instance
        self.photo_map = ImageTk.PhotoImage(map_img)

        return map_img

    def html_to_image(self, html_path):
        # Use a web browser to open the HTML file and save a screenshot
        browser = webdriver.Chrome()  # You need to have the ChromeDriver executable in your PATH
        browser.get(f"file:///{os.path.abspath(html_path)}")
        browser.save_screenshot("temp_map.png")
        browser.quit()

        # Open the saved screenshot and convert it to a PIL Image
        map_img = Image.open("temp_map.png")

        # Resize the image as needed
        map_img = map_img.resize((int(self.screen_width // 2), 600), Image.LANCZOS)

        return map_img



if __name__ == "__main__":
    root = tk.Tk()
    app = App(root, "Manhole Cover Detection with Image")
    root.mainloop()