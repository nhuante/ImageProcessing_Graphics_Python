import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import numpy as np
import math 
import random 
from beeGame_collisions import draw_AABB, collisionTest_AABBs
from beeGame_sceneObjects import read_object_positions_file

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
def rotate_vector(vector, angle_degrees, rot_axis = "Y", custom_axis:tuple=()):
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

    if rot_axis == "CUSTOM" and custom_axis != tuple():
        # ensure unit length
        u = custom_axis / np.linalg.norm(custom_axis)
        ux, uy, uz = u
        # Rodrigues' rotation formula components
        K = np.array([[   0, -uz,  uy],
                      [ uz,   0, -ux],
                      [-uy,  ux,   0]])
        I = np.eye(3)
        R = I*cosine_theta + (1-cosine_theta)*np.outer(u,u) + K*sin_theta
        return R.dot(vector)

    return rotated_vector


class Bee:
    def __init__(self):
        # ---------------- FLYING ANIMATION VARIABLES -------------------
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

        self.pupil_x_offset = 0        # pupil animation parameters
        self.pupil_speed = 0.01
        self.pupil_range_x = 0.27
        self.pupil_range_y = 0.35
        self.pupil_move_timer = 0 
        self.pupil_position = [0, 0]
        self.pupil_target = [0, 0]
        self.pupil_pause_time = random.randint(2000, 3000)  # Random pause time (in milliseconds)
        self.last_pupil_change_time = pygame.time.get_ticks()  # Last time the pupil changed position

        # ---------------- FLYING MOVEMENT VARIABLES -------------------
        self.current_position = ()              # will always hold the bee's current (x, y, z) position

        # freeform movement motion parameters
        self.walk_direction = np.array([0.0, 0.0, 1.0])                 # unit vector; initially aligned with z-axis ()
        self.walk_angle = 0.0                                           # the angle (degrees) between the walk_direction and the z-axis [0, 0, 1] ()
        
        self.walk_speed_mp = 0.7                                                # used for debugging to find the best flying speed
        self.walking_speed = 1.3                                                
        self.walk_speed = self.walk_speed_mp * self.walking_speed       # flying speed of bee

        self.walk_vector = np.array([100.0, 10.0, 0.0])                 # = walk_speed * walk_direction; updated for every iteration to translate the playerBee during walking ()
        self.height_offset = 0.0                                        # how much to initially offset the bee above the y-plane

        self.actively_moving = False
        self.in_reverse = False

        # turning speed 
        self.normal_turn_speed = 3
        self.angry_turn_speed = 6

        # ---------------- PAUSED TRACKER -------------------
        # game controls 
        self.paused = False

        # ---------------- ANGRY MODE VARIABLES -------------------
        # angry mode 
        self.angry_bee_mode = False
        self.angry_mode_start_time = 0              # time angry mode period begins
        self.angry_mode_length = 1000 * 5           # replace the 5 with num of seconds desired

        self.recharge_start_time = 0                # time recharging period begins
        self.is_recharging = False                  # if currently recharging  
        self.recharge_length = 1000 * 10            # replace the 5 with num of seconds desired

        self.current_countdown_num = -1

        # ---------------- TIMER/COUNTDOWNS VARIABLES -------------------
        # timer when paused var 
        self.temp_time_ran_for_pause = 0        # (for angry or recharging mode)
        self.temp_game_time_ran_for_pause = 0   # (for overall game time to play)

        # game timer
        self.initial_game_timer = 1000 * 120        # in-game timer - replace the 5 with num of seconds desired
        self.game_time_to_win = 1000 * 120       
        self.level_timer_start_time = 0

        # ---------------- GAME STATS VARIABLES -------------------
        self.score = 0                               # in-game score count
        self.level = 1                               # in-game level
        self.health_percentage = 100                 # in-game health bar

        # ---------------- POLLEN INTERACTION VARIABLES -------------------
        self.carrying_pollen = None 
        self.leg_carrying_pollen = False




    # resets the bee to be placed at it's spawn point and movement parameters to their starting values
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

        time_ran = current_time - self.level_timer_start_time
        self.temp_game_time_ran_for_pause = time_ran
             
        
    # continuously called to handle pausing (to maintain angry or countdown modes)
    def maintain_countdown_timers_when_paused(self):
        current_time = pygame.time.get_ticks() 
        # if angry, update the angry start time to maintain the time ran 
        if self.angry_bee_mode:
            self.angry_mode_start_time = current_time - self.temp_time_ran_for_pause
        # if recharging, update the recharge start time to maintain the time ran 
        elif self.is_recharging:
            self.recharge_start_time = current_time - self.temp_time_ran_for_pause
        # always maintain the overall level timer 
        self.level_timer_start_time = current_time - self.temp_game_time_ran_for_pause


    # Update bee's walk_direction and walk_vector based on walk_angle changed by key input
    #   - only allows the bee to update it's walk_vector in the proposed direction IF if will not 
    #       collide with any obstacle as a result
    def update_walk_vector(self, reverse, boundaries, obstacles):
        # rotate current walk vector by walk angle 
        rotated_direction = rotate_vector(self.walk_direction, self.walk_angle, rot_axis="Y")
        # print("walk direction:", rotated_direction)   # for testing

        # update walk vector 
        if reverse:
            potent_walk_vector = self.walk_vector - (self.walk_speed * rotated_direction)
            # potent_in_reverse = True
        else:
            potent_walk_vector = self.walk_vector + (self.walk_speed * rotated_direction)
            # potent_in_reverse = False

        for i in range(3):
            # attempted_walk_vector_value = self.walk_vector[i]
            min_value = boundaries[i][0]
            max_value = boundaries[i][1]
            potent_walk_vector[i] = max(min(potent_walk_vector[i], max_value), min_value)
        # print("walk vecctor:", self.walk_vector)      # for testing


        # constrain to the garden's boundaries 
        # boundaries = [ (x_min, x_max), (y_min, y_max), (z_min, z_max)]
        current_pos = (potent_walk_vector[0], potent_walk_vector[1] + self.height_offset, potent_walk_vector[2])
        # current_pos = (self.walk_vector[0], self.walk_vector[1] + self.height_offset, self.walk_vector[2])
        distance = 1.9
        for i in range(3):
            # check if moving to desired x position is valid or if colliding with props 
            # direction = np.sign(self.walk_direction[i])
            # potent_pos = current_pos[i] + (direction * self.walking_speed)
            potent_new_walk_vector = list(current_pos)
            potent_new_walk_vector[i] = potent_walk_vector[i]
            # get the potential next bounding box 
            minc = (potent_new_walk_vector[0] - distance,
                    potent_new_walk_vector[1] - distance,
                    potent_new_walk_vector[2] - distance)
            maxc = (potent_new_walk_vector[0] + distance,
                    potent_new_walk_vector[1] + distance,
                    potent_new_walk_vector[2] + distance)
            # check against each prop 
            blocked = False 
            for prop in obstacles:
                obstacle_min, obstacle_max = prop.get_bounding_volume() 
                if collisionTest_AABBs(minc, maxc, obstacle_min, obstacle_max):
                    blocked = True 
                    break 
            # if not blocked by any prop, allow movement to the desired x position 
            if not blocked:
                self.walk_vector[i] = potent_new_walk_vector[i]
        return True


    # Update bee's height_offset based on key input that is passed in
    #   - only allows the bee to update it's height_offset in the proposed direction IF if will not 
    #       collide with any obstacle as a result
    def update_height_offset(self, height_offset_per, garden_y_boundaries, obstacles):
        if height_offset_per != 0.0:
            # clamp proposed height offset to the garden boundaries 
            wanted = self.height_offset + height_offset_per
            wanted_offset = max(min(wanted, garden_y_boundaries[1]), garden_y_boundaries[0])

            # build the aabb box and check if 
            cx, cz = self.walk_vector[0], self.walk_vector[2]
            cy = self.walk_vector[1] + wanted_offset 
            collision_radius = 2
            minc = (cx - collision_radius, cy - collision_radius, cz - collision_radius)
            maxc = (cx + collision_radius, cy + collision_radius, cz + collision_radius)

            # test for collisions 
            blocked = False 
            for prop in obstacles:
                obstacle_min, obstacle_max = prop.get_bounding_volume() 
                if collisionTest_AABBs(minc, maxc, obstacle_min, obstacle_max):
                    blocked = True 
                    break 
            # if not blocked by any prop, allow movement to the desired x position 
            if not blocked:
                self.height_offset = wanted_offset
            

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
    

    # only called when the level starts 
    def start_level_timer(self):
        self.level_timer_start_time = pygame.time.get_ticks() 
        print(f"--Started Level Timer")


    # decreases the level timer 
    def handle_level_timer(self):
        current_time = pygame.time.get_ticks() 
        self.game_time_to_win = self.initial_game_timer - (current_time - self.level_timer_start_time)


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
    def draw_bee(self, draw_bounding_boxes=False): 
        # color variables 
        black_color = (0, 0, 0)
        white_color = (1, 1, 1)
        eye_grey_color = (224/255, 224/255, 224/255)
        wing_grey_color = (0.7, 0.7, 0.7)
        blue_iris_color = (51/255,153/255,255/255)
        eye_red_color = (204/255, 0, 0)
        red_iris_color = (153/255, 0, 0)
        body_grey_color = (0.541, 0.541, 0.525)

        collision_zone = (2, 2, 2)
        min_coords = ((self.walk_vector[0] - collision_zone[0]), 
                      (self.walk_vector[1] + self.height_offset - collision_zone[1]), 
                      (self.walk_vector[2] - collision_zone[2]))
        
        max_coords = ((self.walk_vector[0] + collision_zone[0]), 
                      (self.walk_vector[1] + self.height_offset + collision_zone[1]), 
                      (self.walk_vector[2] + collision_zone[2]))


        glClearColor(0, 0, 0, 1)                                                # set background RGBA color 
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)                        # clear the buffers initialized in the display mode

        # configure quatratic drawing [$1,470]
        quadratic = gluNewQuadric()
        gluQuadricDrawStyle(quadratic, GLU_FILL)  

        if draw_bounding_boxes:
            draw_AABB(min_coords, max_coords,  
                    (self.walk_vector[0], 
                    self.walk_vector[1] + self.height_offset, 
                    self.walk_vector[2]))

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
        if self.angry_bee_mode:
            glColor3f(*red_iris_color)
        elif self.is_recharging:
            glColor3f(*body_grey_color)
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
            if self.carrying_pollen:
                carry_angle = 8 
                glRotatef(carry_angle, 0, 0, 1)
                if i == 0: glRotatef(-carry_angle, 1, 0, 0)
                elif i == 2: glRotatef(carry_angle, 1, 0, 0)
            elif not self.actively_moving: 
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
            if self.carrying_pollen:
                carry_angle = -8 
                glRotatef(carry_angle, 0, 0, 1)
                if i == 0: glRotatef(carry_angle, 1, 0, 0)
                elif i == 2: glRotatef(-carry_angle, 1, 0, 0)
            elif not self.actively_moving: 
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
    

    # gets the bounding volume of the bee 
    def get_bounding_volume(self, d=2.0 ):
        # position of bee’s center:
        x = self.walk_vector[0]
        y = self.walk_vector[1] + self.height_offset
        z = self.walk_vector[2]
        # half‐extent (tweak as needed for tighter/looser fit)
        # d = 2.0
        return (x-d, y-d, z-d), (x+d, y+d, z+d)

    # create fence geometry 
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




