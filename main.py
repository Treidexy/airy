import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

model_path = "gesture_recognizer.task"
happy_result = vision.GestureRecognizerResult
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

def print_result(result: vision.GestureRecognizerResult, output_image: mp.Image, timestamp_ms: int):
    global happy_result
    happy_result = result

def create_gesture_recognizer():
    base_options = python.BaseOptions(model_asset_path=model_path)
    options = vision.GestureRecognizerOptions(
        base_options=base_options,
        num_hands=1,
        running_mode=mp.tasks.vision.RunningMode.LIVE_STREAM,
        result_callback=print_result
    )
    recognizer = vision.GestureRecognizer.create_from_options(options)
    return recognizer

def main():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return

    recognizer = create_gesture_recognizer()

    frame_count = 0
    while True:
        success, frame = cap.read()
        if not success:
            print("Error: Could not read frame.")
            break

        frame = cv2.flip(frame, 1)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)

        # Get timestamp
        timestamp_ms = int(cap.get(cv2.CAP_PROP_POS_MSEC))
        if timestamp_ms == 0:
            timestamp_ms = frame_count
            frame_count += 1

        recognizer.recognize_async(mp_image, timestamp_ms)

        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        try:
            for hand_landmarks in happy_result.hand_landmarks:
                mp_drawing.draw_landmarks(
                    image, hand_landmarks, mp_hands.HAND_CONNECTIONS,
                    mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=4),  # Landmark style
                    mp_drawing.DrawingSpec(color=(0, 100, 255), thickness=2)  # Connection style
                )

            if len(happy_result.gestures) > 0:
                cv2.putText(image, happy_result.gestures[0][0], (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)
        except NameError:
            pass
        cv2.imshow('Hand Gesture Recognition', image)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    recognizer.close()

if __name__ == "__main__":
    main()
