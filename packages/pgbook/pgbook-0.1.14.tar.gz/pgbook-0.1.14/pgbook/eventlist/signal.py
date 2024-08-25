class Signal:
    def __init__(self,name=None):
        self.name = str(name)
        self.signal = False
        self.first = False
        self.end = False
        
    def give(self,signal):
        if signal:
            if not self.signal:
                self.first = True
                self.end = False
            self.signal = True
        else:
            if self.signal:
                self.end = True
                self.first = False
            self.signal = False
            
    def is_first(self):
        if self.first:
            self.first = False
            return True
        else:
            return False
    
    def is_true(self):
        return self.signal
    
    def is_end(self):
        if self.end:
            self.end = False
            return True
        else:
            return False
            