import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import numpy as np
import math 
import random 
# import time 

'''
    THESE ARE OBJECTS THAT ARE MODELED USING OPENGL METHODS AND FUNCTIONS
        THEY INCLUDE 
        - BEE 
        - FENCE 
        - CAMERA 
        - POLLEN
'''


# Complete the function for rotating the input `vector` around `rot_axis` by `angle_degrees`
#      Construct a 3x3 rotation matrix (no need Homogeneous) and multiply it with the input vector
#      rot_axis: "X", "Y", or "Z"
#      Return the rotated vector.
def rotate_vector(vector, angle_degrees, rot_axis = "Y"):
    rotated_vector = np.array([0.0, 0.0, 0.0])
    
    # convert angle degrees to radians
    rad = np.deg2rad(angle_degrees)

    # construct a 3x3 totation matrix using np.array based on angle and rotation axis
    rot_matrix = np.zeros((3, 3))

    cosine_theta = np.cos([rad])[0]
    sin_theta = np.sin([rad])[0]

    if rot_axis == "X": 
        rot_matrix[1][1], rot_matrix[2][2] = cosine_theta, cosine_theta
        rot_matrix[1][2], rot_matrix[2][1] = -1 * sin_theta, sin_theta
        rot_matrix[0][0] = 1
    elif rot_axis == "Y":
        rot_matrix[0][0], rot_matrix[2][2] = cosine_theta, cosine_theta
        rot_matrix[2][0], rot_matrix[0][2] = -1 * sin_theta, sin_theta
        rot_matrix[1][1] = 1
    elif rot_axis == "Z":
        rot_matrix[0][0], rot_matrix[1][1] = cosine_theta, cosine_theta
        rot_matrix[0][1], rot_matrix[1][0] = -1 * sin_theta, sin_theta
        rot_matrix[2][2] = 1
    # print("rotation matrix: \n", rot_matrix)  # for testing

    # rotate the input vector by multiplying with the matrix using np.dot()
    rotated_vector = np.dot(rot_matrix, vector)

    return rotated_vector


