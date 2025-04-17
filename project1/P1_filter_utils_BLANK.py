import numpy as np
import math 

#============ Task 7 - Implement Different Methdos for Out-Of-Bounds Pixels
'''
README: getPixelRepeated(), getPixelReflected(), and getPixelWrapped() all
have the same input arguments:
- data:     the image's data
- width:    the image's width
- height:   the image's height
- x:        the x coordinate of the pixel you are attempting to access
- y:        the y coordinate of the pixel you are attempting to access
'''

# Repeats the pixel on the edge of the image such that A,B,C,D looks like ...A,A,A,B,C,D,D,D...
# Return the pixel at (new_x, new_y)
def getPixelRepeated(data, width, height, row, col):
    new_row = 0 if row < 0 else min(row, height - 1)
    new_col = 0 if col < 0 else min(col, width - 1)
    pixelToReturn_Index = int(twoDimenToSingleDimenIndex(new_row, new_col, width))
    # print(f"\t\t\tGrabbing image pixel at Position R:{new_row}, C:{new_col} --> 1D Index: {pixelToReturn_Index}") # use for debugging
    return data[pixelToReturn_Index]

# Reflect pixel values about the edge of the image such that A,B,C,D looks like ...C,B,A,B,C,D,C,B...
# Return the pixel at (new_x, new_y)
def getPixelReflected(data, width, height, row, col):
    ''' idea: get the difference from the last row/column to the intended. 
        then, backtrack that num of steps. 
        ex: if one column to the right of the last column in the image, backtrack 1 column inwards from the last column 
            we should get the second to last column 
    '''
    new_row = -1
    new_col = -1
    # new row 
    if row < 0: # below the image
        new_row = -1 * row 
    elif row > height - 1: # above the image
        new_row = (height - 1) - (row - (height - 1))
    else: # within the image 
        new_row = row 
    
    # new col 
    if col < 0: # left of image 
        new_col = -1 * col 
    elif col > width - 1: # right of image 
        new_col = (width - 1) - (col - (width - 1))
    else: # within the image 
        new_col = col 

    pixelToReturn_Index = int(twoDimenToSingleDimenIndex(new_row, new_col, width))
    return data[pixelToReturn_Index]


# Wrap the image such that A,B,C,D looks like ...C,D,A,B,C,D,A,B
# Return the pixel at (new_x, new_y)
def getPixelWrapped(data, width, height, row, col):
    '''idea: get the difference between from the last row/column to the intended - 1
        take that many steps to the right starting from the first column of the image 
        ex: if one column to the right of the last column in the image, we should calc diff of 1 - 1 = 0 
            starting from column 0, take 0 steps, so we end up at that column'''
    
    new_row = -1
    new_col = -1
    # new row 
    if row < 0: # below the image
        new_row = height + row 
    elif row > height - 1: # above the image
        new_row = row % height
    else: # within the image 
        new_row = row 
    
    # new col 
    if col < 0: # left of image 
        new_col = width + col 
    elif col > width - 1: # right of image 
        new_col = col % width 
    else: # within the image 
        new_col = col 

    pixelToReturn_Index = int(twoDimenToSingleDimenIndex(new_row, new_col, width))
    # print(f"\t\t\tGrabbing image pixel at Position R:{new_row}, C:{new_col} --> 1D Index: {pixelToReturn_Index}") # use for debugging
    return data[pixelToReturn_Index]
    

#============ END Task 7

'''Helper Functions Added From Assignment 2'''
# Function to convert (row, column) coordinates 
#   into an index in a 1D array in row-majored order
#   Return index
def twoDimenToSingleDimenIndex(row, column, width):
    index = 0 # initialize variable index

    if row == 0:
        index = column 
    else:
        highest_index_in_row_below = (width * (row)) - 1
        index = highest_index_in_row_below + (column + 1)
    # print("the index is: ", index)
    return index 

def singleDimenToTwoDimenIndex(index, width, height):
    row = index // width 
    column = index - (row * width)

    return row, column 

