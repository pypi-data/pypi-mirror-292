import pygame
import sys,os
import pkg_resources
from ..eventlist.thinglist import ThingList

class Window:
    def __init__(self):
        pygame.init()
        os.environ["SDL_IME_SHOW_UI"] = "1"
        infoObject = pygame.display.Info()
        self.max_width = infoObject.current_w
        self.max_height = infoObject.current_h
        #self.max_width, self.max_height = pygame.display.get_surface().get_size()
        
        self.width = int(self.max_width*0.618)
        self.height = int(self.max_height*0.618)
        self.MaxFps = 60
        
        self.check = ThingList()
        self.event = ThingList()
        
        self.BlackGroungColor=(255,255,255)
        
        @self.event.connect(name='QuitCheckThing')
        def Quit(event):
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
        @self.check.connect(name='UpDateWindows')
        def Update(window):
            pygame.display.flip()
            window.fill(self.BlackGroungColor)
    def show(self):
        self.screen = pygame.display.set_mode((self.width,self.height))
        self.set_ico()
        self.clock = pygame.time.Clock()
        while True:
            self.clock.tick(self.MaxFps)
            for event in pygame.event.get():
                self.event.did(event)
            self.check.did(self.screen)
            
    def set_ico(self,path=None):
        if path==None:
            path = pkg_resources.resource_filename('pgbook', 'static/pic/load.ico')
        img = pygame.image.load(path)
        pygame.display.set_icon(img)
        
    def set_rect(self,width,height):
        if 0<width<=1 and 0<height<=1:
            self.width = int(self.max_width*width)
            self.height = int(self.max_height*height)
        elif width>1 and height>1:
            self.width = int(width)
            self.height = int(height)
        
    def set_name(self,name):
        pygame.display.set_caption(name)