import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import pyautogui
import time

# Initialize the gesture recognizer
base_options = python.BaseOptions(model_asset_path='gesture_recognizer.task')
options = vision.GestureRecognizerOptions(base_options=base_options)
recognizer = vision.GestureRecognizer.create_from_options(options)


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
        #creates an image object
        mp_img = mp.Image(image_format=mp.ImageFormat.SRGB, data=imgRGB)

        #preform the recognition
        start_time = time.time()
        results = recognizer.recognize(mp_img)
        end_time = time.time()

        # Process the results
        if results.gestures:
          top_gesture = results.gestures[0][0]
          index = results.gestures[0][0].index
          print(f"Gesture: {top_gesture.category_name}, Gesture Index: {index}, Score: {top_gesture.score:.2f}")

          cv2.putText(img, top_gesture.category_name, (0, 500), cv2.FONT_HERSHEY_SIMPLEX, 2, (0,0,0), 2)


        cv2.imshow('Hand Tracking', img)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