# Task 6 - Implement Convolve2D
'''
Switch between different edge-pixel handling methods:
`edge_pixel_method`:
- 'Rep': use `getPixelRepeated` method
- 'Ref': use `getPixelReflected` method
- 'Wra': use `getPixelWrapped` method
'''
def convolve2D(data, width, height, kernel, edge_pixel_method):
    # 0. Debugging Print Help 
    debugging_prints = False            # when True will print info about the matrices
    debugging_per_pixel = False         # when True will print out the process of the first 3 pixels
    debugging_kernel_flip = False       # when True will print out the process of flipping the kernel

    # 1. Initialize a 1D numpy array (np.uint8), called 'result', to temporarily store your output image data
    canvas_color = (0, 0, 0, 255) # black color
    result = np.array([canvas_color] * (width * height), dtype=np.uint8)

    if debugging_prints:
        print(f"Result Initial: \n{result}")

    # 0. kernel info
    kernel_width = (math.sqrt(len(kernel)))         # width of the entire kernel
    kernel_side_length =  kernel_width // 2         # side length of the kernel (aka from the center to the edge)
    kernel_center = kernel_side_length              # the row and col value of the center element of the kernel
    if debugging_prints:
        print(f"Kernel Total Width: {kernel_width}, Kernel Side: {kernel_side_length}, Kernel Center Index: {kernel_center}")

    # 2. Rotate the kernel by 180 - think of a clever way to flip the kernel through indexing
    if debugging_prints:
        print("Original Kernel:\n", kernel)
    new_kernel = []
    for element in kernel:
        new_kernel.append(element)

    for index, element in enumerate(kernel):
        # convert the 1d index of the kernel element to a 2d position of row and col
        current_row, current_column = singleDimenToTwoDimenIndex(index, kernel_width, kernel_width)

        # calculate the new and column positions 
        new_row = int(kernel_width - current_row - 1)
        new_column = int(kernel_width - current_column - 1)

        # convert new 2d position to 1d index 
        new_index = int(twoDimenToSingleDimenIndex(new_row, new_column, kernel_width))

        # move the element to the new 1d index
        new_kernel[new_index] = element
       
       # debugging help
        if debugging_kernel_flip:
            print(f"- kernel element at index {index} --> R: {current_row}, C: {current_column}, Elem: {element} -> NewR: {new_row}, NewC: {new_column} --> newIndex: {new_index}")

    # 2b. once all elements have been moved properly, update the kernel with it's flipped equivalent
    for index, element in enumerate(new_kernel):
        kernel[index] = element
        
    if debugging_prints:
        print("New Kernel:\n", kernel)

    printDetails = False
    # 3. having the flipped kernel, iterate through the image and do the convolution
    for row in range(height):
        # see progress of the convolution in the terminal
        if row % 100 == 0:
            print(f"--- row: {row}", flush=True)
        
        for col in range(width):
            # debugging help 
            if debugging_per_pixel:
                if row == 0 and col < 3:
                    printDetails = True
                else:
                    printDetails = False
            
            # a. get the index of the current pixel in row-major order
            index = width * row + col 

            # b. Initialize redAcc, greenAcc, and blueAcc to store accumulated color channels, float
            redAcc = float(0)
            greenAcc = float(0)
            blueAcc = float(0) 

            # c. Iterate over the kernel using its dimensions
            for kernelIndex, kernelWeight in enumerate(kernel):
                    if kernelWeight == 0:
                        continue
                    if printDetails:
                        print(f"\t\t-- Kernel Index: {kernelIndex}", end=", ")

                    # i. get the current kernel element's 2D index 
                    kernelRow, kernelCol = singleDimenToTwoDimenIndex(kernelIndex, kernel_width, kernel_width)
                    if printDetails:
                        print(f"2D position Within Kernel R:{kernelRow}, C:{kernelCol} has weight {kernelWeight}")

                    # ii. get the distance in rows and cols from the center of kernel to the current kernel element 
                    rowDiff = kernelRow - kernel_center
                    colDiff = kernelCol - kernel_center
                    if printDetails:
                        print(f"\t\t\tDistance from center of kernel is {rowDiff} rows, {colDiff} cols")

                    # iii. get the equivalent image pixel that would correspond to the current kernel element 
                    imagePixelMatch_x = row + rowDiff
                    imagePixelMatch_y = col + colDiff
                    if printDetails:
                        print(f"\t\t\tImage Pixel Match Would Be At R:{imagePixelMatch_x}, C:{imagePixelMatch_y}")

                    # iv. Get the pixel at (img_x, img_y) by handling out-of-bounding pixels - switch between 'Rep', 'Ref', 'Wra' here
                    if edge_pixel_method == "Rep":
                        imagePixelMatch_value = getPixelRepeated(data, width, height, imagePixelMatch_x, imagePixelMatch_y)
                    elif edge_pixel_method == "Ref":
                        imagePixelMatch_value = getPixelReflected(data, width, height, imagePixelMatch_x, imagePixelMatch_y)
                    elif edge_pixel_method == "Wra":
                        imagePixelMatch_value = getPixelWrapped(data, width, height, imagePixelMatch_x, imagePixelMatch_y)

            
                    # v. Accumulate `weight * pixel` for each channel in redAcc, greeAcc, and blueAcc accordingly
                    redAcc += kernelWeight * imagePixelMatch_value[0]
                    greenAcc += kernelWeight * imagePixelMatch_value[1]
                    blueAcc += kernelWeight * imagePixelMatch_value[2]

                    if printDetails:
                        print(f"\t\t\tAccum. RGB Values: ({redAcc}, {greenAcc}, {blueAcc})")

            # d. make sure our new RGB values are of correct type
            redAcc = redAcc.astype(np.uint8)
            greenAcc = greenAcc.astype(np.uint8)
            blueAcc = blueAcc.astype(np.uint8)
            
            # debugging help
            if printDetails:
                print(f"\n~  New Color Value: ({redAcc}, {greenAcc}, {blueAcc})")
                print(f"~  Old Color Value: {data[index]}\n\n")

            # e. update the pixel in result with the new RGB values
            result[index][0] = redAcc
            result[index][1] = greenAcc
            result[index][2] = blueAcc
    
    # 4. Copy the RGBA data from `result` to `data`
    for index in range(len(result)):
        data[index] = result[index]


