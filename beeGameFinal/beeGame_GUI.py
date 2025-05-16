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
                 bottomLeft_y = 0, screen_width = 500, screen_height = 500, initial_color=(0.2, 0.2, 0.2)):
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
        self.initial_color = initial_color
        self.pressing_color = (0.0, 1.0, 0.0)
        self.pressed_color = (0.0, 0.5, 0.0)

    # returns if the button has been clicked 
    def is_clicked(self, mouse_x, mouse_y):
        mouse_y = - (mouse_y - self.screen_height)
        # checks if the mouse clicked within the boundaries of the button 
        return (self.bottomLeft_x <= mouse_x <= self.bottomLeft_x + self.button_width) and \
            (self.bottomLeft_y <= mouse_y <= self.bottomLeft_y + self.button_height)
    
    # places the text within the button's space 
    def draw_text(self, font=GLUT_BITMAP_HELVETICA_18, color=(1.0, 1.0, 1.0)):
        text = self.label 
        y = self.bottomLeft_y + (self.button_height // 2.5) 
        x = self.bottomLeft_x + (self.button_width - len(text) * 9) // 2  # Center the text

        # color = (1.0, 1.0, 1.0) # white 
        glColor3f(*color)

        glRasterPos2f(x, y)
        for char in text:
            glutBitmapCharacter(font, ord(char))

    
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

        # text elements
        self.lobby_text = "Lobby"
        self.level_text = "Level 1"
        self.help_menu_title = "Lost?"
        self.room_text_font = GLUT_BITMAP_HELVETICA_18

        # load in bee mode images 
        self.mode_textures = {} 
        for mode, file_name in [    ("normal",   "./resources/imgs/normal_bee_mode.png"), 
                                    ("angry",    "./resources/imgs/angry_bee_mode.png"), 
                                    ("charging",    "./resources/imgs/charging_bee_mode.png"), 
                                    ("hurt",    "./resources/imgs/hurt_bee.png"), 
                                    ("dead",    "./resources/imgs/dead_bee.png"), 
                                    ("won",    "./resources/imgs/winner_bee_2.png")  ]: 
            surf = pygame.image.load(file_name).convert_alpha()
            icon_h = 42
            icon_w = int(icon_h * surf.get_width() / surf.get_height())

            surf = pygame.transform.smoothscale(surf, (icon_w, icon_h))
            # w, h = surf.get_size() 
            tex_data = pygame.image.tostring(surf, "RGBA", True)
            tex_id = glGenTextures(1) 
            glBindTexture(GL_TEXTURE_2D, tex_id)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, icon_w, icon_h, 0, GL_RGBA, GL_UNSIGNED_BYTE, tex_data)
            self.mode_textures[mode] = (tex_id, icon_w, icon_h)
        glBindTexture(GL_TEXTURE_2D, 0)


        # buttons at the bottom (start game and help)
        self.num_of_bottom_buttons_lobby = 3
        self.num_of_bottom_buttons_level = 2
        self.bottom_button_width = 100 
        self.bottom_button_height = 40 
        self.bottom_gap_width_lobby = (self.win_width - self.num_of_bottom_buttons_lobby * self.bottom_button_width) // (self.num_of_bottom_buttons_lobby + 1)
        self.bottom_gap_width_level = (self.win_width - self.num_of_bottom_buttons_level * self.bottom_button_width) // (self.num_of_bottom_buttons_level + 1)

        # start game button - lobby
        self.start_game_button = Button(label="Start Game", button_width=self.bottom_button_width, 
                                        button_height=self.bottom_button_height,

                                        bottomLeft_x=self.bottom_gap_width_lobby,                             # change this to position it's x position 
                                        bottomLeft_y=self.win_height-110, 

                                        screen_height=self.win_height, 
                                        screen_width=self.win_width, 
                                        
                                        initial_color=(0, 91/255, 27/255))  
        
        # change difficulty button - lobby
        self.difficulty_button = Button(label="Normal", button_width=self.bottom_button_width, 
                                        button_height=self.bottom_button_height,

                                        bottomLeft_x=self.bottom_gap_width_lobby * 2 + self.bottom_button_width,                             # change this to position it's x position 
                                        bottomLeft_y=self.win_height-110, 

                                        screen_height=self.win_height, 
                                        screen_width=self.win_width, 
                                        
                                        initial_color=(0.82, 0.671, 0))  

        # help button - lobby
        self.help_button = Button(label="Help", button_width=self.bottom_button_width, 
                                  button_height=self.bottom_button_height,

                                  bottomLeft_x=self.bottom_gap_width_lobby * 3 + self.bottom_button_width * 2,    # change this to position it's x position 
                                  bottomLeft_y=self.win_height-110, 

                                  screen_height=self.win_height, 
                                  screen_width=self.win_width, 
                                  
                                  initial_color=(70/255, 139/255, 243/255))  # Position the button
        
        # help button - in-game 
        self.help_game_button = Button(label="Help", button_width=self.bottom_button_width, 
                                       button_height=self.bottom_button_height, 
                                       
                                       bottomLeft_x=self.bottom_gap_width_level * 2 + self.bottom_button_width * 1.5, 
                                       bottomLeft_y=50, 
                                       
                                       screen_height=self.win_height, 
                                       screen_width=self.win_width, 
                                       
                                       initial_color=(70/255, 139/255, 243/255))
        
        # backToLobby button - in-game 
        self.toLobby_game_button = Button(label="Exit to Lobby", button_width=1.5*self.bottom_button_width, 
                                       button_height=self.bottom_button_height, 
                                       
                                       bottomLeft_x=self.bottom_gap_width_level , 
                                       bottomLeft_y=50, 
                                       
                                       screen_height=self.win_height, 
                                       screen_width=self.win_width, 
                                       
                                       initial_color=(158/255, 28/255, 28/255))
        
        # exit help menu button
        self.exitHelp_button = Button(label="X", button_width=0.5*self.bottom_button_width, 
                                      button_height=self.bottom_button_height, 
                                      
                                      bottomLeft_x=self.win_width-10-0.5*self.bottom_button_width, 
                                      bottomLeft_y=self.win_height-10-self.bottom_button_height, 

                                      screen_height=self.win_height, 
                                      screen_width=self.win_width, 

                                      initial_color=(205/255, 0, 0))

    # draw text on the screen at position (x, y)
    def draw_text(self, text, x, y, font=GLUT_BITMAP_HELVETICA_18, color=(1.0, 1.0, 1.0)):
        glColor3f(*color)  # White color for the text by default
        glRasterPos2f(x, y)
        for char in text:
            glutBitmapCharacter(font, ord(char))

    # draws  a rectangle 
    def draw_rectangle(self, bottomLeft_x, bottomLeft_y, topRight_x, topRight_y, color=(0,0,0)):
        glColor3f(*color)
        glBegin(GL_QUADS)
        glVertex2f(bottomLeft_x, bottomLeft_y)
        glVertex2f(topRight_x, bottomLeft_y)
        glVertex2f(topRight_x, topRight_y)
        glVertex2f(bottomLeft_x, topRight_y)
        glEnd()

    # draw the gui elements (buttons) on the lobby screen
    def draw_lobby_gui(self, bee):

        # draw the top text (lobby)
        self.draw_text(self.lobby_text, self.win_width // 2 - 30, self.win_height - 30)

        # draw the appropriate bee mode image to the right of the lobby text 
        if bee.angry_bee_mode: mode = "angry"
        elif bee.is_recharging: mode = "charging"
        else: mode = "normal"

        tex_id, iw, ih = self.mode_textures[mode]
        icon_x = self.win_width // 2 + 90
        icon_y = self.win_height - 45

        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, tex_id)
        glColor3f(1,1,1)
        glBegin(GL_QUADS)
        # lower-left
        glTexCoord2f(0,0); glVertex2f(icon_x,      icon_y)
        # lower-right
        glTexCoord2f(1,0); glVertex2f(icon_x+iw,   icon_y)
        # upper-right
        glTexCoord2f(1,1); glVertex2f(icon_x+iw,   icon_y+ih)
        # upper-left
        glTexCoord2f(0,1); glVertex2f(icon_x,      icon_y+ih)
        glEnd()
        glBindTexture(GL_TEXTURE_2D, 0)
        glDisable(GL_TEXTURE_2D)

        # draw the current countdown number next to the image to the right of the bee mode image 
        if bee.angry_bee_mode or bee.is_recharging: countdown = str(bee.current_countdown_num)
        else: countdown = ""

        self.draw_text(countdown, self.win_width // 2 + 150, self.win_height - 30)

        # draw the buttons (start game and help)
        self.start_game_button.draw_text()
        self.start_game_button.draw_button()
        
        self.help_button.draw_text()
        self.help_button.draw_button()

        self.difficulty_button.draw_text()
        self.difficulty_button.draw_button()

        # draw header rectangle 
        self.draw_rectangle(bottomLeft_x=-10, bottomLeft_y= self.win_height-55, 
                            topRight_x=810, topRight_y=810, 
                            color=(64/255, 64/255, 64/255))

    # draw the gui elements in the lobby (when paused)
    def draw_lobby_pause_gui(self):
        # draw the top text (level 1)
        self.draw_text("Paused", self.win_width // 2 - 30, self.win_height // 2)

        # draw banner rectangle 
        self.draw_rectangle(bottomLeft_x=-10, bottomLeft_y=self.win_height // 2 - 20, 
                            topRight_x=810, topRight_y=self.win_height // 2 + 30, 
                            color=(0, 153/255, 0))


    # draw the gui elements in the level 
    def draw_level_gui(self, score, level, health, timer_left_ms, bee:Bee):
        distance_from_top = self.win_height - 30
        # draw the top text (level 1)
        self.draw_text(f"Level:{level}", self.win_width - 300, distance_from_top)

        # draw other in-game stats in the header
        self.draw_text(f"Score: {score}", 50, distance_from_top)  # score
                             
        health_color = tuple() 
        if 25 < health <= 50: health_color = (220/255, 228/255, 3/255)
        elif health <= 25: health_color = (204/255, 0, 0)
        else: health_color = (1, 1, 1)
        self.draw_text(f"Health: {health}%", 230, distance_from_top, color=health_color)                  # health 

        

        # draw the appropriate bee mode image at the center of the header
        if bee.angry_bee_mode: mode = "angry"
        elif bee.is_recharging: mode = "charging"
        elif bee.health_percentage < 50: mode = "hurt"
        else: mode = "normal"

        tex_id, iw, ih = self.mode_textures[mode]
        icon_x = self.win_width // 2 -15
        icon_y = self.win_height - 45

        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, tex_id)
        glColor3f(1,1,1)
        glBegin(GL_QUADS)
        # lower-left
        glTexCoord2f(0,0); glVertex2f(icon_x,      icon_y)
        # lower-right
        glTexCoord2f(1,0); glVertex2f(icon_x+iw,   icon_y)
        # upper-right
        glTexCoord2f(1,1); glVertex2f(icon_x+iw,   icon_y+ih)
        # upper-left
        glTexCoord2f(0,1); glVertex2f(icon_x,      icon_y+ih)
        glEnd()
        glBindTexture(GL_TEXTURE_2D, 0)
        glDisable(GL_TEXTURE_2D)

        # draw the current countdown number next to the image to the right of the bee mode image 
        if bee.angry_bee_mode or bee.is_recharging: countdown = str(bee.current_countdown_num)
        else: countdown = ""

        self.draw_text(countdown, self.win_width // 2 + 40, self.win_height - 30)

        
        self.draw_text(f"Sec Left: {timer_left_ms//1000}", self.win_width - 150, distance_from_top)    # timer 

        # draw header rectangle 
        self.draw_rectangle(bottomLeft_x=-10, bottomLeft_y= self.win_height-50, 
                            topRight_x=810, topRight_y=810, 
                            color=(64/255, 64/255, 64/255))


    # draw the gui elements in the level (when paused)
    def draw_level_pause_gui(self):
        # draw the top text (level 1)
        self.draw_text("Paused", self.win_width // 2 - 30, self.win_height // 2)

        # draw the buttons (toLobby, help)
        self.toLobby_game_button.draw_text()
        self.toLobby_game_button.draw_button()
        
        self.help_game_button.draw_text()
        self.help_game_button.draw_button()

        # draw banner rectangle 
        self.draw_rectangle(bottomLeft_x=-10, bottomLeft_y=self.win_height // 2 - 20, 
                            topRight_x=810, topRight_y=self.win_height // 2 + 30, 
                            color=(0, 153/255, 0))
        
    # draw the gui elements in the level (when game is over)
    def draw_end_of_game_gui(self, gameWon: bool, bee:Bee):
        # draw the main text 
        if gameWon: 
            text = "You Won!"
            x_offset_to_center = 30
        else: 
            text = "Game Over...duh duh duhh"
            color = (204/255, 0, 0)
            x_offset_to_center = 100
        self.draw_text(text, self.win_width // 2 - x_offset_to_center, self.win_height // 2)


        # draw the appropriate bee mode image at the center of the header
        if bee.health_percentage <= 0: mode = "dead"
        else: mode = "won"
        
        for offset in [-200, 200]:
            tex_id, iw, ih = self.mode_textures[mode]
            icon_x = self.win_width // 2 + offset
            icon_y = self.win_height // 2 - 15

            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, tex_id)
            glColor3f(1,1,1)
            glBegin(GL_QUADS)
            # lower-left
            glTexCoord2f(0,0); glVertex2f(icon_x,      icon_y)
            # lower-right
            glTexCoord2f(1,0); glVertex2f(icon_x+iw,   icon_y)
            # upper-right
            glTexCoord2f(1,1); glVertex2f(icon_x+iw,   icon_y+ih)
            # upper-left
            glTexCoord2f(0,1); glVertex2f(icon_x,      icon_y+ih)
            glEnd()
            glBindTexture(GL_TEXTURE_2D, 0)
            glDisable(GL_TEXTURE_2D)

        # draw the buttons (toLobby, help)
        self.toLobby_game_button.draw_text()
        self.toLobby_game_button.draw_button()
        
        self.help_game_button.draw_text()
        self.help_game_button.draw_button()

        # draw banner rectangle 
        self.draw_rectangle(bottomLeft_x=-10, bottomLeft_y=self.win_height // 2 - 20, 
                            topRight_x=810, topRight_y=self.win_height // 2 + 30, 
                            color=(64/255, 64/255, 64/255))
        
    # draw the loading screen 
    def draw_loading_screen(self, dots:str):
        self.draw_text(f"Loading{dots}", self.win_width // 2 - 150, self.win_height // 2)
        # draw banner rectangle 
        self.draw_rectangle(bottomLeft_x=-10, bottomLeft_y=self.win_height // 2 - 20, 
                            topRight_x=810, topRight_y=self.win_height // 2 + 30, 
                            color=(153/255, 0, 0))
        # # draw rectangle as the background of the menu - black 
        self.draw_rectangle(bottomLeft_x=0, bottomLeft_y=0, 
                            topRight_x=self.win_width, topRight_y=self.win_height, 
                            color=(0, 0, 0))
    
    # draw the screen that will show if something goes wrong 
    def uh_oh_screen(self):
        self.draw_text(f"Uh Oh!! Something went really wrong!!", self.win_width // 2 - 150, self.win_height // 2)
        self.draw_text(f"Press ESC to quit.", self.win_width // 2 - 75, self.win_height // 2 - 25)
        # draw banner rectangle 
        self.draw_rectangle(bottomLeft_x=-10, bottomLeft_y=self.win_height // 2 - 40, 
                            topRight_x=810, topRight_y=self.win_height // 2 + 30, 
                            color=(153/255, 0, 0))
        # draw rectangle as the background of the menu - black 
        self.draw_rectangle(bottomLeft_x=0, bottomLeft_y=0, 
                            topRight_x=self.win_width, topRight_y=self.win_height, 
                            color=(0, 0, 0))

    # check if a button was clicked. returns name of button or None 
    def check_if_button_clicked(self, mouse_x, mouse_y, mode, help):
        # print(f"Mouse Position: x={mouse_x}, y={mouse_y}")  # Debugging the mouse position
        button_clicked = None 

        if mode == "Lobby":
            if help: # if in help menu only listen for exit help button 
                if self.exitHelp_button.is_clicked(mouse_x, mouse_y):
                    button_clicked="exitHelp"
            else: # if help not showing, only listen for normal lobby buttons
                if self.start_game_button.is_clicked(mouse_x, mouse_y):
                    button_clicked = "start"
                elif self.help_button.is_clicked(mouse_x, mouse_y):
                    button_clicked = "help"
                elif self.difficulty_button.is_clicked(mouse_x, mouse_y):
                    button_clicked = "difficulty"
        elif mode == "Level 1":
            if help: # if in help menu only listen for exit help button 
                if self.exitHelp_button.is_clicked(mouse_x, mouse_y):
                    button_clicked = "exitHelp"
            if self.toLobby_game_button.is_clicked(mouse_x, mouse_y):
                button_clicked = "toLobby"
            elif self.help_game_button.is_clicked(mouse_x, mouse_y):
                button_clicked = "helpGame"

        return button_clicked



    # handles when the help button is clicked 
    def draw_help_menu(self):
        # draw the exit button on top of all other elements 
        self.exitHelp_button.draw_text()
        self.exitHelp_button.draw_button()

        # draw the top text (lost?)
        self.draw_text(self.help_menu_title, self.win_width // 2 - 30, self.win_height - 60)

        # draw the general instructions
        intro_lines = [ '''Welcome to The Bee Game!!!''', 
                        '''                           ''', 
                        '''  This is your home garden. Isn't it just the prettiest thing you've ever seen!! Anways this is''',  
                        '''  the dealio. It's nearing the end of Spring which means we have LITERALLY MINUTES to ''',  
                        '''  collect the rest of the flowers' pollen and the hive needs your  help. But, watch out! ''' , 
                        '''  Don't let the beauty of the garden fool you....there are some pretty dangerous insects ''', 
                        '''  out there.''',  
                        '''                             ''', 
                        '''  Alright, what are you waiting for?! Get out there!''']
        top_offset = 100
        for line in intro_lines:
            self.draw_text(line, 25, self.win_height - top_offset)
            top_offset += 25

        # draw the general instructions
        controls_lines = [ '''----------------------------------------------------------------  ''', 
                            '''Controls''', 
                            # '''          ''', 
                            '''    [W/A/S/D]...........Pan the camera up/left/down/right when in 3rd-person view ''', 
                            '''    [Q/E]...................Zoom the camera in/out when in 3rd-person view ''', 
                            '''    [Arrow Keys]......Move the Bee forward/left/backward/right ''',
                            '''    [Shift/Ctrl]..........Move the Bee up/down, fly higher or lower''', 
                            '''    [Z]......................Activate Attack Mode (lasts 5 seconds)(takes 10 sec to recharge) ''',
                            '''    [P or Esc]...........Pause/UnPause ''',
                            '''    [X]......................Pick up pollen particle  ''',
                            '''    [C]......................Drop off pollen particle ''',
                        ] 
        top_offset = 100 + (len(intro_lines) * 25)
        for line in controls_lines:
            self.draw_text(line, 25, self.win_height - top_offset)
            top_offset += 25

        # draw rectangle as the background of the menu - light brown 
        self.draw_rectangle(bottomLeft_x=22.5, bottomLeft_y=22.5, 
                            topRight_x=self.win_width-22.5, topRight_y=self.win_height-35, 
                            color=(212/255, 151/255, 89/255))
        
        # draw rectangle as the background of the menu - dark brown 
        self.draw_rectangle(bottomLeft_x=15, bottomLeft_y=15, 
                            topRight_x=self.win_width-15, topRight_y=self.win_height-25, 
                            color=(61/255, 38/255, 14/255))
        