# handles all the loading, collisions, and drawing of any imported OBJ objects 
import os
import numpy as np
from OpenGL.GL import *
from beeGame_OBJFileLoader import OBJ       # or wherever your OBJ class lives
from beeGame_collisions import Transform, apply_transform_to_mesh, draw_AABB
import random 

'''
    THESE ARE OBJECTS THAT ARE IMPORTED FROM OBJ FILES AND MIGHT REQURE ACCESSING CACHED POSITIONS
        THEY INCLUDE 
        - PROP [CLASS]
        - GRASS 
        - FLOWERS
        - BEEHIVE
        - 
'''

class Prop:
    # load the OBJ, apply the initial transformations, remember the bv type 
    def __init__(self, obj_filename: str, translation = (0, 0, 0), 
                rotation = (0, 1, 0, 0), scale = (1, 1, 1), bv_type = "AABB"):
        # create OBJ instance
        self.obj = OBJ(obj_filename, swapyz=False)
        # initial transformation
        self.t = Transform(translation=translation, 
                      rotation=rotation, 
                      scale=scale)
        apply_transform_to_mesh(self.obj, self.t)
        # take note of bv choice
        self.bv_type = bv_type

    # draws the prop 
    def draw(self, show_bounding_box:bool=False):
        if show_bounding_box:
                mins, maxs, center, _ = self.obj.cal_minMax()
                draw_AABB(mins, maxs, center)
        glCallList(self.obj.gl_list)

    # gets the bv of the prop 
    def get_bounding_volume(self):
        # returns what it is you need for collision detection 
        # if sphere, you need (1) center (2) radius
        # if AABB, you need   (1) min_coords (2) max_coords
        minc, maxc, center, radius = self.obj.cal_minMax()
        if self.bv_type == "sphere":
            return center, radius 
        elif self.bv_type == "AABB":
            return minc, maxc 
        elif self.bv_type == "NONE":
            return -1, -1

# checks for a text file containing positions of objects 
# ==> returns (needToCreate: bool, positions:list, num_of_positions:int)        
def read_object_positions_file(pathOfFile:str, ):
    # check if the grass objects file exists and if it has positions in it 
    need_to_create_file = False
    positions_formatted = []

    try:
        # try to open the file 
        positions_file = open(pathOfFile, "r")
        # read all the lines 
        positions_from_file = positions_file.readlines()
        # if empty file or the first line is empty space: close it and later we overwrite it
        if (len(positions_from_file) == 0): 
            need_to_create_file = True
            positions_file.close()
            print("--file empty...need to create file")
        else: # if file not empty, parse the contents 
            for line in positions_from_file:
                if type(line) != str:
                    continue
                # looks like this "x_pos y_pos z_pos rot_x rot_y rot_z scale_x scale_y scale_z bv_type"
                # print(line)
                line_items = line.split() 
                if len(line_items) == 11: 
                    positions_formatted.append((float(line_items[0]), float(line_items[1]), float(line_items[2]),                   # translation
                                                float(line_items[3]), int(line_items[4]), int(line_items[5]), int(line_items[6]),   # rotation
                                                float(line_items[7]), float(line_items[8]), float(line_items[9]),                   # scale
                                                line_items[10]))                                                                    # bv type
            positions_file.close()
            print(f"--{pathOfFile} file found...extracted {len(positions_formatted)} positions")
    except FileNotFoundError:
        # if it doesn't exist, let's create it 
        need_to_create_file = True
        print("--file not found...need to create file")
    
    # return values 
    return (need_to_create_file, positions_formatted, len(positions_formatted))

