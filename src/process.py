import mediapipe as mp
import numpy as np
import cv2

from gesture import Gesture
from config import motions

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

HandLandmark = mp.solutions.hands.HandLandmark

recognizer = mp_hands.Hands(
    max_num_hands = 1,
    min_detection_confidence = 0.7,
    min_tracking_confidence = 0.5,
)

handmarks = None
side = None
gesture = None

def get_gesture(landmarks: list, side: int) -> Gesture:
    # gesture = Gesture.from_side(side)
    gesture: Gesture = Gesture.NONE

    s = side - 0.5

    a = landmarks[HandLandmark.INDEX_FINGER_MCP]
    b = landmarks[HandLandmark.PINKY_MCP]
    c = landmarks[HandLandmark.WRIST]
    # https://www.geeksforgeeks.org/orientation-3-ordered-points/
    o = (b.y - a.y) * (c.x - b.x) - (b.x - a.x) * (c.y - b.y)

    dx = a.x - c.x
    dy = a.y - c.y
    angle = np.arctan2(dx, dy)
    del a, b, c

    if 2.8 < angle or angle < -2.5:
        gesture |= Gesture.UP
    elif -1.4 < angle and angle < 0.6:
        gesture |= Gesture.DOWN
    elif -1.4 > angle and angle > -2.5:
        gesture |= Gesture.LEFT
    elif 0.6 < angle and angle < 2.8:
        gesture |= Gesture.RIGHT

    if o * s > 0:
        gesture |= Gesture.BACK


    if gesture.dir() == Gesture.UP:
        t = landmarks[HandLandmark.THUMB_TIP].x - landmarks[HandLandmark.THUMB_IP].x
    elif gesture.dir() == Gesture.DOWN:
        t = landmarks[HandLandmark.THUMB_TIP].x - landmarks[HandLandmark.THUMB_IP].x
        t = -t
    elif gesture.dir() == Gesture.LEFT:
        t = landmarks[HandLandmark.THUMB_TIP].y - landmarks[HandLandmark.THUMB_IP].y
        t = -t
    elif gesture.dir() == Gesture.RIGHT:
        t = landmarks[HandLandmark.THUMB_TIP].y - landmarks[HandLandmark.THUMB_IP].y
    if o * t > 0:
        gesture |= Gesture.THUMB
    
    tip_ids = [HandLandmark.INDEX_FINGER_TIP, HandLandmark.MIDDLE_FINGER_TIP, HandLandmark.RING_FINGER_TIP, HandLandmark.PINKY_TIP]
    pip_ids = [HandLandmark.INDEX_FINGER_PIP, HandLandmark.MIDDLE_FINGER_PIP, HandLandmark.RING_FINGER_PIP, HandLandmark.PINKY_PIP]
    mcp_ids = [HandLandmark.INDEX_FINGER_MCP, HandLandmark.MIDDLE_FINGER_MCP, HandLandmark.RING_FINGER_MCP, HandLandmark.PINKY_MCP]
    for fingy, (tip_id, pip_id, mcp_id) in enumerate(zip(tip_ids, pip_ids, mcp_ids)):
        if gesture.dir() == Gesture.UP:
            a = landmarks[tip_id].y - landmarks[pip_id].y
            b = landmarks[tip_id].y - landmarks[mcp_id].y
        elif gesture.dir() == Gesture.DOWN:
            a = landmarks[tip_id].y - landmarks[pip_id].y
            b = landmarks[tip_id].y - landmarks[mcp_id].y
            a = -a
            b = -b
        elif gesture.dir() == Gesture.LEFT:
            a = landmarks[tip_id].x - landmarks[pip_id].x
            b = landmarks[tip_id].x - landmarks[mcp_id].x
        elif gesture.dir() == Gesture.RIGHT:
            a = landmarks[tip_id].x - landmarks[pip_id].x
            b = landmarks[tip_id].x - landmarks[mcp_id].x
            a = -a
            b = -b

        if a < 0 and b < 0:
            gesture |= Gesture.from_fingy(fingy)
    return gesture

def recognize(frame):
    global handmarks, side, gesture

    results = recognizer.process(frame)
    # handmarks = None
    # side = None
    # gesture = None

    if results.multi_handedness and results.multi_hand_landmarks:
        for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
            side = handedness.classification[0].index
            
            handmarks = hand_landmarks
            old_gesture = gesture
            gesture = get_gesture(hand_landmarks.landmark, side)
            # print(gesture, Gesture.RIGHT | Gesture.FRONT | Gesture.FIVE)
            if old_gesture != gesture:
                old_motionz = motions.get(old_gesture)
                if old_motionz:
                    for old_motion in old_motionz:
                        old_motion.cancel()
            motionz = motions.get(gesture)
            if motionz:
                for motion in motionz:
                    motion.update(hand_landmarks.landmark, frame)
    else:
        handmarks = None
        side = None
        gesture = None

def draw_hands(frame):
    if handmarks and side != None:
        mp_drawing.draw_landmarks(
            frame,
            handmarks,
            mp_hands.HAND_CONNECTIONS,
            mp_drawing_styles.get_default_hand_landmarks_style(),
            mp_drawing_styles.DrawingSpec(color=(side * 255,0, (1 - side) * 255), thickness=2),
        )
    for motionz in motions.values():
        for motion in motionz:
            motion.draw(frame)

def draw_ui(frame):
    if gesture:
        cv2.putText(frame, str(gesture), (0, 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0))