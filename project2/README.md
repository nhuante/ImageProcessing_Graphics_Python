# Project 2: 3D Transformations & Viewing

This project demonstrates hierarchical modeling and animated transformations in 3D using OpenGL and PyGame. A scarecrow character is built using scene graph logic and animated with walking cycles, camera control, and interactive keyboard navigation.

---

## Features

- Scene Graph for Hierarchical Transformations
- Character Animations: Walk-In Place, Freeform Walking
- Dynamic Camera Control: Tilt, Zoom, Different View Modes
- First-Person View (FPV) Integration
- Scarecrow Character Creation

---

## Input/Output
All interactions will be handled through keyboard input. Use the below chart to navigate character controls.

| Key        | Action                                                             | Continuous? |
|------------|--------------------------------------------------------------------|-------------|
| `i` / `o`  | Rotate scarecrow’s head left / right                              | ✅          |
| `u`        | Toggle between basic and upgraded scarecrow versions              | ❌          |
| `l`        | Toggle walk-in-place animation                                     | ❌          |
| `r`        | Toggle freeform walking mode                                       | ❌          |
| `←` / `→`  | Turn scarecrow left / right during freeform walk                  | ✅          |
| `a` / `d`  | Tilt camera left / right                                           | ✅          |
| `w` / `s`  | Tilt camera up / down                                              | ✅          |
| `q` / `e`  | Zoom camera in / out (along gaze direction)                        | ✅          |
| `space`    | Cycle through camera views (front, side, back, first-person)      | ❌          |
| `0`        | Reset camera to original position and orientation                 | ❌          |
| `1` / `2`  | Decrease / increase limb swing speed                               | ❌          |
| `3` / `4`  | Decrease / increase walk speed multiplier                          | ❌          |
| `5`        | Reset scarecrow to origin and default movement parameters          | ❌          |

---

## ▶️ How to Run

1. Navigate to the project folder:
```bash
cd Project2_Transform_Viewing
```
2. Run the main program:
```bash
python P2_transformView_main_BLANK.py # for windows
python3 P2_transformView_main_BLANK.py # for mac
```
3. Make sure you have the required libraries installed:
```bash
pip install numpy pygame PyOpenGL
``` 
