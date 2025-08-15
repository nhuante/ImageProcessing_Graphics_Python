# Basic OBJ file viewer. needs objloader from:
#  http://www.pygame.org/wiki/OBJFileLoader
# LMB + move: rotate
# RMB + move: pan
# Scroll wheel: zoom in/out
import sys, pygame
from pygame.locals import *
from pygame.constants import *
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

from OBJFileLoader_12 import *

import numpy as np
from collections import defaultdict

width, height = 800, 600                                                    # width and height of the screen created
bDrawWireframe = False    # a flag indicating whether or not drawing edges and veritices    
bDrawBV = False # flag for drawing the bounding volues (bv)
bCollide = False # True: Collision detected; False: Collision not detected

########################################### Transformations ####################################################
class Transform:
    def __init__(self, translation=(0,0,0), rotation=(0,0,0), scale=(1,1,1)):
        self.translation = translation  # (x, y, z)
        self.rotation = rotation        # (angle_degrees, x_axis, y_axis, z_axis)
        self.scale = scale              # (sx, sy, sz)

def apply_transform_to_point(point, transform):
    # Convert the point to a numpy array
    p = np.array(point, dtype=float)

    # 1. Scale
    p = p * np.array(transform.scale)

    # 2. Rotation around Y-axis
    angle_rad = np.radians(transform.rotation[0])  # assuming rotation is (angle, x, y, z)
    if transform.rotation[1:] == (0,1,0):  # if rotating around Y-axis
        cos_a = np.cos(angle_rad)
        sin_a = np.sin(angle_rad)
        rotation_matrix = np.array([
            [ cos_a, 0, sin_a],
            [ 0,     1, 0    ],
            [-sin_a, 0, cos_a]])
        p = np.dot(rotation_matrix, p)  # matrix multiplication

    # 3. Translation
    p = p + np.array(transform.translation)

    return list(p)

def apply_transform_to_mesh(obj, transform):
    transformed_vertices = []
    for v in obj.vertices:
        transformed_v = apply_transform_to_point(v, transform)
        transformed_vertices.append(transformed_v)
    obj.vertices = transformed_vertices
    obj.rebuild_gl_list()
    #return transformed_vertices


########################################### Drawing Functions ####################################################
def drawAxes():                                                             # draw x-axis and y-axis
    glDisable(GL_LIGHTING)
    glLineWidth(3.0)                                                        # specify line size (1.0 default)
    glBegin(GL_LINES)                                                       # replace GL_LINES with GL_LINE_STRIP or GL_LINE_LOOP
    glColor3f(1.0, 0.0, 0.0)                                                # x-axis: red
    glVertex3f(0.0, 0.0, 0.0)                                               # v0
    glVertex3f(100.0, 0.0, 0.0)                                             # v1
    glColor3f(0.0, 1.0, 0.0)                                                # y-axis: green
    glVertex3f(0.0, 0.0, 0.0)                                               # v0
    glVertex3f(0.0, 100.0, 0.0)                                             # v1
    glColor3f(0.0, 0.0, 1.0)                                                # z-axis: green
    glVertex3f(0.0, 0.0, 0.0)                                               # v0
    glVertex3f(0.0, 0.0, 100.0)                                             # v1
    glEnd()

def draw_vertices(obj):
    glDisable(GL_LIGHTING)                                                  # points are not affected by lighting
    glColor3f(1.0, 1.0, 1.0)                                                # set point color
    glPointSize(4.0)                                                        # set point size

    glBegin(GL_POINTS)
    for v in obj.vertices:
        glVertex3fv(v)
    glEnd()

    glEnable(GL_LIGHTING)


