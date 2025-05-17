import mediapipe as mp
import cv2

class Gesture:
    def __init__(self, n: int):
        self.n = n

    # def from_side(side):
        # return Gesture(side)
    def dir(self):
        return Gesture(self.n & 0b11)
    def from_face(face):
        return Gesture(face << 2)
    # THUMB IS NOT A FINGY (for convenience)
    def from_fingy(fingy):
        return Gesture(1 << (fingy + 4))

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
        return format(self.n, f"0{8}b")
    
    def __hash__(self):
        return hash(self.n)
    
    def __eq__(self, other):
        if not isinstance(other, Gesture):
            return NotImplemented
        return self.n == other.n

Gesture.UP = Gesture(0b00)
Gesture.DOWN = Gesture(0b01)
Gesture.LEFT = Gesture(0b10)
Gesture.RIGHT = Gesture(0b11)

Gesture.FRONT = Gesture(0 << 2)
Gesture.BACK = Gesture(1 << 2)

Gesture.THUMB = Gesture.from_fingy(-1)
Gesture.INDEX = Gesture.from_fingy(0)
Gesture.MIDDLE = Gesture.from_fingy(1)
Gesture.RING = Gesture.from_fingy(2)
Gesture.PINKY = Gesture.from_fingy(3)

Gesture.NONE = Gesture(0)
Gesture.ONE = Gesture.NONE | Gesture.INDEX
Gesture.TWO = Gesture.ONE | Gesture.MIDDLE
Gesture.THREE = Gesture.TWO | Gesture.RING
Gesture.FOUR = Gesture.THREE | Gesture.PINKY
Gesture.FIVE = Gesture.FOUR | Gesture.THUMB

class Motion:
    def draw(self, frame):
        pass
    def update(self, landmarks, frame):
        pass