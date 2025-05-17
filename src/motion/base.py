import mediapipe as mp
import cv2

class Gesture:
    def __init__(self, n: int):
        self.n = n

    def from_side(side):
        return Gesture(side)
    # THUMB IS NOT A FINGY (for convenience)
    def from_fingy(fingy):
        return Gesture(1 << (fingy + 2))

    def __or__(self, other):
        if isinstance(other, Gesture):
            return Gesture(self.n | other.n)
        raise NotImplemented
    
    def __and__(self, other):
        if isinstance(other, Gesture):
            return Gesture(self.n & other.n)
        raise NotImplemented
    
    def __invert__(self):
        return Gesture(~self.n)
    
    def __str__(self):
        return f"{self.n:b}"

Gesture.LEFT = Gesture(0 << 0)
Gesture.RIGHT = Gesture(1 << 0)

Gesture.THUMB = Gesture(1 << 1)
Gesture.INDEX = Gesture(1 << 2)
Gesture.MIDDLE = Gesture(1 << 3)
Gesture.RING = Gesture(1 << 4)
Gesture.PINKY = Gesture(1 << 5)

Gesture.NONE = Gesture(0)
Gesture.ALL = Gesture.RIGHT | Gesture.THUMB | Gesture.INDEX | Gesture.MIDDLE | Gesture.RING | Gesture.PINKY

class Motion:
    def draw(self, frame):
        pass
    def update(self, hand_landmarks, frame):
        pass