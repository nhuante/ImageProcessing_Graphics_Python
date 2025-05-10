import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import numpy as np
import math 

from beeGame_model import Bee, Camera
from beeGame_GUI import Button, UI

width, height = 800, 600                                                    # width and height of the screen created

# drawing x, y, z axis in world space
def drawAxes():                                                             # draw x-axis and y-axis
    glLineWidth(3.0)                                                        # specify line size (1.0 default)
    glBegin(GL_LINES)                                                       # replace GL_LINES with GL_LINE_STRIP or GL_LINE_LOOP
    glColor3f(1.0, 0.0, 0.0)                                                # x-axis: red
    glVertex3f(0.0, 0.0, 0.0)                                               # v0
    glVertex3f(100.0, 0.0, 0.0)                                             # v1
    glColor3f(0.0, 1.0, 0.0)                                                # y-axis: green
    glVertex3f(0.0, 0.0, 0.0)                                               # v0
    glVertex3f(0.0, 100.0, 0.0)                                             # v1
    glColor3f(0.0, 0.0, 1.0)                                                # z-axis: blue
    glVertex3f(0.0, 0.0, 0.0)                                               # v0
    glVertex3f(0.0, 0.0, 100.0)                                             # v1
    glEnd()

# drawing the ground
def drawGround():
    ground_vertices = [[-500, -12.6, -500],
                       [-500, -12.6, 500],
                       [500, -12.6, 500],
                       [500, -12.6, -500]]

    glColor3f(0.4, 0.4, 0.4)
    glBegin(GL_QUADS)
    for vertex in ground_vertices:
        glVertex3fv(vertex)
    glEnd()

# switch to orthographic mode to draw ui components 
def set_2d_projection():
    glPushMatrix()

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0, width, 0, height, -1, 1)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

# switch to perspective mode to draw 3d game components 
def set_3d_projection():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, width/height, 0.1, 1000.0)

    glMatrixMode(GL_MODELVIEW)



