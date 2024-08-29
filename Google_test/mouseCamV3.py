import cv2
import mediapipe as mp
import pyautogui
import threading
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import time

# Initialize the gesture recognizer
base_options = python.BaseOptions(model_asset_path='gesture_recognizer.task')
options = vision.GestureRecognizerOptions(base_options=base_options)
recognizer = vision.GestureRecognizer.create_from_options(options)

# Low-pass filter for smoothing the mouse movement
prev_x, prev_y = 0, 0
alpha = 0.4  # Smoothing factor, closer to 0 means more smoothing
sensitivity = 2.6 #1.6
pyautogui.FAILSAFE = False
clicking = False
on = True

# Initialize the image 
mpHands = mp.solutions.hands
mpDrawing = mp.solutions.drawing_utils
mpDrawingStyle = mp.solutions.drawing_styles
hands = mpHands.Hands(
    static_image_mode=False,
    model_complexity=1,
    min_detection_confidence=0.75,
    min_tracking_confidence=0.75,
    max_num_hands=1
)
cap = cv2.VideoCapture(0)
threashold = 100;
start = False;
running = True;
times = 0;
tx=False;

def scale(val, src, dst):
    return ((val - src[0]) / (src[1]-src[0])) * (dst[1]-dst[0]) + dst[0]

def move(): #THREAD 1
    global prev_x, prev_y
    global running, on
    #time.sleep(0.5)
    while on:
        while running:
            mx = scale(x, (0, img_width), (0, 1920))
            my = scale(y, (0, img_height), (0, 1080))

            # Apply low-pass filter
            mx = alpha * mx + (1 - alpha) * prev_x
            my = alpha * my + (1 - alpha) * prev_y

            # Calculate the difference in position (dx, dy)
            dx = (mx - prev_x) * sensitivity
            dy = (my - prev_y) * sensitivity

            prev_x, prev_y = mx, my

            # Move the mouse with a smoother easing function
            
            if tx:
                if not (clicking):
                    pyautogui.mouseDown(_pause=False)
                    clicking = True
                cv2.putText(img, 'CLICK!', (centx, centy), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0), 2)
            elif not (tx):
                pyautogui.mouseUp(_pause=False)
                clicking = False
            pyautogui.move(dx,dy, tween=pyautogui.easeInOutQuad, _pause=False)

def Read(): #THREAD 2
    global running, on
    global tx

    while on:
    #preform the recognition
        gesture = recognizer.recognize(mp_img)
        #time.sleep(0.08)
        if gesture.gestures:
            top_gesture = gesture.gestures[0][0]
            cv2.putText(img, top_gesture.category_name, (0, 500), cv2.FONT_HERSHEY_SIMPLEX, 2, (0,0,0), 2)
            if(top_gesture.category_name == "Open_Palm"):
                running = True
                tx = False
                pyautogui.keyUp('ctrl')
                pyautogui.keyUp('up')
            elif(top_gesture.category_name == "None"):
                running = False
                tx = False
            elif(top_gesture.category_name == "Thumb_Up"):
                running = False
                tx = False
                pyautogui.keyUp('ctrl')
                pyautogui.keyUp('up')
                pyautogui.scroll(3, _pause=False)
            elif(top_gesture.category_name == "Thumb_Down"):
                running = False
                tx = False
                pyautogui.keyUp('ctrl')
                pyautogui.keyUp('up')
                pyautogui.scroll(-3, _pause=False)
            elif(top_gesture.category_name == "Closed_Fist"):
                tx = True
                pyautogui.keyUp('ctrl')
                pyautogui.keyUp('up')
            elif(top_gesture.category_name == "Pointing_Up"):
                running = False
                tx = False
                pyautogui.leftClick(_pause=False)
                pyautogui.keyUp('ctrl')
                pyautogui.keyUp('up')
            elif(top_gesture.category_name == "Victory"):
                tx = False
                running = True
                pyautogui.keyDown('ctrl')
                pyautogui.keyDown('up')

def Track():
    global on
    while on:
        myx, myy = pyautogui.position()
        cv2.circle(img, (myx, myy), 10, (0, 255, 255), 1)

if __name__ == "__main__": #MAIN THREAD
    while True:
        success, img = cap.read()
        img = cv2.flip(img, 1)
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        mp_img = mp.Image(image_format=mp.ImageFormat.SRGB, data=imgRGB)
        results = hands.process(imgRGB)
        
        if results.multi_hand_landmarks:
            img_height, img_width, _ = img.shape
            running = True
            for hand_landmarks in results.multi_hand_landmarks:
                Middle = hand_landmarks.landmark[mpHands.HandLandmark.MIDDLE_FINGER_MCP]
                x = int(Middle.x* img.shape[1])
                y = int(Middle.y * img.shape[0])+50
                cv2.circle(img, (x, y), 10, (255, 255, 255), cv2.FILLED)
                
                mpDrawing.draw_landmarks(img,
                    hand_landmarks,
                    mpHands.HAND_CONNECTIONS,
                    mpDrawingStyle.get_default_hand_landmarks_style(),
                    mpDrawingStyle.get_default_hand_connections_style())

            centx = int(img_width/2)
            centy = int(img_height/2)

            if(start == False):
                cv2.circle(img, (centx, centy), threashold, (0,0,255), 2)
                if x>centx-threashold and x<centx+threashold and y>centy-threashold and y<centy+threashold:
                    start = True;

            if(start):
                if(times == 0):
                    pyautogui.moveTo(scale(x, (0, img_width), (0, 1920)), scale(y, (0, img_height), (0, 1920)), _pause=False)
                    t1 = threading.Thread(target=move)
                    t2 = threading.Thread(target=Read)
                    #t3 = threading.Thread(target=Track)
                    t2.start()
                    t1.start()
                    #t3.start()

                    times = 1;

        else:
            running = False

        img2 = cv2.resize(img, None, fx=0.25, fy=0.25)
        cv2.imshow('Hand Tracking', img2)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            running = False
            on = False
            t1.kill();
            t1.join();
            t2.join();
            break

    cap.release()
    cv2.destroyAllWindows()
