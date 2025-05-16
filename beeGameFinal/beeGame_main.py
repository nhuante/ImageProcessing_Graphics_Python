import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import numpy as np
# import math 
# import time 

from beeGame_sceneObjects import Prop, create_grass_objects, create_flower_objects, create_beehive
from beeGame_model import Bee, Camera, Pollen, Moth, Flower, create_flowers
from beeGame_GUI import UI
from beeGame_collisions import collisionTest_AABBs, draw_AABB

width, height = 800, 600                                                    # width and height of the screen created

# drawing x, y, z axis in world space
def drawAxes():                                                             # draw x-axis and y-axis
    glLineWidth(3.0)                                                        # specify line size (1.0 default)
    glBegin(GL_LINES)                                                       # replace GL_LINES with GL_LINE_STRIP or GL_LINE_LOOP
    glColor3f(1.0, 0.0, 0.0)                                                # x-axis: red
    glVertex3f(0.0, 0.0, 0.0)                                               # v0
    glVertex3f(200.0, 0.0, 0.0)                                             # v1
    glColor3f(0.0, 1.0, 0.0)                                                # y-axis: green
    glVertex3f(0.0, 0.0, 0.0)                                               # v0
    glVertex3f(0.0, 200.0, 0.0)                                             # v1
    glColor3f(0.0, 0.0, 1.0)                                                # z-axis: blue
    glVertex3f(0.0, 0.0, 0.0)                                               # v0
    glVertex3f(0.0, 0.0, 200.0)                                             # v1
    glEnd()

# drawing the ground
def drawGround():
    # ground_vertices = [[-500, -12.6, -500], # top left
    #                    [-500, -12.6, 500],  # bottom left 
    #                    [500, -12.6, 500],   # 
    #                    [500, -12.6, -500]]
    x_min, x_max = -20, 220
    y_height = -12.6
    z_min, z_max = -120, 120
    
    grass_vertices = [  [x_min, y_height, z_min],       # top left      
                        [x_min, y_height, z_max],        # bottom left 
                        [x_max, y_height, z_max],      # bottom right
                        [x_max, y_height, z_min]]     # top right 

    glColor3f(0, 82/255, 0)
    glBegin(GL_QUADS)
    for vertex in grass_vertices:
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