def main():
    pygame.init()                                                           # initialize a pygame program
    glutInit()                                                              # initialize glut library 

    # set up screen 
    screen = (width, height)                                                # specify the screen size of the new program window
    display_surface = pygame.display.set_mode(screen, DOUBLEBUF | OPENGL)   # create a display of size 'screen', use double-buffers and OpenGL
    pygame.display.set_caption('BeeGame - Do You Have Any Buzzing Talent?')     # set title of the program window

    # create UI 
    ui = UI(win_width=width, win_height=height)

    # set up GL specs
    glEnable(GL_DEPTH_TEST)
    glMatrixMode(GL_PROJECTION)                                             # set mode to projection transformation
    glLoadIdentity()                                                        # reset transf matrix to an identity
    gluPerspective(45, (width / height), 0.1, 1000.0)                       # specify perspective projection view volume

    glMatrixMode(GL_MODELVIEW)                                              # set mode to modelview (geometric + view transf)
    initmodelMatrix = glGetFloat(GL_MODELVIEW_MATRIX)
    modelMatrix = glGetFloat(GL_MODELVIEW_MATRIX)

    # initialize the playerBee: body dimensions and transformation parameters 
    playerBee = Bee() 

    # initialize the camera: camera parameters 
    camera = Camera(view_mode="front") # FIXME: set correct default view for the bee 

    # initialize the states of all the designated keys

    # bee movement parameters 
    key_left_on = False     # if left-arrow key is HELD on now
    key_right_on = False    # if right-arrow key is held on now
    key_up_on = False 
    key_down_on = False
    key_shift_on = False 
    key_ctrl_on = False

    # camera parameters 
    key_a_on = False        # if key 'A' is HELD on now
    key_d_on = False        # if key 'D' is HELD on now
    key_w_on = False        # if key 'W' is HELD on now
    key_s_on = False        # if key 'S' is HELD on now
    key_q_on = False        # if key 'Q' is HELD on now
    key_e_on = False        # if key 'E' is HELD on now

    # debugging mode 
    debugging_mode = True 


    while True:
        bResetModelMatrix = False
        glPushMatrix()
        glLoadIdentity()

        #--------START: pygame.event.get()
        for event in pygame.event.get():
            # quitting the game, exiting the window basically 
            if event.type == pygame.QUIT:
                pygame.quit()

            # mouse input
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # get mouse position 
                mouse_x, mouse_y = pygame.mouse.get_pos()
                # check if any of the buttons were clicked
                button_clicked = ui.check_if_button_clicked(mouse_x, mouse_y)
                # handle the correct button behavior 
                if button_clicked == "start":           # start game button clicked 
                    ui.room_text = "Level 1"
                    print(" game is starting.....")
                elif button_clicked == "help":
                    print(" help menu loading.....")

                    
            

            # keyboard input - key down
            elif event.type == pygame.KEYDOWN:
                # reset input 
                if event.key == pygame.K_0:                 # reset the current view 
                    bResetModelMatrix = True
                    camera.reset_views()
                # switch camera view input 
                elif event.key == pygame.K_SPACE:           # switch view modes: FIXME: list viewing modes here 
                    camera.reset_views()
                    camera.switch_view()                   
                # bee movement paramter inputs 
                elif event.key == pygame.K_RIGHT:           # start turning right
                    key_right_on = True
                elif event.key == pygame.K_LEFT:            # start turning left
                    key_left_on = True
                elif event.key == pygame.K_UP:
                    key_up_on = True
                elif event.key == pygame.K_DOWN:
                    key_down_on = True
                elif event.key == pygame.K_LSHIFT:
                    key_shift_on = True
                elif event.key == pygame.K_LCTRL:
                    key_ctrl_on = True
                # camera parameter inputs 
                elif event.key == pygame.K_a:               # start looking left 
                    key_a_on = True
                elif event.key == pygame.K_d:               # start looking right 
                    key_d_on = True
                elif event.key == pygame.K_w:               # start looking up 
                    key_w_on = True
                elif event.key == pygame.K_s:               # start looking down 
                    key_s_on = True
                elif event.key == pygame.K_q:               # start zooming in
                    key_q_on = True
                elif event.key == pygame.K_e:               # start zooming out
                    key_e_on = True
                # modifying bee animation/movement speeds 
                elif event.key == pygame.K_1:                       # decrease swing speed for animation
                    playerBee.anim_speed -= 0.5
                    print("Swing Speed:", playerBee.anim_speed)    
                elif event.key == pygame.K_2:                       # increase swing speed for animation
                    playerBee.anim_speed += 0.5
                    print("Swing Speed:", playerBee.anim_speed)    
                elif event.key == pygame.K_3:                       # decrease walk speed mp for walking
                    playerBee.walk_speed_mp -= 0.1
                    print("Walk Speed MP:", playerBee.walk_speed_mp)
                elif event.key == pygame.K_4:                       # increase walk speed mp for walking
                    playerBee.walk_speed_mp += 0.1
                    print("Walk Speed MP:", playerBee.walk_speed_mp)
                # reset bee to origin  
                elif event.key == pygame.K_5:                       # reset playerBee to origin
                    playerBee.resetToOrigin()
                # pause the game 
                elif event.key == pygame.K_p:
                    playerBee.paused = not playerBee.paused       # will pause the current bee animation
                    print(F"\nGAME PAUSED - {playerBee.paused} ")
                # debugging keys 
                elif event.key == pygame.K_y:                       # toggle debugging mode 
                    debugging_mode = not debugging_mode
                    if debugging_mode == False: playerBee.angry_bee_mode = False
                    print(F"\nDEBUGGING MODE - {debugging_mode} ")
                # elif event.key == pygame.K_m and debugging_mode:            # toggle angry mode indefinitely 
                #     playerBee.angry_bee_mode = not playerBee.angry_bee_mode
                #     if playerBee.anim_speed == 1.0: # in normal mode --> switching to mad mode
                #         playerBee.anim_speed = 2.0
                #         playerBee.walk_speed *= 3
                #     else:                           # in angry mode  --> switching to normal mode
                #         playerBee.anim_speed = 1.0
                #         playerBee.walk_speed /= 3
                #     print(F"\nANGRY BEE MODE - {playerBee.angry_bee_mode} ")
                elif event.key == pygame.K_z and (not playerBee.angry_bee_mode and not playerBee.is_recharging):
                    # angry_mode_activated = True
                    playerBee.activate_angry_mode()

                
            # keyboard input - key up
            elif event.type == pygame.KEYUP:
                # bee movement paramter inputs 
                if event.key == pygame.K_RIGHT:             # stop turning right 
                    key_right_on = False 
                elif event.key == pygame.K_LEFT:            # stop turning left 
                    key_left_on = False
                elif event.key == pygame.K_UP:
                    key_up_on = False
                elif event.key == pygame.K_DOWN:
                    key_down_on = False
                elif event.key == pygame.K_LSHIFT:
                    key_shift_on = False
                elif event.key == pygame.K_LCTRL:
                    key_ctrl_on = False
                # camera parameter inputs 
                elif event.key == pygame.K_a:               # stop looking left 
                    key_a_on = False
                elif event.key == pygame.K_d:               # stop looking right 
                    key_d_on = False
                elif event.key == pygame.K_w:               # stop looking up 
                    key_w_on = False
                elif event.key == pygame.K_s:               # stop looking down 
                    key_s_on = False
                elif event.key == pygame.K_q:               # stop zooming in
                    key_q_on = False
                elif event.key == pygame.K_e:               # stop zooming out
                    key_e_on = False
                

            

        
        #--------END: pygame.event.get()
        # if game not paused, handle bee movement
        if not playerBee.paused:
            
            # update the bee's freeform movement parameters 
            if key_up_on or key_down_on:
                reverse = key_down_on
                if key_right_on and not reverse:
                    playerBee.walk_angle -= 1
                elif key_right_on and reverse: 
                    playerBee.walk_angle += 1
                elif key_left_on and not reverse:
                    playerBee.walk_angle += 1
                elif key_right_on and reverse: 
                    playerBee.walk_angle -= 1
                # print("walk angle: ", playerBee.walk_angle)
                playerBee.walk_speed = playerBee.walk_speed_mp * playerBee.anim_speed
                playerBee.update_walk_vector(reverse=reverse)
                playerBee.actively_moving = True 
                # print(F"\nBEE ACTIVELY MOVING - {playerBee.actively_moving} ")
            else:
                if playerBee.actively_moving: 
                    playerBee.actively_moving = False
                    # print(F"\nBEE ACTIVELY MOVING - {playerBee.actively_moving} ")
            # update the bee's height 
            if key_shift_on:
                playerBee.height_offset += 0.2
            elif key_ctrl_on:
                playerBee.height_offset -= 0.2

            # handle angry mode 
            if playerBee.angry_bee_mode or playerBee.is_recharging:
                playerBee.handle_angry_mode()
                # if playerBee.angry_bee_mode == False:
                    # angry_mode_activated = False

        
            # update camera parameters 
            if key_a_on:
                camera.tilt_angle_horizontal += 1
            elif key_d_on:
                camera.tilt_angle_horizontal -= 1
            elif key_w_on:
                # if camera located at negative z position, looking up is negative rotation about X
                if camera.eye_pos[2] < 0: camera.tilt_angle_vertical -= 1
                # if camera located at positive z position, looking up is positive rotation about X
                else: camera.tilt_angle_vertical += 1
            elif key_s_on:
                # if camera located at negative z position, looking down is negative rotation about X
                if camera.eye_pos[2] < 0: camera.tilt_angle_vertical += 1
                # if camera located at positive z position, looking down is positive rotation about X
                else: camera.tilt_angle_vertical -= 1
            # update camera zooming 
            if key_q_on:
                camera.zoom_distance += 0.5 # had to change to 0.5 otherwise get a black screen when actively zooming in 
            elif key_e_on:
                camera.zoom_distance -= 0.5 # to match the speed of zooming in above      

        



        # When '0' is tapped, reset the view 
        if (bResetModelMatrix):
            glLoadIdentity()
            modelMatrix = initmodelMatrix
        glMultMatrixf(modelMatrix)
        modelMatrix = glGetFloatv(GL_MODELVIEW_MATRIX)

        glLoadIdentity()
        
        # Upate camera parameters: eye_position and look_at point
        new_eye_pos, new_lookat = camera.update_view(playerBee)

        
        # Use updated camera parameters to update camera model
        gluLookAt(new_eye_pos[0], new_eye_pos[1], new_eye_pos[2], 
                  new_lookat[0], new_lookat[1],new_lookat[2],
                  camera.view_up[0], camera.view_up[1], camera.view_up[2])


        glMultMatrixf(modelMatrix)        
        
        playerBee.update_animations()
        playerBee.draw_bee()

        # Clear the screen and draw the Lobby GUI
        # glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        set_2d_projection()
        ui.draw_lobby_gui()
        glPopMatrix()
        set_3d_projection()

        # draw other entities in the scene
        drawAxes()
        drawGround()

        glPopMatrix()
        pygame.display.flip()
        pygame.time.wait(10)

main()