class Bee:
    def __init__(self):
        # animation variables 
        self.anim_speed = 1.0           # master bee movement animation speed 

        self.wing_angle = 0             # wing animation parameters
        self.wing_speed = 0.01
        self.wing_range = 40

        self.leg_angle = 0              # leg animation parameters
        self.leg_speed = 0.005
        self.leg_range = 1.1
        self.last_leg_angle = 0

        self.stinger_angle = 0          # stinger animation parameters
        self.stinger_speed = 0.006
        self.stinger_range = 5

        self.pupil_x_offset = 0            # pupil animation parameters
        self.pupil_speed = 0.01
        self.pupil_range_x = 0.27
        self.pupil_range_y = 0.35
        self.pupil_move_timer = 0 
        self.pupil_position = [0, 0]
        self.pupil_target = [0, 0]
        self.pupil_pause_time = random.randint(2000, 3000)  # Random pause time (in milliseconds)
        self.last_pupil_change_time = pygame.time.get_ticks()  # Last time the pupil changed position
    

        # freeform movement motion parameters
        self.walk_direction = np.array([0.0, 0.0, 1.0]) # unit vector; initially aligned with z-axis ()
        self.walk_angle = 0.0 # the angle (degrees) between the walk_direction and the z-axis [0, 0, 1] ()
        self.walk_speed_mp = 0.7
        self.walking_speed = 1.3
        self.walk_speed = self.walk_speed_mp * self.walking_speed # straightline and freeform walking speed ()
        self.walk_vector = np.array([100.0, 10.0, 0.0]) # = walk_speed * walk_direction; updated for every iteration to translate the playerBee during walking ()
        self.height_offset = 0.0
        self.actively_moving = False
        self.in_reverse = False

        # turning speed 
        self.normal_turn_speed = 3
        self.angry_turn_speed = 6


        # game controls 
        self.paused = False

        # angry mode 
        self.angry_bee_mode = False
        self.angry_mode_start_time = 0              # time angry mode period begins
        self.recharge_start_time = 0                # time recharging period begins
        self.is_recharging = False                  # if currently recharging  
        self.angry_mode_length = 1000 * 5           # replace the 5 with num of seconds desired
        self.recharge_length = 1000 * 10            # replace the 5 with num of seconds desired
        self.current_countdown_num = -1

        # timer when paused var 
        self.temp_time_ran_for_pause = 0        # (for angry or recharging mode)
        self.temp_game_time_ran_for_pause = 0   # (for overall game time to play)

        # game stats
        self.initial_game_timer = 1000 * 120        # in-game timer - replace the 5 with num of seconds desired
        self.game_time_to_win = 1000 * 120           
        self.score = 0                               # in-game score count
        self.level = 1                               # in-game level
        self.health_percentage = 100                 # in-game health bar




    # Resets the bee to be placed at the origin and movement parameters to their starting values
    def resetToOrigin(self):
        self.walk_direction = np.array([0.0, 0.0, 1.0])
        self.walk_angle = 0.0 
        self.walk_vector = np.array([100.0, 10.0, 0.0])
    
    # activate pause mode 
    def start_pause(self):
        self.paused = True
        current_time = pygame.time.get_ticks() 

        # if currently counting for angry mode, maintain the time left until end of pause 
        if self.angry_bee_mode:
            # this is what we want to maintain
            time_ran = current_time - self.angry_mode_start_time 
            self.temp_time_ran_for_pause = time_ran
        elif self.is_recharging:
            # this is what we want to maintain 
            time_ran =  current_time - self.recharge_start_time
            self.temp_time_ran_for_pause = time_ran
             
        
    # continuously called to handle pausing (to maintain angry or countdown modes)
    def maintain_countdown_timers_when_paused(self):
        current_time = pygame.time.get_ticks() 
        # if angry, update the angry start time to maintain the time ran 
        if self.angry_bee_mode:
            self.angry_mode_start_time = current_time - self.temp_time_ran_for_pause
        # if recharging, update the recharge start time to maintain the time ran 
        elif self.is_recharging:
            self.recharge_start_time = current_time - self.temp_time_ran_for_pause


    # Update bee's walk_direction and walk_vector based on walk_angle changed by key input
    def update_walk_vector(self, reverse, boundaries):
        # rotate current walk vector by walk angle 
        rotated_direction = rotate_vector(self.walk_direction, self.walk_angle, rot_axis="Y")
        # print("walk direction:", rotated_direction)   # for testing

        # update walk vector 
        if reverse:
            self.walk_vector -= self.walk_speed * rotated_direction
            self.in_reverse = True
        else:
            self.walk_vector += self.walk_speed * rotated_direction
            self.in_reverse = False

        # constrain to the garden's boundaries 
        # boundaries = [ (x_min, x_max), (y_min, y_max), (z_min, z_max)]
        for i in range(3):
            # attempted_walk_vector_value = self.walk_vector[i]
            min_value = boundaries[i][0]
            max_value = boundaries[i][1]
            self.walk_vector[i] = max(min(self.walk_vector[i], max_value), min_value)
        # print("walk vecctor:", self.walk_vector)      # for testing

    # update the animation parameters 
    def update_animations(self):
        if self.paused:
            return 
        # wing flapping (using sine wave for smooth back-and-forth movement)
        self.wing_angle = min(-math.sin(pygame.time.get_ticks() * self.wing_speed * self.anim_speed) * self.wing_range, 
                              math.sin(pygame.time.get_ticks() * self.wing_speed * self.anim_speed) * self.wing_range)  # Adjust speed and range
        
        # leg swinging (similar sine wave motion for a pendulum-like effect)
        self.leg_angle = math.sin(pygame.time.get_ticks() * self.leg_speed * self.anim_speed) * self.leg_range  # Adjust speed and range
        
        # stinger wagging (gentle back-and-forth like a dog tail)
        self.stinger_angle = math.sin(pygame.time.get_ticks() * self.stinger_speed * self.anim_speed) * self.stinger_range  # Adjust speed and range
        
        # pupils moving (left-right movement to give the bee a livelier expression)
        current_time = pygame.time.get_ticks()
        # if the pause time has passed, change the pupil's target position
        if current_time - self.last_pupil_change_time > self.pupil_pause_time:
            # pick a random new position within the eye black's area (this can be fine-tuned)
            self.pupil_target = [random.uniform(-self.pupil_range_x, self.pupil_range_x), 
                                 random.uniform(-self.pupil_range_y, self.pupil_range_y)]
            
            # reset the timer for the next pause
            self.last_pupil_change_time = current_time
            self.pupil_pause_time = random.randint(2000, 6000)  # Random pause time for the next cycle

        # Smoothly move the pupil towards the target position (you can adjust the speed)
        self.pupil_position[0] += (self.pupil_target[0] - self.pupil_position[0]) * self.pupil_speed
        self.pupil_position[1] += (self.pupil_target[1] - self.pupil_position[1]) * self.pupil_speed
    
    # only called when we start angry mode
    def activate_angry_mode(self):
        # if paused, don't do anything
        if self.paused:
            pass
        current_time = pygame.time.get_ticks() 

        self.angry_bee_mode = True
        self.angry_mode_start_time = current_time
        self.anim_speed = 2.0
        self.walk_speed *= 3
        self.current_countdown_num = self.angry_mode_length // 1000
        print(f"\nANGRY MODE ACTIVATED")
        print(f"     Countdown: {self.current_countdown_num}")

    # called at every iteration of the main loop when actively mad or recharging
    def handle_angry_mode(self):
        # if paused, don't do anything
        if self.paused:
            pass
        # get the current time 
        current_time = pygame.time.get_ticks() 

        # if angry mode already active and we still are angry 
        if self.angry_bee_mode:
            # if currently paused, update the 
            # if angry time is up
            if current_time - self.angry_mode_start_time >= self.angry_mode_length:
                self.angry_bee_mode = False
                self.anim_speed = 1.0
                self.walk_speed /= 3
                self.recharge_start_time = current_time
                self.is_recharging = True
                self.current_countdown_num = self.recharge_length // 1000
                print(f"\nANGRY MODE DE-ACTIVATED....RECHARGING")
                print(f"     Countdown: {self.current_countdown_num}")
            # angry time not up yet (countdown every second)
            else:
                diff = current_time - self.angry_mode_start_time
                sec_left = self.angry_mode_length - diff
                if sec_left <= (self.current_countdown_num - 1) * 1000:
                    self.current_countdown_num -= 1
                    print(f"     Countdown: {self.current_countdown_num}")
        # if not angry and we are reacharging 
        elif self.is_recharging:
            # if recharging time is up
            if current_time - self.recharge_start_time >= self.recharge_length:
                self.is_recharging = False 
                print(f"FINISHED RECHARGING - READY TO BE MAD AGAIN")
            else:
                diff = current_time - self.recharge_start_time
                sec_left = self.recharge_length - diff 
                if sec_left <= (self.current_countdown_num - 1) * 1000:
                    self.current_countdown_num -= 1
                    print(f"     Countdown: {self.current_countdown_num}")

    # resets when switching from lobby to level or vice versa 
    def reset_bee_switching_rooms(self):
        self.paused = False 
        self.angry_bee_mode = False 
        self.is_recharging = False
        self.score = 0 
        self.health_percentage = 100
        self.game_time_to_win = self.initial_game_timer
        self.level = 1
        self.resetToOrigin()

    # create bee geometry 
    def draw_bee(self): 
        # color variables 
        black_color = (0, 0, 0)
        white_color = (1, 1, 1)
        eye_grey_color = (224/255, 224/255, 224/255)
        wing_grey_color = (0.7, 0.7, 0.7)
        blue_iris_color = (51/255,153/255,255/255)
        eye_red_color = (204/255, 0, 0)
        red_iris_color = (153/255, 0, 0)



        glClearColor(0, 0, 0, 1)                                                # set background RGBA color 
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)                        # clear the buffers initialized in the display mode

        # configure quatratic drawing [$1,470]
        quadratic = gluNewQuadric()
        gluQuadricDrawStyle(quadratic, GLU_FILL)  

        glPushMatrix() # DO NOT DELETE THIS

        #--------------Code below will create the geometry of the bee-------------------4
        # adjust height of the bee 
        glTranslatef(0, self.height_offset, 0)
        # translate entire bee by the walk vector 
        glTranslatef(*self.walk_vector)
        # rotate the entire bee to face the correct walking direction
        glRotatef(self.walk_angle, 0, 1, 0)



        # ---- MAIN BODY ----
        glPushMatrix()
        glColor3f(1, 1, 0)      # yellow body
        glutSolidCube(4.0)      # create main body cube 
        glPopMatrix()

        # ---- MAIN BODY / BLACK STRIPES ----
        for stripe_height in [0.8, -0.8]:
            glPushMatrix()
            glColor3f(0, 0, 0)      # black stripes
            glTranslatef(0, 0, stripe_height)
            glScalef(2.2, 2.2, 0.4)
            glutSolidCube(2)
            glPopMatrix()

        # ---- LEGS ----
        glPushMatrix()
        glColor3f(0, 0, 0)      # black legs
        direction = 1
        for i in range(3):
            # the left leg 
            glPushMatrix() 
            glTranslatef(-0.8, -3, -1.2 + i * 1.2)  # find the correct position for the leg 
            
            glTranslate(0, 2.2, 0)
            if not self.actively_moving: 
                glRotatef(self.leg_angle * direction, 1, 0, 0)      # animate left legs
            else: 
                drag_factor = 8.5  # Adjust to control how much the legs drag
                leg_drag_angle = max(min(10 + (self.walk_vector[0] * drag_factor), 25), -25)
                if self.in_reverse: 
                    leg_drag_angle *= -1
                    if self.walk_vector[0] <= 0:
                        leg_drag_angle *= -1
                elif self.walk_vector[0] <= 0: 
                    leg_drag_angle *= -1 # if in negative x-axis territory, reverse the angle 
                glRotatef(leg_drag_angle, 1, 0, 0)      # animate left legs
            glTranslate(0, -2.2, 0)

            glScalef(0.5, 2.2, 0.5)
            glutSolidCube(1)
            glPopMatrix()

            # the right leg 
            glPushMatrix() 
            glTranslatef(0.8, -3, -1.2 + i * 1.2)   # find the correct position for the leg 
            
            glTranslate(0, 2.2, 0)
            if not self.actively_moving: 
                glRotatef(-self.leg_angle * direction, 1, 0, 0)      # animate right legs
            else: 
                # if self.walk_vector[2] == 0 or self.walk_vector[2] == 180:
                #     leg_drag_angle = self.last_leg_angle    
                # else:
                drag_factor = 8.5  # Adjust to control how much the legs drag
                leg_drag_angle = max(min(10 + (self.walk_vector[0] * drag_factor), 25), -25) # FIXME: WHEN CROSSING OVER Z-AXIS, THE ANGLE NEUTRALIZES FOR A SEC
                if self.in_reverse: 
                    leg_drag_angle *= -1 # if going backwards, reverse the angle 
                    if self.walk_vector[0] <= 0:
                        leg_drag_angle *= -1
                elif self.walk_vector[0] <= 0: 
                    leg_drag_angle *= -1 # if in negative x-axis territory, reverse the angle 
                self.last_leg_angle = leg_drag_angle
                glRotatef(leg_drag_angle, 1, 0, 0)      # animate right legs
            # glRotatef(-self.leg_angle * direction, 1, 0, 0)      # animate right legs
            glTranslate(0, -2.2, 0)

            glScalef(0.5, 2.2, 0.5)
            glutSolidCube(1)
            glPopMatrix()
            direction *= -1
        glPopMatrix()

        # ---- WINGS ----
        dist_from_center_line = 1.7
        dist_to_line_up_above_bee = 2.2
        scale_wing_length = 2.7
        scale_wing_width = 2.7
        scale_wing_thickness = 0.35 
        # ---- RIGHT WING ----
        glPushMatrix() 
        glColor3f(*wing_grey_color)    # light grey 
        glTranslatef(-dist_from_center_line, dist_to_line_up_above_bee, 0.0)
        glTranslatef(1, 0, 0)
        glRotatef(self.wing_angle, 0, 0, 1)  # Flap the left wing
        glTranslatef(-1, 0, 0)
        glScalef(scale_wing_length, scale_wing_thickness, scale_wing_width)     # flatten
        glutSolidCube(1)
        glPopMatrix()
        # ---- LEFT WING ----
        glPushMatrix() 
        glColor3f(*wing_grey_color)    # light grey 
        glTranslatef(dist_from_center_line, dist_to_line_up_above_bee, 0.0)
        glTranslatef(-1, 0, 0)
        glRotatef(-self.wing_angle, 0, 0, 1)  # Flap the right wing
        glTranslatef(1, 0, 0)
        glScalef(scale_wing_length, scale_wing_thickness, scale_wing_width)     # flatten
        glutSolidCube(1)
        glPopMatrix()
        
        # ---- ANTENNAE ----
        glColor3f(*black_color)    # black

        # ---- RIGHT ANTENNAE ----
        glPushMatrix()
        glTranslatef(1, 1.2, 2.5)       # position relative to head
        glRotatef(90, 1, 0, 0)          # parallel to z-axis
        glScalef(0.2, 1, 0.4)           # stretch to look skinny
        glutSolidCube(1)                # lower antenna 
        glTranslatef(0, 0.5, -0.9)      # 0.5 overlap parallel to wings (horizontally), -0.9 small overlap vertically
        glutSolidCube(1)                # upper antenna
        glPopMatrix()

        # ---- LEFT ANTENNAE ----
        glPushMatrix()
        glTranslatef(-1, 1.2, 2.5)       # position relative to head
        glRotatef(90, 1, 0, 0)          # parallel to z-axis
        glScalef(0.2, 1, 0.4)           # stretch to look skinny
        glutSolidCube(1)                # lower antenna 
        glTranslatef(0, 0.5, -0.9)      # 0.5 overlap parallel to wings (horizontally), -0.9 small overlap vertically
        glutSolidCube(1)                # upper antenna
        glPopMatrix()

        # ---- EYES ----

        # ---- RIGHT EYE WHITE ----
        if not self.angry_bee_mode: glColor3f(*eye_grey_color)    # light grey if normal 
        else: glColor3f(*eye_red_color)         # red if mad
        glPushMatrix()
        glTranslatef(1.42, -0.5, 1.7)
        glScalef(1.2, 1.7, 0.75)
        glutSolidCube(1)

        # ---- RIGHT EYEBROW ----
        glPushMatrix()
        glColor3f(*black_color)
        glTranslatef(0, 0.6, 0.2)
        if self.angry_bee_mode: glRotatef(15, 0, 0, 1)
        glScalef(1.2, 0.14, 1)
        glutSolidCube(1)
        glPopMatrix()

        # ---- RIGHT EYE PUPIL AND IRIS ----
        glTranslatef(self.pupil_position[0], 
                     self.pupil_position[1], 0.3)
        glScalef(0.6, 0.4, 0.5)
        if not self.angry_bee_mode: glColor3f(*blue_iris_color)    # light grey if normal 
        else: glColor3f(*red_iris_color)         # red if mad
        # glColor3f(*blue_iris_color) # blue iris
        glutSolidCube(1)
        glColor3f(*black_color)    # black pupil
        glTranslatef(self.pupil_position[0] * 0.7, 
                     self.pupil_position[1] * 0.7, 0.3)
        glutSolidCube(0.5)
        glPopMatrix()

        # ---- LEFT EYE WHITE ----
        if not self.angry_bee_mode: glColor3f(*eye_grey_color)    # light grey if normal 
        else: glColor3f(*eye_red_color)         # red if mad
        glPushMatrix()
        glTranslatef(-1.42, -0.5, 1.7)
        glScalef(1.2, 1.7, 0.75)
        glutSolidCube(1)

        # ---- LEFT EYEBROW ----
        glPushMatrix()
        glColor3f(*black_color)
        glTranslatef(0, 0.6, 0.2)
        if self.angry_bee_mode: glRotatef(-15, 0, 0, 1)
        glScalef(1.2, 0.14, 1)
        glutSolidCube(1)
        glPopMatrix()

        # ---- LEFT EYE PUPIL AND IRIS----
        glTranslatef(self.pupil_position[0], 
                     self.pupil_position[1], 0.3)
        glScalef(0.6, 0.4, 0.5)
        if not self.angry_bee_mode: glColor3f(*blue_iris_color)    # light grey if normal 
        else: glColor3f(*red_iris_color)         # red if mad
        glutSolidCube(1)
        glColor3f(*black_color)     # black pupil
        glTranslatef(self.pupil_position[0] * 0.7, 
                     self.pupil_position[1] * 0.7, 0.3)
        glutSolidCube(0.5)
        glPopMatrix()


        # ---- MOUTH ----
        glColor3f(*black_color)     # black
        glPushMatrix()
        glTranslatef(0, -1.2, 2)
        if self.angry_bee_mode: glRotatef(180, 1, 0, 0)

        glPushMatrix()              # main mouth 
        glScalef(0.8, 0.2, 0.2)
        glutSolidCube(1)
        glPopMatrix()           
            
        glPushMatrix()              # left curl
        glTranslatef(-0.45, 0.2, 0)
        glScalef(0.15, 0.2, 0.2)
        glutSolidCube(1)
        glPopMatrix()

        glPushMatrix()              # right curl 
        glTranslatef(0.45, 0.2, 0)
        glScalef(0.15, 0.2, 0.2)
        glutSolidCube(1)
        glPopMatrix()

        glPopMatrix()


        # ---- Stinger ----
        glColor3f(*black_color)     # black
        glPushMatrix()
        glTranslatef(0, 0.6, -2.8)
        glRotatef(35, 1, 0, 0)      # angle stinger at a diagonal 

        glTranslatef(0, 0, 2)
        glRotatef(self.stinger_angle, 0, 1, 0)
        glTranslatef(0, 0, -2)

        gluCylinder(quadratic, 0.0, 0.3, 2, 10, 10)  # Create the stinger (base radius, top radius, height, slives, stacks)
        glPopMatrix()

        
        #--------------Code above will create the geometry of the bee -------------------
        glPopMatrix() # DO NOT DELETE THIS
        
    
    
    
    
    
    
    
    
    def draw_fence(self):
        glColor3f(1.0, 1.0, 1.0)  # White color for the fence posts

        # Define the dimensions of the garden and fence posts
        fence_post_width = 5.0
        fence_post_height = 30.0
        fence_post_depth = 2.0  # Depth for the fence posts (to give them thickness)
        post_spacing = 20.0  # Space between fence posts (float spacing)

        # Define the bounds of the garden
        x_min, x_max = 0, 200
        z_min, z_max = -100, 100

        # Draw fence posts along the four sides
        # Front and back sides (along the z-axis)
        x = x_min
        while x <= x_max:
            # Front side (z = -100)
            glPushMatrix()
            glTranslatef(x, 0, z_min - 1.5*fence_post_depth)  # Position along the front side
            glScalef(fence_post_width, fence_post_height, fence_post_depth)
            glutSolidCube(1)  # Draw a fence post
            glPopMatrix()

            for height_offset in [-(fence_post_height / 4), +(fence_post_height / 4)]:
                if x == x_min:
                    horizontal_offset = post_spacing / 2
                elif 0 <= x_max - x <= post_spacing:
                    horizontal_offset = -(post_spacing / 2)
                else:
                    horizontal_offset = 0

                glPushMatrix()
                glTranslatef(x + horizontal_offset, height_offset, z_min - 1.5*fence_post_depth)  # Position along the back side
                glRotatef(90, 1, 0, 0)
                # glRotatef(90, 0, 0, 1)
                glScalef(post_spacing, fence_post_width, fence_post_depth)
                glutSolidCube(1)  # Draw a fence post - vertical
                glPopMatrix()

            # Back side (z = 100)
            glPushMatrix()
            glTranslatef(x, 0, z_max + 1.5*fence_post_depth)  # Position along the back side
            glScalef(fence_post_width, fence_post_height, fence_post_depth)
            glutSolidCube(1)  # Draw a fence post - vertical
            glPopMatrix()

            for height_offset in [-(fence_post_height / 4), +(fence_post_height / 4)]:
                if x == x_min:
                    horizontal_offset = post_spacing / 2
                elif 0 <= x_max - x <= post_spacing:
                    horizontal_offset = -(post_spacing / 2)
                else:
                    horizontal_offset = 0
                glPushMatrix()
                glTranslatef(x + horizontal_offset, height_offset, z_max + 1.5*fence_post_depth)  # Position along the back side
                glRotatef(90, 1, 0, 0)
                # glRotatef(90, 0, 0, 1)
                glScalef(post_spacing, fence_post_width, fence_post_depth)
                glutSolidCube(1)  # Draw a fence post - vertical
                glPopMatrix()

            x += post_spacing  # Increment the position by post_spacing

        # Left and right sides (along the x-axis)
        z = z_min
        while z <= z_max:

            # Left side (x = 0)
            glPushMatrix()
            glTranslatef(x_min - 1.5*fence_post_depth, 0, z)  # Position along the left side
            glRotatef(90, 0, 1, 0)
            glScalef(fence_post_width, fence_post_height, fence_post_depth)
            glutSolidCube(1)  # Draw a fence post
            glPopMatrix()

            for height_offset in [-(fence_post_height / 4), +(fence_post_height / 4)]:
                if z == z_min:
                    horizontal_offset = post_spacing / 2
                elif 0 <= z_max - z <= post_spacing:
                    horizontal_offset = -(post_spacing / 2)
                else:
                    horizontal_offset = 0
                glPushMatrix()
                glTranslatef(x_min - 1.5*fence_post_depth, height_offset, z + horizontal_offset)  # Position along the back side
                glRotatef(90, 0, 0, 1)
                glRotatef(90, 0, 1, 0)
                # glRotatef(90, 0, 0, 1)
                glScalef(post_spacing, fence_post_width, fence_post_depth)
                glutSolidCube(1)  # Draw a fence post - vertical
                glPopMatrix()

            # Right side (x = 200)
            glPushMatrix()
            glTranslatef(x_max + 1.5*fence_post_depth, 0, z)  # Position along the right side
            glRotatef(90, 0, 1, 0)
            glScalef(fence_post_width, fence_post_height, fence_post_depth)
            glutSolidCube(1)  # Draw a fence post
            glPopMatrix()

            for height_offset in [-(fence_post_height / 4), +(fence_post_height / 4)]:
                if z == z_min:
                    horizontal_offset = post_spacing / 2
                elif 0 <= z_max - z <= post_spacing:
                    horizontal_offset = -(post_spacing / 2)
                else:
                    horizontal_offset = 0
                glPushMatrix()
                glTranslatef(x_max + 1.5*fence_post_depth, height_offset, z + horizontal_offset)  # Position along the back side
                glRotatef(90, 0, 0, 1)
                glRotatef(90, 0, 1, 0)
                # glRotatef(90, 0, 0, 1)
                glScalef(post_spacing, fence_post_width, fence_post_depth)
                glutSolidCube(1)  # Draw a fence post - vertical
                glPopMatrix()

            z += post_spacing  # Increment the position by post_spacing


