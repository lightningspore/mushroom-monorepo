import cv2
import numpy as np
#import paho.mqtt.client as mqtt
import time
import argparse


ret, frame = cap.read()
img = cv2.imgread()

img = frame.copy()
height, width = img.shape[:2]
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

cv2.imwrite(f'output.png', frame)




min_radius = int(height * 0.1)  # 20% of the image height
max_radius = int(height * 0.5)  # 30% of the image height

# Adjust the minDist if necessary based on gauge size relative to the image size
min_dist = 50  # This is just an example value

# Adjust the high threshold for the Canny edge detector if the edges are not sharp
canny_high_threshold = 125  # Example value, adjust as necessary

# Adjust the accumulator threshold for detecting circle centers
accumulator_threshold = 120  # Example value, adjust as necessary

# The modified cv2.HoughCircles command
circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1, min_dist, np.array([]),
                        canny_high_threshold, accumulator_threshold, min_radius, max_radius)

# Assuming circles is not None and contains detected circles
# if circles is not None:
#     circles = np.round(circles[0, :]).astype("int")
#     for (x, y, r) in circles:
#         # Draw a small circle (dot) at the center of the detected circle
#         # The color is set to red (0, 0, 255) and thickness to -1 to fill the circle
#         cv2.circle(img, (x, y), r, (0, 0, 255), 1)

# # Save the image with the dots
# cv2.imwrite('output_with_dots.png', img)

circles = np.round(circles[0, :]).astype("int")
a,b,c = circles[0]

    # Calculate the top-left and bottom-right coordinates for the cropping rectangle

cv2.circle(img, (a, b), c, (0, 0, 255), 3)
cv2.circle(img, (a, b), 2, (255, 0, 255), -1)
cv2.imwrite('output_with_dots2.png', img)


x1 = max(a - c - 50, 0)  # Ensure the coordinate doesn't go beyond the image boundary
y1 = max(b - c - 50, 0)
x2 = min(a + c + 50, img.shape[1])  # Ensure the coordinate doesn't go beyond the image width
y2 = min(b + c + 50, img.shape[0])  # Ensure the coordinate doesn't go beyond the image height

# Crop the image using calculated coordinates
cropped_img = img[y1:y2, x1:x2]

# Save the cropped image
cv2.imwrite('cropped_output.png', cropped_img)



minLineLength = 120
maxLineGap = 10
lines = cv2.HoughLinesP(image=closing, rho=3, theta=np.pi / 180, threshold=80, minLineLength=minLineLength, maxLineGap=maxLineGap)  # rho is set to 3 to detect more lines, easier to get more then filter them out later

for i in range(0, len(lines)):
    for x1, y1, x2, y2 in lines[i]:
        cv2.line(img, (x1, y1), (x2, y2), (0, 255, 0), 2)

cv2.imwrite('gauge-69-lines-test.png', img)
num_total_lines =  len(lines)
print(f"Found {num_total_lines} total lines! Most are probably worthless!")
