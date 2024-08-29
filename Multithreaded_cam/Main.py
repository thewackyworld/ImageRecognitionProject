import cv2
import mediapipe as mp
import pyautogui
import time
import threading


def check(x, y, cx, cy, img, threashold, left):

    if (x < cx-threashold):
        cv2.putText(img, 'Move left...', (cx-25, cy+50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
        pyautogui.keyDown("left");
    else:
        pyautogui.keyUp("left");
    if (x > cx+threashold):
        cv2.putText(img, 'Move right...', (cx-25, cy+50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
        pyautogui.keyDown("right");
    else:
        pyautogui.keyUp("right");

    if (y < cy-150):
        cv2.putText(img, 'Move up...', (cx-25, cy+50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
        pyautogui.keyDown("up");
    else:
        pyautogui.keyUp("up");

    if (y > cy+threashold):
        cv2.putText(img, 'Move down...', (cx-25, cy+50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
        pyautogui.keyDown("down");
    else:
        pyautogui.keyUp("down");

# def quit(left):
#     while left:
#         time.sleep(3);
#         pyautogui.press("q");


# def Drawing():
if __name__ == "__main__":
    mpPose = mp.solutions.pose
    pose = mpPose.Pose(static_image_mode=False, model_complexity=1)
    order = ""
    cap = cv2.VideoCapture(0)
    global img
    threashold = 100;
    go = True;
    left = False;
    avg_x=0; avg_y=0; centx=0; centy = 0;

    while go:
        success, img = cap.read()
        img = cv2.flip(img, 1)
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = pose.process(imgRGB)

        if results.pose_landmarks:
            # Get the image dimensions
            img_height, img_width, _ = img.shape

            # Calculate the minimum and maximum coordinates
            min_x = max(0, int(min(landmark.x * img_width for landmark in results.pose_landmarks.landmark)))
            max_x = min(img_width, int(max(landmark.x * img_width for landmark in results.pose_landmarks.landmark)))
            max_y = min(img_height, int(max(landmark.y * img_height for landmark in results.pose_landmarks.landmark)))
            min_y = min(landmark.y * img.shape[0] for landmark in results.pose_landmarks.landmark)
            
            avg_x = int((max_x+min_x)/2)
            avg_y = int((max_y+min_y)/2)-100

            centx = int(img_width/2)
            centy = int(img_height/2)

            cv2.circle(img, (centx, centy), threashold, (0,0,255), 2)
            cv2.circle(img, (avg_x, avg_y), 4, (0,0,255), cv2.FILLED)
            cv2.rectangle(img, (int(min_x), int(min_y)), (int(max_x), int(max_y)), (0, 255, 0), 2)

            t2 = threading.Thread(target=check, args=(avg_x, avg_y, centx, centy, img, threashold, left))
            #t3 = threading.Thread(target=quit, args=(left))

            t2.start()
            #t3.start()

        cv2.imshow('pose Tracking', img)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("******QUITING********")
            go = False

    cap.release()
    cv2.destroyAllWindows()



# if __name__ == "__main__":
#     t1 = threading.Thread(target=Drawing)


#     t1.start()

#     t1.join()