# Task 9 - Create a shift kerenl
'''
Goal: Create a 2D kernel that shifts an image `num` pixels in the given direction `shiftDir`

Args:
    shiftDir (str): "shiftLeft" or "shiftRight"
    num (int): Number of pixels to shift

Returns:
    shift kernel as a 1D list (row-major)
'''
def createShiftKernel(shiftDir, num):
    if shiftDir not in ["shiftLeft", "shiftRight"]:
        raise ValueError("shiftDir must be 'shiftLeft' or 'shiftRight'")

    # Determine kernel size (odd-numbered)
    kernel_width = (2 * num) + 1

    # Initialize kernel as a 1D array with zeros
    kernel = [0 for _ in range(kernel_width ** 2)]
    # print(f"Kernel Shift {num} pixels, Kernel (size {len(kernel)}):")

    # Set `1` at a proper position based on `shiftDir` and `num`
    center_pixel = kernel_width // 2
    if shiftDir == "shiftLeft": # 1 goes on the left-most column 
        pixel_to_one = twoDimenToSingleDimenIndex(center_pixel, 0, kernel_width)
    else: # 1 goes on the right-most column 
        pixel_to_one = twoDimenToSingleDimenIndex(center_pixel, kernel_width - 1, kernel_width)
    kernel[pixel_to_one] = 1

    # Return the kernel 
    # print(kernel)
    # print(f"Kernel Size {num}")
    # print(f"....printing nicely.....")
    # for index, weight in enumerate(kernel): 
    #     if (index + 1) % kernel_width == 0 :
    #         print(weight, "\n")
    #     else: print(weight, end = " ")
    return kernel

    

