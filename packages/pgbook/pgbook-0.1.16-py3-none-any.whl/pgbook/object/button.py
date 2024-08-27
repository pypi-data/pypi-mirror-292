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
        
        #color
        self.DownColor=(200,200,200)
        self.MouseOnColor=(156,156,156)
        self.NoColor=(128,128,128)
    def connect_page(self,page):
        self.pos=Position(0,0,page.screen.width,page.screen.height)
        page.drawlist.connect(self.drawlist)
        page.eventlist.connect(self.eventlist)
        self.drawlist.connect(self.draw,'DrawButton')
        self.drawlist.connect(self.check,'CheckButton')
        
    def draw(self,screen):
        if self.Down.is_true():
            color=self.DownColor
        elif self.MouseOn.is_true():
            color=self.MouseOnColor
        else:
            color=self.NoColor
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
    def __init__(self):
        super().__init__()
        self.text=BaseText()
        self.outline=3
        
    def connect_page(self, page):
        super().connect_page(page)
        self.text.connect_page(page)
        self.text.pos=self.pos
        
    def draw(self,screen):
        self.rect.height=self.text.textbook.get_rect().height+2*self.outline
        self.rect.width=self.text.textbook.get_rect().width+2*self.outline
        super().draw(screen)
