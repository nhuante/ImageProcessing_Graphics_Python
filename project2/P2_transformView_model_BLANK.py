import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import numpy as np

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


class Scarecrow:
    def __init__(self, version = "basic"):
        self.version = version 
        # Scarecrow body part dimensions, for both "basic" and "upgraded"
        self.head_sphere = 2.5 # radius
        self.nose_cylinder = [0.3, 0.0, 1.8] # base radius, top radius, height
        self.torso_cylinder = [2.5, 2.5, 10.0] # base radius, top radius, height
        # basic scarecrow
        self.leg_cylinder = [1.0, 1.0, 12.0] # base radius, top radius, height
        self.arm_cylinder = [1.0, 1.0, 10.0] # base radius, top radius, height
        # upgraded scarecrow
        self.upper_lower_leg_cylinder = [1.0, 1.0, 6.0] # base radius, top radius, height
        self.upper_lower_arm_cylinder = [1.0, 1.0, 5.0] # base radius, top radius, height
        self.joint_leg_sphere = 1.0 # radius
        self.joint_arm_sphere = 1.0 # radius
        self.hand_sphere = 1.1 # radius
        self.foot_cube = 1.5 # cube's side length
        
        # head/limb motion parameters (Task 4: Walk-in-place)
        self.head_angle = 0.0 # head rotation angle used in Task 2 ()
        self.arm_angle = 0.0 # arm rotation angle, with a range [-30,30], used for walk-in-place and freeform walking animations ()
        self.arm_direction = 1 # 1 for swinging backward (CCW), -1 for forward (CW)
        self.leg_angle = 0.0 # leg rotation angle, with a range [-30,30], used for walk-in-place and freeform walking animations ( )
        self.leg_direction = 1 # 1 for swinging backward (CCW), -1 for forward (CW)
        self.swing_speed = 1.0 # arm and leg swinging speed, delta angle to increase/decrease arm_angle and leg_angle each iteration ( )
        
        # walk motion parameters (Task 5: Straightline and Task 6: Freeform)
        self.walk_direction = np.array([0.0, 0.0, 1.0]) # unit vector; initially aligned with z-axis ()
        self.walk_angle = 0.0 # the angle (degrees) between the walk_direction and the z-axis [0, 0, 1] ()
        self.walk_speed_mp = 0.3
        self.walk_speed = self.walk_speed_mp * self.swing_speed # straightline and freeform walking speed ()
        self.walk_vector = np.array([0.0, 0.0, 0.0]) # = walk_speed * walk_direction; updated for every iteration to translate the scarecrow during walking ()
    
    # Resets the scarecrow to be placed at the origin and walking parameters to their starting values
    def resetToOrigin(self):
        self.walk_direction = np.array([0.0, 0.0, 1.0])
        self.walk_angle = 0.0 
        self.walk_vector = np.array([0.0, 0.0, 0.0])
    

    # Task 6 Use: Update Scarecrow's walk_direction and walk_vector based on walk_angle changed by key input
    def update_walk_vector(self):
        # rotate current walk vector by walk angle 
        rotated_direction = rotate_vector(self.walk_direction, self.walk_angle, rot_axis="Y")
        # print("walk direction:", rotated_direction)   # for testing

        # update walk vector 
        self.walk_vector += self.walk_speed * rotated_direction
        # print("walk vecctor:", self.walk_vector)      # for testing


    # Task 1 and Task 2
    # 1. Create a Basic Scarecrow
    # 2. Rotate its head and nose based on transformation parameters updated by key input
    # Body parts needed for the basic scarcrow have been created already
    #       you will need to transform them to approporate positions
    def draw_Scarecrow(self): 
        glClearColor(0, 0, 0, 1)                                                # set background RGBA color 
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)                        # clear the buffers initialized in the display mode

        # configure quatratic drawing
        quadratic = gluNewQuadric()
        gluQuadricDrawStyle(quadratic, GLU_FILL)  

        glPushMatrix() # DO NOT DELETE THIS

        #--------------Write your code below -------------------
 
        # Head (sphere: radius=2.5)
        glRotatef(self.head_angle, 0, 1, 0)
        glTranslatef(0, 12.5, 0)
        glColor3f(0.0, 1.0, 0.0)
        gluSphere(quadratic, self.head_sphere, 32, 32)

        # Nose (cylinder: base-radius=0.3, top-radius=0, length=1.8)
        glTranslatef(0, 0, 2.5)
        glColor3f(1.0, 0.0, 0.0)
        gluCylinder(quadratic, self.nose_cylinder[0], self.nose_cylinder[1], self.nose_cylinder[2], 32, 32)
        glPopMatrix() 

        # Torso (cylinder: radius=2.5, length=10)
        glPushMatrix()
        glRotatef(-90, 1, 0, 0)
        glColor3f(1.0, 1.0, 0.0)
        gluCylinder(quadratic, self.torso_cylinder[0], self.torso_cylinder[1], self.torso_cylinder[2], 32, 32)
        glPopMatrix()

        # Right Leg (cylinders: radius=1.0, length=12)
        glPushMatrix()
        glTranslatef(-1.2, -12, 0)
        glRotatef(-90, 1, 0, 0)
        glColor3f(1.0, 0.0, 0.0)
        gluCylinder(quadratic, self.leg_cylinder[0], self.leg_cylinder[1], self.leg_cylinder[2], 32, 32)
        glPopMatrix()
        # Left Leg (cylinders: radius=1.0, length=12)
        glPushMatrix()
        glTranslatef(1.2, -12, 0)
        glRotatef(-90, 1, 0, 0)
        glColor3f(1.0, 0.0, 0.0)
        gluCylinder(quadratic, self.leg_cylinder[0], self.leg_cylinder[1], self.leg_cylinder[2], 32, 32)
        glPopMatrix()

        # right Arm (cylinders: radius=1.0, length=10)
        glPushMatrix()
        glTranslatef(-12.5, 9, 0)
        glRotatef(90, 0, 1, 0)
        glColor3f(0.0, 0.0, 1.0)
        gluCylinder(quadratic, self.arm_cylinder[0], self.arm_cylinder[1], self.arm_cylinder[2], 32, 32)
        glPopMatrix()
        # left Arm (cylinders: radius=1.0, length=10)
        glPushMatrix()
        glTranslatef(12.5, 9, 0)
        glRotatef(-90, 0, 1, 0)
        glColor3f(0.0, 0.0, 1.0)
        glColor3f(0.0, 0.0, 1.0)
        gluCylinder(quadratic, self.arm_cylinder[0], self.arm_cylinder[1], self.arm_cylinder[2], 32, 32)

        #--------------Write your code above -------------------
        glPopMatrix() # DO NOT DELETE THIS


    # Task 3: Upgrade the Scarecrow with more joints 
    #       Task 4: Walk-in-place animation
    #       Task 5: Walk-in-straightline animation
    #       Task 6: Freeform walk animation with keyboard input
    # NOTE: Create a new Scarecrow with more joints, hands, and feet according to scene graph
    #       Use the given body part dimensions defined within __init__()
    #       Transform them in a cumulative manner 
    def draw_Scarecrow_Upgrade(self): 
        glClearColor(0, 0, 0, 1)                                                # set background RGBA color 
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)                        # clear the buffers initialized in the display mode

        # configure quatratic drawing
        quadratic = gluNewQuadric()
        gluQuadricDrawStyle(quadratic, GLU_FILL)  

        glPushMatrix() # DO NOT DELETE THIS

        #--------------Write your code below -------------------

        # modifications to the entire scarecrow

        # translate entire scarecrow by the walk vector 
        glTranslatef(self.walk_vector[0], self.walk_vector[1], self.walk_vector[2])
        # rotate the entire scarecrow to face the correct walking direction
        glRotatef(self.walk_angle, 0, 1, 0)

        glPushMatrix()
        glRotatef(self.head_angle, 0, 1, 0)     # rotate the head objects by the head angle
        # Head (sphere: radius=2.5)
        glTranslatef(0, 12.5, 0)                # translate 12.5 up along y-axis
        glColor3f(0.0, 1.0, 0.0)
        gluSphere(quadratic, self.head_sphere, 32, 32)  # create the head sphere

        # party hat cone
        glPushMatrix() 
        glColor3f(1.0, 0.0, 1.0)  
        glTranslatef(-2, 5, 0)                  # move hat to be on top of head sphere
        glRotatef(20, 0, 0, 1)                  # give it a silly tilt
        glRotatef(90, 1, 0, 0)                  # stand cone up 
        gluCylinder(quadratic, 0.0, 1.0, 3.0, 32, 32)   # create party cone
        glPopMatrix()

        # little pompom thing on top of the party hat
        glPushMatrix()      
        glColor3f(1.0, 1.0, 0.0)        
        glTranslatef(-2, 5.3, 0)                # move pom-pom to be on top of party cone
        gluSphere(quadratic, 0.5, 16, 16)       # create party hat pom-pom
        glPopMatrix()

        # Nose (cylinder: base-radius=0.3, top-radius=0, length=1.8)
        glTranslatef(0, 0, 2.5)             # translate 2.5 out along z-axis to stick out the head 
        glColor3f(1.0, 0.0, 0.0)
        gluCylinder(quadratic, self.nose_cylinder[0], self.nose_cylinder[1], self.nose_cylinder[2], 32, 32) # create the nose
        glPopMatrix()   

        # Torso (cylinder: radius=2.5, length=10)
        glPushMatrix()          
        glRotatef(-90, 1, 0, 0)             # stand torso up along y-axis
        glColor3f(1.0, 1.0, 0.0)
        gluCylinder(quadratic, self.torso_cylinder[0], self.torso_cylinder[1], self.torso_cylinder[2], 32, 32)  # create torso cylinder
        glPopMatrix()

        ''' left Leg (cylinders: radius=1.0, length=12) '''
        glPushMatrix()
        glTranslatef(-1.2, -6, 0)          # slide leg 6 down and 1.2 to the left (below the torso)

        glTranslatef(0, 6, 0)              # moving entire leg animation (translate to origin ^ rotate ^ translate back)
        glRotatef(self.leg_angle, 1, 0, 0)
        glTranslatef(0, -6, 0)

        glRotatef(90, 1, 0, 0)             # align entire limb with torso
        glColor3f(1.0, 0.0, 0.0)

        # upper left leg 
        glPushMatrix()
        glTranslatef(0, 0, -6)             # slide upper limb to extend off of lower limb
        gluCylinder(quadratic, self.upper_lower_leg_cylinder[0], self.upper_lower_leg_cylinder[1], self.upper_lower_leg_cylinder[2], 32, 32)    # create upper left leg
        glPopMatrix()

        # only swing lower leg more if behind the torso
        if (self.leg_angle >= 0): glRotatef(self.leg_angle, 1, 0, 0)    # extra rotation for lower limb animation 

        gluSphere(quadratic, self.upper_lower_leg_cylinder[1], 32, 32)  # create knee joint
        gluCylinder(quadratic, self.upper_lower_leg_cylinder[0], self.upper_lower_leg_cylinder[1], self.upper_lower_leg_cylinder[2], 32, 32)    # create lower left leg
       
        # left foot creation & scaling
        glTranslatef(0, 1, 6)
        glScalef(1, 1.8, 0.8)
        glColor3f(1.0, 1.0, 0.0)
        glutSolidCube(1.5)
        glPopMatrix()

        ''' right Leg (cylinders: radius=1.0, length=12) '''
        glPushMatrix()
        glTranslatef(1.2, -6, 0)            # slide leg 6 down and 1.2 to the right (below the torso)

        glTranslatef(0, 6, 0)               # moving entire leg animation (translate to origin ^ rotate ^ translate back)
        glRotatef(-self.leg_angle, 1, 0, 0)
        glTranslatef(0, -6, 0)

        glRotatef(90, 1, 0, 0)             # align entire limb with torso
        glColor3f(1.0, 0.0, 0.0)

        # upper right leg creation
        glPushMatrix()
        glTranslatef(0, 0, -6)              # slide upper limb to extend off of lower limb
        gluCylinder(quadratic, self.upper_lower_leg_cylinder[0], self.upper_lower_leg_cylinder[1], self.upper_lower_leg_cylinder[2], 32, 32)    # create upper right leg
        glPopMatrix()

        # only swing lower leg more if behind the torso
        if (self.leg_angle <= 0): glRotatef(-self.leg_angle, 1, 0, 0)    # extra rotation for lower limb animation 

        gluCylinder(quadratic, self.upper_lower_leg_cylinder[0], self.upper_lower_leg_cylinder[1], self.upper_lower_leg_cylinder[2], 32, 32)    # create lower right leg
        gluSphere(quadratic, self.upper_lower_leg_cylinder[1], 32, 32)  # create knee joint
        
        # right foot creation & scaling
        glTranslatef(0, 1, 6)
        glScalef(1, 1.8, 0.8)
        glColor3f(1.0, 1.0, 0.0)
        glutSolidCube(1.5)

        glPopMatrix()


        ''' right arm (cylinders: radius=1.0, length=10) '''
        glPushMatrix()
        glTranslatef(4, 5, 0)                   # slide entire arm limb to be at a normal arm location on the torso 
        glRotatef(15, 0, 0, 1)                  # rotate entire arm limb to have a 15 degree angle with y-axis
        
        glTranslatef(0, 5, 0)
        glRotatef(self.arm_angle, 1, 0, 0)      # moving entire arm animation (translate to origin ^ rotate ^ translate back)
        glTranslatef(0, -5, 0)

        glRotatef(90, 1, 0, 0)                  # align entire limb with torso
        glColor3f(0.0, 0.0, 1.0)

        glPushMatrix()
        glTranslatef(0, 0, -5)                  # slide upper right arm to extend off of lower right arm 
        gluCylinder(quadratic, self.upper_lower_arm_cylinder[0], self.upper_lower_arm_cylinder[1], self.upper_lower_arm_cylinder[2], 32, 32)    # create upper right arm
        glPopMatrix()
        
        # only swing lower arm more if in front of torso
        if (self.arm_angle <= 0): glRotatef(2 * self.arm_angle, 1, 0, 0)    # extra rotation for lower limb animation

        gluCylinder(quadratic, self.upper_lower_arm_cylinder[0], self.upper_lower_arm_cylinder[1], self.upper_lower_arm_cylinder[2], 32, 32)    # create lower right arm 
        gluSphere(quadratic, self.upper_lower_arm_cylinder[1], 32, 32)      # create elbow joint

        # right hand creation & sliding to place at the end of the lower right arm 
        glTranslatef(0, 0, 5)
        glColor3f(0.0, 1.0, 0.0)    
        gluSphere(quadratic, 1.1, 32, 32)                                  
        glPopMatrix()



        ''' left Arm (cylinders: radius=1.0, length=10) '''
        glPushMatrix()
        glTranslatef(-4, 5, 0)                  # slide entire arm limb to be at a normal arm location on the torso 
        glRotatef(-15, 0, 0, 1)                 # rotate entire arm limb to have a 15 degree angle with y-axis

        glTranslatef(0, 5, 0)
        glRotatef(-self.arm_angle, 1, 0, 0)      # moving arm animation (translate to origin ^ rotate ^ translate back)
        glTranslatef(0, -5, 0)


        glRotatef(90, 1, 0, 0)                  # align entire limb with torso
        glColor3f(0.0, 0.0, 1.0)

        glPushMatrix()    
        glTranslatef(0, 0, -5)                  # slide upper left arm to extend off of lower left arm 
        gluCylinder(quadratic, self.upper_lower_arm_cylinder[0], self.upper_lower_arm_cylinder[1], self.upper_lower_arm_cylinder[2], 32, 32)    # create upper left arm 
        glPopMatrix()

        # only swing lower arm more if in front of torso (when the right arm is behind the torso)
        if (self.arm_angle >= 0): glRotate(-2 * self.arm_angle, 1, 0, 0)    # extra rotation for lower limb animation
               
        gluSphere(quadratic, self.upper_lower_arm_cylinder[1], 32, 32)      # create knee joint
        gluCylinder(quadratic, self.upper_lower_arm_cylinder[0], self.upper_lower_arm_cylinder[1], self.upper_lower_arm_cylinder[2], 32, 32)    # create lower left arm 
        
        # left hand creation & sliding to place at the end of the lower left arm 
        glTranslatef(0, 0, 5)
        glColor3f(0.0, 1.0, 0.0)
        gluSphere(quadratic, 1.1, 32, 32)
        glPopMatrix()

        #--------------Write your code above -------------------
        glPopMatrix() # DO NOT DELETE THIS

    # handles drawing some random objects in the world so we can see changes in the fpv (through the scarecrow's eyes)
    def draw_world_scenery(self):
        # trees
        self.draw_single_tree(40, 60)
        self.draw_single_tree(-50, 90)
        self.draw_single_tree(80, -70)
        self.draw_single_tree(-100, -40)

        # orbs
        self.draw_single_orb(-30, 25, 0)
        self.draw_single_orb(20, -35, 1)
        self.draw_single_orb(90, 10, 2)
        self.draw_single_orb(-85, -10, 1)

        # box stacks
        self.draw_single_box_stack(-60, 60, 0)
        self.draw_single_box_stack(55, -50, 1)
        self.draw_single_box_stack(0, 100, 0)
        self.draw_single_box_stack(-100, -80, 1)


    # handles drawing a single tree at the specied x and y position in the world 
    def draw_single_tree(self, x, z):
        glPushMatrix()
        glTranslatef(x, 0, z)   # final translation to specified world position on xz plane

        # trunk rectangle
        glPushMatrix()
        glColor3f(0.55, 0.27, 0.07)     # brown
        glTranslate(0, 5, 0)
        glScalef(1.5, 10, 1.5)
        glutSolidCube(1)
        glPopMatrix()

        # top sphere
        glPushMatrix()
        glColor3f(0.0, 0.5, 0.0)        # green
        glTranslatef(0.0, 12, 0.0)
        glutSolidSphere(5, 20, 20)
        glPopMatrix()

        glPopMatrix()

    # handles drawing a single orb 
    def draw_single_orb(self, x, z, color):
        colors = [  (51.0, 255.0, 255.0), # cyan
                    (153.0, 0.0, 0.0),    # dark red
                    (153.0, 51.0, 255.0)  # purple
                    ]
        r, g, b = [c / 255.0 for c in colors[color]] # converts to correct range
        glPushMatrix()
        glColor3f(r, g, b)
        glTranslatef(x, 15, z)
        glutSolidSphere(2, 20, 20)
        glPopMatrix()

    # handles drawing a single stack of boxes
    def draw_single_box_stack(self, x, z, color):
        colors = [  [0.76, 0.60, 0.42], 
                    [0.71, 0.53, 0.32], ]
        glPushMatrix()
        glTranslate(x, 0, z)
        glColor3f(0.76, 0.60, 0.42)

        for i in range(3):
            glPushMatrix()
            glTranslate(0, i*5, 0)
            glRotate(i * 20, 0, 1, 0)
            glScalef(5, 5, 5)
            glutSolidCube(1)
            glPopMatrix()
        
        glPopMatrix()

