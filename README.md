# Image Processing & Graphics Projects in Python

Welcome! This repository contains two graphics projects developed using Python for a computer graphics course. 
- Project 1 focuses on 2D image filters using convolution
- Project 2 builds and animates a 3D scarecrow character using OpenGL
- The final project aims on combining topics from throughout the semester to create an interactive game and focuses on OpenGL as a means to implement collision detection, transformations, obj file loading, and more. 

---

## Project Descriptions

### Project 1: Filters
**Goal** - Implementations of several image filters and convolution techniques using NumPy and PyGame. 
Includes:
- Grayscale conversion (luma, average, lightness)
- Color inversion
- Brightness adjustment with overflow handling
- Shift filters using 2D convolution
- Sobel edge detection
- Triangle and Gaussian blur with 1D convolution

📄 To Read About the Implementation: [`Project1_Filters_Report.pdf`](project1/Project1_Filters_Report.pdf)

---

### Project 2: Transformation & Viewing
**Goal** - 3D animation project using OpenGL and PyGame to build, animate, and control a scarecrow model. 
Includes:
- Scene graph hierarchy for transformations
- Walk-in-place and freeform walking animation
- Interactive camera views (front, side, back, first-person)
- Dynamic camera tilt and zoom
- Keyboard-controlled movement and animation speed

📄 To Read About the Implementation: [`Project2_Transform_Viewing_Report.pdf`](project2/Project2_Transform_Viewing_Report.pdf)

---

### Final Project: The Bee Game
**Goal** - An open-ended interactive 3D game combining raster/image effects, OpenGL scene graph animation, dynamic camera control, collision detection, and simple gameplay (collect & deposit pollen, avoid enemies).
Includes:
- Articulated bee character with wing, leg, stinger, and pupil animations
- Freeform & first-person camera modes, plus tilt/zoom controls
- Scene objects: grass, flowers, beehive, moth enemies
- Collect pollen and deposit at hive to score; timed level & win/lose conditions
- Developer mode: adjust speeds, toggle bounding boxes, force-regenerate flowers

📄 To Read About the Project: [`beeGameFinal/README.md`](beeGameFinal/README.md)

---

## ▶️ Running the Projects

### Prerequisites
Make sure you have Python 3 and the following packages installed:

```bash
pip install numpy pygame PyOpenGL