# Task 11 - Implement Convolve1D with the row and column kernels from 
#                a separable 2D kernel on the input image (i.e., `data`)
def convolve1D_rowFirst(data, width, height, row_kernel, column_kernel, edge_pixel_method = 'Rep'):
    # printing bools 
    printing = True
    data = np.array(data, dtype=np.int16) # convert to int16 to allow for neg numbers

    # 1. initialize a 1D array, `result`, to stored the processed image data
    canvas_color = (0, 0, 0, 255) # black color
    result = np.array([canvas_color] * (width * height), dtype=np.int16)

    # 2. Slide row_kernel horizontally to each row of the input image (padded, using repeated method) 
    #           from top to bottom row and then update `result`
    #           - NOTE: Use the original image `data` for this convolution
    kernel_center = len(row_kernel) // 2
    print("---Applying Row Kernel---------")
    # a. for each pixel in the image
    for row in range(height):
        if printing and row % 100 == 0:
            print(f"--- row: {row}")

        for col in range(width):
            # b. reset the new pixel value for every pixel
            new_pixel_value = [0, 0, 0]

            # c. for each value in the kernel, multiply the weight by the corresponding pixel
            for index, kernel_value in enumerate(row_kernel):
                # i. skip any kernel elements that have weight 0 
                if kernel_value == 0:
                    continue
                # ii. get the distance from center kernel pixel
                distance_from_center = index - kernel_center
                # iii. get the corresponding neighbor based on edge pixel method
                if edge_pixel_method == "Rep":
                    imagePixelMatch_value = getPixelRepeated(data, width, height, row, col + distance_from_center)
                elif edge_pixel_method == "Ref":
                    imagePixelMatch_value = getPixelReflected(data, width, height, row, col + distance_from_center)
                elif edge_pixel_method == "Wra":
                    imagePixelMatch_value = getPixelWrapped(data, width, height, row, col + distance_from_center)
                else:
                    raise ValueError("Invalid Edge Pixel Method Entered For Convolve1D()")
                # iv. add the weight * neighbor
                new_pixel_value[0] += kernel_value * imagePixelMatch_value[0]
                new_pixel_value[1] += kernel_value * imagePixelMatch_value[1]
                new_pixel_value[2] += kernel_value * imagePixelMatch_value[2]

            # d. calculate the index of the current pixel in row-major order
            curr_pixel_index = width * row + col 
            # e. update the pixel in result with the new RGB values
            for i in range(3):
                if new_pixel_value[i] > 255: new_pixel_value[i] = 255
                elif new_pixel_value[i] < 0: new_pixel_value[i] = 0
                result[curr_pixel_index][i] = new_pixel_value[i]
            # if row <= 1 and col < 10: print(f"--Pixel Row {row}, Col {col} After Row Kernel: {new_pixel_value}")



    # 3. Slide column_kernel vertically to each column of `result`
    #        from left to right column and then update `result`
    #        - NOTE: After doing the convolution with the `row_kernel`, we should use the image data in `result` for this 
    #                next convolution.  
    # a. for each pixel in the image
    print("---Applying Column Kernel---------")
    temp_result = np.copy(result)
    for row in range(height):
        if printing and row % 100 == 0:
            print(f"--- row: {row}")

        for col in range(width):
            # b. calculate the index of the current pixel in row-major order 
            curr_pixel_index = width * row + col

            # c. reset the new pixel value to what the current value is in `result`
            # new_pixel_value = [result[curr_pixel_index][i] for i in range(3)]
            new_pixel_value = [0, 0, 0]

            # d. for each value in the kernel, multiply the weight by the corresponding pixel 
            for index, kernel_value in enumerate(column_kernel):
                # i. skip any kernel elements that have weight 0 
                if kernel_value == 0:
                    continue 
                # ii. get the distance from the center kernel element 
                distance_from_center = kernel_center - index
                # iii. get the corresponding neighbor
                # imagePixelMatch_value = getPixelRepeated(temp_result, width, height, row + distance_from_center, col)
                # iii. get the corresponding neighbor based on edge pixel method
                if edge_pixel_method == "Rep":
                    imagePixelMatch_value = getPixelRepeated(temp_result, width, height, row + distance_from_center, col)
                elif edge_pixel_method == "Ref":
                    imagePixelMatch_value = getPixelReflected(temp_result, width, height, row + distance_from_center, col)
                elif edge_pixel_method == "Wra":
                    imagePixelMatch_value = getPixelWrapped(temp_result, width, height, row + distance_from_center, col)
                else:
                    raise ValueError("Invalid Edge Pixel Method Entered For Convolve1D()")
                # iv. add the weight * neighbor 
                new_pixel_value[0] += kernel_value * imagePixelMatch_value[0]
                new_pixel_value[1] += kernel_value * imagePixelMatch_value[1]
                new_pixel_value[2] += kernel_value * imagePixelMatch_value[2]

            # e. update the pixel in result with the new RGB values
            for i in range(3):
                if new_pixel_value[i] > 255: new_pixel_value[i] = 255
                elif new_pixel_value[i] < 0: new_pixel_value[i] = 0
                result[curr_pixel_index][i] = new_pixel_value[i]
            # if row == 0 and col == 0: print(f"--Pixel 0 After Col Conv Clamping: {new_pixel_value}")

    # return `result` of the original image size
    return result




