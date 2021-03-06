import numpy as np
import cv2 as cv
import time

capture = cv.VideoCapture(0)
ret, first = capture.read()

first_gray = cv.cvtColor(first, cv.COLOR_BGR2GRAY)
first_gray = cv.GaussianBlur(first_gray, (21, 21), 0)

height = first_gray.shape[0]
width = first_gray.shape[1]

threshold_level = 50
threshold_max = 255

distance_pixels = 168

# Drawing position of centroid circle - convert to int, pixels do not have floats
circleY_position = int(height / 2)

print(height)
print(width)

while True:
    centers = []

    rect_color = (0, 255, 0)

    ret, frame = capture.read()

    if not ret:
        break

    gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    gray = cv.GaussianBlur(gray, (21, 21), 0)

    difference = cv.absdiff(gray, first_gray)

    thresh = cv.threshold(difference, threshold_level, threshold_max, cv.THRESH_BINARY)[1]
    # Dilate the threshold source(input array), none in output(output array),
    # iterations = number of times dilation isa pplied
    thresh = cv.dilate(thresh, None, iterations=2)

    (contours, hierarchy) = cv.findContours(thresh.copy(), cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

    for c in contours:
        if cv.contourArea(c) < 1300:
            continue

        (x, y, w, h) = cv.boundingRect(c)

        cv.rectangle(frame, (x, y), (x + w, y + h), rect_color, 2)

        M = cv.moments(c)

        cX = int(M["m10"] / M["m00"])
        cY = int(M["m10"] / M["m00"])
        centers.append([cX, cY])

        cv.circle(frame, (cX, cY), 7, (255, 0, 255), -1)

        cv.putText(frame, "ID:", (cX - 20, cY - 20), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

        if len(centers) >= 2:
            # Distance y and x, [X][Y]
            dX = centers[0][0] - centers[1][0]
            dY = centers[0][1] - centers[1][1]
            D = np.sqrt(dX * dX + dY * dY)
            print(D)

            if D <= distance_pixels:
                cv.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
            else:
                cv.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    cv.imshow("frame", frame)
    cv.imshow("thresh", thresh)

    key = cv.waitKey(1) & 0xFF

    if key == ord('q'):
        break

capture.release()
cv.destroyAllWindows()
