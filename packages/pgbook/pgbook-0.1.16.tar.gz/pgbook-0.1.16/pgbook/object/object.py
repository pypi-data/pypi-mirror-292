class Position:
    def __init__(self,x=0,y=0,max_x=100,max_y=100,
                 use_center=True,use_percent_h=True,
                 use_percent_t=False,percent=None):
        self.max_x=max_x
        self.max_y=max_y
        if use_percent_h:
            self.percent=100
        elif use_percent_t:
            self.percent=1000
        else:
            self.percent=percent
        
        self.use_center=use_center
        self.set_pos(x,y)
        
    def true_pos(self):
        if self.percent!=None:
            tx=self.x*self.max_x/self.percent
            ty=self.y*self.max_y/self.percent
            if self.use_center:
                tx=tx+self.max_x*0.5
                ty=ty+self.max_y*0.5
        else:
            tx=self.x
            ty=self.y
            if self.use_center:
                tx=tx+self.max_x*0.5
                ty=ty+self.max_y*0.5
        return Position(int(tx),int(ty),self.max_x,self.max_y,use_center=False,use_percent_h=False)
    
    def set_pos(self,x,y):
        if self.percent!=None:
            if self.use_center:
                tx=((-self.percent/2)<=x<=(self.percent/2))
                ty=((-self.percent/2)<=y<=(self.percent/2))
                if tx and ty:
                    self.x=x
                    self.y=y
                else:
                    raise Exception("位置数据超出限定范围")
            else:
                tx=(0<=x<=(self.percent))
                ty=(0<=y<=(self.percent))
                if tx and ty:
                    self.x=x
                    self.y=y
                else:
                    raise Exception("位置数据超出限定范围")
        else:
            if self.use_center:
                tx=((-self.max_x/2)<=x<=(self.max_x/2))
                ty=((-self.max_y/2)<=y<=(self.max_y/2))
                if tx and ty:
                    self.x=x
                    self.y=y
                else:
                    raise Exception("位置数据超出限定范围")
            else:
                tx=(0<=x<=(self.max_x))
                ty=(0<=y<=(self.max_y))
                if tx and ty:
                    self.x=x
                    self.y=y
                else:
                    raise Exception("位置数据超出限定范围")
    
    def __str__(self):
        return '('+str(self.x)+','+str(self.y)+')'
    
    def show_pos(self):
        print(self)
        
    def out(self):
        try:
            self.set_pos(self.x,self.y)
        except Exception:
            return True
        return False
    

        
        
        

