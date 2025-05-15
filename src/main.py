MODEL_PATH = 'gesture_recognizer.task'  # Path to the gesture recognizer model file
MIN_DETECTION_CONFIDENCE = 0.7          # Minimum confidence value for hand detection to be considered successful
MIN_TRACKING_CONFIDENCE = 0.5           # Minimum confidence value for hand landmarks to be tracked successfully
MIN_PRESENCE_CONFIDENCE = 0.5           # Minimum confidence value for the hand presence score in the hand landmark detection
NUM_HANDS = 1                           # Maximum number of hands to detect

import os
import cv2
import time
import mediapipe as mp

def main():
    if not os.path.exists(MODEL_PATH):
        print(f"Error: Model file '{MODEL_PATH}' not found.")
        print(f"Please download it from: https://storage.googleapis.com/mediapipe-models/gesture_recognizer/gesture_recognizer/float16/1/gesture_recognizer.task")
        print(f"And place it in the same directory as this script or update MODEL_PATH.")
        return

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return
    
    frame_timestamp_ms = 0
    print("Starting webcam feed. Press 'ESC' to quit.")

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print('Error: Failed to grab frame.')
            break

        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

        frame_timestamp_ms = int(time.time() * 1000)
        display_frame = frame.copy();
        image_height, image_width, _ = display_frame.shape
        cv2.imshow('Airy Hand Magic', display_frame)
        if cv2.waitKey(5) & 0xFF == 27:
            print('Exiting...')
            break
    cap.release()
    cv2.destroyAllWindows()

    
if __name__ == '__main__':
    main()