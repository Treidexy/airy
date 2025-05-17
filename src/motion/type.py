from motion.base import Motion
from timedlist import TimedList

import cv2
import os
import mediapipe as mp
from scipy import stats

HandLandmark = mp.solutions.hands.HandLandmark

class TypeMotion(Motion):
    def __init__(self, text):
        self.list = TimedList()
        self.text = text

    def draw(self, frame):
        pass

    def update(self, hand_landmarks, frame):
        if len(self.list) == 0:
            os.system(f'ydotool type "{self.text}"')
        self.list.add(0, delay=0.8)
    def cancel(self):
        self.list.clear()