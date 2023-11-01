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

# Reading the video file

#Creating a opencv window
cv2.namedWindow('Original Video', cv2.WINDOW_NORMAL)
cv2.resizeWindow('Original Video', 640, 480)

# Import video
gVideo = cv2.VideoCapture("ball.mov")
width  = gVideo.get(3)  
height = gVideo.get(4) 
# print("Width of Video: ", width, "\nHeight of Video: ", height)

# Video Processing
#Loop through the video
while (gVideo.isOpened()):
    ret, frame = gVideo.read()

    if ret == True:
        cv2.imshow("Original Video", frame) 
        # Convert to BGR image to HSV image
        hsvIm = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Define the threshold values for HSV mask (Ref: colorpicker.py)
        minHSV = np.array([1, 155, 133])
        maxHSV = np.array([9, 255, 255])

        # Create a mask
        maskHSV = cv2.inRange(hsvIm, minHSV, maxHSV)
        # cv2.imshow("Masked HSV overlayed on Original Video", maskHSV) 

        # # Apply erosion and dilation to remove noise
        # kernel = np.ones((5,5), np.uint8)

        # procIm1 = cv2.dilate(maskHSV, kernel, iterations=1)
        # procIm2 = cv2.erode(procIm1, kernel, iterations=1)

        # Renaming a processed image to a gray image
        # gray = maskHSV
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.medianBlur(gray, 5)

        # Apply edge detection method on the image
        # edges = cv2.Canny(gray, 300, 400)

        rows = gray.shape[0]
        # print("Rows", rows)

        circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1, rows,
                               param1=50, param2=20,
                               minRadius=0, maxRadius=12)
        
        # print("Circles: ", circles)
        
        if circles is not None:

            circles = np.uint16(np.around(circles))

            for i in circles[0, :]:
                center = (i[0], i[1])
                # circle center
                cv2.circle(frame, center, 1, (0, 100, 100), 3)
                # circle outline
                radius = i[2]
                cv2.circle(frame, center, radius, (255, 255, 0), 3)
                cv2.imshow("Original Video", frame) 

        if cv2.waitKey(25)& 0xFF == ord('q'): #press q to exit
            break
    else:
        break


gVideo.release()
cv2.destroyAllWindows()

# %% Problem 3
# ------------------------------------------------------------------------
# Problem 3:
# Given the photo of a train track, transform the image so that you get a top view of
# the train tracks, find the distance between the train tracks for every row of the
# warped image, and then find the average distance. Show the intermediate
# results.
# -----------------------------------------------------------------------
# -----------------------------------------------------------------------
# Reading the image file
frame = cv2.imread("train_track.jpg")

cv2.namedWindow('Transformed Capture', cv2.WINDOW_NORMAL)
cv2.resizeWindow('Transformed Capture', 640, 480)

cv2.namedWindow('Masked Image', cv2.WINDOW_NORMAL)
cv2.resizeWindow('Masked Image', 640, 480)

print(frame.shape)
# cv2.imshow('Initial Capture', frame) # Initial Capture

# Locate the points on the image for the perspective transformation
src_pts = np.array([(45, 1952), (2931, 1952),
                    (1661, 1063), (1355, 1063)], dtype='float32')
des_pts = np.array([(0, 0), (3008, 0),
                    (3008, 2008), (0, 2008)], dtype='float32')
    
# Apply Perspective Transform Algorithm
H = cv2.getPerspectiveTransform(src_pts, des_pts)
op_img_size = (3009, 2000)
op_img = cv2.warpPerspective(frame, H, op_img_size)
    
# Wrap the transformed image
top_img = cv2.flip(op_img, 0)
cv2.imshow('Transformed Capture', top_img) # Transformed Capture
cv2.imwrite("tarin_track_transformed.jpg", top_img)

# HSV the transformed image
hsvIm = cv2.cvtColor(top_img, cv2.COLOR_BGR2HSV)

# Define the threshold values for HSV mask (Ref: colorpicker.py)
minHSV = np.array([0, 0, 249])
maxHSV = np.array([179, 7, 255])

# Create a mask
maskHSV = cv2.inRange(hsvIm, minHSV, maxHSV)

# Apply erosion and dilation to remove noise
kernel = np.ones((5,5), np.uint8)

procIm2 = cv2.erode(maskHSV, kernel, iterations=1)

gray = procIm2
cv2.imshow('Masked Image', gray) # Transformed Capture

# Apply edge detection method on the image
# edges = cv2.Canny(gray, 240, 250)
# cv2.imshow('Masked Image', edges) # Transformed Capture

dist_bw_tracks = np.array([])

