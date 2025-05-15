import os
import cv2
import time

import const
import gesture

def main():
    if not os.path.exists(const.MODEL_PATH):
        print(f"Error: Model file '{const.MODEL_PATH}' not found.")
        print(f"Please download it from: https://storage.googleapis.com/mediapipe-models/gesture_recognizer/gesture_recognizer/float16/1/gesture_recognizer.task")
        print(f"And place it in the same directory as this script or update MODEL_PATH.")
        return

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return
    
    gesture.init()
    frame_timestamp_ms = 0
    print("Starting webcam feed. Press 'ESC' to quit.")

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print('Error: Failed to grab frame.')
            break

        frame = cv2.flip(frame, 1)
        gesture.recognize(frame, frame_timestamp_ms)

        frame_timestamp_ms = int(time.time() * 1000)
        display_frame = frame.copy();
        image_height, image_width, _ = display_frame.shape

        gesture.draw(display_frame)

        cv2.imshow('Airy Hand Magic', display_frame)
        if cv2.waitKey(5) & 0xFF == 27:
            print('Exiting...')
            break
    cap.release()
    cv2.destroyAllWindows()

    
if __name__ == '__main__':
    main()