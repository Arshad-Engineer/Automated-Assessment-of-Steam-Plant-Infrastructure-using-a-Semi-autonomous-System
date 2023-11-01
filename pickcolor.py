import cv2
import numpy as np

def nothing(x):
    pass

# Create a window - one for GUI and one for output
cv2.namedWindow('GUI', cv2.WINDOW_NORMAL)
cv2.resizeWindow('GUI', 640, 480)

cv2.namedWindow('Masked Image multiplied with Original', cv2.WINDOW_NORMAL)
cv2.resizeWindow('Masked Image multiplied with Original', 640, 480)

# Create trackbars for color change
# Hue is from 0-179 for Opencv
cv2.createTrackbar('HMin', 'GUI', 0, 179, nothing)
cv2.createTrackbar('SMin', 'GUI', 0, 255, nothing)
cv2.createTrackbar('VMin', 'GUI', 0, 255, nothing)
cv2.createTrackbar('HMax', 'GUI', 0, 179, nothing)
cv2.createTrackbar('SMax', 'GUI', 0, 255, nothing)
cv2.createTrackbar('VMax', 'GUI', 0, 255, nothing)

# Set default value for Max HSV trackbars
cv2.setTrackbarPos('HMax', 'GUI', 179)
cv2.setTrackbarPos('SMax', 'GUI', 255)
cv2.setTrackbarPos('VMax', 'GUI', 255)

# Initialize HSV min/max values
hMin = sMin = vMin = hMax = sMax = vMax = 0

while(1):
    # Load image
    frame = cv2.imread("20230329_080926.JPG")
    
    # Get current positions of all trackbars
    hMin = cv2.getTrackbarPos('HMin', 'GUI')
    sMin = cv2.getTrackbarPos('SMin', 'GUI')
    vMin = cv2.getTrackbarPos('VMin', 'GUI')
    hMax = cv2.getTrackbarPos('HMax', 'GUI')
    sMax = cv2.getTrackbarPos('SMax', 'GUI')
    vMax = cv2.getTrackbarPos('VMax', 'GUI')

    # Set lower & upper bounds of HSV mask
    lower = np.array([hMin, sMin, vMin])
    upper = np.array([hMax, sMax, vMax])

    # Convert to HSV format, filter req color/object, and perform bitwise-AND
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower, upper)
    result = cv2.bitwise_and(frame, frame, mask=mask)

    # Display result image
    cv2.imshow('Masked Image multiplied with Original', result)

    if cv2.waitKey(25) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()