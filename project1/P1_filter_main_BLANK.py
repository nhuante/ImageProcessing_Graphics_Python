import os
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLUT import *  # Import GLUT for text rendering
from OpenGL.GLUT import GLUT_BITMAP_HELVETICA_18  # Import GLUT for text rendering
import numpy as np
import time

from P1_filter_canvas_BLANK import Canvas
from P1_filter_GUI_BLANK import UI

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

def draw_canvas(texture_id, canvas_width, canvas_height, canvas_x_offset, canvas_y_offset):
    glColor3f(1.0, 1.0, 1.0)  # Reset color to white
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, texture_id)
    glBegin(GL_QUADS)
    glTexCoord2f(0, 0); glVertex2f(canvas_x_offset, canvas_y_offset)
    glTexCoord2f(1, 0); glVertex2f(canvas_x_offset + canvas_width, canvas_y_offset)
    glTexCoord2f(1, 1); glVertex2f(canvas_x_offset + canvas_width, canvas_y_offset + canvas_height)
    glTexCoord2f(0, 1); glVertex2f(canvas_x_offset, canvas_y_offset + canvas_height)
    glEnd()
    glDisable(GL_TEXTURE_2D)

def draw_button(x, y, width, height, color):
    glColor3f(*color)
    glBegin(GL_QUADS)
    glVertex2f(x, y)
    glVertex2f(x + width, y)
    glVertex2f(x + width, y + height)
    glVertex2f(x, y + height)
    glEnd()

def draw_text(x, y, text, font_size, color):
    glColor3f(*color)
    glRasterPos2f(x, y)
    for char in text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))

def is_button_clicked(mouse_x, mouse_y, button_x, button_y, button_width, button_height):
    return button_x <= mouse_x <= button_x + button_width and button_y <= mouse_y <= button_y + button_height

