class Thing:
    '''
    用于处理单个事件对象
    '''
    def __init__(self):
        pass
        self.func=None
        self.name=None
        
        self.lock=False
        
    def set_name(self,name):
        '''
        设置事件名称，用于检索事件
        '''
        self.name = name
        
    def lock(self,l=None):
        '''
        用于事件上锁(上锁后不执行，无报错)
        l==None:改变锁的方向
        bool(l)==True:上锁
        bool(l)==False:开锁
        '''
        if l == None:
            self.lock = not self.lock
        else:
            self.lock = bool(l)
        
    def connect(self,usfunc=None):
        '''
        用于设置事件内容
        usfunc==None:返回修饰器，修饰保存函数，返回空函数
        usfunc==函数:保存函数
        '''
        if usfunc==None:
            def did(func):
                self.func = func
                def rbook():
                    pass
                return rbook
            return did
        else:
            self.func = usfunc

    def did(self,*args, **kwargs):
        '''
        执行本函数（上锁后不执行）
        '''
        if self.lock:
            return 
        self.func(*args, **kwargs)
            
    def did_n(self,name,*args, **kwargs):
        '''
        检索函数，名称符合执行（上锁后不执行）
        '''
        if self.lock:
            return 
        if name == self.name:
            self.did(*args, **kwargs)
              
class ThingList:
    '''
    用于处理事件列表（可叠多层）
    '''
    def __init__(self):
        self.funclist=[]
        self.name = None
        
        self.lock=False
        
    def set_name(self,name):
        '''
        设置名称，用于检索事件
        '''
        self.name = name 
        
    def lock(self,l=None):
        '''
        用于事件上锁(上锁后不执行，无报错)
        l==None:改变锁的方向
        bool(l)==True:上锁
        bool(l)==False:开锁
        '''
        if l == None:
            self.lock = not self.lock
        else:
            self.lock = bool(l)
    
    def connect(self,func=None,name=None):
        '''
        用于增加事件
        func==事件，事件列表:添加到列表
        else:如func为None,返回修饰器，否则保存函数
        '''
        if isinstance(func, Thing) or isinstance(func, ThingList):
            self.funclist.append(func)
        else:
            t=Thing()
            t.set_name(name)
            self.funclist.append(t)
            return t.connect(func)
    
    def did(self,*args, **kwargs):
        '''
        执行（上锁后不执行）
        '''
        if self.lock:
            return 
        for i in self.funclist:
            i.did(*args, **kwargs)
        
    def did_n(self,name,*args, **kwargs):
        '''
        在列表中检索函数，名称符合执行（上锁后不执行）
        '''
        if self.lock:
            return 
        for i in self.funclist:
            i.did_n(name,*args, **kwargs)
    
    def lock_n(self,name,l=None):
        '''
        对指定名称的子对象上锁
        '''
        for i in self.funclist:
            if name == i.name:
                i.lock(l)
                
    def find_n(self,name):
        '''
        返回指定名称的子对象
        '''
        for i in self.funclist:
            if name == i.name:
                return i
    
