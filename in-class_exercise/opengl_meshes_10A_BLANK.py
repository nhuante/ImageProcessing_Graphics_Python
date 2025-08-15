import pygame
from pygame.locals import *

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

import numpy as np

width, height = 800, 600                                                    # width and height of the screen created

########################################### Lecture examples ####################################################
# mesh data structure (Indexed Triangles)
vertices = [
    [-20.0, -10.0, 1.0],    #v0
    [-10.0, 10.0, 1.0],     #v1
    [0.0, -10.0, 1.0],      #v2
    [10.0, 10.0, 1.0],      #v3
    [20.0, -10.0, 1.0]      #v4
]

edges = [
    [0, 1],                 #v0, v1
    [1, 2],                 #v1, v2
    [2, 3],                 #v2, v3
    [3, 4],                 #v3, v4
    [0, 2],                 #v0, v2
    [2, 4],                 #v2, v4
    [1, 3]                  #v1, v3
]

triangles = [
    [0, 1, 2],              #v0-v1-v2
    [1, 2, 3],              #v1-v2-v3
    [2, 3, 4]               #v2-v3-v4
]

# Example 1: Draw Vertices (using GL_POINTS)
def draw_vertices():
    glColor3f(1.0, 1.0, 1.0)                                                # specify vertex color (r,g,b), white
    glPointSize(10.0)                                                       # specify point size
    glBegin(GL_POINTS)
    for vertex in vertices:
        glVertex3fv(vertex)
    glEnd()

# Example 2: Draw Edges (using GL_LINES)
def draw_edges():
    glColor3f(1.0, 1.0, 1.0)
    glLineWidth(5.0)
    glBegin(GL_LINES)
    for edge in edges:
        for vertex in edge:
            glVertex3fv(vertices[vertex])
    glEnd()

# Example 3: Draw Triangles (using GL_TRIANGLES)
def draw_triangles():                                                       
    colors = ((1.0,0.0,0.0),(0.0,1.0,0.0),(0.0,0.0,1.0))                   # [red, green, blue]
    tri_idx = 0
    glBegin(GL_TRIANGLES)
    for triangle in triangles:
        glColor3fv(colors[tri_idx])                                        # draw each triangle with a diff color 
        for vertex in triangle:
            glVertex3fv(vertices[vertex])
        tri_idx += 1
    glEnd()

########################################### Exercise ####################################################
# TODO: Exercise 1: Draw a Tetrahedral
def draw_tetrahedral():
    # TODO: Construct the mesh using an Indexed Triangles mesh representation
    #           and store it using a list of lists
    # TODO: 4 vertices
    vertices = [ 
        [0, 0, 0],      # v0
        [10, 0, 10],    # v1 
        [20, 0, 0],     # v2
        [10, 20, 0]     # v3
    ]

    # TODO: 4 triangles, vertices of each triangle are in counter-clock order
    triangles = [ 
        [0, 1, 3], # left
        [3, 2, 1], # right
        [2, 0, 3], # back
        [1, 0, 2] # bottom
    ]
    
    # TODO: 4 edges, no order
    edges = [
        [0, 1], 
        [1, 2], 
        [2, 0], 
        [0, 3], 
        [1, 3], 
        [2, 3]
    ]
    
    # Draw all the 4 triangle FACES using GL_TRIANGLES
    # resotre the colors for all the faces in a list of tuples: [(r, g, b), (), ...]
    #   where r, g, b are floats [0., 1]
    # TODO: face colors
    colors = [
        (1, 0, 0),  # red
        (0, 1, 0),  # green
        (0, 0, 1),  # blue 
        (1, 1, 0),  # yellow
        (1, 1, 1)   # white
        
    ]
    # TODO: drawing triangles
    tri_idx = 0
    glBegin(GL_TRIANGLES)
    for triangle in triangles:
        glColor3fv(colors[tri_idx])
        for vertex in triangle:
            glVertex3fv(vertices[vertex])
        tri_idx += 1
    glEnd()

    # TODO: draw all the 4 edges in white with a line width of 5 using GL_LINES
    glLineWidth(5.0)
    glBegin(GL_LINES)
    glColor3fv(colors[4])
    for edge in edges:
        for vertex in edge:
            glVertex3fv(vertices[vertex])
    glEnd()

    return

# TODO: Exercise 2: Draw a Pyramid
def draw_pyramid():
    # TODO: Construct the pyramid using an Indexed Triangles mesh representation
    #       and store it using a list of lists
    # 5 vertices
    vertices = [

    ]

    # 6 triangle faces, vertices of each triangle are in counter-clock order
    triangles = [

    ]

    # 8 edges, no order
    edges = [

    ]

    # TODO: draw all the 6 triangles using GL_TRIANGLES
    # resotre the colors for all the faces in a list of tuples: [(r, g, b), (), ...]
    #   where r, g, b are floats [0., 1]
    # 6 triangle face colors
    colors = [

    ]
    # draw triangles


    # TODO: draw all the 8 edges in white with a line width of 5 using GL_LINES



    return

########################################### OpenGL Program ####################################################
def drawAxes():                                                             # draw x-axis and y-axis
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

def draw():
    glClearColor(0, 0, 0, 1)                                                # set background RGBA color 
    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)                        # clear the buffers initialized in the display mode
    #glEnable(GL_CULL_FACE)                                                  # enable front/back face culling
    #glCullFace(GL_BACK)                                                     # specify which face NOT drawing (culling)
    
    # Example 1: Draw Points
    # draw_vertices()

    # Example 2: Draw Edges
    #draw_edges()

    # Example 3: Draw Triangles
    #draw_triangles()

    #TODO: Exercise 1: Draw a Tetrahedral
    draw_tetrahedral()

    #TODO: Exercise 2: Draw a Pyramid
    #draw_pyramid()


def main():
    pygame.init()                                                           # initialize a pygame program
    glutInit()                                                              # initialize glut library 

    screen = (width, height)                                                # specify the screen size of the new program window
    display_surface = pygame.display.set_mode(screen, DOUBLEBUF | OPENGL)   # create a display of size 'screen', use double-buffers and OpenGL
    pygame.display.set_caption('CPSC 515: Meshes')                      # set title of the program window

    glEnable(GL_DEPTH_TEST)
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)                                             # set mode to projection transformation
    glLoadIdentity()                                                        # reset transf matrix to an identity
    glOrtho(-40, 40, -30, 30, 10, 80)                                       # specify an orthogonal-projection view volume

    glMatrixMode(GL_MODELVIEW)                                              # set mode to modelview (geometric + view transf)
    gluLookAt(0, 0, 50, 0, 0, 0, 0, 1, 0)                                   # set camera's eye, look-at, and view-up in the world
    initmodelMatrix = glGetFloat(GL_MODELVIEW_MATRIX)
    while True:
        bResetModelMatrix = False

        # user interface event handling
        for event in pygame.event.get():

            # quit the window
            if event.type == pygame.QUIT:
                pygame.quit()

            # mouse event
            if event.type == pygame.MOUSEMOTION:
                if pygame.mouse.get_pressed()[0]:
                    glRotatef(event.rel[1], 1, 0, 0)
                    glRotatef(event.rel[0], 0, 1, 0)

            # keyboard event
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_0:
                    bResetModelMatrix = True

        # reset the current model-view back to the initial matrix
        if (bResetModelMatrix):
            glLoadMatrixf(initmodelMatrix)
        
        draw()
        drawAxes()

        pygame.display.flip()
        pygame.time.wait(10)

main()