class Flower:
    def __init__(self, x, y, z, stem_height=2.0, stem_thickness=0.1,
                 petal_size=0.4, petal_thickness=0.05,
                 head_size=0.2, scale=(1, 1, 1)):
        # flower position and dimensions variables
        self.pos = (x, y, z)
        self.stem_height = stem_height
        self.stem_thickness = stem_thickness
        self.petal_size = petal_size
        self.petal_thickness = petal_thickness
        self.head_size = head_size
        self.scale = scale

        # colors
        self.stem_col = (0.0, 0.6, 0.0)          # green
        self.petal_col = (0.4, 0.0, 0.4)         # dark purple
        self.head_col  = (1.0, 1.0, 0.0)         # yellow

    def draw(self, show_bounding_box:bool):
        # draw the bounding box if show_bounding_box is toggled on
        mins, maxs = self.get_bounding_volume()
        if show_bounding_box:
            cx = (mins[0] + maxs[0]) / 2
            cy = (mins[1] + maxs[1]) / 2
            cz = (mins[2] + maxs[2]) / 2
            draw_AABB(mins, maxs, 
                      center=(cx, cy, cz))

        glPushMatrix()
        # move the entire flower to be flush with the ground and at it's xz-position in the garden
        glTranslatef(self.pos[0], ((self.stem_height * self.scale[1]) / 2) + self.pos[1], self.pos[2])
        # scales the entire flower
        glScalef(*self.scale)

        # 1) Stem
        glPushMatrix()
        glColor3f(*self.stem_col)
        glScalef(self.stem_thickness, self.stem_height, self.stem_thickness)
        glutSolidCube(1.0)
        glPopMatrix()

        # 2) Petals (4 flat cubes around the top of the stem)
        petal_offset = self.stem_height/2 + self.petal_thickness/2
        for angle in (0, 90, 180, 270):
            glPushMatrix()
            glColor3f(*self.petal_col)
            glRotatef(angle, 0,1,0)
            glTranslatef(0, petal_offset, self.petal_size/2 + self.stem_thickness/2)
            glScalef(self.petal_size, self.petal_thickness, self.petal_size)
            glutSolidCube(1.0)
            glPopMatrix()

        # 3) Pollen head
        glPushMatrix()
        glColor3f(*self.head_col)
        glTranslatef(0, self.stem_height/2 + self.head_size/2, 0)
        glScalef(self.head_size, 0.75, self.head_size)
        glutSolidCube(1.0)
        glPopMatrix()

        glPopMatrix()

    def get_bounding_volume(self):
        sx, sy, sz = self.scale 
        half_width = (self.stem_thickness * sx) / 2.0 
        height = self.stem_height * sy 
        px, py, pz = self.pos 

        mins = (    px - half_width, 
                    py, 
                    pz - half_width )
        maxs = (    px + half_width, 
                    py + height, 
                    pz + half_width )
        
        return mins, maxs




