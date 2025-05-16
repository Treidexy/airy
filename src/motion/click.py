from motion.base import Motion
from timedlist import TimedList

import cv2
import os
import mediapipe as mp
from scipy import stats

HandLandmark = mp.solutions.hands.HandLandmark

class ClickMotion(Motion):
    def __init__(self):
        super().__init__(hand='Right', gesture='Pointing_Up')
        self.list = TimedList()

    def draw(self, frame):
        pass

    def update(self, hand_landmarks, frame):
        if len(self.list) == 0:
            os.system(f'ydotool click c0')
        self.list.add(0, delay=0.8)
    def clear(self):
        super().clear()