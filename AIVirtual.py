import cv2
import numpy as np
import HandTrackingModule as htm
import time
import autopy
import pyautogui  # only used for scroll, since autopy has no scroll API

#####################################
wCam, hCam = 800, 580
frameR = 100          # Frame Reduction
smoothening = 7

# --- Click gesture tuning (2D, pixels) ---
clickDistThresh = 40

# --- Drag gesture tuning (3D pinch, thumb-index) ---
# NOTE: these numbers depend on your camera + distance from it.
# Print pinchDist3D for a few seconds and watch the console to calibrate.
dragEngageThresh = 45
dragReleaseThresh = 65   # higher than engage -> hysteresis, prevents flicker

# --- Scroll gesture tuning ---
scrollDeadzone = 15      # min vertical pixel movement before it counts as scroll
scrollSensitivity = 3    # multiplier for scroll amount

# --- Pause/resume (fist) gesture tuning ---
fistHoldFramesNeeded = 8   # how many consecutive fist frames trigger toggle
pauseCooldown = 1.0        # seconds before another toggle can fire

###################################
pTime = 0
plocX, plocY = 0, 0
clocX, clocY = 0, 0

lastLeftClickTime = 0
lastRightClickTime = 0
debounceTime = 0.2
doubleClickTime = 0.4
clickCooldown = 0.4

dragging = False
prevScrollY = None
fistFrameCount = 0
lastPauseToggleTime = 0
trackingActive = True

cap = cv2.VideoCapture(0)
print("Camera opened:", cap.isOpened())
cap.set(3, wCam)
cap.set(4, hCam)

detector = htm.handDetector(maxHands=1)
wScr, hScr = autopy.screen.size()
print("Screen size:", wScr, hScr)

while True:
    success, img = cap.read()
    img = detector.findHands(img)
    lmList, bbox = detector.findPosition(img)

    modeText = "Idle"

    if len(lmList) != 0:
        fingers = detector.fingersUp()
        cv2.rectangle(img, (frameR, frameR), (wCam - frameR, hCam - frameR), (255, 0, 255), 2)

        # ---------- 1. PAUSE / RESUME (closed fist) ----------
        if fingers.count(1) == 0:
            fistFrameCount += 1
        else:
            fistFrameCount = 0

        if fistFrameCount >= fistHoldFramesNeeded and (time.time() - lastPauseToggleTime) > pauseCooldown:
            trackingActive = not trackingActive
            lastPauseToggleTime = time.time()
            fistFrameCount = 0
            # release any in-progress drag when pausing
            if dragging:
                autopy.mouse.toggle(autopy.mouse.Button.LEFT, False)
                dragging = False

        if not trackingActive:
            modeText = "PAUSED"
        else:
            x1, y1 = lmList[8][1:3]    # Index tip
            x2, y2 = lmList[12][1:3]   # Middle tip

            # ---------- 2. DRAG & DROP (thumb-index pinch, 3D) ----------
            pinchDist3D = detector.findDistance3D(4, 8)
            print(pinchDist3D)  # uncomment to calibrate thresholds for your setup

            if dragging:
                modeText = "Dragging"
                if pinchDist3D > dragReleaseThresh:
                    autopy.mouse.toggle(autopy.mouse.Button.LEFT, False)
                    dragging = False
                else:
                    x3 = np.interp(x1, (frameR, wCam - frameR), (0, wScr))
                    y3 = np.interp(y1, (frameR, hCam - frameR), (0, hScr))
                    clocX = plocX + (x3 - plocX) / smoothening
                    clocY = plocY + (y3 - plocY) / smoothening
                    autopy.mouse.move(wScr - clocX, clocY)
                    plocX, plocY = clocX, clocY
                    cv2.circle(img, (x1, y1), 15, (0, 165, 255), cv2.FILLED)

            elif pinchDist3D < dragEngageThresh:
                autopy.mouse.toggle(autopy.mouse.Button.LEFT, True)
                dragging = True
                modeText = "Dragging"

            # ---------- 3. MOVE (index only) ----------
            elif fingers[1] == 1 and fingers[2] == 0 and fingers[3] == 0 and fingers[4] == 0:
                modeText = "Moving"
                x3 = np.interp(x1, (frameR, wCam - frameR), (0, wScr))
                y3 = np.interp(y1, (frameR, hCam - frameR), (0, hScr))
                clocX = plocX + (x3 - plocX) / smoothening
                clocY = plocY + (y3 - plocY) / smoothening
                autopy.mouse.move(wScr - clocX, clocY)
                cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
                plocX, plocY = clocX, clocY

            # ---------- 4. LEFT CLICK (index+middle up, ring down) ----------
            elif fingers[1] == 1 and fingers[2] == 1 and fingers[3] == 0:
                modeText = "Left Click"
                length, img, lineInfo = detector.findDistance(8, 12, img)
                if length < clickDistThresh:
                    cv2.circle(img, (lineInfo[4], lineInfo[5]), 15, (0, 255, 0), cv2.FILLED)
                    timeSinceLastClick = time.time() - lastLeftClickTime
                    if timeSinceLastClick > debounceTime:
                        if timeSinceLastClick < doubleClickTime:
                            autopy.mouse.click()
                            time.sleep(0.05)
                            autopy.mouse.click()
                        else:
                            autopy.mouse.click()
                        lastLeftClickTime = time.time()

            # ---------- 5. RIGHT CLICK (index+middle+ring up) ----------
            elif fingers[1] == 1 and fingers[2] == 1 and fingers[3] == 1 and fingers[4] == 0:
                modeText = "Right Click"
                length, img, lineInfo = detector.findDistance(8, 12, img)
                if length < clickDistThresh:
                    cv2.circle(img, (lineInfo[4], lineInfo[5]), 15, (0, 0, 255), cv2.FILLED)
                    if time.time() - lastRightClickTime > clickCooldown:
                        autopy.mouse.click(autopy.mouse.Button.RIGHT)
                        lastRightClickTime = time.time()

            # ---------- 6. SCROLL (index + pinky up, others down) ----------
            elif fingers[1] == 1 and fingers[4] == 1 and fingers[0] == 0 and fingers[2] == 0 and fingers[3] == 0:
                modeText = "Scrolling"
                cv2.circle(img, (x1, y1), 15, (255, 255, 0), cv2.FILLED)
                if prevScrollY is None:
                    prevScrollY = y1
                deltaY = prevScrollY - y1
                if abs(deltaY) > scrollDeadzone:
                    pyautogui.scroll(int(deltaY * scrollSensitivity))
                    prevScrollY = y1
            else:
                prevScrollY = None  # reset scroll reference when not scrolling

    # ---------- FPS + mode overlay ----------
    cTime = time.time()
    fps = 1 / (cTime - pTime) if pTime else 0
    pTime = cTime
    cv2.putText(img, f'FPS: {int(fps)}', (20, 50), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)
    cv2.putText(img, f'Mode: {modeText}', (20, 90), cv2.FONT_HERSHEY_PLAIN, 2, (0, 200, 0), 2)

    cv2.imshow("Image", img)
    cv2.waitKey(1)