# this is the master create flowers function 
#   - here you can change the scalings, offset off the z-plane, and rotation of the flowers 
#   - this will read in the cached positions from two files (if an error occurs will re-generate some and write those to the files)
#       and then return the Flower objects and positions
def create_flowers(num_flowers:int, force_regenerate:bool):
    scalings = [(1, 1, 1), (2.5, 2.5, 2.5)]
    height = -12
    rotation = (0, 1, 0, 0)
    bv_type = "AABB"
    file_path_1 = "./beeGameFinal/crocusFlowers_positions.txt"
    file_path_2 = "./beeGameFinal/crocusFlowers_short_positions.txt"

    x_min, x_max, z_min, z_max = 15, 185, -85, 85

    all_objects, all_positions = [], []
    
    for index, file_path in enumerate([file_path_1, file_path_2]):
        # try to open the file and read in positions 
        need_to_create_file, positions_formatted, num_positions = read_object_positions_file(file_path)

        if num_positions != num_flowers//2:
            num_positions = num_flowers//2
            need_to_create_file = True
            print(f"--positions extracted doesn't match desired count...regenerating")
        if force_regenerate: 
            need_to_create_file = True 
            print(f"--force reset flowers...regenerating")

        # generate the objects 
        crocus_objects, positions = create_flowers_and_writeif(need_to_create_file=need_to_create_file, positions_formatted=positions_formatted, 
                                                num_positions=num_positions, path_of_file_to_write=file_path, 
                                                default_scaling=scalings[index], default_height=height, default_rotation=rotation, 
                                                default_bv_type=bv_type, 
                                                xz_boundaries=(x_min, x_max, z_min, z_max), 
                                                type_of_prop="CROCUS")
        all_objects += crocus_objects
        all_positions += positions
    
    return all_objects, all_positions


