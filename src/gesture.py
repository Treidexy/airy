import mediapipe as mp
import const
from mediapipe.framework.formats import landmark_pb2
import cv2
import numpy as np
from motion.base import Motion
from motion.swap_workspace import SwapWorkspaceMotion
from motion.mouse import MouseMotion
from motion.scroll import ScrollMotion
from motion.click import ClickMotion
import threading

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

HandLandmark = mp.solutions.hands.HandLandmark

hands = mp_hands.Hands(
    min_detection_confidence = 0.7,
    min_tracking_confidence = 0.5,
)

left = None
right = None

def recognize(frame):
    global left, right

    results = hands.process(frame)
    left = None
    right = None

    if results.multi_handedness and results.multi_hand_landmarks:
        for i, hand_landmarks in enumerate(results.multi_hand_landmarks):
            landmarks = hand_landmarks.landmark
            hand = results.multi_handedness[i].classification[0]
            print(hand)

            a = landmarks[HandLandmark.INDEX_FINGER_MCP]
            b = landmarks[HandLandmark.PINKY_MCP]
            c = landmarks[HandLandmark.WRIST]
            # https://www.geeksforgeeks.org/orientation-3-ordered-points/
            o = (b.y - a.y) * (c.x - b.x) - (b.x - a.x) * (c.y - b.y)
            
            if o < 0:
                left = hand_landmarks
            elif o > 0:
                right = hand_landmarks
            else:
                print('we got an anomaly')

def draw_hands(frame):
    if left:
        mp_drawing.draw_landmarks(
            frame,
            left,
            mp_hands.HAND_CONNECTIONS,
            mp_drawing_styles.get_default_hand_landmarks_style(),
            mp_drawing_styles.DrawingSpec(color=(0,0,255), thickness=2),
        )
    if right:
        mp_drawing.draw_landmarks(
            frame,
            right,
            mp_hands.HAND_CONNECTIONS,
            mp_drawing_styles.get_default_hand_landmarks_style(),
            mp_drawing_styles.DrawingSpec(color=(255,0,0), thickness=2),
        )

def draw_ui(frame):
    pass