def main():
    pygame.init()                                                                                               # initialize a pygame program
    window_width, window_height = 600, 800                                                                      # specify the screen size of the pygame window
    screen = pygame.display.set_mode((window_width, window_height), DOUBLEBUF | OPENGL)                         # create a display of size 'screen', use double-buffers and OpenGL
    pygame.display.set_caption('CPSC515: Filters - NATALIE HUANTE')  
    glutInit()                                                # set title of the program window
    
    # Set up the OpenGL viewport and projection
    glViewport(0, 0, window_width, window_height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0, window_width, 0, window_height, -1, 1)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    # Initialize the canvas based on input image
    canvas = Canvas(pixel_size=1)
    # image_path = os.path.join("./resources/imgs/", "5x5Tester.png")   # 5x5 Pixel Tester
    # image_path = os.path.join("./resources/imgs/", "wimdy.jpg")       # Wimdy Fox
    # image_path = os.path.join("./resources/imgs/", "capybara.jpeg")   # Capybara
    # image_path = os.path.join("./resources/imgs/", "pinwheel.png")    # pinwheel
    # image_path = os.path.join("./resources/imgs/", "mona_lisa.jpg")   # mona lisa
    # image_path = os.path.join("./resources/imgs/", "amongus.jpg")     # among us
    image_path = os.path.join("./resources/imgs/", "cat.jpeg")     # cat

    if os.path.exists(image_path):
        canvas.load_image(image_path)
        print(f"Image size: {canvas.width} X {canvas.height}")
    else:
        print(f"Image file not found: {image_path}")

    texture_id = initialize_texture(canvas=canvas)

    # calculate the margins between the canvas and the display window
    canvas_x_offset = (window_width - canvas.width) // 2
    canvas_y_offset = (window_height - canvas.height) // 2


    # Initialize GUI with all buttons for the filters
    ui = UI(win_width=window_width, win_height=window_height)
    grayButton = ui.grayFilterButton
    invertButton = ui.invertFilterButton
    brightenButton = ui.brightenFilterButton
    shiftButton = ui.shiftFilterButton                                                                          # shared by both Shift filter and identity filter
    edgeButton = ui.edgeDetectionButton
    blurButton = ui.blurButton                                                                                  # shared by both Triangle blur and Gaussian blur
    revertButton = ui.revertButton
    statusButton = ui.statusButton
    
    # For shift filter use
    '''
    Switch between different edge-pixel handling methods:
    `edge_pixel_method`:
    - 'Rep': use `getPixelRepeated` method
    - 'Ref': use `getPixelReflected` method
    - 'Wra': use `getPixelWrapped` method
    '''
    edge_pixel_method = 'Wra'   # NOTE: Switch different edge-pixel handling methods here
    shiftDir = 'shiftLeft'      # NOTE: set shift direction here
    num = 5                     # NOTE: set shift pixel number each time here
    # END

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            
            elif event.type == MOUSEBUTTONDOWN and event.button == 1:                                           # Left mouse button is pressed down
                mouse_x, mouse_y = pygame.mouse.get_pos()
                mouse_y = window_height - mouse_y                                                               # Convert to pixel coordinates on the screen
                
                # check which filter button has been pressed
                if revertButton.is_clicked(mouse_x=mouse_x, mouse_y=mouse_y):
                    revertButton.pressing = True
                    print("Revert to Orignal: Start...")
                    canvas.load_image(image_path)
                    # startTime = time.time()
                    update_texture(texture_id=texture_id, canvas=canvas)
                    # print(f"## Time to Execute: {(time.time() - startTime):.4f}")
                    print("Revert to Orginal: Done!")

                elif grayButton.is_clicked(mouse_x=mouse_x, mouse_y=mouse_y):
                    grayButton.pressing = True
                    print("Apply Grayscale Filter: Start...")
                    startTime = time.time()
                    method = "light"        # choose 'luma', 'avg', 'light'
                    canvas.filterGray(method=method)
                    update_texture(texture_id=texture_id, canvas=canvas)
                    print(f"## Time to Execute: {(time.time() - startTime):.4f}")
                    print("Apply Grayscale Filter: Done!")
                    statusButton.label += "+Grayscale"

                elif invertButton.is_clicked(mouse_x=mouse_x, mouse_y=mouse_y):
                    invertButton.pressing = True
                    print("Apply Invert Filter: Start...")
                    startTime = time.time()
                    canvas.filterInvert()
                    update_texture(texture_id=texture_id, canvas=canvas)
                    print(f"## Time to Execute: {(time.time() - startTime):.4f}")
                    print("Apply Invert Filter: Done!")
                    statusButton.label += "+Invert"

                elif brightenButton.is_clicked(mouse_x=mouse_x, mouse_y=mouse_y):
                    brightenButton.pressing = True
                    print("Apply Brighten Filter: Start...")
                    startTime = time.time()
                    canvas.filterBrighten()
                    update_texture(texture_id=texture_id, canvas=canvas)
                    print(f"## Time to Execute: {(time.time() - startTime):.4f}")
                    print("Apply Brighten Filter: Done!")
                    statusButton.label += "+Brighten"

                elif shiftButton.is_clicked(mouse_x=mouse_x, mouse_y=mouse_y):
                    shiftButton.pressing = True
                    print(f"Apply {shiftButton.label} Filter: Start...")
                    startTime = time.time()

                    # Switch identity and shift filter kernels here
                    #=== Identity filter
                    # canvas.filterIdentity(edge_pixel_method=edge_pixel_method)
                    # statusButton.label += "Identity kernel"
                    #=== Identity - end

                    #=== Shift filter 
                    canvas.filterShift(shiftDir=shiftDir, num=num, edge_pixel_method=edge_pixel_method)
                    statusButton.label += "+Shift kernel-" + edge_pixel_method
                    #=== Shift - end

                    update_texture(texture_id=texture_id, canvas=canvas)
                    print(f"## Time to Execute: {(time.time() - startTime):.4f}")
                    print(f"\nApply {shiftButton.label} Filter: Done!")

                elif edgeButton.is_clicked(mouse_x=mouse_x, mouse_y=mouse_y):
                    edgeButton.pressing = True
                    print("Apply Edge Detection: Start...")
                    startTime = time.time()
                    sensitity = 1 # set sensitivity (0, 1] here
                    threshold = 20 # try out different thresholds here, if none it will be auto-calculated
                    canvas.edgeDetection(sensitivity=sensitity, threshold=threshold)
                    update_texture(texture_id=texture_id, canvas=canvas)
                    print(f"## Time to Execute: {(time.time() - startTime):.4f}")
                    print("Apply Edge Detection: Done!")
                    statusButton.label += "+Sobel Kernel"

                elif blurButton.is_clicked(mouse_x=mouse_x, mouse_y=mouse_y):
                    blurButton.pressing = True
                    blurKernel = "Triangle" # NOTE: Switch the blur kernel here; "Triangle" or "Gaussian"
                    print("Apply Image Blur: Start...")
                    startTime = time.time()
                    if blurKernel == "Triangle":
                        kernel_size = 29 # NOTE: Set triangle kernel size here
                        canvas.triangleBlur(kernel_size=kernel_size)
                        statusButton.label += "+Triangle Kernel"
                    elif blurKernel == "Gaussian":
                        blur_radius = 7 # NOTE: Set blur radius here
                        canvas.GaussianBlur(blur_radius=blur_radius)
                        statusButton.label += "+Gaussian Kernel"
                    update_texture(texture_id=texture_id, canvas=canvas)
                    print(f"## Time to Execute: {(time.time() - startTime):.4f}")
                    print("Apply Image Blur: Done!")
            
            elif event.type == MOUSEBUTTONUP and event.button == 1:                                             # Left mouse button release
                ## reset button status
                # "revert to origin" button
                if revertButton.pressing == True:
                    revertButton.pressing = False
                    grayButton.pressed = False
                    invertButton.pressed = False
                    brightenButton.pressed = False
                    shiftButton.pressed = False
                    edgeButton.pressed = False
                    blurButton.pressed = False
                    statusButton.label = "Filter Type: "
                # grayscale button
                if grayButton.pressing == True:
                    grayButton.pressing = False
                    grayButton.pressed = True
                # invert button
                if invertButton.pressing == True:
                    invertButton.pressing = False
                    invertButton.pressed = True
                # brighten button
                if brightenButton.pressing == True:
                    brightenButton.pressing = False
                    brightenButton.pressed = True
                # shift button
                if shiftButton.pressing == True:
                    shiftButton.pressing = False
                    shiftButton.pressed = True
                # edge detection button
                if edgeButton.pressing == True:
                    edgeButton.pressing = False
                    edgeButton.pressed = True
                # blur button
                if blurButton.pressing == True:
                    blurButton.pressing = False
                    blurButton.pressed = True


        glClear(GL_COLOR_BUFFER_BIT)

        # Draw canvas
        draw_canvas(texture_id=texture_id, canvas_width=canvas.width, canvas_height=canvas.height, 
                    canvas_x_offset=canvas_x_offset, canvas_y_offset=canvas_y_offset)

        # Draw buttons with dynamic colors
        revertButton.draw_button()
        statusButton.draw_button()
        grayButton.draw_button()
        invertButton.draw_button()
        brightenButton.draw_button()
        shiftButton.draw_button()
        edgeButton.draw_button()
        blurButton.draw_button()
        
        # refresh the drawing
        glFlush()
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
