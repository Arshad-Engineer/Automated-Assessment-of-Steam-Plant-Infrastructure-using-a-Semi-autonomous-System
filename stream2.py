import cv2

#print("Before URL")
# 
# cap1 = cv2.VideoCapture('rtsp://169.254.51.215/avc/')
cap2 = cv2.VideoCapture('rtsp://169.254.78.161/avc/ch1')
# cap = cv2.VideoCapture('rtsp://admin:123456@192.168.1.216/H264?ch=1&subtype=0')
#print("After URL")

while True:

    #print('About to start the Read command')
    # ret1, frame1 = cap1.read()
    ret2, frame2 = cap2.read()
    #print('About to show frame of Video.')
    # cv2.imshow("Capturing1",frame1)
    cv2.imshow("Capturing2",frame2)
    #print('Running..')

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# cap1.release()
cap2.release()
cv2.destroyAllWindows()