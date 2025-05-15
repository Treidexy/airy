import mediapipe as mp
import const
from mediapipe.framework.formats import landmark_pb2

recognizer = None
latest_landmarks = None

def result_callback(result: mp.tasks.vision.GestureRecognizerResult, output_image: mp.Image, timestamp_ms: int):
    global latest_landmarks
    if result.gestures:
        latest_landmarks = result.hand_landmarks
    else:
        latest_landmarks = None

def init():
    global recognizer

    options = mp.tasks.vision.GestureRecognizerOptions(
        base_options = mp.tasks.BaseOptions(model_asset_path=const.MODEL_PATH),
        running_mode=mp.tasks.vision.RunningMode.LIVE_STREAM,
        num_hands=const.NUM_HANDS,
        min_hand_detection_confidence=const.MIN_DETECTION_CONFIDENCE,
        min_hand_presence_confidence=const.MIN_PRESENCE_CONFIDENCE,
        min_tracking_confidence=const.MIN_TRACKING_CONFIDENCE,
        result_callback=result_callback,
    )
    recognizer = mp.tasks.vision.GestureRecognizer.create_from_options(options)

def recognize(frame, frame_timestamp_ms):
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
    recognizer.recognize_async(mp_image, frame_timestamp_ms)

def draw(frame):
    if latest_landmarks:
        for hand_idx, hand_landmark_list in enumerate(latest_landmarks):
            hand_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
            hand_landmarks_proto.landmark.extend([
                landmark_pb2.NormalizedLandmark(
                    x=landmark.x, y=landmark.y, z=landmark.z
                ) for landmark in hand_landmark_list
            ])


            mp.solutions.drawing_utils.draw_landmarks(
                frame,
                hand_landmarks_proto,
                mp.solutions.hands.HAND_CONNECTIONS,
                mp.solutions.drawing_styles.get_default_hand_landmarks_style(),
                mp.solutions.drawing_styles.get_default_hand_connections_style()
            )