def draw_edges(obj):
    glDisable(GL_LIGHTING)
    glColor3f(0.8, 0.8, 0.8)                                                # set edge color (black)
    glLineWidth(1.0)                                                        # set line thickness
    glBegin(GL_LINES)

    drawn_edges = set()
    for face in obj.faces:
        vertices = face[0]                                                  # just vertex indices

        num_vertices = len(vertices)
        for i in range(num_vertices):
            v1 = vertices[i] - 1
            v2 = vertices[(i + 1) % num_vertices] - 1                       # wrap around

            # ensure each edge is drawn only once (unordered pair)
            edge = tuple(sorted((v1, v2)))
            if edge in drawn_edges:
                continue
            drawn_edges.add(edge)

            glVertex3fv(obj.vertices[v1])
            glVertex3fv(obj.vertices[v2])
    glEnd()

    glEnable(GL_LIGHTING)

# draw the mesh, its edges and vertices, and bounding volume
#   bv_type = "sphere" or "AABB"
def draw_mesh(obj, bv_type): 
    # Enable rendering settings
    glEnable(GL_LIGHTING)
    #glEnable(GL_COLOR_MATERIAL) # disable or not enable to use the setting in MTL file
    glEnable(GL_DEPTH_TEST)
    glShadeModel(GL_SMOOTH)

    glPushMatrix()
    glLoadIdentity()
    # Light 0 - point light from above, left, front
    glEnable(GL_LIGHT0)
    glLightfv(GL_LIGHT0, GL_POSITION, (-40, 200, 100, 1.0))  # point light
    glLightfv(GL_LIGHT0, GL_AMBIENT, (0.3, 0.3, 0.3, 1.0))
    glLightfv(GL_LIGHT0, GL_DIFFUSE, (0.5, 0.5, 0.5, 1.0))
    glLightfv(GL_LIGHT0, GL_SPECULAR, (0.2, 0.2, 0.2, 1.0))

    # Light 1 - point light from the left
    glEnable(GL_LIGHT1)
    glLightfv(GL_LIGHT1, GL_POSITION, (-40.0, 5.0, 40.0, 1.0))  # point light
    glLightfv(GL_LIGHT1, GL_AMBIENT, (0.2, 0.2, 0.2, 1.0))
    glLightfv(GL_LIGHT1, GL_DIFFUSE, (0.2, 0.2, 0.2, 1.0))
    glLightfv(GL_LIGHT1, GL_SPECULAR, (0.1, 0.1, 0.1, 1.0))

    # Light 2 - point light from the right
    glEnable(GL_LIGHT2)
    glLightfv(GL_LIGHT2, GL_POSITION, (40.0, 5.0, 40.0, 1.0))   # point light
    glLightfv(GL_LIGHT2, GL_AMBIENT, (0.2, 0.2, 0.2, 1.0))
    glLightfv(GL_LIGHT2, GL_DIFFUSE, (0.2, 0.2, 0.2, 1.0))
    glLightfv(GL_LIGHT2, GL_SPECULAR, (0.1, 0.1, 0.1, 1.0))

    glPopMatrix()

    # Material properties for specular highlight
    glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, (0.1, 0.1, 0.1, 1.0))   # less shiny white
    glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 5.0)                  # [0–128], higher = tighter highlight

    glPushMatrix()
    # draw mesh and its bounding volume
    if bDrawBV == True:
        # calcuate bounding sphere and box parameters
        min_coords, max_coords, center, radius = obj.cal_minMax()
        # draw bounding volume
        if bv_type == "sphere":
            draw_boundingSphere(center, radius)
        elif bv_type == "AABB":
            draw_AABB(min_coords, max_coords, center)
    # draw mesh
    glCallList(obj.gl_list)

    # Draw edges and vertices over shaded mesh
    if bDrawWireframe:
        draw_edges(obj)
        draw_vertices(obj)

    glPopMatrix()

