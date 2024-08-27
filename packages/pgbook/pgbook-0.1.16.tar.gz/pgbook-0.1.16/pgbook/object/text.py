import pygame
import pkg_resources
from .object import Position
from ..eventlist.thinglist import ThingList

class BaseText:
    def __init__(self,text='Some Text',color=(255,255,255),textsize=24,textfile=None):
        self.objects_type='BaseButton'
        self.drawlist=ThingList()
        self.eventlist=ThingList()
        
        self.new_date(text,color,textsize,textfile)
        
    def connect_page(self,page):
        self.pos=Position(0,0,page.screen.width,page.screen.height)
        page.drawlist.connect(self.drawlist)
        page.eventlist.connect(self.eventlist)
        self.drawlist.connect(self.draw,'DrawButton')
        
    def draw(self,screen):
        textRect = self.textbook.get_rect()
        textRect.center = (self.pos.true_pos().x,self.pos.true_pos().y)
        screen.blit(self.textbook, textRect)
        
    def new_date(self,text='Some Text',color=(255,255,255),textsize=24,textfile=None):
        self.text=text
        self.textcolor=color
        if textfile==None:
            font_path = pkg_resources.resource_filename('pgbook', 'static/fonts/NotoFont.ttf')
        else:
            font_path=textfile
        self.font= pygame.font.Font(font_path,textsize)
        self.textbook = self.font.render(self.text, True, self.textcolor,None)
        
class TextInput:
    def __init__(self,text='',empty_text='Input Some Text',
                 back_color=(128,128,128),cback_color=(96,96,96),
                 text_color=(256,256,256),notext_color=(200,200,200),textsize=24,textfile=None):
        
        #默认文字
        self.DefaultText=text
        self.DefaultEmptyText=empty_text
        #默认颜色
        self.DefaultBackColor=back_color
        self.SelectedBackColor=cback_color
        self.DefaultTextColor=text_color
        self.NoTextColor=notext_color
        
        self.objects_type='BaseButton'
        self.drawlist=ThingList()
        self.eventlist=ThingList()
        
        self.new_date(text,textcolor,textsize,textfile)