# Task 11 - Implement Convolve1D with the row and column kernels from 
#                a separable 2D kernel on the input image (i.e., `data`)
def convolve1D_colFirst(data, width, height, row_kernel, column_kernel, edge_pixel_method = 'Rep'):
    # printing bools 
    printing = True
    data = np.array(data, dtype=np.int16) # convert to int16 to allow for neg numbers

    # 1. initialize a 1D array, `result`, to stored the processed image data
    canvas_color = (0, 0, 0, 255) # black color
    result = np.array([canvas_color] * (width * height), dtype=np.int16)

    
    # 3. Slide column_kernel vertically to each column of `result`
    #        from left to right column and then update `result`
    #        - NOTE: After doing the convolution with the `row_kernel`, we should use the image data in `result` for this 
    #                next convolution.  
    # a. for each pixel in the image
    print("---Applying Column Kernel---------")
    kernel_center = len(column_kernel) // 2
    for row in range(height):
        if printing and row % 100 == 0:
            print(f"--- row: {row}")

        for col in range(width):
            # b. calculate the index of the current pixel in row-major order 
            curr_pixel_index = width * row + col

            # c. reset the new pixel value to what the current value is in `result`
            # new_pixel_value = [result[curr_pixel_index][i] for i in range(3)]
            new_pixel_value = [0, 0, 0]

            # d. for each value in the kernel, multiply the weight by the corresponding pixel 
            for index, kernel_value in enumerate(column_kernel):
                # i. skip any kernel elements that have weight 0 
                if kernel_value == 0:
                    continue 
                # ii. get the distance from the center kernel element 
                distance_from_center = kernel_center - index
                # iii. get the corresponding neighbor
                # imagePixelMatch_value = getPixelRepeated(temp_result, width, height, row + distance_from_center, col)
                # iii. get the corresponding neighbor based on edge pixel method
                if edge_pixel_method == "Rep":
                    imagePixelMatch_value = getPixelRepeated(data, width, height, row + distance_from_center, col)
                elif edge_pixel_method == "Ref":
                    imagePixelMatch_value = getPixelReflected(data, width, height, row + distance_from_center, col)
                elif edge_pixel_method == "Wra":
                    imagePixelMatch_value = getPixelWrapped(data, width, height, row + distance_from_center, col)
                else:
                    raise ValueError("Invalid Edge Pixel Method Entered For Convolve1D()")
                # iv. add the weight * neighbor 
                new_pixel_value[0] += kernel_value * imagePixelMatch_value[0]
                new_pixel_value[1] += kernel_value * imagePixelMatch_value[1]
                new_pixel_value[2] += kernel_value * imagePixelMatch_value[2]

            # e. update the pixel in result with the new RGB values
            for i in range(3):
                if new_pixel_value[i] > 255: new_pixel_value[i] = 255
                elif new_pixel_value[i] < 0: new_pixel_value[i] = 0
                result[curr_pixel_index][i] = new_pixel_value[i]
            # if row == 0 and col == 0: print(f"--Pixel 0 After Col Conv Clamping: {new_pixel_value}")



    # 2. Slide row_kernel horizontally to each row of the input image (padded, using repeated method) 
    #           from top to bottom row and then update `result`
    #           - NOTE: Use the original image `data` for this convolution
    temp_result = np.copy(result)
    kernel_center = len(row_kernel) // 2
    print("---Applying Row Kernel---------")
    # a. for each pixel in the image
    for row in range(height):
        if printing and row % 100 == 0:
            print(f"--- row: {row}")

        for col in range(width):
            # b. reset the new pixel value for every pixel
            new_pixel_value = [0, 0, 0]

            # c. for each value in the kernel, multiply the weight by the corresponding pixel
            for index, kernel_value in enumerate(row_kernel):
                # i. skip any kernel elements that have weight 0 
                if kernel_value == 0:
                    continue
                # ii. get the distance from center kernel pixel
                distance_from_center = index - kernel_center
                # iii. get the corresponding neighbor based on edge pixel method
                if edge_pixel_method == "Rep":
                    imagePixelMatch_value = getPixelRepeated(temp_result, width, height, row, col + distance_from_center)
                elif edge_pixel_method == "Ref":
                    imagePixelMatch_value = getPixelReflected(temp_result, width, height, row, col + distance_from_center)
                elif edge_pixel_method == "Wra":
                    imagePixelMatch_value = getPixelWrapped(temp_result, width, height, row, col + distance_from_center)
                else:
                    raise ValueError("Invalid Edge Pixel Method Entered For Convolve1D()")
                # iv. add the weight * neighbor
                new_pixel_value[0] += kernel_value * imagePixelMatch_value[0]
                new_pixel_value[1] += kernel_value * imagePixelMatch_value[1]
                new_pixel_value[2] += kernel_value * imagePixelMatch_value[2]

            # d. calculate the index of the current pixel in row-major order
            curr_pixel_index = width * row + col 
            # e. update the pixel in result with the new RGB values
            for i in range(3):
                if new_pixel_value[i] > 255: new_pixel_value[i] = 255
                elif new_pixel_value[i] < 0: new_pixel_value[i] = 0
                result[curr_pixel_index][i] = new_pixel_value[i]
            # if row <= 1 and col < 10: print(f"--Pixel Row {row}, Col {col} After Row Kernel: {new_pixel_value}")



    # return `result` of the original image size
    return result

