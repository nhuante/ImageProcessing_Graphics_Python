import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import numpy as np


# Define a Canvas for drawing an image
class Canvas:
    def __init__(self, width=500, height=500, pixel_size = 1):
        self.width = width
        self.height = height
        self.pixel_size = pixel_size

        # Initialize the canvas data
        self.data = []
        self.initCanvas()

        # brush related variables
        self.brush_radius = 1
        self.brush_size = 3                 # mask's height or width (equal); TODO: update its value based on brush_radius in the code below
        self.brush_color = (0, 0, 0, 255)   # black brush by default
        self.brush_mask = []                # use a 1D array of brush_size * brush_size to store mask data

    def initCanvas(self):
        canvas_color = (255, 255, 255, 255) # background color
        self.data = np.array([canvas_color] * (self.width * self.height), dtype=np.uint8)
    
    def initBrush(self, brush_radius, brush_color, brush_type):
        self.brush_radius = brush_radius
        self.brush_color = brush_color

        # TODO: Calculate self.brush_size based on brush_radius

        
        # Initialize a mask of different distributions based on brush type
        if brush_type == "constant":
            self.brush_mask = self.createConstantBrushMask()
        elif brush_type == "linear":
            self.brush_mask = self.createLinearBrushMask()
        elif brush_type == "quadratic":
            self.brush_mask = self.createQuadraticBrushMask()


    # TODO: Create a constant brush mask of brush_size x brush_size, 
    #       Populate the mask with 1s where the distance is within the radius and 0s elsewhere 
    #       Return the mask as a 1D array (float)
    def createConstantBrushMask(self):
        # initialize the mask as an empty 2D array of brush_size x brush_size
        mask = np.zeros((self.brush_size, self.brush_size), dtype=float)
        
        # TODO: iterate and fill up the mask

        # TODO: flatten the mask into a 1D array

        return [] # TODO: return the mask in a 1D array 
    

    # TODO: Create a linear brush mask of brush_size x brush_size,
    #       Linearly descrease the value at each pixel as moving away from the center (1.0)
    #           and the values at the edge is 0.
    #       Return the mask as a 1D array (float)
    def createLinearBrushMask(self):
        # initialize the mask as an empty 2D array of brush_size x brush_size
        mask = np.zeros((self.brush_size, self.brush_size), dtype=float)
        
        # TODO: iterate and fill up the mask based on f(d)

        # TODO: flatten the mask into a 1D array

        return [] # TODO: return the mask in a 1D array 
    

    # TODO: Create a quadratic brush mask of brush_size x brush_size,
    #           value at each pixel: f(d) = A * d^2 + B * d + C
    #             (You may first calculate A, B, and C based on the given 3 conditions)
    #       Return the mask as a 1D array (float)
    def createQuadraticBrushMask(self):       
        # initialize the mask as an empty 2D array of brush_size x brush_size
        mask = np.zeros((self.brush_size, self.brush_size), dtype=float)
        
        # TODO: list the parameters A, B, C for f(d)
        
        # TODO: iterate and fill up the mask based on f(d)

        # TODO: flatten the mask into a 1D array

        return [] # TODO: return the mask in a 1D array 
    

    # TODO: Apply brush_mask, centered at (canvas_x, canvas_y), to the canvas 
    #           by iterating over the mask and apply the brush color to the canvas
    #       For each pixel color, mixing colors of brush and canvas based on the values (weights) stored in the mask
    #       Make sure you update self.data with the mixed color at the end. 
    #       Hint: When mixing colors, convert each channel from uint8 [0, 255] to float [0.0, 1.0] first
    #        and remember to convert it back to np.uint8 before updating self.data
    def apply_brush(self, canvas_x, canvas_y):
        
        

        return 0 # you may remove this once completing the function
                

    
