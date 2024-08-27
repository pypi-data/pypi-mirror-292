## Pygame Function Book

pygame be used easier

#### 1.下载 download

```shell
pip install pgbook
```

#### 2.最简单的程序 easiest program

1.esay

```python
from pgbook.screen.window import Window


mywindow = Window()
#窗口对象
mywindow.show()
#展示


'''
这段代码生成了一个空白窗口
'''
```

2.window

```python
from pgbook.screen.window import Window


mywindow = Window()
#窗口对象
mywindow.set_name('Hello World')
#set_name:用于修改
mywindow.show()
#展示


'''
这段代码生成了一个窗口，大小为屏幕大小的0.618倍
'''
```