def draw_boundingSphere(center, radius):
    # Set wireframe mode
    glPushAttrib(GL_POLYGON_BIT)
    glDisable(GL_LIGHTING)
    glColor3f(1.0, 1.0, 1.0)
    if bCollide == True:
        glColor3f(1.0, 1.0, 0.0)
    glLineWidth(1.0)
    glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

    # Draw the sphere
    glPushMatrix()
    glTranslatef(center[0], center[1], center[2])
    quad = gluNewQuadric()
    gluQuadricDrawStyle(quad, GLU_LINE)  # explicitly wireframe
    gluSphere(quad, radius, 16, 16)
    gluDeleteQuadric(quad)
    glPopMatrix()

    glEnable(GL_LIGHTING)
    glPopAttrib()

def draw_AABB(min_coords, max_coords, center):
    # Calculate size of the box along each axis
    size_x = max_coords[0] - min_coords[0]
    size_y = max_coords[1] - min_coords[1]
    size_z = max_coords[2] - min_coords[2]

    # glutWireCube draws a cube of size 1 centered at (0,0,0), so we scale
    glPushAttrib(GL_POLYGON_BIT)
    glDisable(GL_LIGHTING)
    glColor3f(1.0, 1.0, 1.0)
    if bCollide == True:
        glColor3f(0.25, 0.88, 0.82)
    glLineWidth(1.0)
    glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

    glPushMatrix()
    glTranslatef(center[0], center[1], center[2])
    glScalef(size_x, size_y, size_z)
    glutWireCube(1.0)
    glPopMatrix()

    glEnable(GL_LIGHTING)
    glPopAttrib()

########################################### Laplacian Smoothing ####################################################
def laplacian_smooth(obj, lambda_val = 0.1, iterations=1):
    # Step 1: Build vertex adjacency list
    adjacency = defaultdict(set)
    for face in obj.faces:
        vertices = face[0]  # face[0] is a list of vertex indices (1-based)
        n = len(vertices)
        for i in range(n):
            vi = vertices[i] - 1
            vj = vertices[(i + 1) % n] - 1
            adjacency[vi].add(vj)
            adjacency[vj].add(vi)

    # Convert vertex list to numpy array for easier manipulation
    vertices = np.array(obj.vertices)

    for _ in range(iterations):
        new_vertices = vertices.copy()
        for i in range(len(vertices)):
            neighbors = adjacency[i]
            if neighbors:
                neighbor_positions = np.array([vertices[j] for j in neighbors])
                # Laplacian smoothing - average
                #new_vertices[i] = neighbor_positions.mean(axis=0)

                # TODO: Laplacian smoothing weighted with lambda - COMMENT out the above line first!
                new_vertices[i] = vertices[i] + lambda_val * (neighbor_positions.mean(axis=0) - vertices[i])
                
        vertices = new_vertices

    # Update the mesh with smoothed vertices
    obj.vertices = vertices.tolist()

# Recompute per-vertex normals and update face normal indices
def compute_vertex_normals(obj):
    num_vertices = len(obj.vertices)
    vertex_normals = [np.zeros(3) for _ in range(num_vertices)]

    for face in obj.faces:
        vertex_indices, _, _, _ = face
        v_idxs = [idx - 1 for idx in vertex_indices]  # OBJ is 1-based
        if len(v_idxs) < 3:
            continue  # skip degenerate faces

        v0, v1, v2 = [np.array(obj.vertices[i]) for i in v_idxs[:3]]
        edge1 = v1 - v0
        edge2 = v2 - v0
        face_normal = np.cross(edge1, edge2)
        norm = np.linalg.norm(face_normal)
        if norm != 0:
            face_normal /= norm

        for i in v_idxs:
            vertex_normals[i] += face_normal

    # Normalize and assign
    obj.normals = []
    for n in vertex_normals:
        norm = np.linalg.norm(n)
        if norm != 0:
            n /= norm
        obj.normals.append(n.tolist())

    # Update normal indices in faces
    new_faces = []
    for verts, _, texcoords, material in obj.faces:
        new_norms = verts  # assume one normal per vertex
        new_faces.append((verts, new_norms, texcoords, material))
    obj.faces = new_faces

