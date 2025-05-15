import cv2
import mediapipe as mp
import numpy as np
import time
import os
from mediapipe.framework.formats import landmark_pb2 # Import landmark_pb2

import time
import threading

from scipy import stats

class AutoDeletingList:
    def __init__(self):
        self._data = {}  # {(x, y): expiration_timestamp}
        self._lock = threading.Lock()
        self._stop_event = threading.Event()
        self._cleaner_thread = threading.Thread(target=self._clean_expired_elements, daemon=True)
        self._cleaner_thread.start()

    def add(self, coordinate, delay=1):
        if isinstance(coordinate, tuple) and len(coordinate) == 2:
            with self._lock:
                self._data[coordinate] = time.time() + delay
        else:
            raise ValueError("Input must be a tuple of (x, y)")

    def __contains__(self, coordinate):
        with self._lock:
            return coordinate in self._data and self._data[coordinate] > time.time()

    def __len__(self):
        with self._lock:
            return sum(1 for timestamp in self._data.values() if timestamp > time.time())

    def __iter__(self):
        with self._lock:
            current_time = time.time()
            active_coordinates = [coord for coord, timestamp in self._data.items() if timestamp > current_time]
            return iter(active_coordinates)

    def get_all_active(self):
        with self._lock:
            current_time = time.time()
            return [coord for coord, timestamp in self._data.items() if timestamp > current_time]

    def get_separate_lists(self):
        with self._lock:
            current_time = time.time()
            active_data = [(x, y) for (x, y), timestamp in self._data.items() if timestamp > current_time]
            x_values = [coord[0] for coord in active_data]
            y_values = [coord[1] for coord in active_data]
            return x_values, y_values

    def _clean_expired_elements(self):
        while not self._stop_event.is_set():
            time.sleep(0.1)  # Check for expired elements every 100 milliseconds
            with self._lock:
                expired_items = [item for item, timestamp in self._data.items() if timestamp <= time.time()]
                for item in expired_items:
                    del self._data[item]

    def clear(self):
        with self._lock:
            self._data.clear()

    def stop(self):
        self._stop_event.set()
        self._cleaner_thread.join()

# --- Configuration Constants ---
MODEL_PATH = 'gesture_recognizer.task'  # Path to the gesture recognizer model file
MIN_DETECTION_CONFIDENCE = 0.7          # Minimum confidence value for hand detection to be considered successful
MIN_TRACKING_CONFIDENCE = 0.5           # Minimum confidence value for hand landmarks to be tracked successfully
MIN_PRESENCE_CONFIDENCE = 0.5           # Minimum confidence value for the hand presence score in the hand landmark detection
NUM_HANDS = 1                           # Maximum number of hands to detect

# --- Global Variables to Store Recognition Results ---
# These variables will be updated by the MediaPipe callback function
latest_gesture_result = None
latest_landmarks = None
latest_handedness = None

pointer_fingers = AutoDeletingList()

# --- MediaPipe Setup ---
# Import MediaPipe solutions for drawing and hand tracking
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

# Import MediaPipe Tasks vision components
BaseOptions = mp.tasks.BaseOptions
GestureRecognizer = mp.tasks.vision.GestureRecognizer
GestureRecognizerOptions = mp.tasks.vision.GestureRecognizerOptions
GestureRecognizerResult = mp.tasks.vision.GestureRecognizerResult
VisionRunningMode = mp.tasks.vision.RunningMode


# --- Callback Function for Gesture Recognition ---
# This function is called asynchronously when MediaPipe has processed a frame
def result_callback(result: GestureRecognizerResult, output_image: mp.Image, timestamp_ms: int):
    """
    Callback function to receive and store gesture recognition results.

    Args:
        result: The gesture recognition result from MediaPipe.
        output_image: The MediaPipe Image object that was processed.
        timestamp_ms: The timestamp of the processed frame.
    """
    global latest_gesture_result, latest_landmarks, latest_handedness, pointer_fingers

    if result.gestures:
        latest_gesture_result = result.gestures
        latest_landmarks = result.hand_landmarks
        latest_handedness = result.handedness
        if len(result.hand_landmarks) > 0:
            if latest_gesture_result[0][0].category_name == 'Open_Palm':
                pointer_finger = result.hand_landmarks[0][mp_hands.HandLandmark.INDEX_FINGER_TIP]
                pointer_fingers.add((pointer_finger.x, pointer_finger.y), delay=0.5)
                if len(pointer_fingers) > 15:
                    sep = pointer_fingers.get_separate_lists()
                    x = stats.linregress(sep)
                    swipe = sep[0][-1] - sep[0][0]
                    if x.stderr < 0.1 and abs(swipe) > 0.1 and abs(x.slope) < 0.5:
                        pointer_fingers.clear()
                        if swipe < 0:
                            os.system('hyprctl dispatch workspace -1')
                        else:
                            os.system('hyprctl dispatch workspace +1')
            elif latest_gesture_result[0][0].category_name == 'Pointing_Up':
                
            elif latest_gesture_result[0][0].category_name == 'ILoveYou':
                exit()
    else:
        # If no gestures are detected, clear the previous results
        latest_gesture_result = None
        latest_landmarks = None
        latest_handedness = None
        pointer_finger = None
    # For debugging: print(f'Gesture recognition result: {result.gestures} at {timestamp_ms}ms')

