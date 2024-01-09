'''  
Copyright (c) 2017 Intel Corporation.
Licensed under the MIT license. See LICENSE file in the project root for full license information.
'''

import cv2
import numpy as np
#import paho.mqtt.client as mqtt
import time
import argparse
from datetime import datetime
from pathlib import Path
import uvc
from time import sleep

def avg_circles(circles, b):
    avg_x=0
    avg_y=0
    avg_r=0
    for i in range(b):
        #optional - average for multiple circles (can happen when a gauge is at a slight angle)
        avg_x = avg_x + circles[0][i][0]
        avg_y = avg_y + circles[0][i][1]
        avg_r = avg_r + circles[0][i][2]
    avg_x = int(avg_x/(b))
    avg_y = int(avg_y/(b))
    avg_r = int(avg_r/(b))
    return avg_x, avg_y, avg_r

def dist_2_pts(x1, y1, x2, y2):
    #print np.sqrt((x2-x1)^2+(y2-y1)^2)
    return np.sqrt((x2 - x1)**2 + (y2 - y1)**2)

def calibrate_gauge(calibration_image_path):
    '''
        This function should be run using a test image in order to calibrate the range available to the dial as well as the
        units.  It works by first finding the center point and radius of the gauge.  Then it draws lines at hard coded intervals
        (separation) in degrees.  It then prompts the user to enter position in degrees of the lowest possible value of the gauge,
        as well as the starting value (which is probably zero in most cases but it won't assume that).  It will then ask for the
        position in degrees of the largest possible value of the gauge. Finally, it will ask for the units.  This assumes that
        the gauge is linear (as most probably are).
        It will return the min value with angle in degrees (as a tuple), the max value with angle in degrees (as a tuple),
        and the units (as a string).
    '''
    # calibration_image = "images/gauge-%s.%s" %(gauge_number, file_type)
    print(f"reading calibration image file: {calibration_image_path}")
    calibration_image_path = Path(calibration_image_path)
    img = cv2.imread(calibration_image_path.as_posix())
    height, width = img.shape[:2]
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  #convert to gray
    #gray = cv2.GaussianBlur(gray, (5, 5), 0)
    # gray = cv2.medianBlur(gray, 5)

    #for testing, output gray image
    #cv2.imwrite('gauge-%s-bw.%s' %(gauge_number, file_type),gray)

    #detect circles
    #restricting the search from 35-48% of the possible radii gives fairly good results across different samples.  Remember that
    #these are pixel values which correspond to the possible radii search range.
    # Adjust the min and max radius based on visual estimation of the gauge size
    min_radius = int(height * 0.3)  # 20% of the image height
    max_radius = int(height * 0.5)  # 30% of the image height

    # Adjust the minDist if necessary based on gauge size relative to the image size
    min_dist = 20  # This is just an example value

    # Adjust the high threshold for the Canny edge detector if the edges are not sharp
    canny_high_threshold = 75  # Example value, adjust as necessary

    # Adjust the accumulator threshold for detecting circle centers
    accumulator_threshold = 50  # Example value, adjust as necessary

    # The modified cv2.HoughCircles command
    circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1, min_dist, np.array([]),
                            canny_high_threshold, accumulator_threshold, min_radius, max_radius)
    # average found circles, found it to be more accurate than trying to tune HoughCircles parameters to get just the right one
    a, b, c = circles.shape
    x,y,r = avg_circles(circles, b)

    #draw center and circle
    cv2.circle(img, (x, y), r, (0, 0, 255), 3, cv2.LINE_AA)  # draw circle
    cv2.circle(img, (x, y), 2, (0, 255, 0), 3, cv2.LINE_AA)  # draw center of circle

    #for testing, output circles on image
    #cv2.imwrite('gauge-%s-circles.%s' % (gauge_number, file_type), img)
    new_filename = calibration_image_path.stem + "-circles" + calibration_image_path.suffix
    cv2.imwrite(new_filename, img)

    #for calibration, plot lines from center going out at every 10 degrees and add marker
    #for i from 0 to 36 (every 10 deg)

    '''
    goes through the motion of a circle and sets x and y values based on the set separation spacing.  Also adds text to each
    line.  These lines and text labels serve as the reference point for the user to enter
    NOTE: by default this approach sets 0/360 to be the +x axis (if the image has a cartesian grid in the middle), the addition
    (i+9) in the text offset rotates the labels by 90 degrees so 0/360 is at the bottom (-y in cartesian).  So this assumes the
    gauge is aligned in the image, but it can be adjusted by changing the value of 9 to something else.
    '''
    separation = 10.0 #in degrees
    interval = int(360 / separation)
    p1 = np.zeros((interval,2))  #set empty arrays
    p2 = np.zeros((interval,2))
    p_text = np.zeros((interval,2))
    for i in range(0,interval):
        for j in range(0,2):
            if (j%2==0):
                p1[i][j] = x + 0.9 * r * np.cos(separation * i * 3.14 / 180) #point for lines
            else:
                p1[i][j] = y + 0.9 * r * np.sin(separation * i * 3.14 / 180)
    text_offset_x = 10
    text_offset_y = 5
    for i in range(0, interval):
        for j in range(0, 2):
            if (j % 2 == 0):
                p2[i][j] = x + r * np.cos(separation * i * 3.14 / 180)
                p_text[i][j] = x - text_offset_x + 1.2 * r * np.cos((separation) * (i+9) * 3.14 / 180) #point for text labels, i+9 rotates the labels by 90 degrees
            else:
                p2[i][j] = y + r * np.sin(separation * i * 3.14 / 180)
                p_text[i][j] = y + text_offset_y + 1.2* r * np.sin((separation) * (i+9) * 3.14 / 180)  # point for text labels, i+9 rotates the labels by 90 degrees

    #add the lines and labels to the image
    for i in range(0,interval):
        cv2.line(img, (int(p1[i][0]), int(p1[i][1])), (int(p2[i][0]), int(p2[i][1])),(0, 255, 0), 2)
        cv2.putText(img, '%s' %(int(i*separation)), (int(p_text[i][0]), int(p_text[i][1])), cv2.FONT_HERSHEY_SIMPLEX, 0.3,(255,255,255),1,cv2.LINE_AA)

    new_filename = calibration_image_path.stem + "-calibration" + calibration_image_path.suffix
    cv2.imwrite(new_filename, img)
    

    #get user input on min, max, values, and units
    # print('gauge number: %s' %gauge_number)
    # min_angle = input('Min angle (lowest possible angle of dial) - in degrees: ') #the lowest possible angle
    # max_angle = input('Max angle (highest possible angle) - in degrees: ') #highest possible angle
    # min_value = input('Min value: ') #usually zero
    # max_value = input('Max value: ') #maximum reading of the gauge
    # units = input('Enter units: ')

    #for testing purposes: hardcode and comment out raw_inputs above
    min_angle = 90
    max_angle = 270
    min_value = 0
    max_value = 21
    units = "PSI"

    return min_angle, max_angle, min_value, max_value, units, x, y, r

