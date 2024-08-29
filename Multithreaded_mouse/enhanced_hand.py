import cv2
import mediapipe as mp
import pyautogui
import threading
import time

class HandMouseController:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(
            static_image_mode=False,
            model_complexity=1,
            min_detection_confidence=0.75,
            min_tracking_confidence=0.75,
            max_num_hands=1
        )
        self.running = True
        self.start = False
        self.previous_x, self.previous_y = 0, 0
        self.alpha = 0.6  # Increased smoothing factor to reduce lag
        self.thread_started = False

    def scale(self, val, src, dst):
        return ((val - src[0]) / (src[1]-src[0])) * (dst[1]-dst[0]) + dst[0]

    def move(self):
        while self.running:
            mx = self.scale(self.x, (0, self.img_width), (0, 1900))
            my = self.scale(self.y, (0, self.img_height), (0, 1080))

            # Apply low-pass filter
            mx = self.alpha * mx + (1 - self.alpha) * self.previous_x
            my = self.alpha * my + (1 - self.alpha) * self.previous_y

            self.previous_x, self.previous_y = mx, my

            # Directly move the mouse without delay
            if self.thumb_near:
                pyautogui.dragTo(mx, my, button="left")
            else:
                pyautogui.moveTo(mx,my)
            # Removed the sleep delay for more responsiveness

            # if self.thumb_near:
            #     self.click()

    def click(self):
        pyautogui.click()

    def process_frame(self):
        success, img = self.cap.read()
        if not success:
            print("Failed to read from camera.")
            return None

        img = cv2.flip(img, 1)
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = self.hands.process(imgRGB)
        self.img_height, self.img_width, _ = img.shape

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                index = hand_landmarks.landmark[self.mpHands.HandLandmark.INDEX_FINGER_TIP]
                self.x = int(index.x * img.shape[1])
                self.y = int(index.y * img.shape[0])
                cv2.putText(img, 'Index', (self.x - 25, self.y + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
                cv2.circle(img, (self.x, self.y), 4, (0, 0, 255), cv2.FILLED)
                cv2.putText(img, f'({self.x},{self.y})', (self.x - 25, self.y + 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
                
                thumb = hand_landmarks.landmark[self.mpHands.HandLandmark.THUMB_TIP]
                tx = int(thumb.x * img.shape[1])
                ty = int(thumb.y * img.shape[0])
                self.thumb_near = (abs(self.x - tx) < 50) or (abs(self.y - ty) < 50)

            centx, centy = self.img_width // 2, self.img_height // 2
            if not self.start:
                cv2.circle(img, (centx, centy), 100, (0, 0, 255), 2)
                if centx - 100 < self.x < centx + 100 and centy - 100 < self.y < centy + 100:
                    pyautogui.moveTo(1900 / 2, 1080 / 2)
                    self.start = True

            if self.start and not self.thread_started:
                self.thread_started = True
                threading.Thread(target=self.move).start()

        return img

    def run(self):
        while True:
            img = self.process_frame()
            if img is None:
                break

            cv2.imshow('Hand Tracking', img)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.running = False
                break

        self.cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    controller = HandMouseController()
    controller.run()
