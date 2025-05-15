import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import time

# Model path
model_path = "gesture_recognizer.task"

# Callback function for live stream mode
def print_result(result: vision.GestureRecognizerResult, output_image: mp.Image, timestamp_ms: int):
    global latest_frame

    print("print_result called!")  # Check if the callback is being called

    # Convert the MediaPipe image to an OpenCV image for drawing
    frame = cv2.cvtColor(output_image.numpy_view(), cv2.COLOR_RGB2BGR)

    if result.hand_landmarks:
        print("Hand landmarks detected!")  # Check if landmarks are detected
        for hand_landmarks in result.hand_landmarks:
            # Draw the hand landmarks and connections on the frame
            mp.solutions.drawing_utils.draw_landmarks(
                frame,
                hand_landmarks,
                mp.solutions.hands.HAND_CONNECTIONS,
                mp.solutions.drawing_utils.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=4),
                mp.solutions.drawing_utils.DrawingSpec(color=(0, 100, 255), thickness=2),
            )
            # Get and display finger tip coordinates
            for i, landmark in enumerate(hand_landmarks.landmark):
                # Convert normalized coordinates to pixel coordinates
                height, width, _ = frame.shape
                x, y = int(landmark.x * width), int(landmark.y * height)

                if i in [8, 12, 16, 20]:  # Index, Middle, Ring, Pinky finger tips
                    cv2.circle(frame, (x, y), 10, (255, 0, 0), -1)  # Blue circles
                    cv2.putText(
                        frame,
                        str(i),
                        (x + 5, y - 5),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        (255, 255, 255),
                        1,
                    )

        if result.recognized_gestures:
            print("Gestures detected!") # Check if gestures are detected
            for gesture in result.recognized_gestures:
                if gesture:
                    gesture_name = gesture[0].category_name
                    cv2.putText(
                        frame,
                        gesture_name,
                        (50, 50),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1,
                        (255, 0, 0),
                        2,
                        cv2.LINE_AA,
                    )
                else:
                    cv2.putText(
                        frame,
                        "No Gesture",
                        (50, 50),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1,
                        (255, 0, 0),
                        2,
                        cv2.LINE_AA,
                    )
    latest_frame = frame.copy() # Store the frame.

def create_gesture_recognizer():
    # Base options
    base_options = python.BaseOptions(model_asset_path="gesture_recognizer.task")  # Or your model path

    options = vision.GestureRecognizerOptions(
        base_options=base_options,
        num_hands=1,
        min_hand_detection_confidence=0.7,
        min_tracking_confidence=0.5,
        running_mode=mp.tasks.vision.RunningMode.LIVE_STREAM,
        result_callback=print_result,
    )

    # Create the recognizer
    recognizer = vision.GestureRecognizer.create_from_options(options)
    return recognizer

latest_frame = None

def main():
    # Initialize OpenCV webcam
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return

    # Initialize MediaPipe Gesture Recognizer
    recognizer = create_gesture_recognizer()

    frame_count = 0
    while True:
        # Read frame from webcam
        success, frame = cap.read()
        if not success:
            print("Error: Could not read frame.")
            break

        # Flip the frame horizontally
        frame = cv2.flip(frame, 1)

        # Convert the frame to MediaPipe Image
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)

        # Get timestamp
        timestamp_ms = int(cap.get(cv2.CAP_PROP_POS_MSEC))
        if timestamp_ms == 0:
            timestamp_ms = int(time.time() * 1000)

        # Send frame to recognizer (use recognize_async for live stream)
        recognizer.recognize_async(mp_image, timestamp_ms)

        # Display the frame.  Important:  Display the *latest* frame.
        if latest_frame is not None:
            cv2.imshow('Hand Gesture Recognition', latest_frame)

        # Check for user input
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release resources
    cap.release()
    cv2.destroyAllWindows()
    recognizer.close()

if __name__ == "__main__":
    main()