# Task 12 - Create a 1D triangle kernel based on any input kernel size (odd number)
def createTriangleKernel(kernel_size):
    # initial a 1D array as the kernel
    kernel = [0 for _ in range(kernel_size)]

    # determine the formula for deriving the weights within the kernel
    centerIndex = kernel_size // 2
    def get_weight(index, centerIndex=centerIndex, kernel_size=kernel_size):
        numerator = -1
        denominator = ((kernel_size // 2) + 1) ** 2
        if index <= centerIndex: 
            numerator = index + 1
        else:
            numerator = centerIndex - (index - centerIndex) + 1
        return numerator / denominator    

    # iterate and fill up the kernel with weights based on the formula in a loop
    for index in range(len(kernel)):
        kernel[index] = get_weight(index)

    # return the kernel
    return kernel


# Task 14 - Create a 1D Gaussian kernel based on an arbitrary input `blur radius``
def createGaussianKernel(blur_radius):
    debugging_prints = True
    if debugging_prints: print(f"-blur_radius = {blur_radius}")

    # compute standard deviation and kernel size based on blur_radius, list your formulas here
    sigma = blur_radius / 3         # standard deviation
    if debugging_prints: print(f"-sigma = {sigma}")
    kernel_side = (6 * sigma)        # we can truncate each side length to this (if we extended, the next values would be very close to 0) (don't account for center pixel)
    if debugging_prints: print(f"-kernel_side = {kernel_side}")
    kernel_size = (kernel_side*2+1)  # entire kernel size
    if debugging_prints: print(f"-kernel_size = {kernel_size}")

    # initial a 1D array as the kernel with kernel size
    kernel = np.zeros(int(kernel_size))

    # iterate and fill up the kernel with weights in a loop based on the Gaussian function
    center_index = len(kernel) // 2
    sum_coeff = 0
    for index in range(len(kernel)):
        # get the distance from the center (sign doesn't matter bc we square it anyways)
        x = index - center_index
        # calculate formula for the coefficient
        coeff = math.exp((-(x ** 2) / (2 * (sigma ** 2))))
        sum_coeff += coeff
        # assign 
        kernel[index] = coeff
    
    # normalize given the sum 
    norm_sum = []
    for index in range(len(kernel)):
        norm_sum.append(kernel[index] * (1 / sum_coeff))
    # norm_form = []
    # if debugging_prints: print(f"-normalizing with 1 / sum \n {norm_sum}")
    # if debugging_prints: print(f"\tsum = {sum(norm_sum)}")
    # normalize given the formula constant
    # constant = 1 / (math.sqrt(2 * math.pi * (sigma ** 2)))
    # for index in range(len(kernel)):
    #     norm_form.append(constant)
    # if debugging_prints: print(f"-normalizing with formula constant \n {norm_form}")
    # if debugging_prints: print(f"\tsum = {sum(norm_form)}")

    for index in range(len(kernel)):
        kernel[index] = norm_sum[index]
    # return the kernel
    return kernel

