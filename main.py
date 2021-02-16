import cv2
import numpy as np
import time
import socket
# import pickle
import json
print("Package Imported")

# Socket stuff
UDP_IP = "127.0.0.1"
UDP_PORT = 5065

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


# Start video capture
cap = cv2.VideoCapture(0)


# time calculation
start_time = time.time()
fpsDisplayTime = 1  # displays the frame rate every 1 second
fpsCounter = 0


# font variables
font = cv2.FONT_HERSHEY_SIMPLEX
fontOrigin = (10, 35)
fontScale = 1
fontColour = (255, 255, 255)
fontBorderColour = (0, 0, 0)
fontThickness = 2

def myPutText(img, text):
    outputImage = cv2.putText(img, text, fontOrigin, font, fontScale, fontBorderColour, fontThickness+3, cv2.LINE_AA)
    outputImage = cv2.putText(outputImage, text, fontOrigin, font, fontScale, fontColour, fontThickness, cv2.LINE_AA)
    return outputImage


# stack images for display
def myStackImages(scale, imgArray):
    outputImage = None
    for i in range(len(imgArray)):
        rowStack = np.hstack(imgArray[i])
        if outputImage is not None:
            outputImage = np.vstack((outputImage, rowStack))
        else:
            outputImage = rowStack

    outputImage = cv2.resize(outputImage, (round(outputImage.shape[1]*scale), round(outputImage.shape[0]*scale)))
    return outputImage



imgWidth = 640  # 640, default is 1280
imgHeight = 360  # 360, default is 720
imgHalfHeight = int(imgHeight/2)
imgHalfWidth = int(imgWidth/2)

# 64*3/4 = 48, 36*3/4 = 27
imgSmallWidth = 48
imgSmallHeight = 27
imgBaseWood = np.zeros((imgSmallHeight, imgSmallWidth, 3), np.uint8)
# for i in range(0, imgSmallWidth, 2):
#     imgBaseWood[:, i] = (255, 255, 255)
imgBaseWood = cv2.cvtColor(imgBaseWood, cv2.COLOR_BGR2GRAY)



def empty(a):
    pass

cv2.namedWindow("TrackBars", cv2.WINDOW_NORMAL)
cv2.resizeWindow("TrackBars", 720, 360)
cv2.createTrackbar("Left X", "TrackBars", 0, imgWidth, empty)
cv2.createTrackbar("Right X", "TrackBars", imgWidth, imgWidth, empty)
cv2.createTrackbar("Top Y", "TrackBars", 0, imgHeight, empty)
cv2.createTrackbar("Bottom Y", "TrackBars", imgHeight, imgHeight, empty)


# imgHistory = []
# imgHistoryIndex = 0
# for i in range(10):
#     imgBlack = np.zeros((imgHeight, imgWidth, 3), np.uint8)
#     imgHistory.append(imgBlack)

imgHistory_old = np.zeros((imgHeight, imgWidth, 3), np.uint8)


while True:
    # Capture frame-by-frame
    ret, frame = cap.read()
    imgResize = cv2.resize(frame, (imgWidth, imgHeight))

    imgCalibration = imgResize.copy()
    leftX = cv2.getTrackbarPos("Left X", "TrackBars")
    rightX = cv2.getTrackbarPos("Right X", "TrackBars")
    topY = cv2.getTrackbarPos("Top Y", "TrackBars")
    bottomY = cv2.getTrackbarPos("Bottom Y", "TrackBars")
    imgCalibration = cv2.rectangle(imgCalibration, (leftX, topY), (rightX, bottomY), (255, 255, 0), 2)  # to display calibration rectangle

    # imgCalibration[:, 0:leftX] = (0, 0, 0)
    # imgCalibration[:, rightX:imgWidth] = (0, 0, 0)
    # imgCalibration[0:topY, :] = (0, 0, 0)
    # imgCalibration[bottomY:imgHeight, :] = (0, 0, 0)

    imgCalibration2 = imgResize.copy()
    imgCalibration2 = imgCalibration2[topY:bottomY, leftX:rightX]  # make image with only the selected frame information
    imgCalibration2 = cv2.resize(imgCalibration2, (imgWidth, imgHeight))  # resize so it can be displayed

    imgChange = imgCalibration2.copy()
    imgChange = cv2.GaussianBlur(imgChange, (5, 5), 1)  # blur to remove some noise
    imgChangeDisplay = np.zeros((imgHeight, imgWidth, 3), np.uint8)  # quick way to initiate blank image
    cv2.absdiff(imgChange, imgHistory_old, imgChangeDisplay)
    imageWeight = 0.98
    imgHistory_old = cv2.addWeighted(imgHistory_old, imageWeight, imgChange, 1-imageWeight, 0.0)  # history saving method from Kelvin's SOD

    imgChangeDisplay = cv2.cvtColor(imgChangeDisplay, cv2.COLOR_BGR2GRAY)
    _, imgChangeDisplay = cv2.threshold(imgChangeDisplay, 30, 255, cv2.THRESH_TOZERO)  # threshold to remove more noise when normalising
    (_, maxVal, _, maxLoc) = cv2.minMaxLoc(imgChangeDisplay)  # use max value to normalise image to 255
    # print(maxVal)
    if maxVal == 0:  # remove error when maxVal == 0
        maxVal = 1
    imgChangeDisplay[:, :] = imgChangeDisplay[:, :] * (255.0/maxVal)  # normalise image
    imgChangeDisplay = cv2.cvtColor(imgChangeDisplay, cv2.COLOR_GRAY2BGR)


    imgSmall = imgChangeDisplay.copy()
    imgSmall = cv2.resize(imgSmall, (imgSmallWidth, imgSmallHeight))  # 48, 27
    imgSmall = cv2.cvtColor(imgSmall, cv2.COLOR_BGR2GRAY)
    barkWeightShift = 255.0
    barkWeight = 0.2
    # barkWeight = (maxVal+barkWeightShift)/(255.0+barkWeightShift)
    imgSmall = cv2.addWeighted(imgSmall, 1-barkWeight, imgBaseWood, barkWeight, 0.0)
    # print(imgSmall)

    # sendData = str(imgSmall)
    sendData2 = json.dumps(imgSmall.tolist())
    # print(sendData2)
    sock.sendto(sendData2.encode(), (UDP_IP, UDP_PORT))

    imgSmall = cv2.resize(imgSmall, (imgWidth, imgHeight), interpolation=cv2.INTER_NEAREST)
    imgSmall = cv2.cvtColor(imgSmall, cv2.COLOR_GRAY2BGR)

    # Add text to images
    # imgResize = myPutText(imgResize, 'Camera')

    # Stack the images together
    outputFrame = myStackImages(1, [[imgResize, imgChangeDisplay], [imgCalibration2, imgSmall]])


    # Display the resulting frame
    cv2.imshow('Video1', outputFrame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    fpsCounter += 1
    if (time.time() - start_time) > fpsDisplayTime:
        print("FPS: ", fpsCounter / (time.time() - start_time))
        fpsCounter = 0
        start_time = time.time()
        # sock.sendto(sendData2.encode(), (UDP_IP, UDP_PORT))

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()


