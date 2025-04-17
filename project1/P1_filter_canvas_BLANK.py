import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from collections import namedtuple
import numpy as np
import P1_filter_utils_BLANK

# Task 2 - This function should return the gray value of a pixel 
#    by computing a weighted sum of its red, green, and blue components.
#    Recommend use the "luma method".
#    Return the gray value as np.uint8 
def rgbaToGray(color, method):
    # color = [r, g, b, a]
    if method not in ["luma", "avg", "light"]: 
        raise ValueError("Invalid option chosen for rgbaToGray() method parameter")

    # Option 1 - Luma Method: Weighted Sum 
    if method == "luma": grayColor = ((0.299 * color[0]) + (0.587 * color[1]) + (0.114 * color[2])).astype(np.uint8)

    # Option 2 - Average Method: Assigns Average
    elif method == "avg": grayColor = (sum(color[0:3]) / 3).astype(np.uint8)

    # Option 3 - Lightness Method: Desaturate image --> averages the least prominent and most prominent
    elif method == "light": grayColor = ((max(color[0:3]) + min(color[0:3])) / 2).astype(np.uint8)

    return [grayColor, grayColor, grayColor, 255]

# Define a Canvas for drawing an image
class Canvas:
    def __init__(self, width=500, height=500, pixel_size = 1):
        self.width = width
        self.height = height
        self.pixel_size = pixel_size

        # Initialize the canvas data
        self.data = []
        self.initCanvas()

        # Status of filter application
        self.b_filtered = False

    def initCanvas(self):
        canvas_color = (0, 0, 0, 255) # black color
        self.data = np.array([canvas_color] * (self.width * self.height), dtype=np.uint8)

    def load_image(self, image_path):
        image = pygame.image.load(image_path)
        image_width, image_height = image.get_size() # get image dimensions

        # update teh canvas dimensions to match the image's aspect ratio
        self.width = image_width
        self.height = image_height

        # scale the image to fit the updated canvas dimensions
        image = pygame.transform.scale(image, (self.width, self.height)) 
        image_data = pygame.image.tobytes(image, "RGBA", True)  # Convert to raw pixel data
        self.data = np.frombuffer(image_data, dtype=np.uint8).reshape(self.width * self.height, 4).copy()


    # Task 1 - Implement Grayscale Filter:
    #    Iterate through every pixel in the image (i.e., self.data)
    #    Convert each pixel color into a grayscale value
    #    Update the image (self.data) with the grayscale value (np.uint8)
    def filterGray(self, method):
        # iterate each pixel in the image
       for index, pixel in enumerate(self.data):
            # call rgbaToGray() to convert rbg into grayscale
            # update self.data by updating current pixel's color by setting r,g,b with the same grayscale value
            self.data[index] = rgbaToGray(pixel, method=method)


    # Task 3 - Implement Invert filter:
    #    Iterate through every pixel in the image (i.e., self.data)
    #    Inverting each color channel by subtracting its value from the maximum value, i.e., 255.
    #    Update the image (self.data) with the inverted r,g,b values (np.uint8)
    def filterInvert(self):
        # iterate each pixel in the image
        for index, pixel in enumerate(self.data):
            # invert each color component and Update self.data
            self.data[index] = (255 - self.data[index]).astype(np.uint8)
        


    # Task 4 & Task 5 - Implement Brighten filter:
    #    Iterate through every pixel in the image
    #    Increase each color channel by 30%
    #    Update the image with the brightened r, g, b values (np.uint8)
    def filterBrighten(self):
        # iterate each pixel in the image
        for index, pixel in enumerate(self.data):
            # increase each RGB channel by 30%, but still within [0, 255]
            newColor = pixel
            for index2, value in enumerate(pixel):
                # newColor[index2] = newColor[index2] * 1.3             # don't handle overflow
                newColor[index2] = min(255, newColor[index2] * 1.3)     # handle overflow
            # Update self.data 
            self.data[index] = newColor.astype(np.uint8)

    # Task 8 - Create an identity filter kernel and call convolve2D() from FilterUtils.py with it.
    #   If your kernel is correct, convolving with the identity kernel returns the original image.
    def filterIdentity(self, edge_pixel_method):
        # Create a 3x3 Identity kernel as a 1D list (row-major order)
        ''' [0, 0, 0]
            [0, 1, 0]
            [0, 0, 0]   '''
        kernel = [0, 0, 0, 0, 1, 0, 0, 0, 0] 

        # Convolve the identity kernel to the image
        P1_filter_utils_BLANK.convolve2D(data=self.data, width=self.width, height=self.height, kernel=kernel, edge_pixel_method=edge_pixel_method)


    # Task 9 - Create a Shift filter kernel
    """
    Goal: Applies a shift filter to self.data using 2D convolution.

    Args:
        shiftDir (str): "shiftLeft" or "shiftRight"
        num (int): Number of pixels to shift 
    """
    def filterShift(self, shiftDir, num, edge_pixel_method):
        # Create a shift kernel by calling `createShiftKernel()`
        kernel = P1_filter_utils_BLANK.createShiftKernel(shiftDir=shiftDir, num=num)

        # Apply 2d convolution using the shift kernel
        P1_filter_utils_BLANK.convolve2D(data=self.data, width=self.width, height=self.height, kernel=kernel, edge_pixel_method=edge_pixel_method)


    # Task 10 - Implement Edge Detection using Sobel operators (Separable kernels)
    def edgeDetection(self, sensitivity = 1, edge_pixel_method = 'Rep', threshold = None):
        debugging_prints = False
        # 1. Convert the input image (self.data) into grayscale using `filterGray()`
        self.filterGray(method="avg")
        
        # 2. Represent the separatable Sobel-x kernel (flipped) using a row vector and a column vector (list)
        sobel_x_row = [-1, 0, 1]
        sobel_x_col = [1, 2, 1]
        # sobel_x_row = [0, 1, 0]
        # sobel_x_col = [0, 1, 0]
        
        # 3. Represent the separatable Sobel-y kernel (flipped) using a row vector and a column vector (list)
        sobel_y_row = [1, 2, 1]
        sobel_y_col = [-1, 0, 1]
        # sobel_y_row = [0, 1, 0]
        # sobel_y_col = [0, 1, 0]

        # 4. Apply Sobel-x kernel, separated into a row vector and a column vector, to the original image using 1D convolution implemented in "P1_filter_utils.py"
        #      Store the processed image into, Gx, of the same size as the original image
        print("--Gx Convolution------------")
        Gx = P1_filter_utils_BLANK.convolve1D_rowFirst(data=self.data, width=self.width, height=self.height, row_kernel=sobel_x_row, column_kernel=sobel_x_col, edge_pixel_method="Rep")
        Gx = np.array(Gx, dtype=np.float32) # convert before we square (to deal with overflow)

        # 5. Apply Sobel-y kernel, separated into a row vector and a column vector, to the original image using 1D convolution implemented in "P1_filter_utils.py"
        #      Store the processed image into, Gy, of the same size as the original image
        print("--Gy Convolution------------")
        Gy = P1_filter_utils_BLANK.convolve1D_rowFirst(data=self.data, width=self.width, height=self.height, row_kernel=sobel_y_row, column_kernel=sobel_y_col, edge_pixel_method="Rep")
        Gy = np.array(Gy, dtype=np.float32) # convert before we square (to deal with overflow)

        # 6. Combine each the corresponding pixel values from Gx and Gy into G
        #      Apply sensibity parameter by multiplying it with G for each pixel color channel
        #      Then clamp the scaled gradient value to be [0,255]
        G = np.sqrt(np.add(np.square(Gx), np.square(Gy)))
        G = G * sensitivity
        G = np.clip(G, 0, 255).astype(np.uint8)

        # 7. Initialize a 1D numpy array (np.uint8), called 'result', of the same size as the input image, 
        canvas_color = (0, 0, 0, 255) # black color
        result = np.array([canvas_color] * (self.width * self.height), dtype=np.uint8)

        # 8. Calculate Threshold (if none was given)
        if threshold == None:
            threshold = np.median(G) * 0.5  # Use half the median value as the threshold
        print(f"Threshold={threshold}")

        # 9. Set those pixels in `result` whose corresponding values in G exceed the threshold with color white
        for index in range(len(G)):
            if G[index][0] > threshold:
                result[index] = (255, 255, 255, 255)

        # 10. Copy `result` to self.data 
        for index, element in enumerate(result):
            self.data[index] = element
        
        # debugging prints    
        if debugging_prints:   
            print(f"Gx Matrix-------------\n{Gx[:10]}")
            print(f"Gy Matrix-------------\n{Gy[:10]}")
            print(f"G Matrix-------------\n{G[:10]}")
            print(f"Result Matrix-------------\n{result[:10]}")
            print(f"Self.Data Matrix-------------\n{self.data[:10]}")




    # Task 13 - Implement Triangle Blur using a Triangle filter (separable kernels)
    def triangleBlur(self, kernel_size):
        # check if the input kernel size is valid (i.e., odd number, >= 3)
        if not ((kernel_size % 2 == 1) and (kernel_size >= 3)) :
            raise ValueError("The kernel size inputted for triangle blur is invalid.")

        # create a 1D triangle kernel based on kernel_size by calling `createTriangleFilter` from "P1_filter_utils.py"
        triangle_kernel = P1_filter_utils_BLANK.createTriangleKernel(kernel_size)
        print(f"--Triangle Kernel = {triangle_kernel}")
        # print(f"--Corresponding Box Kernel")
        # for row in triangle_kernel:
        #     print("[", end=" ")
        #     for col in triangle_kernel:
        #         print(f"{row*col:.2f}", end=" ")
        #     print("]", end="\n")

        # Apply two 1D triangle kernels sequentially to the image, self.data, using `convolve1D()` from "P1_filter_utils.py"
        result = P1_filter_utils_BLANK.convolve1D_rowFirst(self.data, self.width, self.height, row_kernel=triangle_kernel, column_kernel=triangle_kernel, edge_pixel_method="Rep")
        # print(f"--Result Matrix--------\n{result}")
        # print(f"--Data Matrix--------\n{self.data}")

        # Update self.data
        for index in range(len(result)):
            self.data[index] = result[index]


    # Task 15 - Implement Gaussian Blur using a Gaussian filter (separable kernels)
    def GaussianBlur(self, blur_radius):
        # create a 1D triangle kernel based on blur radius by calling `createGaussianFilter` from "P1_filter_utils.py"
        guassian_kernel = P1_filter_utils_BLANK.createGaussianKernel(blur_radius)
        print(f"--Gaussian Kernel = {guassian_kernel}")

        # Apply two 1D Gaussian kernels sequentially to the image, self.data, using `convolve1D()` from "P1_filter_utils.py"
        result = P1_filter_utils_BLANK.convolve1D_rowFirst(self.data, self.width, self.height, row_kernel=guassian_kernel, column_kernel=guassian_kernel, edge_pixel_method="Rep")

        # Update self.data
        for index in range(len(result)):
            self.data[index] = result[index]