# regenerate flowers and pollen particles
def generate_flowers_pollen(force_regnerate:bool):
    # flowers 
    flowers, flower_positions = create_flowers(num_flowers=6, force_regenerate=force_regnerate) 

    # pollen particles 
    pollen_particles = []
    for n in range(len(flower_positions)):
        if n > (len(flower_positions)//2) - 1: 
            pollen_height = flower_positions[n][1] + (70 * 3.5) + 12
        else: 
            pollen_height = flower_positions[n][1] + (70 * 2) + 12
        pollen_particles.append(Pollen( radius=2, color=(215/255, 215/255, 25/255), pollen_id=n+1, 
                                        initial_x=flower_positions[n][0],                 # x_pos 
                                        initial_y=pollen_height ,  # y_pos
                                        initial_z=flower_positions[n][2]))                  # z_pos
        
    return flowers, flower_positions, pollen_particles


def main():
    pygame.init()                                                           # initialize a pygame program
    glutInit()                                                              # initialize glut library 

    # set up screen 
    screen = (width, height)                                                # specify the screen size of the new program window
    display_surface = pygame.display.set_mode(screen, DOUBLEBUF | OPENGL)   # create a display of size 'screen', use double-buffers and OpenGL
    pygame.display.set_caption('BeeGame - Waiting To Load')     # set title of the program window

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

    # initialize all the props 
    props = []
    # flower_positions = []
    grass_objects = []
    for grass in create_grass_objects(150):
        grass_objects.append(grass)

    # beehive 
    beehive = create_beehive()
    props.append(beehive)


    # FIXME: flowers and pollen 
    flowers, flower_positions, pollen_particles = generate_flowers_pollen(force_regnerate=False)



    # moth enemies 
    moth_enemies = [] 
    moth_target_positions = [   [(25, 35, 75), (50, 15, 75), (50, 20, 20), (25, 35, 20)], 
                                [(125, 10, 35), (150, 15, 75), (175, 10, 35), (150, 16, 0)],
                                [(16, 16, -90), (32, 16, -50), (80, 16, -70), (55, 16, -95)],
                                [(125, 40, -10), (165, 20, -40), (180, 45, -80), (100, 35, -50)], 

                            ]
    for n in range(len(moth_target_positions)):
        moth_enemies.append(Moth(moth_id=n, 
                                initial_x=25, initial_y=40, initial_z=75, 
                                target_positions=moth_target_positions[n]))
        print(f"---done drawing moth with id: {moth_enemies[n].moth_id}")



    # initialize the camera: camera parameters 
    camera = Camera(view_mode="follow") # FIXME: set correct default view for the bee 

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

    # game mode 
    game_mode = "Lobby"
    help_showing = False
    game_over = False 
    game_result = None

    # garden properties 
    garden_x_boundaries = (0, 200)
    garden_y_boundaries = (-18, 2000)
    garden_z_boundaries = (-100, 100)

    # loading screen 
    loading_game = True 
    loading_game_time = 2 * 1000
    num_dots = 1

    # developer vars 
    show_bounding_boxes = True

    # error handling in case the game crashes 
    error = None 

    while True:
        if error is None:
            try:
                bResetModelMatrix = False
                glPushMatrix()
                glLoadIdentity()

                #--------START: pygame.event.get()
                for event in pygame.event.get():
                    # quitting the game, exiting the window basically 
                    if event.type == pygame.QUIT:
                        pygame.quit()
                    
                    # loading game scren (no input whatsoever)
                    if loading_game:
                        pass

                    # mouse input
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        # get mouse position 
                        mouse_x, mouse_y = pygame.mouse.get_pos()

                        # if not currently in level and not paused, don't check for mouse clicks 
                        if game_over or (game_mode == "Lobby" and not playerBee.paused) or (game_mode == "Level 1" and playerBee.paused):  
                            # check if any of the buttons were clicked
                            button_clicked = ui.check_if_button_clicked(mouse_x, mouse_y, game_mode, help_showing)
                            # handle the correct button behavior 
                            if button_clicked == "start":           # start game button clicked 
                                print(" game is starting.....")
                                game_over = False 
                                game_result = None
                                game_mode = "Level 1"       # update game mode 
                                playerBee.reset_bee_switching_rooms()
                            elif button_clicked == "help":
                                print(" help-lobby menu loading.....")
                                # handle the ui change 
                                # ui.handle_help_click()  
                                help_showing = True
                            elif button_clicked == "toLobby":
                                print(" exiting to lobby....")
                                game_mode = "Lobby"         # update game mode 
                                playerBee.reset_bee_switching_rooms()
                            elif button_clicked == "helpGame":
                                print(" help-inGame menu loading....")
                                help_showing = True

                        # if showing the help button, listen for exit help button click 
                        if help_showing:
                            button_clicked = ui.check_if_button_clicked(mouse_x, mouse_y, game_mode, help_showing)
                            if button_clicked == "exitHelp":
                                help_showing = False
                                if game_mode == "Lobby": 
                                    playerBee.paused = False
                                    # for moth in moth_enemies:
                                    #     moth.paused = False

                        
                        
                    # keyboard input - key down
                    elif event.type == pygame.KEYDOWN:
                        # if game paused, only listen for the `P` or `Esc` keys to unpause. no other keyboard input
                        if playerBee.paused:
                            # pause the game 
                            if event.key == pygame.K_p or event.key == pygame.K_ESCAPE:
                                playerBee.paused = not playerBee.paused       # will pause the current bee animation
                                if playerBee.paused: 
                                    playerBee.start_pause()
                                    # for moth in moth_enemies:
                                    #     moth.paused = True
                                # else:
                                #     for moth in moth_enemies:
                                #         moth.paused = False
                                print(F"\nGAME PAUSED - {playerBee.paused} ")
                        # if game not pause, listen for all keys 
                        else:
                            # reset camera input ----------------------------------------------------- 
                            if event.key == pygame.K_0:                 # reset the current view 
                                bResetModelMatrix = True
                                camera.reset_views()
                            # switch camera view input -----------------------------------------------------
                            elif event.key == pygame.K_SPACE:           # switch view modes: FIXME: list viewing modes here 
                                camera.reset_views()
                                camera.switch_view()                   
                            # bee movement paramter inputs -----------------------------------------------------
                            elif event.key == pygame.K_RIGHT:           # start turning right
                                key_right_on = True
                            elif event.key == pygame.K_LEFT:            # start turning left
                                key_left_on = True
                            elif event.key == pygame.K_UP:              # move forward
                                key_up_on = True                
                            elif event.key == pygame.K_DOWN:            # move backward
                                key_down_on = True
                            elif event.key == pygame.K_LSHIFT:          # ascend
                                key_shift_on = True
                            elif event.key == pygame.K_LCTRL:           # descend
                                key_ctrl_on = True
                            elif event.key == pygame.K_z and (not playerBee.angry_bee_mode and not playerBee.is_recharging and not playerBee.paused):
                                # angry_mode_activated = True
                                playerBee.activate_angry_mode()         # angry mode
                            # camera parameter inputs -----------------------------------------------------
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
                            # DEVELOPER BUTTONS -----------------------------------------------------
                            elif event.key == pygame.K_0:
                                camera.reset_views()
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
                            elif event.key == pygame.K_5:                       # decrease bee health 
                                playerBee.health_percentage -= 20
                                print("Bee Health: ", playerBee.health_percentage)
                            elif event.key == pygame.K_6:                       # increase score points 
                                playerBee.score += 50
                                print("Bee Score: ", playerBee.score)
                            elif event.key == pygame.K_7:                       # toggle bounding boxes shown 
                                show_bounding_boxes = not show_bounding_boxes
                            elif event.key == pygame.K_8:                       # force regenerate flower positions 
                                flowers, flower_positions, pollen_particles = generate_flowers_pollen(force_regnerate=True) 
                            elif event.key == pygame.K_9:
                                raise ValueError("testing the uh oh screen")
                            # un-pause the game -----------------------------------------------------
                            elif event.key == pygame.K_p or event.key == pygame.K_ESCAPE:
                                playerBee.paused = not playerBee.paused       # will pause the current bee animation
                                if playerBee.paused: playerBee.start_pause()
                                print(F"\nGAME PAUSED - {playerBee.paused} ")
                            # pick up pollen -----------------------------------------------------
                            elif event.key == pygame.K_x:
                                # if not already carrying a piece of pollen 
                                if playerBee.carrying_pollen == None: 
                                    # check if within range of a piece of pollen 
                                    bee_min, bee_max = playerBee.get_bounding_volume()
                                    for pollen in pollen_particles:
                                        # if this piece of pollen is not currently being carried 
                                        pollen_min, pollen_max = pollen.get_bounding_volume() 
                                        if collisionTest_AABBs(bee_min, bee_max, pollen_min, pollen_max):
                                            # if close enough to this piece of pollen, pick it up 
                                            pollen.carried = True 
                                            playerBee.carrying_pollen = pollen 
                                            playerBee.leg_carrying_pollen = True 
                                            print(f"--picked up pollen number {pollen.pollen_id}")
                                            break
                            # drop off pollen -----------------------------------------------------
                            elif event.key == pygame.K_c:
                                # only if the bee is already carrying pollen and is touching the beehive
                                if playerBee.carrying_pollen:
                                    bee_min, bee_max = playerBee.get_bounding_volume(d=3)
                                    hive_min, hive_max = beehive.get_bounding_volume() 
                                    pollen = playerBee.carrying_pollen
                                    # if colliding with the beehive 
                                    if collisionTest_AABBs(bee_min, bee_max, hive_min, hive_max):
                                        # drop off at beehive 
                                        playerBee.score += 20  
                                        print(f"--Dropped off pollen {pollen.pollen_id} at the hive")
                                        pollen.carried = False 
                                        pollen.falling = False
                                    else:
                                        # drop off and start falling 
                                        pollen.falling = True 
                                        pollen.carried = False 

                                    # pollen.carried = False 
                                    playerBee.carrying_pollen = None 
                                    playerBee.leg_carrying_pollen = False

                        
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
                # if game is loading, recheck the time passed 
                if loading_game:
                    # recheck time 
                    current_time = pygame.time.get_ticks()
                    # print(current_time)
                    if current_time >= loading_game_time:
                        loading_game = False

                # if game is not loading, do all the game stuff
                else:
                    # if game is paused, handle the pause for the countdown timers 
                    if playerBee.paused:
                        playerBee.maintain_countdown_timers_when_paused()
                    # if game not paused, handle bee movement
                    else:
                        if playerBee.angry_bee_mode: turn_speed = playerBee.angry_turn_speed
                        else: turn_speed = playerBee.normal_turn_speed
                        # update the bee's freeform movement parameters 
                        if key_right_on or key_left_on:
                            reverse = key_down_on
                            if key_right_on and not reverse:    # forward or still and turning right -1
                                playerBee.walk_angle -= turn_speed
                            elif key_right_on and reverse:      # backwards and turning right +1
                                playerBee.walk_angle += turn_speed       
                            elif key_left_on and reverse:       # backwards and turning left -1
                                playerBee.walk_angle -= turn_speed
                            elif key_left_on and not reverse:  # forwards and turning left +1
                                playerBee.walk_angle += turn_speed   
                            # print("walk angle: ", playerBee.walk_angle)
                        if key_up_on or key_down_on:
                            reverse = key_down_on
                            playerBee.walk_speed = playerBee.walk_speed_mp * playerBee.anim_speed
                            playerBee.update_walk_vector(reverse=reverse, 
                                                        boundaries=[garden_x_boundaries, garden_y_boundaries, garden_z_boundaries], 
                                                        obstacles=(props + flowers))
                            playerBee.actively_moving = True 
                            # print(F"\nBEE ACTIVELY MOVING - {playerBee.actively_moving} ")
                        else:
                            if playerBee.actively_moving: 
                                playerBee.actively_moving = False
                                # print(F"\nBEE ACTIVELY MOVING - {playerBee.actively_moving} ")



                        # update the bee's height
                        height_offset_per = 0.0 
                        if key_shift_on:
                            height_offset_per = +0.25
                            playerBee.update_height_offset(height_offset_per, garden_y_boundaries, (props + flowers))
                        elif key_ctrl_on:
                            height_offset_per = -0.25
                            playerBee.update_height_offset(height_offset_per, garden_y_boundaries, (props + flowers))

                        # handle angry mode 
                        if playerBee.angry_bee_mode or playerBee.is_recharging:
                            playerBee.handle_angry_mode()
                            # if playerBee.angry_bee_mode == False:
                                # angry_mode_activated = False

                        # camera.tilt_angle_horizontal, camera.tilt_angle_vertical = 0.0, 0.0
                        # update camera parameters 
                        if key_a_on:
                            if camera.view_mode in ["first-person", "follow"]:
                                max_horizontal_tilt = 15
                            else:
                                max_horizontal_tilt = 45
                            camera.tilt_angle_horizontal  = min(camera.tilt_angle_horizontal + 2, max_horizontal_tilt)
                        elif key_d_on:
                            if camera.view_mode in ["first-person", "follow"]:
                                min_horizontal_tilt = -15
                            else:
                                min_horizontal_tilt = -45
                            camera.tilt_angle_horizontal  = max(camera.tilt_angle_horizontal - 2, min_horizontal_tilt)
                        elif key_w_on:
                            if camera.view_mode in ["first-person", "follow"]:
                                max_vertical_tilt = -15
                            else:
                                max_vertical_tilt = -65
                            camera.tilt_angle_vertical  = max(camera.tilt_angle_vertical - 2, max_vertical_tilt)
                        elif key_s_on:
                            if camera.view_mode in ["first-person", "follow"]:
                                min_vertical_tilt = 15
                            else:
                                min_vertical_tilt = 25
                            camera.tilt_angle_vertical  = min(camera.tilt_angle_vertical + 2, min_vertical_tilt)
                        # update camera zooming 
                        if key_q_on:
                            camera.zoom_distance += 0.5 # had to change to 0.5 otherwise get a black screen when actively zooming in 
                        elif key_e_on:
                            camera.zoom_distance -= 0.5 # to match the speed of zooming in above      

                    
                    # check if the game is over 
                    if playerBee.health_percentage <= 0:
                        game_over = True 
                        game_result = False
                    elif playerBee.score >= 100:
                        game_over = True 
                        game_result = True


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
                
                # draw all the models that are made with primitive glu shapes 
                # bee
                playerBee.update_animations()
                playerBee.draw_bee(draw_bounding_boxes=show_bounding_boxes)
                # pollen
                for pollen in pollen_particles:
                    pollen.draw_pollen(draw_bounding_boxes=show_bounding_boxes, bee=playerBee)
                # fence
                playerBee.draw_fence()
                # moths 
                if game_mode == "Level 1":
                    for moth in moth_enemies:
                        moth.paused = playerBee.paused
                        moth.draw_moth(bee=playerBee, draw_bounding_boxes=show_bounding_boxes, obstacles=(props + flowers))
                # flowers 
                # for flower in flowers:
                #     flower.draw(show_bounding_box=show_bounding_boxes)

                # draw all the props that were imported as obj files 
                for prop in (props + flowers):
                    prop.draw(show_bounding_box=show_bounding_boxes)
                    # curr_position = prop.t.translation
                for grass in grass_objects:
                    grass.draw()
                    

                
                set_2d_projection()     # switch to 2d mode so we can draw the gui 

                # draw gui elements based on room
                if loading_game:
                    # loading screen 
                    num_dots = int((num_dots + 1) % 10) 
                    dots = num_dots * "."
                    ui.draw_loading_screen(dots)
                elif game_mode == "Lobby":
                    if playerBee.paused and not help_showing: 
                        ui.draw_lobby_pause_gui()   # lobby pause screen
                    elif help_showing:  
                        ui.draw_help_menu()         # help screen (pause while we show)
                        playerBee.paused = True
                        # for moth in moth_enemies:
                        #     moth.paused = True

                    else:
                        ui.draw_lobby_gui(bee=playerBee)         # normal lobby ui
                elif game_mode == "Level 1":
                    if help_showing:
                        ui.draw_help_menu()         # help screen (pause while we show)
                        playerBee.paused = True
                    elif game_over:
                        ui.draw_end_of_game_gui(gameWon=game_result, bee=playerBee)
                    elif playerBee.paused and not help_showing: 
                        ui.draw_level_pause_gui()   # level pause screen 
                    else:
                        ui.draw_level_gui(score=playerBee.score, health=playerBee.health_percentage, 
                                        timer_left_ms=playerBee.game_time_to_win, level=playerBee.level, bee=playerBee)         # normal level ui
                

                glPopMatrix()           # get rid of the matrix changes from gui drawing 
                set_3d_projection()     # and change back to 3d mode for the game environment elements

                # draw other entities in the scene
                drawAxes()
                drawGround()
                glPopMatrix()
                pygame.display.flip()
                pygame.time.wait(10)
                continue 
            except Exception as e:
                import traceback; traceback.print_exc()
                error = e 
        
        # if we get here, error != None
        # clear screen + set 2D projection for your UI
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
        glPopMatrix()
        set_2d_projection()
        ui.uh_oh_screen()         # draw your “uh-oh” overlay
        pygame.display.flip()
        # give the user a moment (or handle a quit event here)
        # handle quit-on-ESC while we’re showing the uh-oh
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
        pygame.time.wait(100)

main()
