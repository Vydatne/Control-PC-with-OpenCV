import cv2
import numpy as np
import time
import math
import HandTrackingModule as htm
import autopy
import screen_brightness_control as sbc
import pyautogui
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

time_init = True
rad = 40
ctime = 0
cap = cv2.VideoCapture(0)
cap.set(3, 640)# cài đặt chiều rộng của khung hình
cap.set(4, 480)#cài đặt chiều cao của khung hình
pTime = 0
detector = htm.handDectector()

wScr, hScr = autopy.screen.size()# Lấy chiều dài mặc định của khung hình
plocX, plocY = 0, 0
clocX, clocY = 0, 0

devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
# volume.GetMute()
# volume.GetMasterVolumeLevel()

# Lấy dải âm lượng của máy tính
volume_range = volume.GetVolumeRange()

# Giải nén các giá trị tối thiểu và tối đa
min_Vol = volume_range[0]
max_Vol = volume_range[1]


minBrightness = 0
maxBrightness = 100


take_screenshot = False  # Biến cờ để xác định liệu bạn muốn chụp ảnh hay không, mặc định là false
screenshot_count = 1  # Biến để đếm số lượng ảnh đã chụp

#Hàm xác định các chức năng
def getTool(x):
    if 70 < x < 170:
        return "Mouse"
    elif 170 < x < 270:
        return "Volume"
    elif 270 < x < 370:
        return"Brightness"
    elif 370 < x < 470:
        return "ScreenCap"
    elif 470 < x < 570:
        return 'Exit'


tipIds = [4, 8, 12, 16, 20]
mode = ''
active = 0


