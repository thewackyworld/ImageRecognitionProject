import cv2
import mediapipe as mp
import pyautogui
import threading

def scale(val, src, dst):
    return ((val - src[0]) / (src[1]-src[0])) * (dst[1]-dst[0]) + dst[0]

# Low-pass filter for smoothing the mouse movement
previous_x, previous_y = 0, 0
alpha = 0.6  # Smoothing factor, closer to 0 means more smoothing

def move():
    global previous_x, previous_y
    while running:
        
        mx = scale(x, (0, img_width), (0, 1920))
        my = scale(y, (0, img_height), (0, 1080))

        # Apply low-pass filter
        mx = alpha * mx + (1 - alpha) * previous_x
        my = alpha * my + (1 - alpha) * previous_y

        previous_x, previous_y = mx, my

        # Move the mouse with a smoother easing function
        if tx:
            pyautogui.dragTo(mx, my, duration=0.01, tween=pyautogui.easeInOutQuad, button="left")
            cv2.putText(img, 'CLICK!', (centx, centy), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0), 2)
        else:
            pyautogui.moveTo(mx,my)
       

def Thumb():
    click=False 
    thumb = hand_landmarks.landmark[mpHands.HandLandmark.THUMB_TIP]
    tx = int(thumb.x* img.shape[1])
    ty = int(thumb.y * img.shape[0])
    cv2.putText(img, 'thumb', (tx - 25, ty + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
    cv2.circle(img, (tx, ty), 4, (0, 0, 255), cv2.FILLED)
    cv2.putText(img, f'({tx},{ty})', (tx - 25, ty + 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
   
    if (abs(x-tx)<25) and (abs(y-ty)<25):
        click= True;
        
    return click;

def click():
    pyautogui.click();
    cv2.putText(img, 'CLICK!', (centx, centy), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0), 2)

mpHands = mp.solutions.hands
hands = mpHands.Hands(
    static_image_mode=False,
    model_complexity=1,
    min_detection_confidence=0.75,
    min_tracking_confidence=0.75,
    max_num_hands=1
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
            
            for hand_landmarks in results.multi_hand_landmarks:
                index = hand_landmarks.landmark[mpHands.HandLandmark.INDEX_FINGER_TIP]
                x = int(index.x* img.shape[1])
                y = int(index.y * img.shape[0])
                cv2.putText(img, 'Index', (x - 25, y + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
                cv2.circle(img, (x, y), 4, (0, 0, 255), cv2.FILLED)
                cv2.putText(img, f'({x},{y})', (x - 25, y + 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
                
                tx = Thumb();
            centx = int(img_width/2)
            centy = int(img_height/2)

            if(start == False):
                cv2.circle(img, (centx, centy), threashold, (0,0,255), 2)
                if x>centx-threashold and x<centx+threashold and y>centy-threashold and y<centy+threashold:
                    pyautogui.moveTo(1900/2, 1080/2)
                    start = True;

            if(start):
                if(times == 0):
                    t1 = threading.Thread(target=move)
                    t1.start()
                    times = 1;

        
        cv2.imshow('Hand Tracking', img)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            running = False
            t1.join();
            break

    cap.release()
    cv2.destroyAllWindows()