# helper function for create_flower()
#   - will take care of the I/O part and returns the positions of the flowers 
def create_flowers_and_writeif(need_to_create_file:bool, positions_formatted:list, num_positions:int, 
                               path_of_file_to_write:str, 
                               default_scaling:tuple, default_height:int, default_rotation:tuple,
                               default_bv_type:str, 
                               xz_boundaries:tuple, 
                               type_of_prop:str="default_prop_name"):
    # initialize our objects list 
    flower_objects = []
    positions = []

    stem_height = 70
    stem_thickness = 1.5
    petal_thickness = 1.25
    petal_size = 10
    head_size = 2


    # unpack arguments 
    x_min, x_max, z_min, z_max = xz_boundaries[0], xz_boundaries[1], xz_boundaries[2], xz_boundaries[3]
    length_along_z = z_max - z_min

    # if needed, generate random nums and write them to the file for next time                                                    
    if need_to_create_file: 
        object_positions_file = open(path_of_file_to_write, "w")
        for _ in range(num_positions):   
            # generate a random position on the xz-plane
            random_x_pos = random.random() * x_max
            random_z_pos = (random.random() * length_along_z) + z_min

            # generate it in the world 
            flower_objects.append(Flower(x=random_x_pos, y=default_height, z=random_z_pos, 
                                         stem_height=stem_height, stem_thickness=stem_thickness,
                                         petal_size=petal_size, petal_thickness=petal_thickness, 
                                         head_size=head_size, scale=default_scaling))
            # save it's position to the file 
            object_positions_file.write(f"{random_x_pos} {default_height} {random_z_pos} {default_rotation[0]} {default_rotation[1]} {default_rotation[2]} {default_rotation[3]} {default_scaling[0]} {default_scaling[1]} {default_scaling[2]} {default_bv_type}\n")
            if type_of_prop == "CROCUS": positions.append((random_x_pos, default_height, random_z_pos))
        object_positions_file.close() 
        print(f"--random positions generated for {type_of_prop} and written to file")
    # if no file creation needed, 
    #   consider the read in and formatted the positions from the file, just use them to populate 
    else: 
        for line in range(num_positions):
            # grab the nect object's position tuple
            current_object = positions_formatted[line]
            # print(f"--extracted line {line} as a tuple: {current_object}--")

            # unpack the tuple 
            pos_x = current_object[0]
            pos_y = current_object[1]
            pos_z = current_object[2]
            scaling = (current_object[7], current_object[8], current_object[9])
            # print("--extracted positions--")

            # generate it in the world 
            flower_objects.append(Flower(x=pos_x, y=pos_y, z=pos_z, 
                                         stem_height=stem_height, stem_thickness=stem_thickness,
                                         petal_size=petal_size, petal_thickness=petal_thickness, 
                                         head_size=head_size, scale=scaling))
            if type_of_prop == "CROCUS": positions.append((pos_x, pos_y, pos_z))
            print(f"--generated {type_of_prop} object from file's line {line} as a tuple: {current_object}--")
    return flower_objects, positions








