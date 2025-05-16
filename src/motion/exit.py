from motion.base import Motion
from timedlist import TimedList

import cv2
import os
import mediapipe as mp
from scipy import stats

HandLandmark = mp.solutions.hands.HandLandmark

class ExitMotion(Motion):
    def __init__(self):
        self.list = TimedList()
        self.toolazy = TimedList()

    def draw(self, frame):
        pass

    def update(self, gesture, hand_landmarks, frame):
        frame_height, frame_width, _ = frame.shape

        if gesture.category_name == 'ILoveYou':
            exit(0)