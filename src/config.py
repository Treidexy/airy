from gesture import Gesture
from motion.base import Motion
from motion.swap_workspace import SwapWorkspaceMotion
from motion.mouse import MouseMotion
from motion.click import ClickMotion
from motion.scroll import ScrollMotion
from motion.type import TypeMotion

MIN_DETECTION_CONFIDENCE = 0.7
MIN_TRACKING_CONFIDENCE = 0.5
NUM_HANDS = 1

for name in dir(Gesture):
    if not name.startswith("__"):  # Avoid special methods/attributes
        value = getattr(Gesture, name)
        globals()[name] = value

motions: dict[Gesture, list[Motion]] = {
    UP | FRONT | FIVE: [SwapWorkspaceMotion()],
    UP | FRONT | ONE: [MouseMotion()],
    DOWN | BACK | ONE: [ClickMotion('0'), MouseMotion()],
    DOWN | BACK | TWO: [ClickMotion('1'), MouseMotion()],
    UP | FRONT | TWO: [ScrollMotion()],
    UP | BACK | ONE: [ClickMotion('0')],
    UP | BACK | TWO: [ClickMotion('1')],
    RIGHT | BACK | FOUR: [TypeMotion('https://youtube.com\\n')],
    UP | BACK | FOUR: [TypeMotion('f')],
    LEFT | BACK | TWO: [TypeMotion('j')],
    RIGHT | BACK | TWO: [TypeMotion('l')],
}