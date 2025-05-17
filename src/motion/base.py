import mediapipe as mp
import cv2

class Motion:
    def __init__(self, hand, gesture):
        self.hand = hand
        self.gesture = gesture
        self.active = False
    def draw(self, frame):
        pass
    def update(self, hand_landmarks, frame):
        pass