def get_current_value(img, img_path, min_angle, max_angle, min_value, max_value, x, y, r):

    #for testing purposes
    #img = cv2.imread('gauge-%s.%s' % (gauge_number, file_type))

    img_path = Path(img_path)

    gray2 = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Set threshold and maxValue
    thresh = 150
    maxValue = 255

    # for testing purposes, found cv2.THRESH_BINARY_INV to perform the best
    # th, dst1 = cv2.threshold(gray2, thresh, maxValue, cv2.THRESH_BINARY)
    # th, dst2 = cv2.threshold(gray2, thresh, maxValue, cv2.THRESH_BINARY_INV)
    # th, dst3 = cv2.threshold(gray2, thresh, maxValue, cv2.THRESH_TRUNC)
    # th, dst4 = cv2.threshold(gray2, thresh, maxValue, cv2.THRESH_TOZERO)
    # th, dst5 = cv2.threshold(gray2, thresh, maxValue, cv2.THRESH_TOZERO_INV)
    # cv2.imwrite('gauge-%s-dst1.%s' % (gauge_number, file_type), dst1)
    # cv2.imwrite('gauge-%s-dst2.%s' % (gauge_number, file_type), dst2)
    # cv2.imwrite('gauge-%s-dst3.%s' % (gauge_number, file_type), dst3)
    # cv2.imwrite('gauge-%s-dst4.%s' % (gauge_number, file_type), dst4)
    # cv2.imwrite('gauge-%s-dst5.%s' % (gauge_number, file_type), dst5)

    # apply thresholding which helps for finding lines
    th, dst2 = cv2.threshold(gray2, thresh, maxValue, cv2.THRESH_BINARY_INV)

    adaptive_threshold_image = cv2.adaptiveThreshold(gray2, 255, 
                                                    cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                                    cv2.THRESH_BINARY, 11, 2)

    new_filename = img_path.stem + "-gray2" + img_path.suffix
    cv2.imwrite(new_filename, adaptive_threshold_image)

    # dst2 = adaptive_threshold_image

    new_filename = img_path.stem + "-gray" + img_path.suffix
    cv2.imwrite(new_filename, gray2)
    # import code
    # code.interact(local=locals())

    # found Hough Lines generally performs better without Canny / blurring, though there were a couple exceptions where it would only work with Canny / blurring
    #dst2 = cv2.medianBlur(dst2, 5)
    #dst2 = cv2.Canny(dst2, 50, 150)
    #dst2 = cv2.GaussianBlur(dst2, (5, 5), 0)

    # for testing, show image after thresholding
    new_filename = img_path.stem + "-tempdst2" + img_path.suffix
    cv2.imwrite(new_filename, dst2)
    # cv2.imwrite('gauge-%s-tempdst2.%s' % (gauge_number, file_type), dst2)

    # find lines
    minLineLength = 80
    maxLineGap = 20
    lines = cv2.HoughLinesP(image=dst2, rho=3, theta=np.pi / 180, threshold=100,minLineLength=minLineLength, maxLineGap=maxLineGap)  # rho is set to 3 to detect more lines, easier to get more then filter them out later

    #for testing purposes, show all found lines
    for i in range(0, len(lines)):
        for x1, y1, x2, y2 in lines[i]:
            cv2.line(img, (x1, y1), (x2, y2), (0, 255, 0), 2)

    new_filename = img_path.stem + "-lines-test" + img_path.suffix
    cv2.imwrite(new_filename, img)
    num_total_lines =  len(lines)
    print(f"Found {num_total_lines} total lines! Most are probably worthless!")

    # remove all lines outside a given radius
    final_line_list = []
    #print "radius: %s" %r

    diff1LowerBound = 0.01 #diff1LowerBound and diff1UpperBound determine how close the line should be from the center
    diff1UpperBound = 0.35
    diff2LowerBound = 0.01 #diff2LowerBound and diff2UpperBound determine how close the other point of the line should be to the outside of the gauge
    diff2UpperBound = 1.0
    for i in range(0, len(lines)):
        for x1, y1, x2, y2 in lines[i]:
            diff1 = dist_2_pts(x, y, x1, y1)  # x, y is center of circle
            diff2 = dist_2_pts(x, y, x2, y2)  # x, y is center of circle
            #set diff1 to be the smaller (closest to the center) of the two), makes the math easier
            if (diff1 > diff2):
                temp = diff1
                diff1 = diff2
                diff2 = temp
            # check if line is within an acceptable range
            if (((diff1<diff1UpperBound*r) and (diff1>diff1LowerBound*r) and (diff2<diff2UpperBound*r)) and (diff2>diff2LowerBound*r)):
                line_length = dist_2_pts(x1, y1, x2, y2)
                # add to final list
                final_line_list.append([x1, y1, x2, y2])
            else:
                # print("skiiping line!", x1, x2, y1, y2)
                pass

    #testing only, show all lines after filtering
    for i in range(0,len(final_line_list)):
        x1 = final_line_list[i][0]
        y1 = final_line_list[i][1]
        x2 = final_line_list[i][2]
        y2 = final_line_list[i][3]
        # Draw all filtered lines in GREEN
        cv2.line(img, (x1, y1), (x2, y2), (0, 255, 0), 2)

    num_filtered_lines =  len(final_line_list)
    if num_filtered_lines > 0:
        print(f"Found {num_filtered_lines} filtered lines! Success is in here somewhere!")
    else:
        print("NO LINES FOUND!")

    import code
    # code.interact(local=locals())

    for aline in final_line_list:
        # assumes the first line is the best one
        # x1 = final_line_list[0][0]
        # y1 = final_line_list[0][1]
        # x2 = final_line_list[0][2]
        # y2 = final_line_list[0][3]
        x1 = aline[0]
        y1 = aline[1]
        x2 = aline[2]
        y2 = aline[3]
        # Draw the chosen line in RED
        cv2.line(img, (x1, y1), (x2, y2), (0, 0, 255), 2)

        #for testing purposes, show the line overlayed on the original image
        # cv2.imwrite('gauge-1-test.jpg', img)
        # cv2.imwrite('gauge-%s-lines.%s' % (gauge_number, file_type), img)
        new_filename = img_path.stem + "-lines" + img_path.suffix
        cv2.imwrite(new_filename, img)

        #find the farthest point from the center to be what is used to determine the angle
        dist_pt_0 = dist_2_pts(x, y, x1, y1)
        dist_pt_1 = dist_2_pts(x, y, x2, y2)
        if (dist_pt_0 > dist_pt_1):
            x_angle = x1 - x
            y_angle = y - y1
        else:
            x_angle = x2 - x
            y_angle = y - y2
        # take the arc tan of y/x to find the angle
        res = np.arctan(np.divide(float(y_angle), float(x_angle)))
    #np.rad2deg(res) #coverts to degrees

    # print x_angle
    # print y_angle
    # print res
    # print np.rad2deg(res)

    #these were determined by trial and error
        res = np.rad2deg(res)
        if x_angle > 0 and y_angle > 0:  #in quadrant I
            final_angle = 270 - res
        if x_angle < 0 and y_angle > 0:  #in quadrant II
            final_angle = 90 - res
        if x_angle < 0 and y_angle < 0:  #in quadrant III
            final_angle = 90 - res
        if x_angle > 0 and y_angle < 0:  #in quadrant IV
            final_angle = 270 - res

        print(f"found gauge to be at angle: {final_angle}")

        old_min = float(min_angle)
        old_max = float(max_angle)

        new_min = float(min_value)
        new_max = float(max_value)

        old_value = final_angle

        old_range = (old_max - old_min)
        new_range = (new_max - new_min)
        new_value = (((old_value - old_min) * new_range) / old_range) + new_min

        # iterate until we find one in the specified range
        if min_value < new_value < max_value:
            break
        else:
            continue

    return new_value

