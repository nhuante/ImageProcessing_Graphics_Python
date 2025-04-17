import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GLUT import GLUT_BITMAP_HELVETICA_18    # Import GLUT for text rendering
import numpy as np

# Define a button class 
class Button:
    def __init__(self, label = "", button_width = 100, button_height = 30, bottomLeft_x = 0, bottomLeft_y = 0):
        self.label = label
        self.button_width = button_width
        self.button_height = button_height

        # button position in the window: top-left corner (x, y)
        self.bottomLeft_x = bottomLeft_x
        self.bottomLeft_y = bottomLeft_y

        self.pressing = False                        # button is current being pressed
        self.pressed = False                         # button was pressed before
        self.initial_color = (0.2, 0.2, 0.2)         # button initial color
        self.pressing_color = (0.0, 1.0, 0.0)        # button color when being pressed
        self.pressed_color = (0.0, 0.5, 0.0)         # button color when pressed before
    

    # check if the button is clicked by the mouse
    def is_clicked(self, mouse_x, mouse_y):         
        is_in_x_range = self.bottomLeft_x <= mouse_x <= self.bottomLeft_x + self.button_width
        is_in_y_range = self.bottomLeft_y <= mouse_y <= self.bottomLeft_y + self.button_height
        return is_in_x_range and is_in_y_range
    
    # draw button label
    def draw_text(self):
        text = self.label
        y = self.bottomLeft_y + 10
        if text == "Gray":
            x = self.bottomLeft_x + 10        
        elif text == "Inv":
            x = self.bottomLeft_x + 20
        elif text == "Brit":
            x = self.bottomLeft_x + 15
        elif "Shift" in text:
            x = self.bottomLeft_x + 10 
        elif text == "Edge":
            x = self.bottomLeft_x + 10
        elif text == "Blur":
            x = self.bottomLeft_x + 12
        elif "Revert" in text:
            x = self.bottomLeft_x + 8
        elif "Filter Type: " in text:
            x = self.bottomLeft_x + 2
        
        color = (1.0, 1.0, 1.0) # white text
        glColor3f(*color)
        glRasterPos2f(x, y)
        for char in text:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))

    # draw button
    def draw_button(self):
        color = self.initial_color
        if self.pressed == True and "Revert" not in self.label:
            color = self.pressed_color
        
        if self.pressing == True:
            color = self.pressing_color

        if "Filter Type: " in self.label:           
            color = (0.0, 0.0, 0.0)                 # status button color is the same as the backgroun, black
        
        glColor3f(*color)
        glBegin(GL_QUADS)
        glVertex2f(self.bottomLeft_x, self.bottomLeft_y)
        glVertex2f(self.bottomLeft_x + self.button_width, self.bottomLeft_y)
        glVertex2f(self.bottomLeft_x + self.button_width, self.bottomLeft_y + self.button_height)
        glVertex2f(self.bottomLeft_x, self.bottomLeft_y + self.button_height)
        glEnd()

        # draw button text
        self.draw_text()

