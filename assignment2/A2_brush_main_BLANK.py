import pygame
from pygame.locals import *
from OpenGL.GL import *

from A2_brush_canvas_BLANK import Canvas

def initialize_texture(canvas):
    # Convert the array of Pixel containers into a flat numpy array
    flat_image_data = canvas.data.flatten()

    texture_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture_id)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    
    # Initialize the texture with flattened canvas data
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, canvas.width, canvas.height, 0, GL_RGBA, GL_UNSIGNED_BYTE, flat_image_data)
    return texture_id

def update_texture(texture_id, canvas):
    # Convert the array of Pixel containers into a flat numpy array
    flat_image_data = canvas.data.flatten()

    glBindTexture(GL_TEXTURE_2D, texture_id)
    glTexSubImage2D(GL_TEXTURE_2D, 0, 0, 0, canvas.width, canvas.height, GL_RGBA, GL_UNSIGNED_BYTE, flat_image_data)


def draw_canvas(texture_id):
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, texture_id)
    #glEnable(GL_BLEND)
    #glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    glBegin(GL_QUADS)
    glTexCoord2f(0, 0); glVertex2f(-1, -1)
    glTexCoord2f(1, 0); glVertex2f(1, -1)
    glTexCoord2f(1, 1); glVertex2f(1, 1)
    glTexCoord2f(0, 1); glVertex2f(-1, 1)
    glEnd()
    glDisable(GL_TEXTURE_2D)

def main():
    pygame.init()                                                                                   # initialize a pygame program
    width, height = 600, 600                                                                        # specify the screen size of the pygame window
    screen = pygame.display.set_mode((width, height), DOUBLEBUF | OPENGL)                           # create a display of size 'screen', use double-buffers and OpenGL
    pygame.display.set_caption('CPSC515: Brushes - YOUR NAME')                                      # set title of the program window
    
    
    # Set up the OpenGL viewport and projection
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(-1, 1, -1, 1, -1, 1)                                                                    # Set up a simple orthographic projection
    glMatrixMode(GL_MODELVIEW)
    
    # Create a canvas and brush
    canvas = Canvas(width=width, height=height, pixel_size=1)                                       # Initialize a canvas of the same resolution as the pygame window
    texture_id = initialize_texture(canvas=canvas)
    brush_color = (255, 0, 0, 255) # R,G,B,A
    brush_radius = 30
    canvas.initBrush(brush_radius=brush_radius, brush_color=brush_color,brush_type="constant")      # TODO: switch brush_type here

    glClearColor(1.0, 1.0, 1.0, 1.0)  # White background

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == MOUSEMOTION:
                if pygame.mouse.get_pressed()[0]:  # Left mouse button pressed
                    x, y = pygame.mouse.get_pos()
                    # Map mouse to canvas coordinates
                    canvas_x = int(x / width * width)
                    canvas_y = int((height - y) / height * height)
                    
                    # apply selected brush to the canvas
                    canvas.apply_brush(canvas_x=canvas_x, canvas_y=canvas_y)
                
                    update_texture(texture_id=texture_id, canvas=canvas)

        glClear(GL_COLOR_BUFFER_BIT)
        draw_canvas(texture_id)
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
