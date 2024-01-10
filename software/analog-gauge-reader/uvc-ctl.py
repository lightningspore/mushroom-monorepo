import uvc
import cv2
# from matplotlib import pyplot as plt


devices = uvc.device_list()
cap = uvc.Capture(devices[1]["uid"])
cap.frame_size = (1920, 1080)
frame = cap.get_frame_robust()





# set zoom value
# cap.controls[5].value = 200
# frame = cap.get_frame_robust()

# cv2.imwrite("test.png", frame.img)

# set absolute focus value
cap.controls[3].value = 0
cap.controls[4].value = 70
frame = cap.get_frame_robust()
cv2.imwrite("test3.png", frame.img)

from time import sleep
# for i in range(0,100,10):
#     print(f"taking image with focus: {i}")
#     cap.controls[4].value = i
#     sleep(1)
#     frame = cap.get_frame_robust()
#     cv2.imwrite(f"test{i/10}.png", frame.img) 



for i in range(0,len(cap.controls)):
    i
    cap.controls[i].doc


# plt.ion()


import code
code.interact(local=locals())
# while True:
#     plt.imshow(frame.img)
#     plt.title('Image Preview')
#     plt.axis('off')  # Turn off axis numbers
#     plt.show()
#     code.interact(local=locals())