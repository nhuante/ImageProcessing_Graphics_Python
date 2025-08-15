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

from OBJFileLoader_11 import *

import numpy as np
from collections import defaultdict

width, height = 800, 600                                                    # width and height of the screen created
bDrawWireframe = False                                                      # a flag indicating whether or not drawing edges and veritices

########################################### OpenGL Program ####################################################
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
    glColor3f(0.0, 0.0, 0.0)                                                # set point color
    glPointSize(5.0)                                                        # set point size

    glBegin(GL_POINTS)
    for v in obj.vertices:
        glVertex3fv(v)
    glEnd()

    glEnable(GL_LIGHTING)


def draw_edges(obj):
    glDisable(GL_LIGHTING)
    glColor3f(0.0, 0.0, 0.0)                                                # set edge color (black)
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


def draw_mesh(obj):
    # Set background and depth
    glClearColor(0, 0, 0, 1)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    # Enable rendering settings
    glEnable(GL_LIGHTING)
    glEnable(GL_COLOR_MATERIAL)
    glEnable(GL_DEPTH_TEST)
    glShadeModel(GL_SMOOTH)

    glPushMatrix()
    glLoadIdentity()
    # Light 0 - point light from above, left, front
    glEnable(GL_LIGHT0)
    glLightfv(GL_LIGHT0, GL_POSITION, (-40, 200, 100, 1.0))  # point light
    glLightfv(GL_LIGHT0, GL_AMBIENT, (0.2, 0.2, 0.2, 1.0))
    glLightfv(GL_LIGHT0, GL_DIFFUSE, (0.5, 0.5, 0.5, 1.0))
    glLightfv(GL_LIGHT0, GL_SPECULAR, (0.5, 0.5, 0.5, 1.0)) # softer white highlight

    # Light 1 - point light from the left
    glEnable(GL_LIGHT1)
    glLightfv(GL_LIGHT1, GL_POSITION, (-10.0, 0.0, 0.0, 1.0))  # point light
    #glLightfv(GL_LIGHT1, GL_AMBIENT, (0.2, 0.2, 0.2, 1.0))
    #glLightfv(GL_LIGHT1, GL_DIFFUSE, (0.5, 0.5, 0.5, 1.0))     # red-tinted light
    glLightfv(GL_LIGHT1, GL_DIFFUSE, (0.5, 0.5, 0.5, 1.0))
    #glLightfv(GL_LIGHT1, GL_SPECULAR, (1.0, 0.5, 0.5, 1.0))    # red specular
    #glLightfv(GL_LIGHT1, GL_SPECULAR, (0.5, 0.5, 0.5, 1.0))     # softer white highlight

    # Light 2 - point light from the right
    glEnable(GL_LIGHT2)
    glLightfv(GL_LIGHT2, GL_POSITION, (10.0, 0.0, 0.0, 1.0))   # point light
    #glLightfv(GL_LIGHT2, GL_AMBIENT, (0.2, 0.2, 0.2, 1.0))
    #glLightfv(GL_LIGHT2, GL_DIFFUSE, (0.2, 0.2, 0.8, 1.0))     # blue-tinted light
    glLightfv(GL_LIGHT2, GL_DIFFUSE, (0.5, 0.5, 0.5, 1.0))
    #glLightfv(GL_LIGHT2, GL_SPECULAR, (0.5, 0.5, 1.0, 1.0))    # blue specular
    #glLightfv(GL_LIGHT2, GL_SPECULAR, (0.5, 0.5, 0.5, 1.0))     # softer white highlight

    glPopMatrix()

    # Material properties for specular highlight
    glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, (0.5, 0.5, 0.5, 1.0))   # less shiny white
    glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 32.0)                  # [0–128], higher = tighter highlight

    # draw mesh
    glPushMatrix()
    #glRotatef(90, 0, 1, 0) # only for panther.obj
    glCallList(obj.gl_list)

    # Draw edges and vertices over shaded mesh
    if bDrawWireframe:
        draw_edges(obj)
        draw_vertices(obj)

    glPopMatrix()

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
                new_vertices[i] = neighbor_positions.mean(axis=0)

                # TODO: Laplacian smoothing weighted with lambda - COMMENT out the above line first!

                
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


def main():
    pygame.init()                                                           # initialize a pygame program
    glutInit()                                                              # initialize glut library 

    screen = (width, height)                                                # specify the screen size of the new program window
    display_surface = pygame.display.set_mode(screen, DOUBLEBUF | OPENGL)   # create a display of size 'screen', use double-buffers and OpenGL
    pygame.display.set_caption('CPSC 515: Meshes')                          # set title of the program window

    glEnable(GL_DEPTH_TEST)
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)                                             # set mode to projection transformation
    glLoadIdentity()                                                        # reset transf matrix to an identity
    gluPerspective(45.0, width/height, 0.1, 1000.0)                         # specify an perspective-projection view volume

    glMatrixMode(GL_MODELVIEW)                                              # set mode to modelview (geometric + view transf)
    gluLookAt(0, 0, 50, 0, 0, 0, 0, 1, 0)                                   # set camera's eye, look-at, and view-up in the world
    initmodelMatrix = glGetFloat(GL_MODELVIEW_MATRIX)

    # load OBJ mesh
    model_path = os.path.join("./resources/models/", "panther.obj")
    if not os.path.exists(model_path):
        raise ValueError(f"OBJ file not found: {model_path}")
    obj = OBJ(filename=model_path, swapyz=False)

    # mouse controled dynamic view
    rx, ry = (0,0)
    tx, ty = (0,0)
    zpos = 5
    rotate = False
    move = False
    global bDrawWireframe
    while True:
        for e in pygame.event.get():
            if e.type == QUIT:
                sys.exit()
            elif e.type == KEYDOWN and e.key == K_ESCAPE:
                sys.exit()
            elif e.type == KEYDOWN and e.key == K_l:
                # apply Laplacian smoothing
                laplacian_smooth(obj, iterations=1)
                compute_vertex_normals(obj)
                obj.rebuild_gl_list()
            elif e.type == KEYDOWN and e.key == K_w:
                bDrawWireframe = not bDrawWireframe
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
        
        # draw mesh
        glLoadIdentity()
        glTranslate(tx/20., ty/20., - zpos)
        glRotate(ry, 1, 0, 0)
        glRotate(rx, 0, 1, 0)
        draw_mesh(obj=obj)
        drawAxes()

        pygame.display.flip()
        pygame.time.wait(10)

main()