from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import (
    NumericProperty, ReferenceListProperty, ObjectProperty
)
from kivy.clock import  Clock
from kivy.graphics.texture import Texture
import cv2
#from kivy.uix.camera import Camera
from kivy.logger import Logger
import dlib

class CameraBox(BoxLayout):
    button = ObjectProperty(None)
    img1 = ObjectProperty(None)

    def __init__(self,*args,**kwargs):
        super(CameraBox,self).__init__(*args,**kwargs)
        self.camera = cv2.VideoCapture(0)
        self.is_gray_scale = False
        self.detector = dlib.get_frontal_face_detector()
        #self.predictor = dlib.shape_predictor(args["shape_predictor"])

    def change_color(self):
        self.is_gray_scale = not self.is_gray_scale

    def detect_face(self,frame):
        img = frame.copy()
        rects = self.detector(img,1)

        for i,rect in enumerate(rects):
            #shape = self.predictor(frame,rect)
            cv2.rectangle(img,(rect.left(),rect.top()),(rect.right(),rect.bottom()),(255,0,0),1)

        return img        

    def update_image(self,dt):
        try:
            if self.camera.isOpened():
                Logger.info('MY_CAMERA_APP: CAMERA OPENED!')
            else:
                Logger.info('MY_CAMERA_APP: CAMERA NOT OPENED!')

            _,frame = self.camera.read()

            if self.is_gray_scale:
                frame = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
            
            frame = self.detect_face(frame)
            buf = cv2.flip(frame,-1).tostring()            

            if self.is_gray_scale:
                colorfmt = 'luminance'
            else:
                colorfmt = 'bgr'

            texture = Texture.create(size=(frame.shape[1],frame.shape[0]),colorfmt=colorfmt)
            texture.blit_buffer(buf, colorfmt=colorfmt,bufferfmt='ubyte')    
                         
            self.img1.texture = texture
        
        except Exception as e:
            Logger.info('MY_CAMERA_APP: Occurred Exception {0}!'.format(e))


class CameraApp(App):
    def __init__(self,*args,**kwargs):
        super(CameraApp,self).__init__(*args,**kwargs)
        self.camera = None
    
    def build(self):
        self.camera = CameraBox()
        Clock.schedule_interval(self.camera.update_image, 1.0/30.0)
        return self.camera
    
    def on_request_close(self, *args):
        self.camera.camera.release()
        return True

if __name__ == '__main__':
    CameraApp().run()