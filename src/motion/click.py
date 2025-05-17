from motion.base import Motion
from timedlist import TimedList

import os
import mediapipe as mp
from scipy import stats

HandLandmark = mp.solutions.hands.HandLandmark

class ClickMotion(Motion):
    def __init__(self, button):
        self.list = TimedList()
        self.button = button

    def draw(self, frame):
        pass

    def update(self, hand_landmarks, frame):
        if len(self.list) == 0:
            os.system(f'ydotool click 4{self.button}')
        self.list.add(0, delay=0.8)
    def cancel(self):
        os.system(f'ydotool click 8{self.button}')