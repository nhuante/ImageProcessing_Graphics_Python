from OpenGL.GL import *
from beeGame_OBJFileLoader import OBJ       
from beeGame_collisions import Transform, apply_transform_to_mesh, draw_AABB
import random 

'''
    THESE ARE OBJECTS THAT ARE IMPORTED FROM OBJ FILES AND MIGHT REQURE ACCESSING CACHED POSITIONS
        THEY INCLUDE 
        - PROP [CLASS]
        - GRASS 
        - FLOWERS (NOT USED IN FINAL SUBMISSION, SUPER LARGE MESH, NOT EFFICIENT TO USE THEM)
        - BEEHIVE
        - 
'''
# used for obj objects that are loaded in
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
#   ==> returns (needToCreate: bool, positions:list, num_of_positions:int)        
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
        # if file not empty, parse the contents
        else:  
            for line in positions_from_file:
                if type(line) != str:
                    continue
                # each line looks like this:
                #       "x_pos y_pos z_pos rot_x rot_y rot_z scale_x scale_y scale_z bv_type"
                # print(line)                               # NOTE: uncomment if you want to see each line print as it is read in (before it gets processed)
                line_items = line.split() 
                # if the line has 11 elements (if not we pass so we don't get indexing issues )
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

# if read in file successfully, returns those positions
# elif needs to overwrite and repopulate the file, generates new positions, writes them to the file, returns those new positions
#   ==> returns (positions:List<Tuples>)
def create_objects_and_writeif(need_to_create_file:bool, positions_formatted:list, num_positions:int, 
                               path_of_file_to_write:str, obj_files:list, 
                               default_scaling:tuple, default_height:int, default_rotation:tuple,
                               default_bv_type:str, 
                               xz_boundaries:tuple, 
                               type_of_prop:str="default_prop_name"):
    # initialize our objects list 
    positions = []

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

            # save it's position to the file 
            new_position_data = f"{random_x_pos} {default_height} {random_z_pos} {default_rotation[0]} {default_rotation[1]} {default_rotation[2]} {default_rotation[3]} {default_scaling[0]} {default_scaling[1]} {default_scaling[2]} {default_bv_type}\n"
            object_positions_file.write(new_position_data)
            positions.append(new_position_data.split())

        object_positions_file.close() 
        print(f"--random positions generated for {type_of_prop} and written to file")
    # if no file creation needed, 
    #   consider the read in and already formatted positions from the file, just use them to populate 
    else: 
        for line in range(num_positions):
            # grab the nect object's position tuple
            current_object = positions_formatted[line]
            # print(f"--extracted line {line} as a tuple: {current_object}--")
            positions.append(current_object)
            print(f"--using {type_of_prop} object from file's line {line} as a tuple: {current_object}--")
    return positions

# master creating all the grass objects function (the positions i mean)
#   - here you can change the scalings, height, and rotation of the grass objects 
#   ==> returns the positions for the grass objects (either read-in and formatted or generated)
def read_write_grass_objects(num_grass_chunks:int):
    scaling = (3, 3, 3)
    height = -12.4
    rotation = (0, 1, 0, 0)
    bv_type = "NONE"
    file_path = "./beeGameFinal/grass_objects_positions.txt"

    # try to open the file and read in the positions
    need_to_create_file, positions_formatted, num_positions = read_object_positions_file(file_path)
    print(f"--need_to_create_file: {need_to_create_file}, \n---positions_formatted:\n{positions_formatted[:10]}, \n--num_positions{num_positions}")
    
    # if the number of positions extracted from the file is 0, change back to desired number 
    #   - this will cause the the called function to regenerate the positions
    if num_positions == 0:
        num_positions = num_grass_chunks

    # get the positions  
    positions = create_objects_and_writeif(need_to_create_file=need_to_create_file, positions_formatted=positions_formatted, 
                                               num_positions=num_positions, path_of_file_to_write=file_path, 
                                               obj_files=["Grass1.obj", "Grass2.obj", "Grass3.obj"], 
                                               default_scaling=scaling, default_height=height, default_rotation=rotation, 
                                               default_bv_type=bv_type, 
                                               xz_boundaries=(0, 200, -100, 100), 
                                               type_of_prop="GRASS")

    return positions

# master creating all the flower objects function (the positions i mean)
#   - here you can change the scalings, height, and rotation of the flower objects 
#   ==> returns the positions for the flower objects (either read-in and formatted or generated)
#   NOTE: NOT USED IN FINAL SUBMISSION BECAUSE THE OBJ FLOWER BOGGED DOWN THE GAME TOO MUCH
def create_flower_objects(num_flowers:int):
    scalings = [(0.25, 0.25, 0.25), (0.5, 0.5, 0.5)]
    height = -10
    rotation = (-90.0, 1, 0, 0)
    bv_type = "AABB"
    file_path_1 = "./beeGameFinal/crocusFlowers_positions.txt"
    file_path_2 = "./beeGameFinal/crocusFlowers_short_positions.txt"

    x_min, x_max, z_min, z_max = 15, 185, -85, 85

    all_positions = []

    for index, file_path in enumerate([file_path_1, file_path_2]):
        # try to open the file and read in positions 
        need_to_create_file, positions_formatted, num_positions = read_object_positions_file(file_path)

        if num_positions != num_flowers//2:
            num_positions = num_flowers//2
            need_to_create_file = True
            print(f"--positions extracted doesn't match desired count...regenerating")

        # generate the objects 
        positions = create_objects_and_writeif(need_to_create_file=need_to_create_file, positions_formatted=positions_formatted, 
                                                num_positions=num_positions, path_of_file_to_write=file_path, 
                                                obj_files=["12974_crocus_flower_v1_l3.obj"], 
                                                default_scaling=scalings[index], default_height=height, default_rotation=rotation, 
                                                default_bv_type=bv_type, 
                                                xz_boundaries=(x_min, x_max, z_min, z_max), 
                                                type_of_prop="CROCUS")
        all_positions += positions
    
    return all_positions

# loads the beehive as an obj file 
#    - here you can change the rotation and bounding volume type of the beehive   
# ==> returns the beehive as a Prop object
def create_beehive(scaling:tuple, pos_x:float, height:float, pos_z:float):
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