class Pollen: 
    def __init__(self, radius:float, color:tuple, pollen_id:int, initial_x:float, initial_y:float, initial_z:float):
        self.x_pos, self.initial_x = initial_x, initial_x
        self.y_pos, self.initial_y = initial_y, initial_y
        self.z_pos, self.initial_z = initial_z, initial_z
        self.pollen_id = pollen_id
        self.color = color 
        self.radius = radius

        self.carried = False 
        self.in_beehive = False
        self.falling = False


    def draw_pollen(self):
        if self.in_beehive:
            # should not render at all
            pass 
        elif self.carried:
            # offset from the bee's current position 
            pass 
        elif self.falling:
            # should keep falling until hits the ground --> go to spawn location 
            pass 
        else:
            # go to spawn position 
            pass
        glPushMatrix()
        glColor3f(*self.color)
        glTranslatef(self.x_pos, self.y_pos, self.z_pos)
        glutSolidSphere(self.radius, 6, 6)
        glPopMatrix()



class Moth: 
    def __init__(   self, moth_id:int, 
                    initial_x:float, initial_y:float, initial_z:float, 
                    target_positions:list ):
        # where the next target point is, current position, the spawn position
        self.current_x_pos, self.initial_x = initial_x, initial_x
        self.current_y_pos, self.initial_y = initial_y, initial_y
        self.current_z_pos, self.initial_z = initial_z, initial_z

        self.target_positions = target_positions
        self.current_target_index = 0
        self.target_x_pos = target_positions[0][0]
        self.target_y_pos = target_positions[0][1]
        self.target_z_pos = target_positions[0][2]

        self.moth_id = moth_id

        self.orangeish = (179/255, 125/255, 18/255)
        self.brown = (119/255, 80/255, 0/255)
        self.mud = (88/255, 72/255, 41/255)
        self.black = (0, 0, 0)
        self.white = (1, 1, 1)

        self.head_color, self.thorax_color, self.abdomen_color = self.brown, self.orangeish, self.brown, 

        self.wing_color = self.mud
        self.leg_color = self.black
        self.antenna_color = self.black

        self.health = 100
        self.max_health = 100

        self.move_speed = 0.05 
        self.anim_speed = 1

        self.wing_speed = 0.01
        self.wing_range = 20
        self.wing_angle = 0 

        self.leg_angle = 0
        self.leg_speed = 1
        self.leg_range = 1.1

        self.paused = False 

        self.draw_moth()


    
    # update the animation parameters 
    def update_animations(self):
        if self.paused:
            return 
        # wing flapping (using sine wave for smooth back-and-forth movement)
        self.wing_angle = min(-math.sin(pygame.time.get_ticks() * self.wing_speed * self.anim_speed) * self.wing_range, 
                              math.sin(pygame.time.get_ticks() * self.wing_speed * self.anim_speed) * self.wing_range)  # Adjust speed and range
        
        # leg swinging (similar sine wave motion for a pendulum-like effect)
        self.leg_angle = math.sin(pygame.time.get_ticks() * self.leg_speed * self.anim_speed) * self.leg_range  # Adjust speed and range
    

    def draw_moth(self):
        if self.health <= 0:
            # if dead, don't render 
            pass 

        self.update_animations()

        glPushMatrix()
        # check if we are already at the target positions 
        current_target = (self.target_x_pos, self.target_y_pos, self.target_z_pos)
        current_pos = (self.current_x_pos, self.current_y_pos, self.current_z_pos)
        spawn_point = (self.initial_x, self.initial_y, self.initial_z)
        if np.abs(current_pos[0] - current_target[0]) <= 1 and \
            np.abs(current_pos[1] - current_target[1]) <= 1 and \
            np.abs(current_pos[2] - current_target[2]) <= 1:
            # get the next target position in the list 
            new_target = self.target_positions[(self.target_positions.index(current_target) + 1) % len(self.target_positions)]
            print(f"--hit a target points...new target point is {new_target}")
            self.target_x_pos, self.target_y_pos, self.target_z_pos = new_target[0], new_target[1], new_target[2]
        # elif current_target == spawn_point:
        #     # make it to the first spawn positions 
        # Smoothly move the moth towards the target position (you can adjust the speed) 
        dx, dy, dz = 0, 0, 0
        if not (np.abs(current_pos[0] - current_target[0]) <= 1): 
            if current_pos[0] < current_target[0]: dx = 1
            else: dx = -1
            self.current_x_pos += dx * self.move_speed
        if not (np.abs(current_pos[1] - current_target[1]) <= 1): 
            if current_pos[1] < current_target[1]: dy = 1
            else: dy = -1
            self.current_y_pos += dy * self.move_speed
        if not (np.abs(current_pos[2] - current_target[2]) <= 1): 
            if current_pos[2] < current_target[2]: dz = 1
            else: dz = -1
            self.current_z_pos += dz * self.move_speed

        # face_direction_norm = [float(i)/max(face_direction) for i in face_direction]
        yaw = math.degrees(math.atan2(dx, dz))
        h = math.hypot(dx, dz)
        pitch = math.degrees(math.atan2(dy, h))

        glTranslatef(self.current_x_pos, self.current_y_pos, self.current_z_pos)
        glRotatef(yaw,   0, 1, 0)
        # glRotatef(pitch, 1, 0, 0)

        glScalef(3, 3, 3)

        # ---- BODY ----
        #
        glColor3f(*self.head_color)
        # Head
        glPushMatrix()
        glTranslatef(0, 0, 0.5)
        glutSolidSphere(0.3, 16, 16)

        for offset in [-0.1, 0.1]:
            glPushMatrix()
            glColor3f(*self.black)
            glTranslate(offset, 0, 0.28)
            glutSolidSphere(0.05, 16, 16)
            glColor3f(*self.white)
            glTranslate(0, 0, 0.033)
            glutSolidSphere(0.025, 16, 16)
            glPopMatrix()
        glPopMatrix()

        # Thorax
        glPushMatrix()
        glColor3f(*self.thorax_color)
        glTranslatef(0, 0, 0)
        glScalef(0.5, 0.5, 0.7)
        glutSolidSphere(0.5, 16, 16)
        glPopMatrix()

        # Abdomen
        glPushMatrix()
        glColor3f(*self.abdomen_color)
        glTranslatef(0, 0, -0.8)
        glScalef(0.4, 0.4, 1.0)
        glutSolidSphere(0.5, 16, 16)
        glPopMatrix()

        #
        # ---- WINGS ----
        # glPushMatrix() 
        # glColor3f(*wing_grey_color)    # light grey 
        # glTranslatef(-dist_from_center_line, dist_to_line_up_above_bee, 0.0)
        # glTranslatef(1, 0, 0)
        # glRotatef(self.wing_angle, 0, 0, 1)  # Flap the left wing
        # glTranslatef(-1, 0, 0)
        # glScalef(scale_wing_length, scale_wing_thickness, scale_wing_width)     # flatten
        # glutSolidCube(1)
        # glPopMatrix()

        glColor3f(*self.wing_color)
        # Right wing
        glPushMatrix()
        glTranslatef(0.4, -0.1, 0)

        # for animation: 
        glTranslatef(-1, 0, 0)
        glRotatef(-self.wing_angle, 0, 0, 1)  # Flap the wing
        glTranslatef(1, 0, 0)

        glScalef(1, 0.05, 0.55)
        glutSolidCube(1.0)
        glPopMatrix()

        # Left wing
        glPushMatrix()
        glTranslatef(-0.4, -0.1, 0)

        # for animation: 
        glTranslatef(1, 0, 0)
        glRotatef(self.wing_angle, 0, 0, 1)  # Flap the wing
        glTranslatef(-1, 0, 0)

        glScalef(1.5, 0.05, 0.55)
        glutSolidCube(1.0)
        glPopMatrix()

        #
        # ---- LEGS (3 per side) ----
        #
        glColor3f(*self.leg_color)
        for side in (-0.5, 0.5):
            for i in range(3):
                z_off = 0.3 - i * 0.3
                glPushMatrix()
                glTranslatef(side * 0.3, -0.1, z_off)
                # for animation later: glRotatef(self.leg_angle * side, 1,0,0)
                glTranslatef(0, -0.3, 0)
                glScalef(0.05, 0.6, 0.05)
                glutSolidCube(1.0)
                glPopMatrix()

        #
        # ---- ANTENNAE ----
        #
        glColor3f(*self.antenna_color)
        for side in (-1, 1):
            glPushMatrix()
            glTranslatef(side * 0.15, 0.25, 0.7)
            glRotatef(60 * side, 0,1,0)
            glScalef(0.05, 0.05, 0.5)
            glutSolidCube(1.0)
            glPopMatrix()

        glPopMatrix()





