from .object import Position
from ..eventlist.thinglist import ThingList
from ..eventlist.signal import Signal

from .text import BaseText
import pygame
class BaseButton():
    '''
    所有按钮的基类
    '''
    def __init__(self):
        self.objects_type='BaseButton'
        self.drawlist=ThingList()
        self.eventlist=ThingList()
        
        self.Down=Signal()
        self.MouseOn=Signal()
        
        self.rect=pygame.rect.Rect(0,0,128,48)
    def connect_page(self,page):
        self.pos=Position(0,0,page.screen.width,page.screen.height)
        page.drawlist.connect(self.drawlist)
        page.eventlist.connect(self.eventlist)
        self.drawlist.connect(self.draw,'DrawButton')
        self.drawlist.connect(self.check,'CheckButton')
        
    def draw(self,screen):
        if self.Down.is_true():
            color=(200,200,200)
        elif self.MouseOn.is_true():
            color=(156,156,156)
        else:
            color=(128,128,128)
        self.rect.center=(self.pos.true_pos().x,self.pos.true_pos().y)
        
        self.drawrect=pygame.draw.rect(screen,color,self.rect,width=0,
                                       border_radius=6)
        
    def check(self,screen):
        mouse_presses = pygame.mouse.get_pressed()
 
        if mouse_presses[0]:
            if self.rect.collidepoint(pygame.mouse.get_pos()):
                self.Down.give(True)
                self.MouseOn.give(False)
            else:
                self.Down.give(False)
                self.MouseOn.give(False)
        else:
            if self.rect.collidepoint(pygame.mouse.get_pos()):
                self.Down.give(False)
                self.MouseOn.give(True)
            else:
                self.Down.give(False)
                self.MouseOn.give(False)
        

class TextButton(BaseButton):
    
    pass