# creates all the necessary prop objects and writes to a new file if necessary 
# ==> returns (prop_objects:list<Prop>)
def create_objects_and_writeif(need_to_create_file:bool, positions_formatted:list, num_positions:int, 
                               path_of_file_to_write:str, obj_files:list, 
                               default_scaling:tuple, default_height:int, default_rotation:tuple,
                               default_bv_type:str, 
                               xz_boundaries:tuple, 
                               type_of_prop:str="default_prop_name"):
    # initialize our objects list 
    prop_objects = []
    positions = []

    # unpack arguments 
    x_min, x_max, z_min, z_max = xz_boundaries[0], xz_boundaries[1], xz_boundaries[2], xz_boundaries[3]
    length_along_z = z_max - z_min

    # if needed, generate random nums and write them to the file for next time                                                    
    if need_to_create_file: 
        object_positions_file = open(path_of_file_to_write, "w")
        for _ in range(num_positions):
            # open up the obj file (considering random variations - like the grass)
            object_variation_index = random.randint(0, len(obj_files) - 1)
            object_file_name = obj_files[object_variation_index]
            

            # generate a random position on the xz-plane
            random_x_pos = random.random() * x_max
            random_z_pos = (random.random() * length_along_z) + z_min

            # generate it in the world 
            prop_objects.append(Prop(f"./resources/models/{object_file_name}", 
                                    translation=(   random_x_pos,
                                                    default_height, 
                                                    random_z_pos), 
                                    rotation=default_rotation, 
                                    scale=default_scaling, 
                                    bv_type=default_bv_type))
            
            # save it's position to the file 
            object_positions_file.write(f"{random_x_pos} {default_height} {random_z_pos} {default_rotation[0]} {default_rotation[1]} {default_rotation[2]} {default_rotation[3]} {default_scaling[0]} {default_scaling[1]} {default_scaling[2]} {default_bv_type}\n")
            if type_of_prop == "CROCUS": positions.append((random_x_pos, default_height, random_z_pos))
        object_positions_file.close() 
        print(f"--random positions generated for {type_of_prop} and written to file")
    # if no file creation needed, 
    #   consider the read in and formatted the positions from the file, just use them to populate 
    else: 
        for line in range(num_positions):
            # open up the obj file (considering random variations - like the grass)
            object_variation_index = random.randint(0, len(obj_files) - 1)
            object_file_name = obj_files[object_variation_index]

            # grab the nect object's position tuple
            current_object = positions_formatted[line]
            # print(f"--extracted line {line} as a tuple: {current_object}--")

            # unpack the tuple 
            pos_x = current_object[0]
            pos_y = current_object[1]
            pos_z = current_object[2]
            rotation = (current_object[3], current_object[4], current_object[5], current_object[6])
            scaling = (current_object[7], current_object[8], current_object[9])
            bv_type = current_object[10]
            # print("--extracted positions--")

            # generate it in the world 
            prop_objects.append(Prop(f"./resources/models/{object_file_name}", 
                                    translation=(   pos_x,
                                                    pos_y, 
                                                    pos_z), 
                                    rotation=rotation, 
                                    scale=scaling, 
                                    bv_type=bv_type))
            if type_of_prop == "CROCUS": positions.append((pos_x, pos_y, pos_z))
            print(f"--generated {type_of_prop} object from file's line {line} as a tuple: {current_object}--")
    return prop_objects, positions

# draws all of the grass objects
def create_grass_objects(num_grass_chunks:int):
    scaling = (3, 3, 3)
    height = -12.4
    rotation = (0, 1, 0, 0)
    bv_type = "NONE"
    file_path = "./beeGameFinal/grass_objects_positions.txt"

    # try to open the file and read in the positions
    need_to_create_file, positions_formatted, num_positions = read_object_positions_file(file_path)
    print(f"--need_to_create_file: {need_to_create_file}, \n---positions_formatted:\n{positions_formatted[:10]}, \n--num_positions{num_positions}")
    
    if num_positions == 0:
        num_positions = num_grass_chunks

    # generate the objects 
    grass_objects, positions = create_objects_and_writeif(need_to_create_file=need_to_create_file, positions_formatted=positions_formatted, 
                                               num_positions=num_positions, path_of_file_to_write=file_path, 
                                               obj_files=["Grass1.obj", "Grass2.obj", "Grass3.obj"], 
                                               default_scaling=scaling, default_height=height, default_rotation=rotation, 
                                               default_bv_type=bv_type, 
                                               xz_boundaries=(0, 200, -100, 100), 
                                               type_of_prop="GRASS")

    return grass_objects

# draws all of the flower objects 
def create_flower_objects(num_flowers:int):
    scalings = [(0.25, 0.25, 0.25), (0.5, 0.5, 0.5)]
    height = -10
    rotation = (-90.0, 1, 0, 0)
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

        # generate the objects 
        crocus_objects, positions = create_objects_and_writeif(need_to_create_file=need_to_create_file, positions_formatted=positions_formatted, 
                                                num_positions=num_positions, path_of_file_to_write=file_path, 
                                                obj_files=["12974_crocus_flower_v1_l3.obj"], 
                                                default_scaling=scalings[index], default_height=height, default_rotation=rotation, 
                                                default_bv_type=bv_type, 
                                                xz_boundaries=(x_min, x_max, z_min, z_max), 
                                                type_of_prop="CROCUS")
        all_objects += crocus_objects
        all_positions += positions
    
    return all_objects, all_positions

# draws the beehive 
def create_beehive():
    scaling = (0.15, 0.15, 0.15)
    pos_x = 50
    pos_z = -50
    height = 10

    rotation = (-90.0, 1, 0, 0)
    bv_type = "AABB"

    beehive = Prop(f"./resources/models/beehive.obj", 
                    translation=( pos_x,
                                  height, 
                                  pos_z), 
                    rotation=rotation, 
                    scale=scaling, 
                    bv_type=bv_type)

    return beehive