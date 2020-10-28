import numpy as np
import cv2 as cv
import turtle

capture = cv.VideoCapture(1)
ret, first = capture.read()

first_gray = cv.cvtColor(first, cv.COLOR_BGR2GRAY)
first_gray = cv.GaussianBlur(first_gray, (21, 21), 0)

height = first_gray.shape[0]
width = first_gray.shape[1]

threshold_level = 60
threshold_max = 255

distance_pixels = 160

personID = 0
currentPerson = []

D = 1000

cX = 0
cY = 0

# Distance hit, true or not
hit = False

# Drawing position of centroid circle - convert to int, pixels do not have floats
circleY_position = int(height / 2)

print(height)
print(width)

# Turtle variables (Graphics)
window = turtle.Screen()
window.setup(width=1.0, height=1.0)
window.mode("world")
window.setworldcoordinates(0, window.window_height(), window.window_width(), 0)
window.bgcolor("black")
window.screensize()
# window.setup(640, 480)


def buttonclick(x, y):
    print("You clicked at this coordinate({0},{1})".format(x, y))

    # onscreen function to send coordinate


turtle.onscreenclick(buttonclick, 1)

print(window.screensize())

t = turtle.Turtle()
t.shape("circle")
t.color("green", "black")
t.penup()  # Prevent drawing lines
# stretch_wid, stretch_len, outline
t.turtlesize(10, 10, 10)

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
    # iterations = number of times dilation is applied
    thresh = cv.dilate(thresh, None, iterations=2)

    (contours, hierarchy) = cv.findContours(thresh.copy(), cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

    for i in range(len(contours)):
        personID = i
        currentPerson = contours[i]

    for c in contours:
        if cv.contourArea(c) < 1300:
            continue

        (x, y, w, h) = cv.boundingRect(c)

        # Change rect color if distance is not held
        if D <= distance_pixels:
            cv.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
            hit = True
        else:
            cv.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            hit = False

        M = cv.moments(c)

        cX = int(M["m10"] / M["m00"])
        cY = int(M["m01"] / M["m00"])
        centers.append([cX, cY])

        cv.circle(frame, (cX, cY), 7, (255, 0, 255), -1)

        cv.putText(frame, "ID:", (cX - 20, cY - 20), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

    if len(centers) >= 2:
        # Distance y and x, [X][Y]
        dX = centers[0][0] - centers[1][0]
        dY = centers[0][1] - centers[1][1]
        D = np.sqrt(dX * dX + dY * dY)
        # print(D)

    cv.imshow("frame", frame)
    cv.imshow("thresh", thresh)

    #print(cX)

    # Turtle x drawing position
    if cX > 195 and cX < 475:
        t.goto(cX * 3, 0)

    # Turtle color change
    if hit:
        t.color("red", "black")
    else:
        t.color("green", "black")

    key = cv.waitKey(1) & 0xFF

    if key == ord('q'):
        break


capture.release()
cv.destroyAllWindows()