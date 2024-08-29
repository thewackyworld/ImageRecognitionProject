import time
import cv2



def check(x, y, cx, cy, img, threashold):
    while (x < cx-threashold):
        cv2.putText(img, 'Move Right...', (cx-25, cy+50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)

    while (x > cx+threashold):
        cv2.putText(img, 'Move Left...', (cx-25, cy+50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
        

    while (y < cy-150):
        cv2.putText(img, 'Move Down...', (cx-25, cy+50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)

    while (y > cy+threashold):
        cv2.putText(img, 'Move Up...', (cx-25, cy+50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
