import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import numpy as np

# Draw an image using OpenGL functions
def draw_image(pixels, pixel_size, width, height, show_grid = False):
    # Draw the pixels 
    for index, pixel in enumerate(pixels):
        row_idx = index // width
        col_idx = index % width
        glColor4ub(pixel[0], pixel[1], pixel[2], pixel[3])
        x = -1 + col_idx * pixel_size / 250.0  # Map to [-1, 1] in X
        y = -1 + row_idx * pixel_size / 250.0  # Map to [-1, 1] in Y
        glRectf(x, y, x + pixel_size / 250.0, y + pixel_size / 250.0)

    # Draw grid lines
    if show_grid == True:
        draw_gridline(width=width, height=height, pixel_size=pixel_size)

# Draw the grid lines on canvas (optional)
def draw_gridline(width, height, pixel_size):
    glColor3f(0.5, 0.5, 0.5)  # Grid line color (dark gray)
    for row_idx in range(height + 1):
        y = -1 + row_idx * pixel_size / 250.0
        glBegin(GL_LINES)
        glVertex2f(-1, y)
        glVertex2f(1, y)
        glEnd()
    for col_idx in range(width + 1):
        x = -1 + col_idx * pixel_size / 250.0
        glBegin(GL_LINES)
        glVertex2f(x, -1)
        glVertex2f(x, 1)
        glEnd()


# Define a Canvas for drawing an image
class Canvas:
    def __init__(self, width=500, height=500, pixel_size = 1, canvas_type="randomColor", show_grid = False):
        self.width = width
        self.height = height
        self.pixel_size = pixel_size
        self.canvas_type = canvas_type
        self.show_grid = show_grid

        # Initialize the canvas data (list of RGBA namedtuples)
        self.data = []
        if canvas_type == "color":
            self.initColorCanvas()
        elif canvas_type == "grayscale":
            self.initGrayCanvas()
            self.show_grid = True
        elif canvas_type == "randomColor":
            self.data = [(r, g, b, 255) for r, g, b in ((np.random.randint(0, 256), np.random.randint(0, 256), np.random.randint(0, 256)) for _ in range(width * height))]

    # Function to convert intensity (float, [0, 1]) to an integer [0 - 255]
    #   Return grayscale as an integer
    def floatToInt(self, intensity):
        grayscale = 0 # initialize variable grayscale
        # TODO: Task 1.1: Write your code below


        return grayscale

    # Function to convert (row, column) coordinates 
    #   into an index in a 1D array in row-majored order
    #   Return index
    def posToIndex(self, row, column):
        index = 0 # initialize variable index

        # TODO: Task 2.1: Write your code below


        return index 

    # Initialize the canvas data with grayscale (int, [0 - 255])
    def initGrayCanvas(self):
        # TODO: Task 1.2: Write your code below
        intensity = 0.123 # TODO: Task 1.4: Modify this to see the difference in grayscale
 
        
        # TODO: Task 2.3: call your function `createHeart()` below


    # Initialize the canvas data with RGBA color data
    def initColorCanvas(self):
        constant_color = (0, 123, 123, 255) # (r,g,b,a)
        # TODO: Task 4.1: Write your code below


    # Function to create a heart on a grayscale image
    #   Modify specific pixels in self.data by set the intensity to 1.0 so it draws a heart 
    def createHeart(self):
        # TODO: Task 2.2: Write your code below


        return 0 # you may remove this

    # Function to draw a flower centered onthe input position
    def draw_flower(self, x, y):
        # TODO: Task 5.1: Write your code below



        return 0 # you may remove this

    # Function to render the image on the canvas using OpenGL
    def render(self):
        draw_image(pixels=self.data, pixel_size=self.pixel_size, width=self.width, height=self.height, show_grid=self.show_grid)
        

