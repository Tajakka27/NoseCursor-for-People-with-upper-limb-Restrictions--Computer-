from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.uic import loadUi
import sys
from face import *
import subprocess


# The Main Frame class...
class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi("interface.ui", self)
        self.video = FaceMeshWidget()
        self.calibrate()
        
        # Define Widgets...
        menu_camera_button = self.actionCamera
        menu_keyboard_button = self.actionKeyboard
               
        self.video_layout= self.findChild(QVBoxLayout, 'verticalLayout_3')
        self.pages = self.findChild(QStackedWidget, 'stackedWidget')
        
        self.camera_page = self.findChild(QWidget, 'cameraPage')
        self.keyboard_page = self.findChild(QWidget, 'keyboardPage')
        
        self.start_video_button = self.findChild(QPushButton, 'startVideoButton')
        self.end_video_button = self.findChild(QPushButton, 'endVideoButton')
        self.calibrate_button = self.findChild(QPushButton, 'calibrateButton')
        
        # Edit widget UI...
        self.calibrate_button.hide()
        self.end_video_button.hide()
        
        # Button Controls
        menu_camera_button.triggered.connect(self.startVideo)
        menu_keyboard_button.triggered.connect(self.startTyping)
        
        self.start_video_button.clicked.connect(self.startVideo)
        self.end_video_button.clicked.connect(self.endVideo)
        self.calibrate_button.clicked.connect(self.calibrate)

    def startVideo(self):
        self.pages.setCurrentWidget(self.camera_page)
        self.video_layout.addWidget(self.video)
        self.start_video_button.hide()
        self.calibrate_button.show()
        self.end_video_button.show()
        
    def calibrate(self):
        self.video.calibrate()
    
    def endVideo(self):        
        self.video.cap.release()
        self.video.timer.stop()
        
        self.video_layout.removeWidget(self.video)
        self.video.deleteLater()
        self.video = None
        
        self.start_video_button.show()
        self.calibrate_button.hide()
        self.end_video_button.hide()
        
    def startTyping(self):
        # self.pages.setCurrentWidget(self.keyboard_page)
         try:
            # Run the 'keyboard.py' script as a separate process
            subprocess.Popen(['python', 'keyboard.py'])
         except Exception as e:
            # Handle any exceptions here
            print(f"Error: {str(e)}")

        

    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWindow()
    window.setWindowIcon(QIcon('Images\logo.png'))
    window.show()
    app.exec()