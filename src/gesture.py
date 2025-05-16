import mediapipe as mp
import const
from mediapipe.framework.formats import landmark_pb2
import cv2
import numpy as np
from motion.base import Motion
from motion.swap_workspace import SwapWorkspaceMotion
from motion.scroll import ScrollMotion
from motion.mouse import MouseMotion
from motion.exit import ExitMotion

recognizer = None

latest_gestures = None
latest_landmarks = None
latest_handedness = None

HandLandmark = mp.solutions.hands.HandLandmark

fframe = None

motions: list[Motion] = [
    ScrollMotion(),
    MouseMotion(),
    SwapWorkspaceMotion(),
    ExitMotion()
]

def result_callback(result: mp.tasks.vision.GestureRecognizerResult, output_image: mp.Image, timestamp_ms: int):
    global latest_gestures, latest_landmarks, latest_handedness
    if result.gestures:
        latest_gestures = result.gestures
        latest_landmarks = result.hand_landmarks
        latest_handedness = result.handedness

        for hand_idx in range(len(result.gestures)):
            for motion in motions:
                motion.update(latest_gestures[hand_idx][0], latest_landmarks[hand_idx], fframe)
    else:
        latest_gestures = None
        latest_landmarks = None
        latest_handedness = None

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
    global fframe
    fframe = frame

    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
    recognizer.recognize_async(mp_image, frame_timestamp_ms)

def draw(frame):
    if latest_landmarks:
        for hand_idx, hand_landmark_list in enumerate(latest_landmarks):
            draw_hand(frame, hand_idx, hand_landmark_list)
            draw_gesture(frame, hand_idx, hand_landmark_list)
    for motion in motions:
        motion.draw(frame)

def draw_hand(frame, hand_idx, hand_landmark_list):
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

def draw_gesture(frame, hand_idx, hand_landmark_list):
    frame_height, frame_width, _ = frame.shape

    gesture_text = 'No gesture detected'
    handedness_text = ''
    gesture_confidence = 0.0

    if latest_gestures and hand_idx < len(latest_gestures):
        if latest_gestures[hand_idx]:
            gesture = latest_gestures[hand_idx][0]
            gesture_text = gesture.category_name
            gesture_confidence = gesture.score
            handedness_text = latest_handedness[hand_idx][0].category_name
        
        text = f'{handedness_text} Hand: {gesture_text} ({gesture_confidence:.2f})'
        wrist_landmark = hand_landmark_list[HandLandmark.WRIST]
        text_x = int(wrist_landmark.x * frame_width)
        text_y = int(wrist_landmark.y * frame_height) - 30

        (text_width, text_height), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)
        if text_y < text_height: # If text goes above the top edge
            text_y = text_y + text_height + 40 # Move it below the wrist
        if text_x + text_width > frame_width: # If text goes beyond the right edge
            text_x = frame_width - text_width
        if text_x < 0: # If text goes beyond the left edge
            text_x = 0
        cv2.putText(frame, text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2, cv2.LINE_AA)