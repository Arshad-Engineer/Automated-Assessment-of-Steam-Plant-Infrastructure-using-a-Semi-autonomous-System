import cv2

def get_user_selected_roi(video_capture):
    while True:
        # Capture frame-by-frame
        ret, frame = video_capture.read()

        # Display the frame
        cv2.imshow('Select ROI', frame)

        # Break the loop on 'ESC' key press
        key = cv2.waitKey(1) & 0xFF
        if key == 27:
            break

    # Close the video capture window
    cv2.destroyAllWindows()

    # Allow the user to select the ROI
    roi = cv2.selectROI('Select-ROI', frame, showCrosshair=False)

    # Print the selected ROI coordinates
    print("Selected ROI coordinates:", roi)

    return roi

def main():
    # Open a video capture object (0 is the default camera)
    video_capture = cv2.VideoCapture('rtsp://169.254.78.161/avc/')

    # Get the user-selected ROI
    selected_roi = get_user_selected_roi(video_capture)

    # Release the video capture object
    video_capture.release()

if __name__ == "__main__":
    main()
