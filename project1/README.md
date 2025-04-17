# Project 1: Image Filters

This project explores image processing techniques using Python, NumPy, and PyGame. A graphical user interface allows users to apply various filters to images and view results instantly. The focus is on developing a foundational understanding of image convolution and filter behavior.

---

## Features

- Grayscale Conversion:
  - Luma
  - Average
  - Lightness
- Color Inversion
- Brightness Adjustment (handles overflow)
- Shift Filters using 2D convolution
- Sobel Edge Detection (with 1D convolution)
- Triangle & Gaussian Blur (with 1D separable convolution)

---

## Input/Output
Most interactions will be handled through the GUI system. There are buttons that can be clicked to activate each filter. 
There may be some occasional output in the terminal that indicates the time each filter took to compute. If this is not of interest to you, you may focus your attention on the GUI. 

_Note: Some filters are more time-costly than others, so be sure to wait sufficiently for the program to "think" before the modified image is shown in the GUI._

---

## ▶️ How to Run

1. Navigate to the project folder:
```bash
cd Project1_Filters
```
2. Run the main program:
```bash
python P1_filter_main_BLANK.py # for windows
python3 P1_filter_main_BLANK.py # for mac
```
3. Make sure you have the required libraries installed:
```bash
pip install numpy pygame
``` 