while True:
    success, img = cap.read()
    img, result = detector.findHands(img)
    lmlist, bbox = detector.findPosition(img)
    fingers = detector.finger_up()

    #Đọc các hình ảnh biểu hiện cho các chức năng
    image1 = cv2.imread('D:\Python\Project\image\Mouse.jpg')
    image2 = cv2.imread('D:\Python\Project\image\Volume.jpg')
    image3 = cv2.imread('D:\Python\Project\image\Light.jpg')
    image4 = cv2.imread('D:\Python\Project\image\ScrCap.jpg')
    image5 = cv2.imread('D:\Python\Project\image\Exit.jpg')

    #Xác định vị trí của các ảnh trên khung hình
    img[:image1.shape[0], 70:70 + image1.shape[1]] = image1
    img[:image2.shape[0], 70 + image1.shape[1]:70 + image1.shape[1] + image2.shape[1]] = image2
    img[:image3.shape[0], 70 + image1.shape[1] + image2.shape[1]:70 + image1.shape[1] + image2.shape[1] + image3.shape[1]] = image3
    img[:image4.shape[0], 70 + image1.shape[1] + image2.shape[1] + image3.shape[1]:70 + image1.shape[1] + image2.shape[1] + image3.shape[1] + image4.shape[1]] = image4
    img[:image5.shape[0], 70 + image1.shape[1] + image2.shape[1] + image3.shape[1] + image4.shape[1]: 70 + image1.shape[1] + image2.shape[1] + image3.shape[1] + image4.shape[1] + image5.shape[1]] = image5

    if result.multi_hand_landmarks: #kiểm trai dữ liệu phát hiện và trả về điểm mốc không
        for i in result.multi_hand_landmarks: #vòng lặp duyệt qua các điểm mốc được phát hiện
            x, y = int(i.landmark[8].x * 640), int(i.landmark[8].y * 480) # xác định các điểm mốc trên khung hình tương ứng (640,480)
            if (70 < x < 570 and y < 100): # kiểm tra điểm mốc nếu trong vùng hình ảnh các chức năng
                if time_init: #nếu biến thời gian khởi tạo là True
                    ctime = time.time() #thời gian hiện tại
                    time_init = False # đặt cờ thời gian khởi tạo là False - dừng điều kiện
                ptime = time.time() # lưu thời gian hiện tại vào ptime 

                cv2.circle(img, (x, y), rad, (0, 255, 255), 2) #vẽ vòng tròn bán kính rad lên khung hình tại điểm mốc
                rad -= 1 #giảm dần giá trị bán kính

                if (ptime - ctime) > 0.5: #nếu thời gian điểm mốc tại hình ảnh chức năng lớn hơn 0.5s
                    mode = getTool(x) #gọi hàm getTool xác định chế độ
                    print("your current mode set to : ", mode)
                    time_init = True #đặt cờ thời gian khởi tạo True và trả bán kính về lại 40
                    rad = 40
            else: #nếu điểm mốc không nằm trong vùng hình ảnh các chức năng
                time_init = True
                rad = 40
        if mode == "Mouse":
            active = 1
            frameR = 120
            wCam, hCam = 640, 480
            if len(lmlist) != 0:
                x1, y1 = lmlist[8][1:]  # Đầu ngón trỏ id = 8
                x2, y2 = lmlist[12][1:]  # Đầu ngón giữa id = 12
                
                # Vẽ hình chữ nhật giới hạn khu vực di chuột khả dụng
                cv2.rectangle(img, (frameR, frameR), (wCam - frameR, hCam - frameR), (255, 0, 255), 2)

                # 1. Chế độ di chuột, ngón trỏ mở
                if fingers == [0, 1, 0, 0, 0]:
                    # 2. Chuyển đổi toạ độ phù hợp khung hình
                    x3 = np.interp(x1, (frameR, wCam - frameR), (0, wScr))
                    y3 = np.interp(y1, (frameR, hCam - frameR), (0, hScr))

                    # 3. Làm mượt, giá trị smooth = 5
                    clocX = plocX + (x3 - plocX) /5
                    clocY = plocY + (y3 - plocY) /5

                    # 4. Di chuyển chuột
                    cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
                    autopy.mouse.move(plocX, plocY)
                    plocX = clocX
                    plocY = clocY

                # 5. Ngón trỏ và ngón giữa mở: click trái
                if fingers[1] == 1 and fingers[2] == 1:

                    # 6. Xác định khoảng cách hai ngón
                    length, img, lineInfo = detector.find_Distance(8, 12, img)
                    print(length)

                    # 7. Click
                    if length < 20:
                        cv2.circle(img, (lineInfo[4], lineInfo[5]), 7, (0, 255, 0), cv2.FILLED)
                        autopy.mouse.click()
                        time.sleep(0.25)

                # 8. Ngón trỏ và ngón cái: click phải
                if fingers[0] == 1 and fingers[1] == 1:

                    # 9. Xác định khoảng cách giữa hai ngón
                    length, img, lineInfo = detector.find_Distance(4, 8, img)
                    print(length)

                    # 10. Click
                    if length < 20:
                        cv2.circle(img, (lineInfo[4], lineInfo[5]), 7, (0, 255, 0), cv2.FILLED)
                        autopy.mouse.click(button=autopy.mouse.Button.RIGHT)
                        time.sleep(0.25)
                if fingers == [0, 0, 0, 0, 0]: # Trở về menu nếu nắm bàn tay
                    active = 0
                    mode = 'None'
                    print(mode)

        elif mode == 'Volume':
            active = 1
            if len(lmlist) != 0:
                if fingers == [0, 0, 0, 0, 0]:# Trở về menu nếu nắm bàn tay
                    active = 0
                    mode = 'None'
                    print(mode)
                else:
                    x11,y11 = lmlist[4][1], lmlist[4][2] #ngon cai
                    x22,y22 = lmlist[8][1], lmlist[8][2] #ngon tro
                    x10,y10 = lmlist[12][1], lmlist[12][2] #ngón giữa
                    #cv2.circle(frame,(x1,y1),12,(0,255,255),cv2.FILLED)
                    cv2.circle(img, (x22, y22), 12, (0, 255, 255), cv2.FILLED)

                    x33,y33 = (x11+x22)//2, (y11+y22)//2

                    x4,y4 = 0,y22
                    x5,y5 = x22-x4,y22-y4

                    length = math.hypot(x5, y5)
                    length3 = math.hypot(x10-x22, y10-y22)
                    length2 = math.hypot(x22-x11, y22-y11)
                    #print(length)
                    # do dai tay tu 17 - 193
                    # cv2.circle(img,(x10,y10), 12, (0, 255, 255), cv2.FILLED)
                    if length3 < 60:
                        cv2.circle(img,((x10+x22)//2,(y10+y22)//2),12,(0,0,0),cv2.FILLED)
                    if length3 > 60:

                        # cv2.circle(frame,(x3,y3),12,(0,0,0),cv2.FILLED)

                        vol = np.interp(length, [0, 640], [min_Vol,max_Vol])
                        thanhamluong = np.interp(length, [35,183], [300, 100])
                        vol_phantram = np.interp(length, [35,183], [0, 100])
                        #print(vol,length)
                        # print(type(vol))
                        # print(type(thanhamluong))
                        volume.SetMasterVolumeLevel(vol, None)
                        a = volume.GetMasterVolumeLevelScalar() * 100
                        print(a)
                        cv2.putText(img,f"Volume : {int(a)}",(230,150),3,cv2.FONT_HERSHEY_PLAIN,(0,0,0),4)
                        # pham vi am luong -65.25 -> 0

        elif mode == "Brightness":
            active = 1
            if lmlist != 0:
                if fingers == [0, 0, 0, 0, 0]:
                    active = 0
                    mode = 'None'
                    print(mode)
                else:
                    x_cai,y_cai = lmlist[4][1], lmlist[4][2] #ngon cai
                    x_tro,y_tro = lmlist[8][1], lmlist[8][2] #ngon tro
                    x_giua,y_giua = lmlist[12][1], lmlist[12][2] #ngón giữa
                    #cv2.circle(frame,(x1,y1),12,(0,255,255),cv2.FILLED)
                    cv2.circle(img, (x_tro,y_tro), 12, (0, 255, 255), cv2.FILLED)
                    x4,y4 = 0, y_tro
                    x55,y55 = x_tro-x4, y_tro-y4

                    length = math.hypot(x55,y55)
                    length3 = math.hypot(x_giua-x_tro,y_giua-y_tro)

                    #print(length)
                    # do dai tay tu 17 - 193
                    cv2.circle(img,(x_giua,y_giua),12,(0,255,255),cv2.FILLED)
                    if length3 < 60:

                        cv2.circle(img,((x_giua+x_tro)//2,(y_giua+y_tro)//2),12,(0,0,0),cv2.FILLED)
                    if length3 > 60:

                        #cv2.circle(frame,(x3,y3),12,(0,0,0),cv2.FILLED)
                        brightness = np.interp((length), [0,640], [minBrightness, maxBrightness])
                        sbc.set_brightness(int(brightness))
                        a = sbc.get_brightness()
                        cv2.putText(img,f"Brightness : {a}",(180,150), 3,cv2.FONT_HERSHEY_PLAIN,(0,0,0),4)
                        # pham vi am luong -65.25 -> 0

        elif mode == "ScreenCap" or fingers == [1, 1, 1, 1, 1]:# Chụp màn hình nếu chọn nút ScreenCap hoặc 5 ngón tay mở
            active = 1
            if fingers == [0, 0, 0, 0, 0]:# Trở về menu nếu nắm bàn tay
                active = 0
                mode = 'None'
                print(mode)
            else:
                take_screenshot = True # Đặt cờ lên True để chụp ảnh
                if take_screenshot:  # Kiểm tra nếu biến cờ là True thì chụp ảnh
                    filename = f"D:\Python\Project\image\capture_{screenshot_count}.png"  # Tạo tên tập tin
                    my_screenshot = pyautogui.screenshot() #Chụp ảnh
                    my_screenshot.save(filename) #Lưu ảnh
                    print(f"Captured {filename}")
                    screenshot_count += 1
                    take_screenshot = False  # Sau khi chụp ảnh, đặt biến cờ về False để ngừng chụp
                    time.sleep(1)
        elif mode == 'Exit':
            break

    cTime = time.time()
    fps = 1/((cTime + 0.01)-pTime)
    pTime = cTime

    cv2.putText(img,f'FPS:{int(fps)}', (480, 130), cv2.FONT_ITALIC,1, (255,0,0),3)
    cv2.imshow('Menu Function', img)

    key = cv2.waitKey(1)
    if key == 27:
        break