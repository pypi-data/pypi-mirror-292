from ..eventlist.thinglist import ThingList as ThingList

class Page:
    def __init__(self):
        self.drawlist=ThingList()
        self.eventlist=ThingList()
        self.show=False
        self.screen = None
        
    def connect(self,screen=None):
        if screen!=None:
            self.screen=screen
            screen.check.connect(self.drawlist)
            screen.event.connect(self.eventlist)
        self.show=True
        
    def hide(self):
        self.show=False
        
    