import cv2
import mediapipe as mp
import pyautogui
import threading
import time

# Low-pass filter for smoothing the mouse movement
prev_x, prev_y = 0, 0
alpha = 0.6  # Smoothing factor, closer to 0 means more smoothing
sensitivity = 2
pyautogui.FAILSAFE = False
clicking = False
on = True
clock = False

def move():
    global prev_x, prev_y
    while on:
        while running:
            # Apply low-pass filter
            mx = alpha * x + (1 - alpha) * prev_x
            my = alpha * y + (1 - alpha) * prev_y

            # mx = x; my = y;
            dx = (mx - prev_x) * sensitivity
            dy = (my - prev_y) * sensitivity

            prev_x, prev_y = mx, my

            if clock:
                if not (clicking):
                    pyautogui.mouseDown()
                    clicking = True
                pyautogui.move(dx,dy, duration=0.1, tween=pyautogui.easeInOutQuad, _pause=False)

            elif not (clock):
                pyautogui.mouseUp()
                pyautogui.move(dx,dy, duration=0.1, tween=pyautogui.easeInOutQuad, _pause=False)
                clicking = False
        
def Thumb():
    global clock;
    click=False 
    thumb = hand_landmarks.landmark[mpHands.HandLandmark.THUMB_TIP]
    tx = int(thumb.x* img.shape[1])
    ty = int(thumb.y * img.shape[0])
    
    if (abs(ix-tx)<40) and (abs(iy-ty)<40):
        click= True;
    if (abs(ix-tx)<100) and (abs(iy-ty)>100):
        click= False;
        
    clock = click;

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

if __name__ == "__main__":
    while True:
        success, img = cap.read()
        img = cv2.flip(img, 1)
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = hands.process(imgRGB)

        if results.multi_hand_landmarks:
            img_height, img_width, _ = img.shape
            running = True
            for hand_landmarks in results.multi_hand_landmarks:
                Middle = hand_landmarks.landmark[mpHands.HandLandmark.MIDDLE_FINGER_MCP]
                x = int(Middle.x* img.shape[1])
                y = int(Middle.y * img.shape[0])+50

                index = hand_landmarks.landmark[mpHands.HandLandmark.INDEX_FINGER_TIP]
                ix = int(index.x* img.shape[1])
                iy = int(index.y * img.shape[0])

            centx = int(img_width/2)
            centy = int(img_height/2)

            if(start == False):                
                if x>centx-threashold and x<centx+threashold and y>centy-threashold and y<centy+threashold:
                    start = True;

            if(start):
                if(times == 0):
                    t1 = threading.Thread(target=move)
                    t2 = threading.Thread(target=Thumb)
                    t1.start()
                    t2.start()
                    times = 1;
        else:
            running = False

        if cv2.waitKey(1) & 0xFF == ord('q'):
            on = False
            t1.join();
            break

    cap.release()
