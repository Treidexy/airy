from motion.base import Motion, Gesture
from motion.swap_workspace import SwapWorkspaceMotion
from motion.mouse import MouseMotion
from motion.click import ClickMotion
from motion.scroll import ScrollMotion
from motion.type import TypeMotion

MIN_DETECTION_CONFIDENCE = 0.7          # Minimum confidence value for hand detection to be considered successful
MIN_TRACKING_CONFIDENCE = 0.5           # Minimum confidence value for hand landmarks to be tracked successfully
MIN_PRESENCE_CONFIDENCE = 0.5           # Minimum confidence value for the hand presence score in the hand landmark detection
NUM_HANDS = 1                           # Maximum number of hands to detect

for name in dir(Gesture):
    if not name.startswith("__"):  # Avoid special methods/attributes
        value = getattr(Gesture, name)
        globals()[name] = value

motions: dict[Gesture, list[Motion]] = {
    UP | FRONT | FIVE: [SwapWorkspaceMotion()],
    UP | FRONT | ONE: [MouseMotion()],
    UP | BACK | ONE: [ClickMotion('0'), MouseMotion()],
    UP | FRONT | TWO: [ScrollMotion()],
    UP | BACK | ONE | THUMB: [ClickMotion('0')],
    UP | BACK | TWO: [ClickMotion('1')],
    UP | BACK | THREE: [TypeMotion('https://youtube.com\\n')],
    UP | BACK | FOUR: [TypeMotion('f')],
    LEFT | BACK | TWO: [TypeMotion('j')],
    RIGHT | BACK | TWO: [TypeMotion('l')],
}