# for each row in the edges image, group the points for each track
for row in range(len(maskHSV)):

    track1_y_coor = np.array([])
    track2_y_coor = np.array([])
    
    track1_y_coor_max = 0
    track2_y_coor_min = 0
    length = 0

    indices = np.argwhere(maskHSV[row])
    # print("indices", indices)
    for col in (indices):
        if col > 800 and col < 1200:
            track1_y_coor = np.append(track1_y_coor, col)
        if col > 1800 and col < 2200:
            track2_y_coor = np.append(track2_y_coor, col)       
        
        if len(track1_y_coor) > 0 and len(track2_y_coor) > 0:
            track1_y_coor_max = np.max(track1_y_coor)
            track2_y_coor_min = np.min(track2_y_coor)
            length = abs(track2_y_coor_min - track1_y_coor_max)
           
            if length > 500 and length < 1300:
                dist_bw_tracks = np.append(dist_bw_tracks, length)
        
                if row == 320 and col > 800 and col < 1200:
                    start_point = (int(col), row)
                    st = 1
                if row == 1000 and col > 1800 and col < 2200: 
                    start_point = (int(np.max(track1_y_coor)), row)                   
                    end_point = (int(col), row)              
    
                    color = (0, 255, 0)
                    thickness = 10                  
                    top_img = cv2.arrowedLine(top_img, start_point, end_point, color, thickness)
                    top_img = cv2.arrowedLine(top_img, end_point, start_point, color, thickness)
                    

dist_bw_tracks_mean = np.mean(dist_bw_tracks)
print("Average distance between tracks:", dist_bw_tracks_mean)
top_img = cv2.putText(
                        img = top_img,
                        text = "Avg. Distance:" + str(round(dist_bw_tracks_mean,2)),
                        org = (1100, int(1100)),
                        fontFace = cv2.FONT_HERSHEY_DUPLEX,
                        fontScale = 2.0,
                        color = (0, 0, 255),
                        thickness = 8
                    )


cv2.imshow('Transformed Capture', top_img)
cv2.waitKey(0)
cv2.destroyAllWindows()
# ------------------------------------------------------------------------
# %% Problem 4:
# Detect each hot balloon in a given image of hot air balloons. Find the number of
# hot air balloons automatically. The final results should show each hot air balloon
# labeled with different colors.
# Note: Do not worry about resolving occlusion, occluded balloons can be
# combined as one.
# -----------------------------------------------------------------------
# -----------------------------------------------------------------------
# Reading the image file
frame = cv2.imread("hotairbaloon.jpg")
#Creating a opencv window
cv2.namedWindow('Initial Capture', cv2.WINDOW_NORMAL)
cv2.resizeWindow('Initial Capture', 640, 480)

cv2.namedWindow('Masked Image', cv2.WINDOW_NORMAL)
cv2.resizeWindow('Masked Image', 640, 480)

#  HSV Image
hsvIm = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
# cv2.imshow('HSV Image', hsvIm) # Initial Capture
# cv2.imshow("HSV Image", hsvIm) 

# Define the threshold values for HSV mask (Ref: colorpicker.py)
minHSV = np.array([0, 108, 0])
maxHSV = np.array([179, 179, 255])

# Create a mask
maskHSV = cv2.inRange(hsvIm, minHSV, maxHSV)
# cv2.imshow("Masked HSV overlayed on Original Video", maskHSV) 

# Apply erosion and dilation to remove noise
kernel = np.ones((9,9), np.uint8)

procIm1 = cv2.dilate(maskHSV, kernel, iterations=1)
procIm2 = cv2.dilate(procIm1, kernel, iterations=1)
procIm3 = cv2.dilate(procIm2, kernel, iterations=1)
procIm4 = cv2.erode(procIm3, kernel, iterations=1)
# procIm3 = cv2.erode(procIm2, kernel, iterations=1)

# Renaming a processed image to a gray image
gray = procIm4

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

    # convert the radius and center to integer number
    center = (int(x),int(y))
    radius = int(radius)

    if(radius > 50):
        #  Draw the enclosing circle on the image
        cv2.circle(frame,center,radius,(255,255,0),10)

        frame = cv2.putText(
            img = frame,
            text = "Balloon-" + str(count),
            org = center,
            fontFace = cv2.FONT_HERSHEY_DUPLEX,
            fontScale = 3.0,
            color = (int(colorb[i]), int(colorg[i]), int(colorr[i])),
            thickness = 3
        )
        
        count += 1

print("Number of hot air balloons detected:", count-1)
cv2.imshow('Initial Capture', frame) 

# print("Length of edges:,", len(edges))
cv2.waitKey(0)
 
cv2.destroyAllWindows()