class Camera:
    def __init__(self, view_mode = "front"):
        self.view_mode = view_mode
        # camera parameters
        self.eye_pos = np.array([0.0, 10.0, 50.0]) # initial setting for the front view
        self.look_at = np.array([0.0, 0.0, -1.0])
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
        view_modes = ["front", "side", "back", "first-person"]
        self.view_mode = view_modes[(view_modes.index(self.view_mode) + 1) % len(view_modes)]

        
        # Front view
        if self.view_mode == "front":
            self.eye_pos = np.array([0.0, 10.0, 50.0]) 
            self.look_at = np.array([0.0, 10.0, -1.0])
            self.view_up = np.array([0.0, 1.0, 0.0])
        # Side view
        elif self.view_mode == "side":
            self.eye_pos = np.array([50.0, 10.0, 0.0]) 
            self.look_at = np.array([-1.0, 10.0, 0.0])
            self.view_up = np.array([0.0, 1.0, 0.0])
        # Back view
        elif self.view_mode == "back":
            self.eye_pos = np.array([60.0, 30.0, -80.0]) 
            self.look_at = np.array([37.5, 15.0, 10.0])
            self.view_up = np.array([0.0, 1.0, 0.0])
        elif self.view_mode == "first-person":
            pass
        
        
    # Helper Function for Extra Credit First-Person View 
    #   Takes in a scarecrow object and uses its information to determine the 
    #   new eye position and look at point of the camera
    def update_fpv(self, scarecrow: Scarecrow):
        # calculate the current position of the scarecrow's head 
        head_position = np.array([0.0, 13, 3.0])     # let's start at 13 (above the nose) on the y-axis and 5 on the z-axis
        head_position = rotate_vector(head_position, scarecrow.head_angle, "Y")     # rotation 1 - head angle (i, o controls)
        head_position = rotate_vector(head_position, scarecrow.walk_angle, "Y")     # rotation 2 - walk angle (<-, -> controls)
        head_position += scarecrow.walk_vector  # translate based on current walk vector
        new_eye_pos = head_position            


        # calculate the new look at point of the camera by looking at
        base_gaze = np.array([0.0, 0.0, 1.0])       # let's start at a gaze of down the positive z-axis
        base_gaze = rotate_vector(base_gaze, scarecrow.head_angle, "Y")     # rotation 1 - head angle " "
        base_gaze = rotate_vector(base_gaze, scarecrow.walk_angle, "Y")     # rotation 2 - walk angle " "
        new_lookat = new_eye_pos + base_gaze * 2    # extend along the gaze so the lookat point is not stuck inside the head

        return new_eye_pos, new_lookat

    # Task 8: Update camera parameters (eye_pos and look_at) based on the new 
    #               tilt_angle_horizontal, tilt_angle_vertical, and zoom_distance updated by key input (A, D, W, S, Q, E)
    def update_view(self, scarecrow: Scarecrow):
        # if in first-person view, we update the view based on the scarecrow's head position
        if self.view_mode == "first-person":
            # we handle this in a separate function 
            new_eye_pos, new_lookat = self.update_fpv(scarecrow)
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