########################################### In-Class Exercises: Collision Detection ####################################################
# TODO: Collision detection: Sphere vs. Sphere
#   Collision if distance between two centers <= (radius1 + radius2)
def collisionTest_spheres(center1, radius1, center2, radius2):
    dx = center1[0] - center2[0]
    dy = center1[1] - center2[1]
    dz = center1[2] - center2[2]
    distance_squared = dx*dx + dy*dy + dz*dz
    radius_sum = radius1 + radius2
    return distance_squared <= radius_sum * radius_sum

# TODO: Collision detection: AABB vs. AABB
#   Collision if their ranges (min, max) on EACH axis (x, y, z) overlap
def collisionTest_AABBs(min_coords1, max_coords1, min_coords2, max_coords2):
    for i in range(3):  # 0=x, 1=y, 2=z
        if max_coords1[i] < min_coords2[i] or min_coords1[i] > max_coords2[i]:
            return False
    return True

# TODO: Collision detection: Sphere vs. AABB
#   Collision if the distance from AABB's closest point to the sphere 
#       to the sphere center is less or equal to radius
def collisionTest_sphereAABB(center1, radius1, min_coord2, max_coords2):
    # get box closest point to sphere center by clamping
    c_x = max(min_coord2[0], min(center1[0], max_coords2[0]))
    c_y = max(min_coord2[1], min(center1[1], max_coords2[1]))
    c_z = max(min_coord2[2], min(center1[2], max_coords2[2]))

    # calculate the distance between closest point to the center
    dx = center1[0] - c_x
    dy = center1[1] - c_y
    dz = center1[2] - c_z
    distance_squared = dx*dx + dy*dy + dz*dz

    # compare distance with radius 
    return distance_squared <= radius1 * radius1

