import pygame
from pygame.locals import *

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

import numpy as np

width, height = 800, 600                                                    # width and height of the screen created
bLaplacianSmoothing = False
########################################### Lecture examples ####################################################
# Tetrahedral Mesh
# Vertices
vertices = [[0, 0, 0],      # v0
            [10, 0, 10],    # v1
            [20, 0, 0],     # v2
            [10, 20, 0]     # v3
]

# Edges
edges = [
    [0, 1],
    [1, 2],
    [0, 2],
    [2, 3],
    [3, 0],
    [1, 3]
]

# Faces, vertices of each triangle are in CCW order
triangles = [
    [0, 2, 1],              # bottom
    [3, 1, 2],              # right
    [3, 0, 1],              # left
    [3, 2, 0]               # back
]

# Face colors
colors = [
    [1.0, 1.0, 0.0],        # yellow
    [0.0, 1.0, 0.0],        # green
    [1.0, 0.0, 0.0],        # red
    [0.0, 0.0, 1.0]         # blue  
]

########################################### Exercise ####################################################
# TODO: Laplacian Smoothing: Average
def laplacian_smoothing_avg():
    # TODO: Apply Laplacian smoothing on the vertex v3
    #       by taking the average of v0, v1, and v2
    global vertices
    # convert vertex list to numpy array for easier manipulation
    vertices = np.array(vertices)
    
    # store the indices of all the vertices that are adjacent to v3 in a list, neighbors
    neighbors = [0, 1, 2]

    # calculating the average position of the neighbors
    avg_pos = np.mean(vertices[neighbors], axis=0)

    # assign the average position to v3 (index 3)
    vertices[3] = avg_pos

    # convert back to list
    vertices = vertices.tolist()

    return

# TODO: Iterative Laplacian Smoothing with Lambda 
#       Apply Laplacian smoothing to vertex v3 in each step:
#           v3 = v3 + lambda_val * (avg(neighbors) - v3)
def laplacian_smoothing(lambda_val = 0.1):
    global vertices
    # convert vertex list to numpy array for easier manipulation
    vertices = np.array(vertices)
    
    # store the indices of all the vertices that are adjacent to v3 in a list, neighbors
    neighbors = [0, 1, 2]

    # apply Laplacian smoothing weighted with lambda
    avg_pos = np.mean(vertices[neighbors], axis=0)
    vertices[3] = vertices[3] + lambda_val * (avg_pos - vertices[3])

    # convert back to list
    vertices = vertices.tolist()   

    return

# Draw the Tetrahedral
def draw_tetrahedral(): 
    # Drawing triangles
    tri_idx = 0
    glBegin(GL_TRIANGLES)
    for triangle in triangles:
        glColor3fv(colors[tri_idx])
        for vertex in triangle:
            glVertex3fv(vertices[vertex])
        tri_idx += 1
    glEnd()

    # Draw all the 4 edges in white with a line width of 5 using GL_LINES
    glLineWidth(5.0)
    glColor3f(1, 1, 1)
    glBegin(GL_LINES)
    for edge in edges:
        for vertex in edge:
            glVertex3fv(vertices[vertex])
    glEnd()

    # Draw all the 4 points in white and size of 5 using GL_POINTS
    glColor3f(1.0, 1.0, 1.0)                                                # specify vertex color (r,g,b), white
    glPointSize(5.0)                                                       # specify point size
    glBegin(GL_POINTS)
    for vertex in vertices:
        glVertex3fv(vertex)
    glEnd()

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
    glEnable(GL_CULL_FACE)                                                  # enable front/back face culling
    glCullFace(GL_BACK)                                                     # specify which face NOT drawing (culling)
    
    # TODO: Apply Laplacian Smoothing (average) to the tetrahedral mesh
    # laplacian_smoothing_avg()

    # TODO: Apply Iterative Laplacian Smoothing with lambda 
    #       NOTE: Comment out `laplacian_smoothing_avg` before running
    if bLaplacianSmoothing:
        laplacian_smoothing(lambda_val=0.1)

    # Draw the Tetrahedral
    draw_tetrahedral()


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
        global bLaplacianSmoothing
        bLaplacianSmoothing = False

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
                elif event.key == pygame.K_l:
                    bLaplacianSmoothing = True

        # reset the current model-view back to the initial matrix
        if (bResetModelMatrix):
            glLoadMatrixf(initmodelMatrix)
        
        draw()
        drawAxes()

        pygame.display.flip()
        pygame.time.wait(10)

main()