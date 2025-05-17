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

recognizer = mp_hands.Hands(
    min_detection_confidence = 0.7,
    min_tracking_confidence = 0.5,
)

left = None
right = None

def recognize(frame):
    global left, right

    results = recognizer.process(frame)
    left = None
    right = None

    if results.multi_handedness and results.multi_hand_landmarks:
        for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
            hand = handedness.classification[0].index
            
            if hand == 0:
                left = hand_landmarks
            elif hand == 1:
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