# Define a GUI layout on top of the pygame display window
class UI:
    def __init__(self, win_width=500, win_height=500):
        self.win_width = win_width
        self.win_height = win_height

        # Top: initialize 2 buttons
        self.top_button_height = 30
        self.topMiddle_button_width = 200                   # status button showing the current filter type
        self.topRight_button_width = 150                    # revert to original button
        self.revertButton = self.initRevertButton()
        self.statusButton = self.initStatusButton()

        # Bottom: initialize 6 buttons evenly distribiuted on the bottom
        num_bottom_buttons = 6
        self.bottom_button_width = 60
        self.bottom_button_height = 30
        self.bottom_gap_height = 10 # distance from window bottom to button
        self.bottom_gap_width = self.calculateGapWidth(num_bottom_buttons=num_bottom_buttons)
        
        # create a button for gray filter
        bottomLeft_x = self.bottom_gap_width
        self.grayFilterButton = self.initGrayFilterButton(bottomLeft_x=bottomLeft_x)

        # create a button for invert filter
        bottomLeft_x = self.grayFilterButton.bottomLeft_x + self.bottom_button_width + self.bottom_gap_width
        self.invertFilterButton = self.initInvertFilterButton(bottomLeft_x=bottomLeft_x)

        # create a button for brighten filter
        bottomLeft_x = self.invertFilterButton.bottomLeft_x + self.bottom_button_width + self.bottom_gap_width
        self.brightenFilterButton = self.initBrightenFilterButton(bottomLeft_x=bottomLeft_x)

        # create a button for shift filter (and identity filter)
        bottomLeft_x = self.brightenFilterButton.bottomLeft_x + self.bottom_button_width + self.bottom_gap_width
        self.shiftFilterButton = self.initShiftFilterButton(bottomLeft_x=bottomLeft_x)

        # create a button for edge detector
        bottomLeft_x = self.shiftFilterButton.bottomLeft_x + self.bottom_button_width + self.bottom_gap_width
        self.edgeDetectionButton = self.initEdgeDetectionButton(bottomLeft_x=bottomLeft_x)

        # create a button for image blur
        bottomLeft_x = self.edgeDetectionButton.bottomLeft_x + self.bottom_button_width + self.bottom_gap_width
        self.blurButton = self.initBlurButton(bottomLeft_x=bottomLeft_x)

    def initRevertButton(self):
        bottomLeft_x = self.win_width - self.topRight_button_width - 10
        bottomLeft_y = self.win_height - self.top_button_height - 10
        button = Button(label="Revert to Original", button_width=self.topRight_button_width,
                                                        button_height=self.top_button_height,
                                                        bottomLeft_x=bottomLeft_x,
                                                        bottomLeft_y=bottomLeft_y)
        return button
    
    def initStatusButton(self):
        bottomLeft_x = 20
        bottomLeft_y = self.win_height - self.top_button_height - 10
        button = Button(label="Filter Type: ", button_width=self.topMiddle_button_width,
                                                        button_height=self.top_button_height,
                                                        bottomLeft_x=bottomLeft_x,
                                                        bottomLeft_y=bottomLeft_y)
        return button
    
    def calculateGapWidth(self, num_bottom_buttons):
        gap_width = (self.win_width - self.bottom_button_width * num_bottom_buttons) // (num_bottom_buttons + 1)
        return gap_width

    def initGrayFilterButton(self, bottomLeft_x):
        button = Button(label="Gray", button_width=self.bottom_button_width, 
                                            button_height=self.bottom_button_height,
                                            bottomLeft_x=bottomLeft_x, 
                                            bottomLeft_y=self.bottom_gap_height)
        return button
    
    def initInvertFilterButton(self, bottomLeft_x):
        button = Button(label="Inv", button_width=self.bottom_button_width, 
                                            button_height=self.bottom_button_height,
                                            bottomLeft_x=bottomLeft_x, 
                                            bottomLeft_y=self.bottom_gap_height)
        return button
    
    def initBrightenFilterButton(self, bottomLeft_x):
        button = Button(label="Brit", button_width=self.bottom_button_width, 
                                            button_height=self.bottom_button_height,
                                            bottomLeft_x=bottomLeft_x, 
                                            bottomLeft_y=self.bottom_gap_height)
        return button
    
    def initShiftFilterButton(self, bottomLeft_x):
        button = Button(label="Shift", button_width=self.bottom_button_width, 
                                            button_height=self.bottom_button_height,
                                            bottomLeft_x=bottomLeft_x, 
                                            bottomLeft_y=self.bottom_gap_height)
        return button
    
    def initEdgeDetectionButton(self, bottomLeft_x):
        button = Button(label="Edge", button_width=self.bottom_button_width, 
                                            button_height=self.bottom_button_height,
                                            bottomLeft_x=bottomLeft_x, 
                                            bottomLeft_y=self.bottom_gap_height)
        return button
    
    def initBlurButton(self, bottomLeft_x):
        button = Button(label="Blur", button_width=self.bottom_button_width, 
                                            button_height=self.bottom_button_height,
                                            bottomLeft_x=bottomLeft_x, 
                                            bottomLeft_y=self.bottom_gap_height)
        return button