def take_photo():
    file_type = "png"

    devices = uvc.device_list()
    cap = uvc.Capture(devices[0]["uid"])

    # set image size
    cap.frame_size = (1920, 1080)
    cap.controls[3].value = 1
    sleep(2)
    # cap.controls[2].value = 200

    # Do an initial frame to set the settings to be sane
    # cap.controls[3].value = 1
    # frame = cap.get_frame_robust()
    # frame = cap.get_frame_robust()
    # .... then change some stuff

    # for i in range(0,len(cap.controls)):
    #     print(f"{i} -- {cap.controls[i].doc}")
    #     print(cap.controls[i].value)

    # set autofocus off!
    cap.controls[3].value = 0
    # set absolute focus to 70!
    cap.controls[4].value = 70
    cap.controls[5].value = 200
    
    sleep(2)
    cap.controls[12].value = 0
    cap.controls[14].value = 0
    frame = cap.get_frame_robust()
    frame = frame.img
    # cap.stop_stream()
    # cap = cv2.VideoCapture(0)

    # if not cap.isOpened():
    #     print("Error: Camera not accessible")
    #     exit()
    # ret, frame = cap.read()
    img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    timestamp = str(int(datetime.timestamp(datetime.now())))
    image_path = f"images/gauge-{timestamp}.{file_type}"
    cv2.imwrite(image_path, img)
    return image_path, img

