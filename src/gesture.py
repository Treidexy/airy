import mediapipe as mp
import numpy as np
from motion.base import Motion, Gesture
from motion.swap_workspace import SwapWorkspaceMotion

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

HandLandmark = mp.solutions.hands.HandLandmark

recognizer = mp_hands.Hands(
    min_detection_confidence = 0.7,
    min_tracking_confidence = 0.5,
)

motions: dict[Gesture, Motion] = {
    Gesture.ALL: SwapWorkspaceMotion()
}

hands = [None, None]

def get_gesture(landmarks: list, side: int) -> Gesture:
    gesture = Gesture.from_side(side)

    
    
    finger_tips_ids = [HandLandmark.INDEX_FINGER_TIP, HandLandmark.MIDDLE_FINGER_TIP, HandLandmark.RING_FINGER_TIP, HandLandmark.PINKY_TIP]
    for fingy, tip_id in enumerate(finger_tips_ids):
        if landmarks[tip_id].y < landmarks[tip_id - 2].y:
            gesture |= Gesture.from_fingy(fingy)
    return gesture

def recognize(frame):
    global hands

    results = recognizer.process(frame)
    hands = [None, None]

    if results.multi_handedness and results.multi_hand_landmarks:
        for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
            side = handedness.classification[0].index
            
            hands[side] = hand_landmarks
            gesture = get_gesture(hand_landmarks.landmark, side)
            print(gesture)

def draw_hands(frame):
    for side, hand_landmarks in enumerate(hands):
        if hand_landmarks:
            mp_drawing.draw_landmarks(
                frame,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS,
                mp_drawing_styles.get_default_hand_landmarks_style(),
                mp_drawing_styles.DrawingSpec(color=(side * 255,0, (1 - side) * 255), thickness=2),
            )

def draw_ui(frame):
    pass