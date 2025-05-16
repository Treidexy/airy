from motion.base import Motion
from timedlist import TimedList

import cv2
import os
import mediapipe as mp
from scipy import stats

HandLandmark = mp.solutions.hands.HandLandmark

class ScrollMotion(Motion):
    def __init__(self):
        self.list = TimedList()

    def draw(self, frame):
        frame_height, frame_width, _ = frame.shape
        for mark in self.list:
            cv2.circle(frame, (int(mark[0] * frame_width), int(mark[1] * frame_height)), 20, (0, 255, 0), 2)

    def update(self, gesture, hand_landmarks):
        if gesture.category_name == 'Victory':
            hand = hand_landmarks[HandLandmark.INDEX_FINGER_TIP]
            self.list.add((hand.x, hand.y), delay=0.4)

            if len(self.list) > 9:
                x, y = self.list.get_separate_lists()
                r = stats.linregress(y, x)
                swipe = y[-1] - y[0]
                if r.stderr < 0.1 and abs(swipe) > 0.11 and abs(r.slope) < 0.3:
                    self.list.clear()
                    print(swipe)
                    os.system(f'ydotool mousemove -w -x 0 -y {40*swipe}')
        else:
            self.list.clear()
    