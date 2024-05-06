import cv2
import numpy as np
import time
import mediapipe as mp
import math

class handDectector():
    def __init__(self, mode=False, maxHands=2,model_complexity=1, detectionCon=0.5, trackCon=0.5):
        self.mode = mode
        self.maxHands = maxHands
        self.model_complexity = model_complexity
        self.detectioncon = detectionCon
        self.trackcon = trackCon

        self.mphands = mp.solutions.hands
        self.Hands = self.mphands.Hands(self.mode, self.maxHands, self.model_complexity, self.detectioncon, self.trackcon)

        self.mpDraw = mp.solutions.drawing_utils
        self.tip_finger = [4, 8, 12, 16, 20]
  
    def findHands(self, img, draw=True):
        img = cv2.flip(img, 1)# lat camera
        imgRGB = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
        self.result = self.Hands.process(imgRGB)
        #print(self.result.multi_hand_landmarks)

        if self.result.multi_hand_landmarks:
            for handLms in self.result.multi_hand_landmarks:
                if draw:
                    self.mpDraw.draw_landmarks(img,handLms,self.mphands.HAND_CONNECTIONS)

        return img, self.result

    def findPosition(self, img, handNo = 0, draw = True):
        xList = []
        yList = []
        bbox = []
        self.lmlist = []

        if self.result.multi_hand_landmarks:
            myhand = self.result.multi_hand_landmarks[handNo]
            for i,j in enumerate(myhand.landmark):
                h,w,c = img.shape
                cx,cy = int(j.x * w), int(j.y*h)

                xList.append(cx)
                yList.append(cy)
                self.lmlist.append([i,cx,cy])

            max_xlist, max_ylist = max(xList), max(yList)
            min_xlist, min_ylist = min(xList), min(yList)
            bbox = [min_xlist,min_ylist,max_xlist,max_ylist]   


        return self.lmlist, bbox    



    def finger_up(self):
        fingers = []
        if len(self.lmlist) != 0:
            #Ngon cai
            if self.lmlist[self.tip_finger[0]][1] < self.lmlist[self.tip_finger[0] - 1][1]:
                
                fingers.append(1)
            else:
                fingers.append(0)

            # 4 ngon con lai 

            for i in range(1,5):
                if self.lmlist[self.tip_finger[i]][2] < self.lmlist[self.tip_finger[i] -2][2]:
                    fingers.append(1)
                else:
                    fingers.append(0)

        return fingers            

    def find_Distance(self, p1, p2, img, draw = True, r=15, t=3):
        x1,y1 = self.lmlist[p1][1:]
        x2,y2 = self.lmlist[p2][1:]

        cx, cy = (x1+x2)//2, (y1+y2)//2

        if draw:
            #cv2.line(img,(x1,y1),(x2,y2),(0,255,255),t)
            cv2.circle(img, (x1, y1), r, (0,255,255), cv2.FILLED)
            cv2.circle(img, (x2, y2), r, (0,255,255), cv2.FILLED)
            cv2.circle(img,(cx,cy),r,(0,255,255),cv2.FILLED)

        length = math.hypot((x2-x1),(y2-y1))
        coordinate = [x1, y1, x2, y2, cx, cy]
        return length, img, coordinate





def main():
    cTime = 0
    pTime = 0


    cap = cv2.VideoCapture(0)
    detector = handDectector()

    while True:
        ret,img = cap.read()
        img = detector.findHands(img)
        lmlist, bbox = detector.findPosition(img)
        # finger = detector.finger_up()

        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime
 
        cv2.putText(img, f"fps : {int(fps)}", (10, 70), cv2.FONT_HERSHEY_PLAIN, 3,
                    (255, 0, 255), 3)
 
        cv2.imshow("Image", img)
        if cv2.waitKey(1) == ord("q"):
            break
 
 
if __name__ == "__main__":
    main()
