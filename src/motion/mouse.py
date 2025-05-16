from motion.base import Motion
from timedlist import TimedList

import cv2
import os
import mediapipe as mp
from scipy import stats

HandLandmark = mp.solutions.hands.HandLandmark

class MouseMotion(Motion):
    def __init__(self):
        self.list = TimedList()
        self.toolazy = TimedList()

    def draw(self, frame):
        frame_height, frame_width, _ = frame.shape
        for mark in self.list:
            cv2.circle(frame, (int(mark[0] * frame_width), int(mark[1] * frame_height)), 20, (0, 0, 255), 2)

    def update(self, gesture, hand_landmarks, frame):
        frame_height, frame_width, _ = frame.shape

        if gesture.category_name == 'Pointing_Up':
            self.toolazy.clear()

            hand = hand_landmarks[HandLandmark.INDEX_FINGER_TIP]
            self.list.add((hand.x, hand.y), delay=0.4)

            if len(self.list) > 9:
                x, y = self.list.get_separate_lists()
                dx = (x[1] - x[0]) * frame_width * 3
                dy = (y[1] - y[0]) * frame_height * 3
                # print(dx, dy)
                os.system(f'ydotool mousemove -x {dx} -y {dy}')
        elif gesture.category_name == 'Thumb_Up':
            self.list.clear()
            if len(self.toolazy) == 0:
                os.system('ydotool click c0')
            self.toolazy.add(0, delay=0.8)
        else:
            self.toolazy.clear()
            self.list.clear()