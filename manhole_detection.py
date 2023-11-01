# %% Code Header
# **************Steam Plant Project ***************
# ***************  Date: March 16, 2023 **********************************
# ------------------------------------------------------------------------
# Author: Arshad Shaik, UID: 118438832
# ------------------------------------------------------------------------
# Description:
#
# -----------------------------------------------------------------------
# %% Section 1: Import necessary packages
import numpy as np
import cv2
import math 

# %% Reading the image file
frame = cv2.imread("20230329_080926.jpg")
#Creating a opencv window
cv2.namedWindow('Initial Capture', cv2.WINDOW_NORMAL)
cv2.resizeWindow('Initial Capture', 640, 480)

cv2.namedWindow('Masked Image', cv2.WINDOW_NORMAL)
cv2.resizeWindow('Masked Image', 640, 480)

# %%
print(frame.shape)

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

cv2.imshow('Masked Image', gray) # Transformed Capture

# Apply edge detection method on the image
# edges = cv2.Canny(gray, 240, 250)
# cv2.imshow('Masked Image', edges) # Transformed Capture

contours, hierarchy = cv2.findContours(image=gray, mode=cv2.RETR_EXTERNAL, method=cv2.CHAIN_APPROX_SIMPLE)
print("Number of contours detected:", len(contours))

# print("Contours:", contours)
count = 1
colorr = np.random.randint(255, size=500)
# print(type(int(colorr[0])))
colorg = np.random.randint(255, size=500)
colorb = np.random.randint(255, size=500)
for i in range(len(contours)):
    # find the minimum enclosing circle
    (x,y),radius = cv2.minEnclosingCircle(contours[i])
    perimeter = cv2.arcLength(contours[i],True)
    area = cv2.contourArea(contours[i])
    circularity = int(4*math.pi*area / (perimeter) ** 2 * 100)

    # convert the radius and center to integer number
    center = (int(x),int(y))
    radius = int(radius)

    if(radius > 300 and circularity > 4):
        #  Draw the enclosing circle on the image
        # cv2.circle(frame,center,radius,(255,255,0),10)
        ellipse = cv2.fitEllipse(contours[i])
        # cv2.ellipse(frame,ellipse,(0,255,0),10)
        _x,_y,_w,_h = cv2.boundingRect(contours[i])
        cv2.rectangle(frame,(_x,_y),(_x+_w,_y+_h),(0,255,0),10)
        print("Perimeter", str(count), perimeter)
        print("Circularity", str(count), circularity)        

        frame = cv2.putText(
            img = frame,
            text = "MH_ID:" + str(count),
            org = (_x,_y-50),
            fontFace = cv2.FONT_HERSHEY_DUPLEX,
            fontScale = 3.0,
            color = (0, 255, 0),
            thickness = 3
        )        
        frame = cv2.putText(
            img = frame,
            text = "Loc:" + "WLBG",
            org = (_x,_y+100+_h),
            fontFace = cv2.FONT_HERSHEY_DUPLEX,
            fontScale = 3.0,
            color = (0, 255, 0),
            thickness = 3
        )
        frame = cv2.putText(
            img = frame,
            text = "Temp:" + str(90) + "F",
            org = (_x+_w-200,_y-50),
            fontFace = cv2.FONT_HERSHEY_DUPLEX,
            fontScale = 3.0,
            color = (0, 255, 0),
            thickness = 3
        )
        
        count += 1

print("Number of hot air balloons detected:", count-1)
cv2.imshow('Initial Capture', frame) 

# print("Length of edges:,", len(edges))
cv2.waitKey(0)
 
cv2.destroyAllWindows()

# %%
