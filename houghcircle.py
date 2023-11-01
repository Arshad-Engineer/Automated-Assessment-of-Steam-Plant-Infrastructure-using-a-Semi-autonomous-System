# %% Code Header
# **************EMPM673 - Perception for Autonomous Robots ***************
# **************** Mid-term Exam *****************************************
# ***************  Date: March 16, 2023 **********************************
# ------------------------------------------------------------------------
# Author: Arshad Shaik, UID: 118438832
# ------------------------------------------------------------------------
# %% Problem 2:
# From the given video, assuming that the width of the ball is around 11 pixels, 
# using Hough transform to detect the ball.
# -----------------------------------------------------------------------
# -----------------------------------------------------------------------
# Import necessary packages
import numpy as np
import cv2

# %% Reading the image file
frame = cv2.imread("20230329_080926.jpg")
#Creating a opencv window
cv2.namedWindow('Initial Capture', cv2.WINDOW_NORMAL)
cv2.resizeWindow('Initial Capture', 640, 480)

cv2.namedWindow('Masked Image', cv2.WINDOW_NORMAL)
cv2.resizeWindow('Masked Image', 640, 480)

# %% Main Program

hsvIm = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
# cv2.imshow('HSV Image', hsvIm) # Initial Capture
# cv2.imshow("HSV Image", hsvIm) 

# Define the threshold values for HSV mask (Ref: colorpicker.py)
minHSV = np.array([127, 12, 0])
maxHSV = np.array([179, 25, 255])

# Create a mask
maskHSV = cv2.inRange(hsvIm, minHSV, maxHSV)
# cv2.imshow("Masked HSV overlayed on Original Video", maskHSV) 

# Apply erosion and dilation to remove noise
kernel = np.ones((9,9), np.uint8)

procIm1 = cv2.dilate(maskHSV, kernel, iterations=1)
# procIm2 = cv2.dilate(procIm1, kernel, iterations=1)
#procIm3 = cv2.dilate(procIm2, kernel, iterations=1)
# procIm4 = cv2.erode(procIm3, kernel, iterations=1)
# procIm3 = cv2.erode(procIm2, kernel, iterations=1)

# Renaming a processed image to a gray image
gray = procIm1
gray = cv2.medianBlur(gray, 5)
cv2.imshow('Masked Image', gray) # Transformed Capture

rows = gray.shape[0]
# print("Rows", rows)

circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1, 200,
                        param1=300, param2=40,
                        minRadius=250, maxRadius=700)

print("Circles: ", circles)

if circles is not None:

    circles = np.uint16(np.around(circles))

    for i in circles[0, :]:
        center = (i[0], i[1])
        # circle center
        cv2.circle(frame, center, i[2], (0, 100, 100), 3)
        # circle outline
        radius = i[2]
        cv2.circle(frame, center, radius, (255, 255, 0), 3)
        

cv2.imshow('Initial Capture', frame) 

# print("Length of edges:,", len(edges))
cv2.waitKey(0)
 
cv2.destroyAllWindows()