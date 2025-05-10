import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import numpy as np
from OpenGL.GLUT import GLUT_BITMAP_HELVETICA_18    # Import GLUT for text rendering
from beeGame_model import Bee
import math
# import time 


# button class 
class Button:
    def __init__(self, label, button_width = 100, button_height = 30, bottomLeft_x = 0, 
                 bottomLeft_y = 0, screen_width = 500, screen_height = 500):
        # placement and text properties
        self.label = label 
        self.button_width = button_width
        self.button_height = button_height
        self.bottomLeft_x = bottomLeft_x 
        self.bottomLeft_y = bottomLeft_y 
        self.screen_width = screen_width
        self.screen_height = screen_height

        # function properties 
        self.pressing = False
        self.pressed = False

        # color properties
        self.initial_color = (0.2, 0.2, 0.2)
        self.pressing_color = (0.0, 1.0, 0.0)
        self.pressed_color = (0.0, 0.5, 0.0)

    # returns if the button has been clicked 
    def is_clicked(self, mouse_x, mouse_y):
        mouse_y = - (mouse_y - self.screen_height)
        # checks if the mouse clicked within the boundaries of the button 
        return (self.bottomLeft_x <= mouse_x <= self.bottomLeft_x + self.button_width) and \
            (self.bottomLeft_y <= mouse_y <= self.bottomLeft_y + self.button_height)
    
    # places the text within the button's space 
    def draw_text(self):
        text = self.label 
        y = self.bottomLeft_y + (self.button_height // 2.5) 
        x = self.bottomLeft_x + (self.button_width - len(text) * 9) // 2  # Center the text

        color = (1.0, 1.0, 1.0) # white 
        glColor3f(*color)

        glRasterPos2f(x, y)
        for char in text:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))

    
    # draws the button as a rectangle 
    def draw_button(self):
        color = self.initial_color
        if self.pressed:
            color = self.pressed_color
        elif self.pressing:
            color = self.pressing_color
        glColor3f(*color)
        glBegin(GL_QUADS)
        glVertex2f(self.bottomLeft_x, self.bottomLeft_y)
        glVertex2f(self.bottomLeft_x + self.button_width, self.bottomLeft_y)
        glVertex2f(self.bottomLeft_x + self.button_width, self.bottomLeft_y + self.button_height)
        glVertex2f(self.bottomLeft_x, self.bottomLeft_y + self.button_height)
        glEnd()
        self.draw_text()


# main GUI layout
class UI:
    def __init__(self, win_width = 500, win_height = 500):
        # window dimensions 
        self.win_width = win_width
        self.win_height = win_height

        # lobby label is the default 
        self.room_text = "Lobby"
        self.room_text_font = GLUT_BITMAP_HELVETICA_18

        # buttons at the bottom (start game and help)
        self.num_of_bottom_buttons = 2
        self.bottom_button_width = 100 
        self.bottom_button_height = 40 
        self.bottom_gap_width = (self.win_width - self.num_of_bottom_buttons * self.bottom_button_width) // (self.num_of_bottom_buttons + 1)

        # start game button 
        self.start_game_button = Button(label="Start Game", button_width=self.bottom_button_width, 
                                        button_height=self.bottom_button_height,

                                        bottomLeft_x=self.bottom_gap_width,                             # change this to position it's x position 
                                        bottomLeft_y=self.win_height-75, 

                                        screen_height=self.win_height, 
                                        screen_width=self.win_width)  

        # help button
        self.help_button = Button(label="Help", button_width=self.bottom_button_width, 
                                  button_height=self.bottom_button_height,

                                  bottomLeft_x=self.bottom_gap_width * 2 + self.bottom_button_width,    # change this to position it's x position 
                                  bottomLeft_y=self.win_height-75, 

                                  screen_height=self.win_height, 
                                  screen_width=self.win_width)  # Position the button

    # draw text on the screen at position (x, y)
    def draw_text(self, text, x, y, font=GLUT_BITMAP_HELVETICA_18):
        glColor3f(1.0, 1.0, 1.0)  # White color for the text
        glRasterPos2f(x, y)
        for char in text:
            glutBitmapCharacter(font, ord(char))

    # draw the gui elements (buttons) on the lobby screen
    def draw_lobby_gui(self):
        # draw the top text (lobby)
        self.draw_text(self.room_text, self.win_width // 2 - 30, self.win_height - 30)

        # draw the buttons (start game and help)
        self.start_game_button.draw_text()
        self.start_game_button.draw_button()
        
        self.help_button.draw_text()
        self.help_button.draw_button()
        


    # check if a button was clicked. returns name of button or None 
    def check_if_button_clicked(self, mouse_x, mouse_y):
        # print(f"Mouse Position: x={mouse_x}, y={mouse_y}")  # Debugging the mouse position
        button_clicked = None 

        if self.start_game_button.is_clicked(mouse_x, mouse_y):
            button_clicked = "start"
            print("start button clicked...")
        elif self.help_button.is_clicked(mouse_x, mouse_y):
            button_clicked = "help"
            print("help button clicked...")

        return button_clicked
        