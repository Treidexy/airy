from motion.base import Motion, Gesture
from timedlist import TimedList

import cv2
import os
import mediapipe as mp
from scipy import stats

HandLandmark = mp.solutions.hands.HandLandmark

class SwapWorkspaceMotion(Motion):
    def __init__(self):
        self.list = TimedList()

    def draw(self, frame):
        frame_height, frame_width, _ = frame.shape
        for mark in self.list:
            cv2.circle(frame, (int(mark[0] * frame_width), int(mark[1] * frame_height)), 20, (255, 0, 0), 2)

    def update(self, landmarks, frame):
        hand = landmarks[HandLandmark.INDEX_FINGER_TIP]
        self.list.add((hand.x, hand.y), delay=0.5)

        if len(self.list) > 5:
            x, y = self.list.get_separate_lists()
            r = stats.linregress(x, y)
            swipe = x[-1] - x[0]
            if r.stderr < 0.1 and abs(swipe) > 0.11 and abs(r.slope) < 0.5:
                self.list.clear()
                if swipe < 0:
                    os.system('hyprctl dispatch workspace -1')
                else:
                    os.system('hyprctl dispatch workspace +1')
    def cancel(self):
        self.list.clear()