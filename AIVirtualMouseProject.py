'''import cv2
import numpy as np
import HandTrackingModule as htm
import time
import autopy

#####################################
wCam, hCam = 640, 480
frameR = 100  # Frame Reduction
smoothening = 7

###################################
pTime = 0
plocX, plocY = 0, 0
clocX, clocY = 0, 0

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
    #print(lmList)
    # print("Success:", success)
    # print("Image is None:", img is None)
    # img = cv2.flip(img, 1)
    # cTime = time.time()
    # fps = 1 / (cTime - pTime)
    # pTime = cTime
    # cv2.putText(img, str(int(fps)), (20, 50), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 3)
    # 2. Get the tip of the index and middle fingers
    if len(lmList) != 0:
        x1, y1 = lmList[8][1:]  # Index Finger Tip
        x2, y2 = lmList[12][1:]  # Middle Finger Tip
        #x1, y1 = lmList[8][1:]  # Index Finger Tip
        x8, y8 = lmList[4][1:]  # Thumb Tip
        #print(x1, y1, x2, y2)
    
    # 3. Check which fingers are up
        fingers = detector.fingersUp()
    #    print(fingers)
        cv2.rectangle(img, (frameR, frameR),(wCam - frameR, hCam - frameR), (255, 0, 255), 2)

    # 4. Only Index Finger : Moving Mode
        if (fingers[1] == 1 and fingers[2] == 0) or (fingers[0] == 1 and fingers[1] == 0):
            # 5. Convert Coordinates
            x3 = np.interp(x1, (frameR, wCam - frameR), (0, wScr))
            y3 = np.interp(y1, (frameR, hCam - frameR), (0, hScr))
            
            # 6. Smoothen Values
            clocX = plocX + (x3 - plocX) / smoothening
            clocY = plocY + (y3 - plocY) / smoothening
            # 7. Move Mouse
            autopy.mouse.move(wScr - clocX, clocY)
            cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
            plocX, plocY = clocX, clocY
        # 5. Convert Coordinates
    # 6. Smoothen Values

    # 7. Move Mouse
    # 8. Both Index and Middle fingers are up : Clicking Mode
        if (fingers[1] == 1 and fingers[2] == 1) or (fingers[0] == 1 and fingers[1] == 1):
            #detector.findDistance(8, 12, img, draw=False)
            # 9. Find distance between fingers
            length, img, lineInfo = detector.findDistance(8, 12,img)
            print(length)
            # 10. Click mouse if distance short
            if length < 40:
                cv2.circle(img, (lineInfo[4], lineInfo[5]), 15, (0, 255, 0), cv2.FILLED)
                autopy.mouse.click()
    """if len(lmList) != 0:
        x1, y1 = lmList[8][1:]  # Index Finger Tip
        x2, y2 = lmList[4][1:]  # Thumb Tip
        #print(x1, y1, x2, y2)
    
    # 3. Check which fingers are up
        fingers = detector.fingersUp()
    #    print(fingers)
        cv2.rectangle(img, (frameR, frameR),(wCam - frameR, hCam - frameR), (255, 0, 255), 2)

    # 4. Only Index Finger : Moving Mode
        if fingers[0] == 1 and fingers[1] == 0:
            # 5. Convert Coordinates
            x3 = np.interp(x1, (frameR, wCam - frameR), (0, wScr))
            y3 = np.interp(y1, (frameR, hCam - frameR), (0, hScr))
            
            # 6. Smoothen Values
            clocX = plocX + (x3 - plocX) / smoothening
            clocY = plocY + (y3 - plocY) / smoothening
            # 7. Move Mouse
            autopy.mouse.move(wScr - clocX, clocY)
            cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
            plocX, plocY = clocX, clocY
        # 5. Convert Coordinates
    # 6. Smoothen Values

    # 7. Move Mouse
    # 8. Both Index and Middle fingers are up : Clicking Mode
        if fingers[0] == 1 and fingers[1] == 1:
            #detector.findDistance(8, 12, img, draw=False)
            # 9. Find distance between fingers
            length, img, lineInfo = detector.findDistance(8, 4, img)
            print(length)
            # 10. Click mouse if distance short
            if length < 40:
                cv2.circle(img, (lineInfo[4], lineInfo[5]), 15, (0, 255, 0), cv2.FILLED)
                autopy.mouse.click()"""

    # 9. Find distance between fingers
    # 10. Click mouse if distance short

    # 11. Frame Rate
    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime
    cv2.putText(img, str(int(fps)), (20, 50), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 3)
    
    # 12. Display
    cv2.imshow("Image", img)
    cv2.waitKey(1)'''








