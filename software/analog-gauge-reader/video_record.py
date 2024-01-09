import cv2
import numpy as np
import datetime
from time import sleep

def zoom_image(image, zoom_factor=2):
    """
    Zooms in on the center of the image.
    Zoom factor: 1 = original size, 2 = double size, etc.
    """
    height, width = image.shape[:2]
    new_height, new_width = int(height / zoom_factor), int(width / zoom_factor)

    # Calculating the center of the image
    center_x, center_y = int(width / 2), int(height / 2)

    # Crop the center of the image
    cropped = image[center_y - new_height // 2:center_y + new_height // 2,
                    center_x - new_width // 2:center_x + new_width // 2]

    # Resizing cropped image back to original size
    return cv2.resize(cropped, (width, height))

def crop_image(image):
    height, width = image.shape[:2]
    cropped = image[654:1200,210:748]
    return cv2.resize(cropped, (width, height))

# Start the camera
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Camera not accessible")
    exit()

counter = 0
while True:

    ret, frame = cap.read()
    timenow = datetime.datetime.now().replace(microsecond=0).isoformat()

    if ret:
        # Show the captured frame
        # cv2.imshow('Captured Image', frame)
        # cv2.waitKey(0)

        # Apply zoom and show the zoomed image
        # zoomed_frame = zoom_image(frame, zoom_factor=2)
        # cv2.imshow('Zoomed Image', zoomed_frame)
        # cv2.waitKey(0)
        # cont = input("save a shot? y/n")
        cv2.imwrite(f'output.png', frame)
        cropped_frame = zoom_image(frame)
        cv2.imwrite(f'output-cropped.png', cropped_frame)
        sleep(1)
        # counter += 1
        # if counter == 5:
        #     filename = f'{timenow}.png'
        #     cv2.imwrite(filename, frame)
        #     counter = 0
        #     print(f"saved image as: {filename}")

        

# Release the camera and close all OpenCV windows
cap.release()
cv2.destroyAllWindows()
