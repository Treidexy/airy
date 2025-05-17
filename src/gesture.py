import mediapipe as mp
import numpy as np
from motion.base import Motion, Gesture
from motion.swap_workspace import SwapWorkspaceMotion
from motion.mouse import MouseMotion
from motion.click import ClickMotion
from motion.scroll import ScrollMotion
from motion.type import TypeMotion

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

HandLandmark = mp.solutions.hands.HandLandmark

recognizer = mp_hands.Hands(
    max_num_hands = 1,
    min_detection_confidence = 0.7,
    min_tracking_confidence = 0.5,
)

motions: dict[Gesture, Motion] = {
    Gesture.RIGHT | Gesture.FRONT | Gesture.FIVE: SwapWorkspaceMotion(),
    Gesture.RIGHT | Gesture.FRONT | Gesture.ONE: MouseMotion(),
    Gesture.RIGHT | Gesture.FRONT | Gesture.TWO: ScrollMotion(),
    Gesture.RIGHT | Gesture.BACK | Gesture.ONE: ClickMotion(0),
    Gesture.RIGHT | Gesture.BACK | Gesture.TWO: ClickMotion(1),
    Gesture.RIGHT | Gesture.BACK | Gesture.THREE: TypeMotion('youtube.com\\n'),
    Gesture.RIGHT | Gesture.BACK | Gesture.FOUR: TypeMotion('f'),
}

handmarks = None
side = None

def get_gesture(landmarks: list, side: int) -> Gesture:
    gesture = Gesture.from_side(side)

    a = landmarks[HandLandmark.INDEX_FINGER_MCP]
    b = landmarks[HandLandmark.PINKY_MCP]
    c = landmarks[HandLandmark.WRIST]
    # https://www.geeksforgeeks.org/orientation-3-ordered-points/
    o = (b.y - a.y) * (c.x - b.x) - (b.x - a.x) * (c.y - b.y)

    if o * (side - .5) > 0:
        print('he')
        gesture |= Gesture.BACK

    if o * (landmarks[HandLandmark.THUMB_TIP].x - landmarks[HandLandmark.THUMB_IP].x) > 0:
        gesture |= Gesture.THUMB
    
    tip_ids = [HandLandmark.INDEX_FINGER_TIP, HandLandmark.MIDDLE_FINGER_TIP, HandLandmark.RING_FINGER_TIP, HandLandmark.PINKY_TIP]
    pip_ids = [HandLandmark.INDEX_FINGER_PIP, HandLandmark.MIDDLE_FINGER_PIP, HandLandmark.RING_FINGER_PIP, HandLandmark.PINKY_PIP]
    mcp_ids = [HandLandmark.INDEX_FINGER_MCP, HandLandmark.MIDDLE_FINGER_MCP, HandLandmark.RING_FINGER_MCP, HandLandmark.PINKY_MCP]
    for fingy, (tip_id, pip_id, mcp_id) in enumerate(zip(tip_ids, pip_ids, mcp_ids)):
        if landmarks[tip_id].y < landmarks[mcp_id].y and landmarks[tip_id].y < landmarks[pip_id].y:
            gesture |= Gesture.from_fingy(fingy)
    return gesture

def recognize(frame):
    global handmarks, side

    results = recognizer.process(frame)
    handmarks = None
    side = None

    if results.multi_handedness and results.multi_hand_landmarks:
        for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
            side = handedness.classification[0].index
            
            handmarks = hand_landmarks
            gesture = get_gesture(hand_landmarks.landmark, side)
            # print(gesture, Gesture.RIGHT | Gesture.FRONT | Gesture.FIVE)
            motion = motions.get(gesture)
            if motion:
                motion.update(hand_landmarks.landmark, frame)

def draw_hands(frame):
    if handmarks and side:
        mp_drawing.draw_landmarks(
            frame,
            handmarks,
            mp_hands.HAND_CONNECTIONS,
            mp_drawing_styles.get_default_hand_landmarks_style(),
            mp_drawing_styles.DrawingSpec(color=(side * 255,0, (1 - side) * 255), thickness=2),
        )
    for motion in motions.values():
        motion.draw(frame)

def draw_ui(frame):
    pass