class Pollen: 
    def __init__(self, radius:float, color:tuple, pollen_id:int, initial_x:float, initial_y:float, initial_z:float):
        self.pollen_id = pollen_id

        # position variables
        self.x_pos, self.initial_x = initial_x, initial_x
        self.y_pos, self.initial_y = initial_y, initial_y
        self.z_pos, self.initial_z = initial_z, initial_z

        # size and color
        self.color = color 
        self.radius = radius

        # pollen mode 
        self.carried = False 
        self.falling = False
        self.falling_difference = 0


    # resets to its spawn point (on top of its respective flower)
    def reset_pollen(self):
        self.carried = False 
        self.falling = False 
        self.falling_difference = 0 


    def draw_pollen(self, draw_bounding_boxes:bool, bee:Bee):
        if draw_bounding_boxes:
            minc, maxc = self.get_bounding_volume()
            draw_AABB(minc, maxc, center=(self.x_pos, self.y_pos, self.z_pos))

        if self.carried:                                    # carried by bee
            self.falling_difference = 0
            # offset from the bee's current position 
            self.x_pos = bee.walk_vector[0]
            self.y_pos = bee.walk_vector[1] + bee.height_offset - 5.5
            self.z_pos = bee.walk_vector[2]
        elif self.falling:                                  # falling or on ground
            self.falling_difference -= .1
            # should keep falling until hits the ground --> stays at the ground 
            self.y_pos = max(self.y_pos + self.falling_difference, -12)
            # print(f"---pollen falling, at position ({self.x_pos}, {self.y_pos}, {self.z_pos}")
        elif not self.carried and not self.falling:         # at spawn point
            self.falling_difference = 0
            # go to spawn position 
            self.x_pos = self.initial_x
            self.y_pos = self.initial_y
            self.z_pos = self.initial_z

        glPushMatrix()
        glColor3f(*self.color)
        glTranslatef(self.x_pos, self.y_pos, self.z_pos)
        glutSolidSphere(self.radius, 6, 6)
        glPopMatrix()

    def get_bounding_volume(self):
        min_x = self.x_pos - self.radius
        min_y = self.y_pos - self.radius
        min_z = self.z_pos - self.radius
        max_x = self.x_pos + self.radius
        max_y = self.y_pos + self.radius
        max_z = self.z_pos + self.radius
        return (min_x, min_y, min_z), (max_x, max_y, max_z)
    



