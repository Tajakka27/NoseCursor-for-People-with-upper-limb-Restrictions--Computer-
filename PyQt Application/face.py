import cv2
import pyautogui
import threading
import mediapipe as mp
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from math import sqrt
from time import time
import screen_brightness_control as sbc

pyautogui.FAILSAFE = False
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_face_mesh = mp.solutions.face_mesh
drawing_spec = mp_drawing.DrawingSpec(thickness=1, circle_radius=1)
class FaceMeshWidget(QWidget):
    def __init__(self):
        super().__init__()        
        self.layout = QVBoxLayout(self)
        self.video_label = QLabel(self)
        self.layout.addWidget(self.video_label)
        self.click_time=0
        self.left = False
        self.right = False
        self.up = False
        self.down = False
        self.screenx,self.screeny=  pyautogui.size()
        # print(self.screenx,self.screeny)
        self.cap = cv2.VideoCapture(0)
        self.face_mesh = mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

        self.p_lip = False
        self.calibrated = False
        self.nose_calibration = [0, 0, 0, 0]
        self.face_timer = 0
        self.face_timer_start=0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(5)
        self.right_click_activated,self.drag_and_drop_activated,self.drag_or_drop=0,0,0

        self.face_timer, self.face_timer_start,self.face_detected,self.one =0, 0, None,None

        # Create a thread for mouse control
        self.mouse_control_thread = threading.Thread(target=self.mouse_control)
        self.mouse_control_thread.daemon = True  # The thread will terminate when the main program exits
        self.mouse_control_thread.start()

        
    def update_frame(self):
        success, image = self.cap.read()
        if not success:
            return

        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(image)
        
        if self.one!=2 and self.one!=None and self.one!=0:
            if  results.multi_face_landmarks:
                print("ekhane ashche",self.one)
                sbc.set_brightness(100)
                self.one=2
            
            

        if results.multi_face_landmarks:      
            if self.one!=1:
                self.face_timer, self.face_timer_start,self.face_detected,self.one=0, 0, None,0
                for face_landmarks in results.multi_face_landmarks:
                    for id, lm in enumerate(face_landmarks.landmark):
                        ih, iw, ic = image.shape
                        
                        if id == 4:
                            nose_x, nose_y = int(lm.x*iw),int(lm.y*ih)
                            cv2.circle(image, (nose_x, nose_y), radius=3, color=(225, 0, 100), thickness=1)
                        
                        elif id == 102:
                            nose_l_x, nose_l_y = int(lm.x*iw),int(lm.y*ih)
                            cv2.circle(image, (nose_l_x, nose_l_y), radius=3, color=(225, 0, 100), thickness=1)
                        
                        elif id == 331:
                            nose_r_x, nose_r_y = int(lm.x*iw),int(lm.y*ih)
                            cv2.circle(image, (nose_r_x, nose_r_y), radius=3, color=(225, 0, 100), thickness=1)
                        
                        elif id == 164:
                            nose_d_x, nose_d_y = int(lm.x*iw),int(lm.y*ih)
                            cv2.circle(image, (nose_d_x, nose_d_y), radius=3, color=(225, 0, 100), thickness=1)
                        
                        elif id == 197:
                            nose_u_x, nose_u_y = int(lm.x*iw),int(lm.y*ih)
                            cv2.circle(image, (nose_u_x, nose_u_y), radius=3, color=(225, 0, 100), thickness=1)
                            
                            
                        elif id == 13:
                            lip_u_x, lip_u_y = int(lm.x*iw),int(lm.y*ih)                     
                            cv2.circle(image, (lip_u_x, lip_u_y), radius=3, color=(0, 225, 100), thickness=1)
                        elif id == 14:
                            lip_d_x, lip_d_y = int(lm.x*iw),int(lm.y*ih)                     
                            cv2.circle(image, (lip_d_x, lip_d_y), radius=3, color=(0, 225, 100), thickness=1)
                    
                self.checkLips(lip_d_y, lip_u_y, lip_d_x, lip_u_x)
                self.checkNose(nose_x, nose_y, nose_l_x, nose_l_y, nose_r_x, nose_r_y, nose_d_x, nose_d_y, nose_u_x, nose_u_y)

        
        # elif results.multi_face_landmarks and self.one==1:
        #     self.one=0
        #     print("ekhane ashche",self.one)
        #     sbc.set_brightness(100)

        elif results.multi_face_landmarks == None and self.face_detected == False:
            self.face_timer =time()-self.face_timer_start
            # print("time difference holo : ",self.face_timer)

        elif results.multi_face_landmarks == None:
            self.face_timer_start=time()
            self.face_detected=False
            # print ("shurur time : ", self.face_timer_start)

        if self.face_timer>10:
            sbc.set_brightness(50)
            self.one=1
        


        h, w, ch = image.shape
        bytes_per_line = ch * w
        qt_image = QImage(image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_image)
        self.video_label.setPixmap(pixmap)

    def closeEvent(self, event):
        self.cap.release()
        self.timer.stop()
        event.accept()
            
    def calibrate(self):
        self.calibrated = False
    

        
    def checkLips(self, lip_d_y, lip_u_y, lip_d_x, lip_u_x):
        distance = sqrt((lip_d_x - lip_u_x)**2 + (lip_d_y - lip_u_y)**2)
        if distance > 10 and self.drag_and_drop_activated%2==1:
            print("drag and drop mode e ase")
            # posx,posy=pyautogui.position()
            if self.drag_or_drop%2==0:
                print("select hoise file")
                pyautogui.mouseDown(button='left')
                # pyautogui.moveTo(posx+60,posy+60)
            else :
                print("unselectmhoise file")
                pyautogui.mouseUp(button='left')
                # pyautogui.moveTo(posx+60,posy+60)

        self.drag_or_drop= self.drag_or_drop+1


        if distance > 10 and self.right_click_activated%2==1:
        #    //left click
        #    print("double Clicked")
             pyautogui.click(clicks=2)
        #    print("edclidian distace is ",distance)
        elif distance > 25:
            if not self.p_lip:
                # print("Clicked", lip_d_x-lip_u_x, lip_d_y-lip_u_y,self.click_time)
                # print("edclidian distace is : ",distance)
                pyautogui.click(button='right')
            self.p_lip = True
        elif distance > 10:
            if not self.p_lip:
                # print("Clicked", lip_d_x-lip_u_x, lip_d_y-lip_u_y,self.click_time)
                # print("edclidian distace is : ",distance)
                pyautogui.click(clicks=1)
            self.p_lip = True
        else:
            self.p_lip = False

            
            
    def checkNose(self, x, y, l_x, l_y, r_x, r_y, d_x, d_y, u_x, u_y):
        delta_l = sqrt((x - l_x) ** 2 + (y - l_y) ** 2)
        delta_r = sqrt((x - r_x) ** 2 + (y - r_y) ** 2)
        delta_u = sqrt((x - u_x) ** 2 + (y - u_y) ** 2)
        delta_d = sqrt((x - d_x) ** 2 + (y - d_y) ** 2)
        
        if not self.calibrated:
            self.calibrated = True
            self.nose_calibration[0] = delta_l
            self.nose_calibration[1] = delta_r
            self.nose_calibration[2] = delta_u
            self.nose_calibration[3] = delta_d
            print(self.nose_calibration[0], self.nose_calibration[1],self.nose_calibration[2],self.nose_calibration[3])
            
        self.left = self.right = self.up = self.down = False
        
        posx,posy=pyautogui.position()

        # if posx==0: 
        #     pyautogui.moveTo(500, 500) 
        #     pyautogui.scroll(-100000000)
        if (posy>=0 and posy<self.screeny/2) and posx==0:
            #print(self.screeny)
            pyautogui.moveTo(500, 500) 
            pyautogui.scroll(100000000)
        if (posy>=self.screeny/2 and posy<self.screeny) and posx==0:
            #print(self.screeny)
            pyautogui.moveTo(500, 500) 
            pyautogui.scroll(-100000000)
        
        if (posx>0 and posx<self.screenx/2) and posy==0:
            self.right_click_activated=self.right_click_activated+1
            # print("double click r jnno gese",self.right_click_activated)
            pyautogui.moveTo(500, 500) 
        if (posx>=self.screenx/2 and posx<self.screenx) and posy==0:
            # drag and drop r kaj
            self.drag_and_drop_activated=self.drag_and_drop_activated+1
            pyautogui.moveTo(500, 500)
            



        if delta_l-self.nose_calibration[0] > 5:
            print("Left: ", delta_l)
            self.left = True
        if delta_r-self.nose_calibration[1] > 5:
            print("Right: ", delta_r)
            self.right = True
        if self.nose_calibration[2]-delta_u > 5:
            print("Up: ", delta_u)
            self.up = True
        if self.nose_calibration[3]-delta_d > 3:
            print("Down: ", delta_d)
            self.down = True

            
            
            
    def mouse_control(self):
        while True:
            if self.left:
                for _ in range(5):
                    pyautogui.moveRel(-10, 0)
            if self.right:
                for _ in range(5):
                    pyautogui.moveRel(10, 0)
            if self.up:
                for _ in range(5):
                    pyautogui.moveRel(0, -10)
            if self.down:
                for _ in range(5):
                    pyautogui.moveRel(0, 10)
            

