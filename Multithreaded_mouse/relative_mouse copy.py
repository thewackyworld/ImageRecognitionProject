import cv2
import mediapipe as mp
import pyautogui
import threading
import time

def scale(val, src, dst):
    return ((val - src[0]) / (src[1]-src[0])) * (dst[1]-dst[0]) + dst[0]

# Low-pass filter for smoothing the mouse movement
prev_x, prev_y = 0, 0
alpha = 0.6  # Smoothing factor, closer to 0 means more smoothing
sensitivity = 2
pyautogui.FAILSAFE = False
clicking = False
on = True

def move():
    global prev_x, prev_y
    time.sleep(0.5)
    while on:
        while running:

            # Apply low-pass filter
            mx = alpha * x + (1 - alpha) * prev_x
            my = alpha * y + (1 - alpha) * prev_y

            # if prev_x is not None and prev_y is not None:
            #     # Calculate the difference in position (dx, dy)
            dx = (mx - prev_x) * sensitivity
            dy = (my - prev_y) * sensitivity

            prev_x, prev_y = mx, my

            # Move the mouse with a smoother easing function
            if tx:
                if not (clicking):
                    pyautogui.mouseDown()
                    clicking = True
                pyautogui.move(dx,dy, tween=pyautogui.easeInOutQuad, _pause=False)
                cv2.putText(img, 'CLICK!', (centx, centy), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0), 2)
            elif not (tx):
                pyautogui.mouseUp()
                pyautogui.move(dx,dy, tween=pyautogui.easeInOutQuad, _pause=False)
                clicking = False
        

def Thumb():
    click=False 
    thumb = hand_landmarks.landmark[mpHands.HandLandmark.THUMB_TIP]
    tx = int(thumb.x* img.shape[1])
    ty = int(thumb.y * img.shape[0])
    
    if (abs(ix-tx)<40) and (abs(iy-ty)<40):
        click= True;
    if (abs(ix-tx)<100) and (abs(iy-ty)>100):
        click= False;
        
    return click;

def click():
    pyautogui.click();
    cv2.putText(img, 'CLICK!', (centx, centy), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0), 2)

mpHands = mp.solutions.hands
mpDrawing = mp.solutions.drawing_utils
mpDrawingStyle = mp.solutions.drawing_styles

hands = mpHands.Hands(
    static_image_mode=False,
    model_complexity=1,
    min_detection_confidence=0.75,
    min_tracking_confidence=0.75,
    max_num_hands=2
)

z =0;
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
                cv2.circle(img, (x, y), 10, (255, 255, 255), cv2.FILLED)

                index = hand_landmarks.landmark[mpHands.HandLandmark.INDEX_FINGER_TIP]
                ix = int(index.x* img.shape[1])
                iy = int(index.y * img.shape[0])
                
                mpDrawing.draw_landmarks(img,
                    hand_landmarks,
                    mpHands.HAND_CONNECTIONS,
                    mpDrawingStyle.get_default_hand_landmarks_style(),
                    mpDrawingStyle.get_default_hand_connections_style())

                tx = Thumb();
            centx = int(img_width/2)
            centy = int(img_height/2)

            if(start == False):
                cv2.circle(img, (centx, centy), threashold, (0,0,255), 2)
                if x>centx-threashold and x<centx+threashold and y>centy-threashold and y<centy+threashold:
                    start = True;

            if(start):
                if(times == 0):
                    t1 = threading.Thread(target=move)
                    t1.start()
                    times = 1;
        else:
            running = False

        cv2.imshow('Hand Tracking', img)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            on = False
            t1.join();
            break

    cap.release()
    cv2.destroyAllWindows()