def zoom_to_gauge(image_path):
    img = cv2.imread(image_path)
    original_image_path = Path(image_path)
    height, width = img.shape[:2]
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
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
    
    print(circles)
    circles = np.round(circles[0, :]).astype("int")
    a,b,c = circles[0]

    # Calculate the top-left and bottom-right coordinates for the cropping rectangle

    cv2.circle(img, (a, b), c, (0, 0, 255), 3)
    cv2.circle(img, (a, b), 2, (255, 0, 255), -1)
    new_filename = original_image_path.stem + "-circles" + original_image_path.suffix

    cv2.imwrite(new_filename, img)

    mask = np.zeros(img.shape[:2], dtype=np.uint8)
    cv2.circle(mask, (a, b), c, 1, thickness=-1)  # Fill the circle with white (1)

    # Invert the mask to create a mask for the background
    background_mask = cv2.bitwise_not(mask)

    # Create an image with the background color you want (e.g., blue)
    background_color = [0, 0, 0]  # Change to the color you want (BGR format)
    background_img = np.full(img.shape, background_color, dtype=np.uint8)

    # Apply the mask to the original image to keep only the circle area
    img_with_circle = cv2.bitwise_and(img, img, mask=mask)

    # Apply the inverted mask to the background image to keep only the background area
    background = cv2.bitwise_and(background_img, background_img, mask=background_mask)

    # Combine the two images: the image with the circle and the background
    final_img = cv2.add(img_with_circle, background)

    new_filename = original_image_path.stem + "-focused1" + original_image_path.suffix
    new_filename = original_image_path.stem + "-focused" + original_image_path.suffix

    # Save the final image
    cv2.imwrite(new_filename, final_img)


    # Crop image
    x1 = max(a - c - 20, 0)  # Ensure the coordinate doesn't go beyond the image boundary
    y1 = max(b - c - 20, 0)
    x2 = min(a + c + 20, img.shape[1])  # Ensure the coordinate doesn't go beyond the image width
    y2 = min(b + c + 20, img.shape[0])  # Ensure the coordinate doesn't go beyond the image height

    # Crop the image using calculated coordinates
    cropped_img = final_img[y1:y2, x1:x2]
    new_filename = original_image_path.stem + "-cropped" + original_image_path.suffix

    # Save the cropped image
    cv2.imwrite(new_filename, cropped_img)
    return new_filename, cropped_img

