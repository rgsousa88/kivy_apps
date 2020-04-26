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

class CameraBox(BoxLayout):
    button = ObjectProperty(None)
    img1 = ObjectProperty(None)

    def __init__(self,*args,**kwargs):
        super(CameraBox,self).__init__(*args,**kwargs)
        self.capture = cv2.VideoCapture(0)
        self.is_gray_scale = False

    def change_color(self):
        self.is_gray_scale = not self.is_gray_scale

    def update_image(self,dt):
        ret, frame = self.capture.read()

        if self.is_gray_scale:
            frame1 = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        else:
            frame1 = frame

        buf2 = cv2.flip(frame1,-1).tostring()

        if self.is_gray_scale:
            texture1 = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='luminance' )
            texture1.blit_buffer(buf2, colorfmt='luminance', bufferfmt='ubyte')
             
        else:
            texture1 = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr' )
            texture1.blit_buffer(buf2, colorfmt='bgr', bufferfmt='ubyte')     
                         
        self.img1.texture = texture1


class CameraApp(App):
    def build(self):
        camera = CameraBox()
        Clock.schedule_interval(camera.update_image, 1.0/30.0)
        return camera   

if __name__ == '__main__':
    CameraApp().run()