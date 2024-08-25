#__all__=['eventlist','screen','test_load']
from .eventlist import *
from .screen import *

import pygame

pygame.init()
print('pgbook open!')

def test_load():
    print('pybook was loaded')

