from motion.base import Motion
from timedlist import TimedList

class SwapWorkspaceMotion(Motion):
    def __init__(self):
        self.list = TimedList()

    def update(self, gesture, hand_landmarks):
        self.list.add(hand_landmarks[4])
    