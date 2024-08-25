import pygame

__all__ = ['mouse']

class Mouse():
    def __init__(self):
        self.x = 0
        self.y = 0
        self.buttons_num = 3 # 默认按键数为3：0-左键，1-中键，2-右键；可以设置为5，额外两个功能键：3和4
    def left_click(self):
        btns = pygame.mouse.get_pressed(num_buttons=self.buttons_num)
        return btns[0]
    def right_click(self):
        btns = pygame.mouse.get_pressed(num_buttons=self.buttons_num)
        return btns[2]
    def middle_click(self):
        btns = pygame.mouse.get_pressed(num_buttons=self.buttons_num)
        return btns[1]

mouse = Mouse()