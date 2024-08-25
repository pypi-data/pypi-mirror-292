import pygame
from hellopy.gameobject.rectangle import Rectangle
from hellopy.gameobject.gameobject import GameObject
from hellopy.collision import CollisionComponent
from hellopy.window import window
from hellopy.resource import rss

cache_images = {}

# 绘制图片
def image(x=100, y=200, width=100,height=100,src="./hellopy/src/images/Logo.png"):
    img = pygame.image.load(rss.get(src))
    img = pygame.transform.scale(img,(width,height))
    window.screen.blit(img,(x-width/2, y-height/2))

# 精灵类
class Sprite(GameObject, pygame.sprite.Sprite, CollisionComponent):
    def __init__(self,x=100, y=200, width=None,height=None,src="./hellopy/src/images/Logo.png"):
        self.ox = x
        self.oy = y
        self.img = pygame.image.load(rss.get(src))
        self._w = width or self.img.get_width()
        self._h = height or self.img.get_height()
        self.img = pygame.transform.scale(self.img,(self.w,self.h))
        self._x = x
        self._y = y
        self._src = src
        self.mask =  pygame.mask.from_surface(self.img.convert_alpha())
        self.min_collision = 5
        self.is_moving = False
        relPs = list(self.mask.outline(self.min_collision))
        points = [(p[0]+self.x-self.w/2,p[1]+self.y-self.h/2) for p in relPs]
        
        self.points = points
        
        
        
        super().__init__(self.get_rect())
        self.color = "blue"
        self.scale = 1
        self.line_width = 1
        self.angle = 0
        self.show_rect= False
        self.show_outline = False

    @property
    def x(self):
        return self._x
    @x.setter
    def x(self,x):
        if self._x != x:
            self._x = x
            self.is_moving = True
    @property
    def y(self):
        return self._y
    @y.setter
    def y(self,y):
        if self._y != y:
            self._y = y
            self.is_moving = True
    @property
    def w(self):
        return self._w
    @w.setter
    def w(self,w):
        if self._w != w:
            self.is_moving = True
            self._w = w
            pygame.transform.scale(self.img,(self._w,self._h))
    @property
    def h(self):
        return self._h
    @h.setter
    def h(self,h):
        if self._h != h:
            self.is_moving = True
            self._h = h
            pygame.transform.scale(self.img,(self._w,self._h))
    @property
    def src(self):
        return self._src
    @src.setter
    def src(self, src):
        if src not in cache_images:
            try:
                file_name = rss.get(src)
                if file_name[-4:] == ".gif":
                    print("Can't use GIF resource.")
                    pass
                else:
                    img = pygame.image.load(file_name)
            except pygame.image.codecs.ImageDecodeException:
                import os, sys
                print("Couldn't load image, please delete the picture and retry.")
                print("Error picture: {}\\{}".format(os.getcwd(), rss.get(src)))
                sys.exit()

            cache_images[src] = img
        self._src = src
        self.img = cache_images[src]
        self.img = pygame.transform.scale(self.img,(self.w,self.h))
        
    def get_rect(self):
        x_list = []
        y_list = []
        for dot in self.points:
            x_list.append(dot[0])
            y_list.append(dot[1])
        return (min(x_list),min(y_list),max(x_list)-min(x_list),max(y_list)-min(y_list))
    def update_points(self):
        self.mask =  pygame.mask.from_surface(self.img.convert_alpha())
        relPs = list(self.mask.outline(self.min_collision))
        points = [(p[0]+self.x-self.mask.get_size()[0]/2,p[1]+self.y-self.mask.get_size()[1]/2) for p in relPs]
        self.points = points
    def draw(self):
        if self.is_moving:
            self.update_points()
        window.screen.blit(self.img,(self.x-self.img.get_width()/2,self.y-self.img.get_height()/2))
        if self.show_rect or self.show_outline:
            pygame.draw.polygon(window.screen,self.color,self.points,self.line_width)
    def rotate(self, angle=0, center=None):
        self.angle = (self.angle + angle) % 360
        self.r_center = (self.x,self.y)
        if center != None:
            self.r_center = center    
        self.display_rect = self.get_rect()
        self.img = pygame.image.load(rss.get(self.src))
        self.img = pygame.transform.scale(self.img,(self.w,self.h))
        self.img = pygame.transform.rotate(self.img, -self.angle)
        if angle != 0:
            self.is_moving = True
        return self.points
    def rotate_to(self, angle=0, center=None):
        a = (angle - self.angle)%360
        self.angle = (angle) % 360
        self.r_center = (self.x,self.y)
        if center != None:
            self.r_center = center    
        self.display_rect = self.get_rect()
        self.img = pygame.image.load(rss.get(self.src))
        self.img = pygame.transform.scale(self.img,(self.w,self.h))
        self.img = pygame.transform.rotate(self.img, -self.angle)
        if a != 0:
            self.is_moving = True
        return self.points
    def set_scale(self,scale):
        if self.scale == scale:
            return
        sc = scale/self.scale
        # nps = []
        # for p in self.points:
        #     rc = (self.x,self.y)
        #     nps.append((rc[0]+(p[0]-rc[0])*sc,rc[1]+(p[1]-rc[1])*sc))
        # self.points = nps.copy()
        self.w = self.w * sc
        self.h = self.h * sc
        self.scale = scale
        self.img = pygame.image.load(self.src)
        self.img = pygame.transform.scale(self.img,(self.w,self.h))
        self.img = pygame.transform.rotate(self.img, self.angle)
        self.is_moving = True