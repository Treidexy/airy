from motion.base import Motion
from timedlist import TimedList

import cv2
import os
import mediapipe as mp

HandLandmark = mp.solutions.hands.HandLandmark

class ScrollMotion(Motion):
    def __init__(self):
        self.list = TimedList()

    def draw(self, frame):
        frame_height, frame_width, _ = frame.shape
        for mark in self.list:
            cv2.circle(frame, (int(mark[0] * frame_width), int(mark[1] * frame_height)), 20, (0, 0, 255), 2)

    def update(self, landmarks, frame):
        frame_height, frame_width, _ = frame.shape

        hand = landmarks[HandLandmark.INDEX_FINGER_TIP]
        self.list.add((hand.x, hand.y), delay=0.4)

        if len(self.list) > 5:
            x, y = self.list.get_separate_lists()
            dx = (x[1] - x[0]) * frame_width * 0.1
            dy = (y[1] - y[0]) * frame_height * 0.1
            # print(dx, dy)
            os.system(f'ydotool mousemove -w -x {dx} -y {-dy}')
    def cancel(self):
        self.list.clear()