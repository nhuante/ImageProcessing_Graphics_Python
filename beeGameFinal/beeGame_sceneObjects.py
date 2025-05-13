# handles all the loading, collisions, and drawing of any imported OBJ objects 
import os
import numpy as np
from OpenGL.GL import *
from beeGame_OBJFileLoader import OBJ       # or wherever your OBJ class lives
from beeGame_collisions import Transform, apply_transform_to_mesh
import random 


class Prop:
    # load the OBJ, apply the initial transformations, remember the bv type 
    def __init__(self, obj_filename: str, translation = (0, 0, 0), 
                rotation = (0, 1, 0, 0), scale = (1, 1, 1), bv_type = "AABB"):
        # create OBJ instance
        self.obj = OBJ(obj_filename, swapyz=False)
        # initial transformation
        t = Transform(translation=translation, 
                      rotation=rotation, 
                      scale=scale)
        apply_transform_to_mesh(self.obj, t)
        # take note of bv choice
        self.bv_type = bv_type

    # draws the prop 
    def draw(self):
        glCallList(self.obj.gl_list)

    # gets the bv of the prop 
    def get_bounding_volume(self):
        # returns what it is you need for collision detection 
        # if sphere, you need (1) center (2) radius
        # if AABB, you need   (1) min_coords (2) max_coords
        minc, maxc, center, radius = self.obj.cal_minMax()
        if self.bv_type == "sphere":
            return center, radius 
        else:
            return minc, maxc 
        

# draws all of the grass objects
def create_grass_objects():
    grass_objects = []
    
    scaling = (3, 3, 3)
    height = -12.4

    x_min, x_max, z_min, z_max = 0, 200, -100, 100
    length_along_z = z_max - z_min
    for _ in range(50):
        grass_objects.append(Prop("./resources/models/Grass1.obj", 
                                  translation=(random.random() * x_max,
                                               height, 
                                               (random.random() * length_along_z) + z_min), 
                                  rotation=(0, 1, 0, 0), 
                                  scale=scaling, 
                                  bv_type="AABB"))

    return grass_objects