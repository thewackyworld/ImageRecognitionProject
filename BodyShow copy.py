import cv2
import mediapipe as mp
import pyautogui
import time

mpPose = mp.solutions.pose
pose = mpPose.Pose(static_image_mode=False, model_complexity=1)
threashold = 100
order = ""

stime = 0;
cap = cv2.VideoCapture(0)

def check(x, y, cx, cy):
    if (x < cx-threashold):
        cv2.putText(img, 'Move Right...', (cx-25, cy+50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
        # time = 0;

    if (x > cx+threashold):
        stime =time.time();
        cv2.putText(img, 'Move Left...', (cx-25, cy+50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)

    if (y < cy-150):
        cv2.putText(img, 'Move Down...', (cx-25, cy+50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
        # time = 0;

    if (y > cy+threashold):
        cv2.putText(img, 'Move Up...', (cx-25, cy+50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
        # time = 0;
    # else:
        # time = 0;


while True:
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

        check(avg_x, avg_y, centx, centy);


        
    cv2.imshow('Hand Tracking', img)

    if((time.time())-stime>20000 ):
        pyautogui.press("q");
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("******QUITING********")
        break

cap.release()
cv2.destroyAllWindows()


