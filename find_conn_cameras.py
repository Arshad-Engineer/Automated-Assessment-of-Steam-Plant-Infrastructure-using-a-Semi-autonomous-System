import cv2

def find_connected_cameras():
    index = 0
    while True:
        cap = cv2.VideoCapture(index)
        if not cap.isOpened():
            break
        print(f"Camera at index {index} is connected.")
        cap.release()
        index += 1

if __name__ == "__main__":
    find_connected_cameras()