class Moth: 
    def __init__(   self, moth_id:int, 
                    initial_x:float, initial_y:float, initial_z:float, 
                    target_positions:list ):
        # initial target position (just the first one in the list)
        self.target_positions = target_positions
        self.current_target_index = 0

        # initial location
        self.current_x_pos, self.initial_x, self.target_x_pos = target_positions[0][0], target_positions[0][0], target_positions[0][0]
        self.current_y_pos, self.initial_y, self.target_y_pos = target_positions[0][1], target_positions[0][1], target_positions[0][1]
        self.current_z_pos, self.initial_z, self.target_z_pos = target_positions[0][2], target_positions[0][2], target_positions[0][2]

        # id
        self.moth_id = moth_id

        # colors
        self.orangeish = (179/255, 125/255, 18/255)
        self.brown = (119/255, 80/255, 0/255)
        self.mud = (88/255, 72/255, 41/255)
        self.black = (0, 0, 0)
        self.white = (1, 1, 1)

        self.head_color, self.thorax_color, self.abdomen_color = self.brown, self.orangeish, self.brown, 

        self.wing_color = self.mud
        self.leg_color = self.black
        self.antenna_color = self.black

        # health stats (NOTE: not actually used at the moment)
        self.health = 100
        self.max_health = 100

        # move / animation speeds
        self.move_speed = 0.30 
        self.anim_speed = 1
        self.yaw = 0

        self.wing_speed = 0.01
        self.wing_range = 20
        self.wing_angle = 0 

        self.leg_angle = 0
        self.leg_speed = 1
        self.leg_range = 1.1

        # modes
        self.paused = False 
        self.chasing_bee = False



    
    # update the animation parameters 
    def update_animations(self):
        if self.paused:
            return 
        # wing flapping (using sine wave for smooth back-and-forth movement)
        self.wing_angle = min(-math.sin(pygame.time.get_ticks() * self.wing_speed * self.anim_speed) * self.wing_range, 
                              math.sin(pygame.time.get_ticks() * self.wing_speed * self.anim_speed) * self.wing_range)  # Adjust speed and range
        
        # leg swinging (similar sine wave motion for a pendulum-like effect)
        self.leg_angle = math.sin(pygame.time.get_ticks() * self.leg_speed * self.anim_speed) * self.leg_range  # Adjust speed and range
    

    # draw obv
    def draw_moth(self, bee:Bee, draw_bounding_boxes=False, obstacles:list=[]):
        # if dead, don't render 
        if self.health <= 0:
            return 

        # if not dead, first update flying animations 
        self.update_animations()

        glPushMatrix()
        # get the current position
        current_pos = (self.current_x_pos, self.current_y_pos, self.current_z_pos)

        # if following it's patrol route, check if the bee is in range to chase 
        if not self.chasing_bee:
            # check if bee is within range before we continue upon our path 
            if  np.abs(current_pos[0] - bee.walk_vector[0])                         <= 15 and \
                np.abs(current_pos[1] - (bee.walk_vector[1] + bee.height_offset))   <= 15 and \
                np.abs(current_pos[2] - bee.walk_vector[2])                         <= 15:
                self.chasing_bee = True

        # if bee is within range, follow the bee 
        if self.chasing_bee:
            current_target = (bee.walk_vector[0], bee.walk_vector[1] + bee.height_offset, bee.walk_vector[2])
            # NOTE: may add so it stop chasing you if out of range again here...tbd if i finish the project by friday 
        # if bee not within range, follow our patrol route 
        else:
            # check if we are already at the target positions 
            current_target = (self.target_x_pos, self.target_y_pos, self.target_z_pos)

        # collisision aabb zone 
        if self.chasing_bee: distance = 3 # if chasing, check if bee is within a radius of 3 cube 
        else: distance = 1  # if patrolling, check if next target point is within a radius of 1 cube 

        # get the min, max coords of the appropriate bounding box 
        min_coords = ((current_pos[0] - distance), (current_pos[1] - distance), (current_pos[2] - distance))
        max_coords = ((current_pos[0] + distance), (current_pos[1] + distance), (current_pos[2] + distance))

        # draw aabb box 
        if draw_bounding_boxes:
            draw_AABB(min_coords, max_coords, center=current_pos)

        # if collided with it's target positions (either the bee or the next checkpoint in it's patrol route)
        if  np.abs(current_pos[0] - current_target[0])  < distance and \
            np.abs(current_pos[1] - current_target[1])  < distance and \
            np.abs(current_pos[2] - current_target[2])  < distance:
            # if on the patrol path, go to the next target point 
            if not self.chasing_bee: 
                # get the next target position in the list 
                new_target = self.target_positions[(self.target_positions.index(current_target) + 1) % len(self.target_positions)]
                # print(f"--hit a target point...new target point is {new_target}")
                self.target_x_pos, self.target_y_pos, self.target_z_pos = new_target[0], new_target[1], new_target[2]
            # if chasing bee, this means we got close enough to the bee
            else:  
                print(f"--hit the bee...going back to spawn to patrol")
                # if bee was angry, we lose health, bee gets points 
                if bee.angry_bee_mode:
                    bee.score += 10
                    self.health -= 34
                    print(f"--bee health is now {self.health}")
                # if bee was not angry, bee loses health
                else:
                    bee.health_percentage -= 20

                # for all moth-bee collisions, moth is set back to its spawn point
                self.chasing_bee = False 
                self.target_x_pos = self.target_positions[0][0]
                self.target_y_pos = self.target_positions[0][1]
                self.target_z_pos = self.target_positions[0][2]

                self.current_x_pos = self.initial_x
                self.current_y_pos = self.initial_y
                self.current_z_pos = self.initial_z
                
        # if game is paused, no updates to the position or rotation of the moth 
        if not self.paused:
            # get the directions the moth is moving in (positive or negative) 
            dx, dy, dz = 0, 0, 0

            # 1. check if moving to desired x positions is valid or if colliding with props 
            if not (np.abs(current_pos[0] - current_target[0]) <= 1): 
                if current_pos[0] < current_target[0]: dx = 1
                else: dx = -1
            potent_x_pos = self.current_x_pos + (dx * self.move_speed)
            # get the potential next bounding box 
            distance_for_prop_collision = 1
            minc = (potent_x_pos - distance_for_prop_collision,
                    self.current_y_pos - distance_for_prop_collision,
                    self.current_z_pos - distance_for_prop_collision)
            maxc = (potent_x_pos + distance_for_prop_collision,
                    self.current_y_pos + distance_for_prop_collision,
                    self.current_z_pos + distance_for_prop_collision)
            draw_AABB(minc, maxc, center=current_pos, blueColor=True)
            # check against each prop 
            blocked = False 
            for prop in obstacles:
                obstacle_min, obstacle_max = prop.get_bounding_volume() 
                if collisionTest_AABBs(minc, maxc, obstacle_min, obstacle_max):
                    blocked = True 
                    break 
            # if not blocked by any prop, allow movement to the desired x position 
            if not blocked:
                self.current_x_pos = potent_x_pos


            # 2. check if moving to desired y position is valid or if colliding with props 
            if not (np.abs(current_pos[1] - current_target[1]) <= 1): 
                if current_pos[1] < current_target[1]: dy = 1
                else: dy = -1
            potent_y_pos = self.current_y_pos + (dy * self.move_speed)
            # get the potential next bounding box 
            minc = (self.current_x_pos - distance,
                    potent_y_pos - distance,
                    self.current_z_pos - distance)
            maxc = (self.current_x_pos + distance,
                    potent_y_pos + distance,
                    self.current_z_pos + distance)
            # check against each prop 
            blocked = False 
            for prop in obstacles:
                obstacle_min, obstacle_max = prop.get_bounding_volume() 
                if collisionTest_AABBs(minc, maxc, obstacle_min, obstacle_max):
                    blocked = True 
                    break 
            # if not blocked by any prop, allow movement to the desired x position 
            if not blocked:
                self.current_y_pos = potent_y_pos



            # 3. check if moving to desired x position is valid or if colliding with props 
            if not (np.abs(current_pos[2] - current_target[2]) <= 1): 
                if current_pos[2] < current_target[2]: dz = 1
                else: dz = -1
            potent_z_pos = self.current_z_pos + (dz * self.move_speed)
            # get the potential next bounding box 
            minc = (self.current_x_pos - distance,
                    self.current_y_pos - distance,
                    potent_z_pos - distance)
            maxc = (self.current_x_pos + distance,
                    self.current_y_pos + distance,
                    potent_z_pos + distance)
            # check against each prop 
            blocked = False 
            for prop in obstacles:
                obstacle_min, obstacle_max = prop.get_bounding_volume() 
                if collisionTest_AABBs(minc, maxc, obstacle_min, obstacle_max):
                    blocked = True 
                    break 
            # if not blocked by any prop, allow movement to the desired x position 
            if not blocked:
                self.current_z_pos = potent_z_pos

            # turns directions into angles 
            self.yaw = math.degrees(math.atan2(dx, dz))

        # rotate moth to face the correct direction and translate to correct position in the world 
        glTranslatef(self.current_x_pos, self.current_y_pos, self.current_z_pos)
        glRotatef(self.yaw,   0, 1, 0)
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

        
        # ---- WINGS ----
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

    # Switch between 3 standard view modes: front, side, and back
    #               For each view mode, pre-define camera parameters here 
    def switch_view(self):
        # Switch the current view_mode to the next in the cycle: 
        #   front -> side -> back -> (first_person) -> front -> side -> ...
        view_modes = ["corner1", "corner2", "corner3", "corner4", "first-person", "follow"]
        self.view_mode = view_modes[(view_modes.index(self.view_mode) + 1) % len(view_modes)]

        
        # corner1 view
        if self.view_mode == "corner1":
            self.eye_pos = np.array([-50.0, 50.0, 150.0]) 
            self.look_at = np.array([100.0, 10.0, 0.0])
            self.view_up = np.array([0.0, 1.0, 0.0])
        # corner2 view
        elif self.view_mode == "corner2":
            self.eye_pos = np.array([250.0, 50.0, 150.0]) 
            self.look_at = np.array([100.0, 10.0, 0.0])
            self.view_up = np.array([0.0, 1.0, 0.0])
        # corner3 view
        elif self.view_mode == "corner3":
            self.eye_pos = np.array([250.0, 50.0, -150.0]) 
            self.look_at = np.array([100.0, 10.0, 0.0])
            self.view_up = np.array([0.0, 1.0, 0.0])
        # corner4 view
        elif self.view_mode == "corner4":
            self.eye_pos = np.array([-50.0, 50.0, -150.0]) 
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




    # Update camera parameters (eye_pos and look_at) based on the new 
    #               tilt_angle_horizontal, tilt_angle_vertical, and zoom_distance updated by key input (A, D, W, S, Q, E)
    def update_view(self, playerBee):
        
        # if in first-person view, we update the view based on the playerBee's direction
        if self.view_mode in ["first-person", "follow"]:
            # we handle this in a separate function (follow the bee basically) 
            fpv_eye, fpv_look_at = self.update_fpv(playerBee, follow=(self.view_mode=="follow"))

            # using that new information, calc the current gaze vector
            gaze = fpv_look_at - fpv_eye

            # rotate it on its own right and up vectors 
            camera_right_axis = np.cross(self.view_up, gaze)
            camera_right_axis /= np.linalg.norm(camera_right_axis)

            gaze_after_pitch = rotate_vector(vector=gaze, angle_degrees=self.tilt_angle_vertical, 
                                            rot_axis="CUSTOM", custom_axis=camera_right_axis)
            
            final_gaze = rotate_vector(vector=gaze_after_pitch, angle_degrees=self.tilt_angle_horizontal, 
                                            rot_axis="CUSTOM", custom_axis=self.view_up)
            
            # calc new look at point
            new_lookat = fpv_eye + final_gaze

            return fpv_eye, new_lookat


        # if in any of the third-person views, we update the view based on keyboard input

        # calculate the current gaze vector
        starting_look_at, starting_eye_pos = self.look_at, self.eye_pos
        base_gaze = starting_look_at - starting_eye_pos

        # axis to rotate on for vertical movements 
        camera_right_axis = np.cross(self.view_up, base_gaze)
        camera_right_axis /= np.linalg.norm(camera_right_axis)
        # tilt vertically
        gaze_after_pitch = rotate_vector(vector=base_gaze, angle_degrees=self.tilt_angle_vertical, 
                                            rot_axis="CUSTOM", custom_axis=camera_right_axis)

        # tilt horizontally
        final_gaze = rotate_vector(vector=gaze_after_pitch, angle_degrees=self.tilt_angle_horizontal, 
                                            rot_axis="CUSTOM", custom_axis=self.view_up)

        new_lookat = self.eye_pos + final_gaze

        unit_rotated_gaze = final_gaze / np.linalg.norm(final_gaze)

        # calculate the new eye_position
        new_eye_pos = self.eye_pos + unit_rotated_gaze * self.zoom_distance

        # move the rotated look at point along the same amount as the eye position
        new_lookat = new_lookat + unit_rotated_gaze * self.zoom_distance

        # return new eye position and look-at point
        return new_eye_pos, new_lookat

