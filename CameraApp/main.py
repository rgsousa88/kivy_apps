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
import numpy as np
#from kivy.uix.camera import Camera
from kivy.logger import Logger
import dlib
import cvlib

class CameraBox(BoxLayout):
    button = ObjectProperty(None)
    img1 = ObjectProperty(None)

    def __init__(self,*args,**kwargs):
        super(CameraBox,self).__init__(*args,**kwargs)
        self.camera = cv2.VideoCapture(0)
        self.is_gray_scale = False
        self.do_anonymization = False
        self.detector = dlib.get_frontal_face_detector()
        #self.predictor = dlib.shape_predictor(args["shape_predictor"])

    def change_color(self):
        self.is_gray_scale = not self.is_gray_scale

    def apply_anonymization(self):
        self.do_anonymization = not self.do_anonymization

    def detect_face(self,frame):
        img = frame.copy()
        rects = self.detector(img,1)
        return rects

    def anonymize(self,frame,rect,detect_alg="dlib"):
        channel = frame.shape[2]
        output = frame.copy()
        step_x = 10
        step_y = 10
        if detect_alg == "dlib":
            left,top = rect.left(),rect.top()
            right,bottom = rect.right(),rect.bottom()
        elif detect_alg == "cvlib":
            left,top = rect[0],rect[1]
            right,bottom = rect[2],rect[3]
        else:
            return
        H,W = (right - left,bottom - top)
        factor_x = np.ceil(H/step_x+1) - 1
        factor_y = np.ceil(W/step_y+1) - 1

        for c in np.arange(channel):
            for start_x in np.arange(left,left+factor_x*step_x,step_x,dtype='int'):
                for start_y in np.arange(top,top+factor_y*step_y,step_y,dtype='int'):
                    frame[start_y:start_y+step_y,start_x:start_x+step_x,c] = np.median(frame[start_y:start_y+step_y,start_x:start_x+step_x,c])

    
    def update_image(self,dt):
        try:
            if self.camera.isOpened():
                Logger.info('MY_CAMERA_APP: CAMERA OPENED!')
            else:
                Logger.info('MY_CAMERA_APP: CAMERA NOT OPENED!')

            _,frame = self.camera.read()

            # if self.is_gray_scale:
            #     frame = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)

            if self.do_anonymization:                        
                detect_alg="dlib"
                
                if detect_alg == "dlib":
                    rects = self.detect_face(frame)
                else:
                    rects,confidence = cvlib.detect_face(frame)

                for i,rect in enumerate(rects):                
                    try:
                        if detect_alg == "dlib":
                            cv2.rectangle(frame,(rect.left(),rect.top()),(rect.right(),rect.bottom()),(255,0,0),1)
                        else:
                            cv2.rectangle(frame,(rect[0],rect[1]),(rect[2],rect[3]),(255,0,0),1)

                        self.anonymize(frame,rect,detect_alg=detect_alg)
                    except Exception as e:
                        print(e)
            
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
        Clock.schedule_interval(self.camera.update_image, 1.0/15.0)
        return self.camera
    
    def on_request_close(self, *args):
        self.camera.camera.release()
        return True

if __name__ == '__main__':
    CameraApp().run()