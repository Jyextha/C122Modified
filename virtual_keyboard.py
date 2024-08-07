import cv2
import mediapipe as mp
from pynput.keyboard import Key, Controller
import pyautogui
from time import sleep

keyboard = Controller()

cap = cv2.VideoCapture(0)
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

hands = mp_hands.Hands(min_detection_confidence=0.8, min_tracking_confidence=0.5)

tipIds = [4, 8, 12, 16, 20]

# Initialize the state variable
state = None

# Define a function to count fingers
def countFingers(image, hand_landmarks, handNo=0):
    global state

    if hand_landmarks:
        # Get all Landmarks of the FIRST Hand VISIBLE
        landmarks = hand_landmarks[handNo].landmark

        # Count Fingers        
        fingers = []

        for lm_index in tipIds:
            # Get Finger Tip and Bottom y Position Value
            finger_tip_y = landmarks[lm_index].y
            finger_bottom_y = landmarks[lm_index - 2].y

            # Check if ANY FINGER is OPEN or CLOSED
            if lm_index != 4:
                if finger_tip_y < finger_bottom_y:
                    fingers.append(1)
                else:
                    fingers.append(0)

        totalFingers = fingers.count(1)

        # PLAY or PAUSE a Video
        if totalFingers == 4:
            state = "Play"
        elif totalFingers == 0 and state == "Play":
            state = "Pause"
            keyboard.press(Key.space)
            sleep(0.05)
            keyboard.release(Key.space)
        finger_tip_y = (landmarks[8].y)*height
        if totalFingers == 2:
            if  finger_tip_y < height-400:
                print("Decrease Volume")
                pyautogui.press("volumedown")

            if finger_tip_y > height-50:
                print("Increase volume")
                pyautogui.press("volumeup")

        # Move Video FORWARD & BACKWARDS 
        finger_tip_x = (landmarks[8].x) * width
        if totalFingers == 1:
            if finger_tip_x < width - 400:
                print("play backward")
                keyboard.press(Key.left)
                sleep(0.05)
                keyboard.release(Key.left)
            elif finger_tip_x > width - 50:
                print("play forward")
                keyboard.press(Key.right)
                sleep(0.05)
                keyboard.release(Key.right)

# Define a function to draw hand landmarks
def drawHandLandmarks(image, hand_landmarks):
    # Draw connections between landmark points
    if hand_landmarks:
        for landmarks in hand_landmarks:
            mp_drawing.draw_landmarks(image, landmarks, mp_hands.HAND_CONNECTIONS)

while True:
    success, image = cap.read()

    if not success:
        break

    image = cv2.flip(image, 1)
    
    # Detect the Hands Landmarks 
    results = hands.process(image)

    # Get landmark position from the processed result
    hand_landmarks = results.multi_hand_landmarks

    # Draw Landmarks
    drawHandLandmarks(image, hand_landmarks)

    # Get Hand Fingers Position        
    countFingers(image, hand_landmarks)

    cv2.imshow("Media Controller", image)

    # Quit the window on pressing the Escape key
    key = cv2.waitKey(1)
    if key == 27:
        break

cap.release()
cv2.destroyAllWindows()