def focus_on_gauge():
    pass


def main():
    parser = argparse.ArgumentParser(description="Process a filename.")
    parser.add_argument("file_base", help="The base-name of the file to process")
    parser.add_argument("file_number", help="The number of the file to process")
    parser.add_argument("file_type", help="The type (png or jpeg) of the file to process")
    parser.add_argument("take_photo", help="Ingest camera data from camera?", default=None)


    args = parser.parse_args()
    gauge_file_base = args.file_base
    gauge_number = args.file_number
    file_type = args.file_type
    take_photo = bool(args.take_photo)

    if take_photo:
        cap = cv2.VideoCapture(0)

        if not cap.isOpened():
            print("Error: Camera not accessible")
            exit()
        ret, frame = cap.read()
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        gauge_number = str(int(datetime.timestamp(datetime.now())))
        cv2.imwrite(f"images/{gauge_file_base}-{gauge_number}.{file_type}", img)
    else:
        img_path = f"images/{gauge_file_base}-{gauge_number}.{file_type}"
        print(f"Reading image: {img_path}")
        img = cv2.imread(img_path)

    # name the calibration image of your gauge 'gauge-#.jpg', for example 'gauge-5.jpg'.  It's written this way so you can easily try multiple images
    min_angle, max_angle, min_value, max_value, units, x, y, r = calibrate_gauge(gauge_number, file_type)

    # feed an image (or frame) to get the current value, based on the calibration, by default uses same image as calibration

    # val = get_current_value(img, min_angle, max_angle, min_value, max_value, x, y, r, gauge_number, file_type)
    # print("Current reading: %s %s" %(val, units))

if __name__=='__main__':
    # main()
    photo_path, photo  = take_photo()
    zoomed_image_path, zoomed_img = zoom_to_gauge(photo_path)
    min_angle, max_angle, min_value, max_value, units, x, y, r = calibrate_gauge(zoomed_image_path)
    val = get_current_value(zoomed_img, zoomed_image_path, min_angle, max_angle, min_value, max_value, x, y, r)
    print("Current reading: %s %s" %(val, units))
    # import code
    # code.interact(local=locals())
   	