# --- Main Script Execution ---
def main():
    global latest_gesture_result, latest_landmarks, latest_handedness # Allow modification of global variables

    # Check if the model file exists
    if not os.path.exists(MODEL_PATH):
        print(f"Error: Model file '{MODEL_PATH}' not found.")
        print(f"Please download it from: https://storage.googleapis.com/mediapipe-models/gesture_recognizer/gesture_recognizer/float16/1/gesture_recognizer.task")
        print(f"And place it in the same directory as this script or update MODEL_PATH.")
        return

    # --- Initialize Gesture Recognizer ---
    try:
        base_options = BaseOptions(model_asset_path=MODEL_PATH)
        options = GestureRecognizerOptions(
            base_options=base_options,
            running_mode=VisionRunningMode.LIVE_STREAM, # Process a live stream of data
            num_hands=NUM_HANDS,
            min_hand_detection_confidence=MIN_DETECTION_CONFIDENCE,
            min_hand_presence_confidence=MIN_PRESENCE_CONFIDENCE,
            min_tracking_confidence=MIN_TRACKING_CONFIDENCE,
            result_callback=result_callback  # Set the callback function
        )
        recognizer = GestureRecognizer.create_from_options(options)
    except Exception as e:
        print(f"Error initializing Gesture Recognizer: {e}")
        return

    # --- OpenCV Video Capture ---
    cap = cv2.VideoCapture(0)  # 0 for the default webcam
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return

    frame_timestamp_ms = 0
    print("Starting webcam feed. Press 'ESC' to quit.")

    while cap.isOpened():
        # Read a frame from the webcam
        ret, frame = cap.read()
        if not ret:
            print("Error: Failed to grab frame.")
            break

        # Flip the frame horizontally for a selfie-view display
        # This makes the interaction more intuitive
        frame = cv2.flip(frame, 1)

        # Convert the BGR image (OpenCV default) to RGB (MediaPipe requirement)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Convert the OpenCV frame to MediaPipe's Image format
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

        # Get current timestamp in milliseconds
        frame_timestamp_ms = int(time.time() * 1000)

        # Perform gesture recognition asynchronously
        # The results will be delivered to the `result_callback` function
        try:
            recognizer.recognize_async(mp_image, frame_timestamp_ms)
        except Exception as e:
            print(f"Error during recognition: {e}")
            # Continue to the next frame or handle as appropriate
            continue


        # --- Display Results on Frame ---
        # Create a copy of the frame to draw on, to keep the original clean if needed
        display_frame = frame.copy()
        image_height, image_width, _ = display_frame.shape

        if latest_landmarks:
            for hand_idx, hand_landmark_list in enumerate(latest_landmarks):
                # Draw hand landmarks
                # Create a NormalizedLandmarkList protobuf object
                hand_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
                # Populate the protobuf object with landmarks from the result
                hand_landmarks_proto.landmark.extend([
                    landmark_pb2.NormalizedLandmark(
                        x=landmark.x, y=landmark.y, z=landmark.z
                    ) for landmark in hand_landmark_list
                ])
                
                # Draw the landmarks on the display frame
                mp_drawing.draw_landmarks(
                    display_frame,
                    hand_landmarks_proto,
                    mp_hands.HAND_CONNECTIONS,  # Connections between landmarks
                    mp_drawing_styles.get_default_hand_landmarks_style(),
                    mp_drawing_styles.get_default_hand_connections_style()
                )

                # Prepare text for gesture and handedness
                gesture_text = "No gesture detected"
                handedness_text = ""
                gesture_confidence = 0.0

                if latest_gesture_result and hand_idx < len(latest_gesture_result):
                    if latest_gesture_result[hand_idx]: # Check if gesture list is not empty
                        gesture = latest_gesture_result[hand_idx][0] # Get the top gesture
                        gesture_text = gesture.category_name
                        gesture_confidence = gesture.score

                if latest_handedness and hand_idx < len(latest_handedness):
                    if latest_handedness[hand_idx]: # Check if handedness list is not empty
                        handedness_text = latest_handedness[hand_idx][0].category_name

                full_text = f"{handedness_text} Hand: {gesture_text} ({gesture_confidence:.2f})"

                # Get coordinates of the wrist (landmark 0) to position the text
                # Landmarks are normalized, so multiply by frame dimensions
                wrist_landmark = hand_landmark_list[0] # WRIST landmark
                text_x = int(wrist_landmark.x * image_width)
                text_y = int(wrist_landmark.y * image_height) - 30  # Position text slightly above the wrist

                # Ensure text stays within frame boundaries
                (text_width, text_height), _ = cv2.getTextSize(full_text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)
                if text_y < text_height: # If text goes above the top edge
                    text_y = text_y + text_height + 40 # Move it below the wrist
                if text_x + text_width > image_width: # If text goes beyond the right edge
                    text_x = image_width - text_width
                if text_x < 0: # If text goes beyond the left edge
                    text_x = 0

                # Draw the text on the frame
                cv2.putText(display_frame, full_text, (text_x, text_y),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2, cv2.LINE_AA)
        else:
            # Optional: Display a message if no hands are detected
            cv2.putText(display_frame, "No hands detected", (20, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv2.LINE_AA)

        for pointer_finger in pointer_fingers:
            point = pointer_finger
            cv2.circle(display_frame, center=(int(point[0] * image_width), int(point[1] * image_height)), radius=15, color=0x00ff00)

        # Display the annotated frame
        cv2.imshow('Hand Gesture Recognition - Press ESC to quit', display_frame)

        # Check for 'ESC' key press to exit
        if cv2.waitKey(5) & 0xFF == 27:
            print("Exiting...")
            break

    # --- Cleanup ---
    if 'recognizer' in locals() and recognizer:
        recognizer.close() # Release MediaPipe recognizer resources
    cap.release()          # Release the webcam
    cv2.destroyAllWindows()# Close all OpenCV windows

if __name__ == '__main__':
    main()