class Camera:
    def __init__(self, view_mode = "corner1"):
        self.view_mode = view_mode
        # camera parameters
        self.eye_pos = np.array([0.0, 50.0, 100.0]) 
        self.look_at = np.array([100.0, 10.0, 0.0])
        self.view_up = np.array([0.0, 1.0, 0.0])

        # viewing parameters adjustable by keyboard input
        self.tilt_angle_horizontal = 0.0 # the angle (degrees) to rotate the gaze vector to the left or right
        self.tilt_angle_vertical = 0.0 # the angle (degrees) to rotate the gaze vector upward or downward
        self.zoom_distance = 0.0 # camera forward/backward distance along the gaze vector, positive or negative
        self.okay_to_change_eye_pos = False

    # Helper Function - to reset any horizontal or vertical tilts done in the previous view 
    def reset_views(self):
        self.tilt_angle_vertical = 0.0
        self.tilt_angle_horizontal = 0.0
        self.zoom_distance = 0.0

    # Task 7: Switch between 3 standard view modes: front, side, and back
    #               For each view mode, pre-define camera parameters here 
    def switch_view(self):
        # Switch the current view_mode to the next in the cycle: 
        #   front -> side -> back -> (first_person) -> front -> side -> ...
        view_modes = ["corner1", "corner2", "corner3", "corner4", "first-person", "follow"]
        self.view_mode = view_modes[(view_modes.index(self.view_mode) + 1) % len(view_modes)]

        
        # corner1 view
        if self.view_mode == "corner1":
            self.eye_pos = np.array([0.0, 50.0, 100.0]) 
            self.look_at = np.array([100.0, 10.0, 0.0])
            self.view_up = np.array([0.0, 1.0, 0.0])
        # corner2 view
        elif self.view_mode == "corner2":
            self.eye_pos = np.array([200.0, 50.0, 100.0]) 
            self.look_at = np.array([100.0, 10.0, 0.0])
            self.view_up = np.array([0.0, 1.0, 0.0])
        # corner3 view
        elif self.view_mode == "corner3":
            self.eye_pos = np.array([200.0, 50.0, -100.0]) 
            self.look_at = np.array([100.0, 10.0, 0.0])
            self.view_up = np.array([0.0, 1.0, 0.0])
        # corner4 view
        elif self.view_mode == "corner4":
            self.eye_pos = np.array([0.0, 50.0, -100.0]) 
            self.look_at = np.array([100.0, 10.0, 0.0])
            self.view_up = np.array([0.0, 1.0, 0.0])
        # follow view 
        elif self.view_mode == "follow":
            pass
        # first person view 
        elif self.view_mode == "first-person":
            pass
        
        print(f"Camera View: {self.view_mode}")
        
        
    # Helper Function for Extra Credit First-Person View 
    #   Takes in a playerBee object and uses its information to determine the 
    #   new eye position and look at point of the camera
    def update_fpv(self, playerBee: Bee, follow: bool):
        # calculate the current position of the playerBee's head 
        if follow:
            head_position = np.array([0.0, 30 + playerBee.height_offset, -45])    
        else:
            head_position = np.array([0.0, 10 + playerBee.height_offset, 5])    
        # head_position = rotate_vector(head_position, playerBee.head_angle, "Y")     # rotation 1 - head angle (i, o controls)
        head_position = rotate_vector(head_position, playerBee.walk_angle, "Y")     # rotation 2 - walk angle (<-, -> controls)
        head_position += playerBee.walk_vector  # translate based on current walk vector
        new_eye_pos = head_position            


        # calculate the new look at point of the camera by looking at
        if follow:
            base_gaze = np.array([0.0, -0.3, 0.7])
        else:
            base_gaze = np.array([0.0, 0.0, 1.0])       # let's start at a gaze of down the positive z-axis
        # base_gaze = rotate_vector(base_gaze, playerBee.head_angle, "Y")     # rotation 1 - head angle " "
        base_gaze = rotate_vector(base_gaze, playerBee.walk_angle, "Y")     # rotation 2 - walk angle " "
        new_lookat = new_eye_pos + base_gaze * 2    # extend along the gaze so the lookat point is not stuck inside the head

        return new_eye_pos, new_lookat




    # Task 8: Update camera parameters (eye_pos and look_at) based on the new 
    #               tilt_angle_horizontal, tilt_angle_vertical, and zoom_distance updated by key input (A, D, W, S, Q, E)
    def update_view(self, playerBee):
        # if in first-person view, we update the view based on the playerBee's direction
        if self.view_mode in ["first-person", "follow"]:
            if self.view_mode == "follow": follow = True 
            else: follow = False
            # we handle this in a separate function 
            new_eye_pos, new_lookat = self.update_fpv(playerBee, follow=follow)
        # if in any of the third-person views, we update the view based on keyboard input
        else:
            # calculate the current gaze vector
            base_gaze = self.look_at - self.eye_pos

            # temp for title angle vertical 
            new_title_angle_vertical = self.tilt_angle_vertical

            # axis to rotate on for vertical movements 
            vert_tilt_axis = "X"
            # if in side view, change the rotation axis and negate the degrees
            if self.view_mode == "side":
                vert_tilt_axis = "Z"
                new_title_angle_vertical = self.tilt_angle_vertical * -1
        
            # tilt vertically
            rotated_gaze = rotate_vector(base_gaze, new_title_angle_vertical, vert_tilt_axis)

            # tilt horizontally
            rotated_gaze = rotate_vector(rotated_gaze, self.tilt_angle_horizontal, "Y")

            new_lookat = self.eye_pos + rotated_gaze 

            ## calculate new eye position by moving the camera along the gaze vector by zoom_distance
            # calculate the unit vector of the current gaze vector
            unit_rotated_gaze = rotated_gaze / np.linalg.norm(rotated_gaze)

            # calculate the new eye_position
            new_eye_pos = self.eye_pos + unit_rotated_gaze * self.zoom_distance

            # move the rotated look at point along the same amount as the eye position
            new_lookat = new_lookat + unit_rotated_gaze * self.zoom_distance

        # return new eye position and look-at point
        return new_eye_pos, new_lookat