########################################### OpenGL Program ####################################################
def main():
    pygame.init()                                                           # initialize a pygame program
    glutInit()                                                              # initialize glut library 

    screen = (width, height)                                                # specify the screen size of the new program window
    display_surface = pygame.display.set_mode(screen, DOUBLEBUF | OPENGL)   # create a display of size 'screen', use double-buffers and OpenGL
    pygame.display.set_caption('CPSC 515: Collisions')                      # set title of the program window

    glEnable(GL_DEPTH_TEST)
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)                                             # set mode to projection transformation
    glLoadIdentity()                                                        # reset transf matrix to an identity
    gluPerspective(45.0, width/height, 0.1, 1000.0)                         # specify an perspective-projection view volume

    glMatrixMode(GL_MODELVIEW)                                              # set mode to modelview (geometric + view transf)
    gluLookAt(0, 0, 50, 0, 0, 0, 0, 1, 0)                                   # set camera's eye, look-at, and view-up in the world
    initmodelMatrix = glGetFloat(GL_MODELVIEW_MATRIX)

    # load OBJ mesh
    # load suzanne as obj1
    model1_name = "suzanne.obj"
    model_path = os.path.join("./resources/models/", model1_name)
    if not os.path.exists(model_path):
        raise ValueError(f"OBJ file not found: {model_path}")
    obj1 = OBJ(filename=model_path, swapyz=False)
    # transform suzanne
    transform_suzanne = Transform(
    translation=(0, 0, 0),
    rotation=(0, 0, 1, 0),   # no rotation
    scale=(0.5, 0.5, 0.5))
    apply_transform_to_mesh(obj1, transform_suzanne) # here we physically transform each vertex position

    BV1_type = "sphere" # bounding volume type: "sphere", "AABB"

    # load panther as obj2
    model2_name = "panther.obj"
    model_path = os.path.join("./resources/models/", model2_name)
    if not os.path.exists(model_path):
        raise ValueError(f"OBJ file not found: {model_path}")
    obj2 = OBJ(filename=model_path, swapyz=False)

    # transform panther
    transform_panther = Transform(
    translation=(2, 0, 0),   # moved by 2
    rotation=(-90, 0, 1, 0), # rotated -90 degrees around Y
    scale=(1, 1, 1))
    apply_transform_to_mesh(obj2, transform_panther) # here we physically transform each vertex position

    BV2_type = "AABB" # bounding volume type: "sphere", "AABB"    

    # mouse controled dynamic view
    rx, ry = (0,0)
    tx, ty = (0,0)
    zpos = 5
    rotate = False
    move = False
    move_left, move_right = False, False
    global bDrawWireframe, bDrawBV, bCollide
    while True:
        move_left = False
        move_right = False
        for e in pygame.event.get():
            if e.type == QUIT:
                sys.exit()
            elif e.type == KEYDOWN and e.key == K_ESCAPE:
                sys.exit()
            elif e.type == KEYDOWN and e.key == K_l:
                # apply Laplacian smoothing
                laplacian_smooth(obj1, iterations=1)
                compute_vertex_normals(obj1)
                obj1.rebuild_gl_list()
            elif e.type == KEYDOWN and e.key == K_w:
                bDrawWireframe = not bDrawWireframe
            elif e.type == KEYDOWN and e.key == K_c:
                bDrawBV = not bDrawBV           
            elif e.type == KEYDOWN and e.key == K_LEFT:
                move_left = True
                move_panther = True
            elif e.type == KEYDOWN and e.key == K_RIGHT:
                move_right = True
                move_panther = True
            elif e.type == MOUSEBUTTONDOWN:
                if e.button == 4: zpos = max(1, zpos-1)
                elif e.button == 5: zpos += 1
                elif e.button == 1: rotate = True
                elif e.button == 3: move = True
            elif e.type == MOUSEBUTTONUP:
                if e.button == 1: rotate = False
                elif e.button == 3: move = False
            elif e.type == MOUSEMOTION:
                i, j = e.rel
                if rotate:
                    rx += i
                    ry += j
                if move:
                    tx += i
                    ty -= j
        
        # transform panther if key pressed
        if move_left == True or move_right == True:
            x_offset = 0.0
            if move_left:
                x_offset = -0.5
            if move_right:
                x_offset = 0.5
            transform_panther = Transform(
            translation=(x_offset, 0, 0),   # moved by x_offset
            rotation=(0, 0, 1, 0),          
            scale=(1, 1, 1))
            apply_transform_to_mesh(obj2, transform_panther) # here we physically transform each vertex position

        # collision detection
        min_coords1, max_coords1, center1, radius1 = obj1.cal_minMax()
        min_coords2, max_coords2, center2, radius2 = obj2.cal_minMax()
        if BV1_type == BV2_type: 
            if BV1_type == "sphere":
                bCollide = collisionTest_spheres(center1, radius1, center2, radius2)
            elif BV1_type == "AABB":
                bCollide = collisionTest_AABBs(min_coords1, max_coords1, min_coords2, max_coords2)
        else:
            if BV1_type == "sphere" and BV2_type == "AABB":
                bCollide = collisionTest_sphereAABB(center1, radius1, min_coords2, max_coords2)
            elif BV2_type == "sphere" and BV1_type == "AABB":
                bCollide = collisionTest_sphereAABB(center2, radius2, min_coords1, max_coords1)

        # Clear screen ONCE per frame
        glClearColor(0, 0, 0, 1)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # draw mesh
        glLoadIdentity()
        glTranslate(tx/20., ty/20., - zpos)
        glRotate(ry, 1, 0, 0)
        glRotate(rx, 0, 1, 0)
        glPushMatrix()
        # draw obj1
        draw_mesh(obj=obj1, bv_type=BV1_type)
        # draw obj2
        draw_mesh(obj=obj2, bv_type=BV2_type)
        glPopMatrix()
        drawAxes()

        pygame.display.flip()
        pygame.time.wait(10)

main()