import cv2
import numpy as np
import HandTrackingModule as htm
import time
import autopy

#####################################
wCam, hCam = 800, 580
frameR = 100  # Frame Reduction
smoothening = 7
clickCooldown = 0.4  # seconds between clicks, prevents click-spam while pinched

###################################
pTime = 0
plocX, plocY = 0, 0
clocX, clocY = 0, 0
lastLeftClickTime = 0
lastRightClickTime = 0
debounceTime = 0.2
doubleClickTime = 0.4

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

    if len(lmList) != 0:
        x1, y1 = lmList[8][1:]   # Index Finger Tip
        x2, y2 = lmList[12][1:]  # Middle Finger Tip

        # 3. Check which fingers are up -> [thumb, index, middle, ring, pinky]
        fingers = detector.fingersUp()
        cv2.rectangle(img, (frameR, frameR), (wCam - frameR, hCam - frameR), (255, 0, 255), 2)

        # 4. Moving Mode: ONLY index finger up
        if fingers[1] == 1 and fingers[2] == 0 and fingers[3] == 0:
            # 5. Convert Coordinates
            x3 = np.interp(x1, (frameR, wCam - frameR), (0, wScr))
            y3 = np.interp(y1, (frameR, hCam - frameR), (0, hScr))

            # 6. Smoothen Values
            clocX = plocX + (x3 - plocX) / smoothening
            clocY = plocY + (y3 - plocY) / smoothening

            # 7. Move Mouse
            autopy.mouse.move(wScr - clocX, clocY)
            cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
            plocX, plocY = clocX, clocY

        # 8. Left Click Mode: Index + Middle up, Ring down
        elif fingers[1] == 1 and fingers[2] == 1 and fingers[3] == 0:
            length, img, lineInfo = detector.findDistance(8, 12, img)
            if length < 40:
                cv2.circle(img, (lineInfo[4], lineInfo[5]), 15, (0, 255, 0), cv2.FILLED)
                timeSinceLastClick = time.time() - lastLeftClickTime
                if timeSinceLastClick > debounceTime:
                    if timeSinceLastClick < doubleClickTime:
                        autopy.mouse.click()
                        time.sleep(0.05)  # Small delay to prevent double click from being registered as two single clicks
                        autopy.mouse.click()
                    else :
                        
                        autopy.mouse.click()
                        lastLeftClickTime = time.time()
                
                
                    

        # 9. Right Click Mode: Index + Middle + Ring all up
        elif fingers[1] == 1 and fingers[2] == 1 and fingers[3] == 1:
            length, img, lineInfo = detector.findDistance(8, 12, img)
            if length < 40:
                cv2.circle(img, (lineInfo[4], lineInfo[5]), 15, (0, 0, 255), cv2.FILLED)
                if time.time() - lastRightClickTime > clickCooldown:
                    autopy.mouse.click(autopy.mouse.Button.RIGHT)
                    lastRightClickTime = time.time()

    # 11. Frame Rate
    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime
    cv2.putText(img, str(int(fps)), (20, 50), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 3)

    # 12. Display
    cv2.imshow("Image", img)
    cv2.waitKey(1)