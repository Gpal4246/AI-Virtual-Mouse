# AI Virtual Mouse — Gesture Guide

Control your mouse using one hand in front of the webcam. All gestures are read from a single hand (`maxHands=1`).

Finger order used below: **Thumb, Index, Middle, Ring, Pinky** (1 = up/extended, 0 = down/folded).

---

## Operations

| Operation | Gesture | Fingers Up | How it Works |
|---|---|---|---|
| **Move Cursor** | Point with index finger only | Index only | Moves the mouse cursor to match your index fingertip position on screen. |
| **Left Click / Double Click** | Index + Middle fingers up, brought close together (pinch) | Index + Middle | Pinching index and middle tips together (<40px) triggers a click. Pinch again quickly (within 0.4s) and it registers as a double-click. |
| **Right Click** | Index + Middle + Ring fingers up, pinch Index+Middle together | Index + Middle + Ring | Same pinch gesture as left click, but with the ring finger also raised. Has a 0.4s cooldown to prevent repeat right-clicks. |
| **Drag & Drop** | Pinch Thumb + Index together and hold | Thumb + Index close (3D pinch) | Bringing thumb and index tip together in 3D space (uses depth, not just x/y) engages a mouse-down "grab." Move your hand while pinched to drag; release the pinch to drop. |
| **Scroll** | Index + Pinky up, others down | Index + Pinky | Move your hand up/down while holding this gesture to scroll the active window. Moving hand up = scroll up, moving hand down = scroll down. |
| **Pause / Resume Tracking** | Closed fist, held briefly | No fingers up | Holding a closed fist for about 8 frames toggles mouse control on/off. Useful so the cursor doesn't move just because your hand is in frame (e.g. while talking, adjusting position, etc). A 1-second cooldown prevents accidental double-toggles. |

---

## On-Screen Feedback

The camera window shows:
- **FPS** — top-left, frame rate of hand tracking.
- **Mode** — top-left below FPS, shows current gesture mode: `Idle`, `Moving`, `Left Click`, `Right Click`, `Dragging`, `Scrolling`, or `PAUSED`.
- A magenta circle appears on your index fingertip while moving.
- A colored circle appears at the pinch point during clicks (green = left click, red = right click, orange = dragging).

---

## Tuning Notes

If gestures feel too sensitive or not sensitive enough, adjust these constants near the top of the main script:

- `clickDistThresh` — pixel distance for left/right click pinch (default 40).
- `dragEngageThresh` / `dragReleaseThresh` — 3D pinch distance to start/stop a drag (default 45 / 65). These depend on your camera and distance from it — print `pinchDist3D` and watch the console to find good values for your setup.
- `scrollDeadzone` — minimum vertical hand movement (px) before it counts as a scroll (default 15).
- `scrollSensitivity` — multiplier controlling how fast scrolling happens (default 3).
- `fistHoldFramesNeeded` — how long you must hold a fist before pause/resume toggles (default 8 frames).
- `smoothening` — higher values = smoother but laggier cursor movement (default 7).

---

## Requirements

```
pip install opencv-python mediapipe autopy pyautogui numpy
```

## Files

- `HandTrackingModule.py` — hand landmark detection wrapper (MediaPipe).
- `AIVirtual.py` — main script; run this to start the virtual mouse.