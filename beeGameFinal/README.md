# The Bee Game

**An OpenGL + Pygame "Race-Against-the-Clock" Game**

Spring 2025 • Natalie Huante • CPSC 515: Advanced Computer Graphics

**Quick Links**

* [Play The Bee Game Here]()
* [The Bee Game Presentation](https://www.canva.com/design/DAGnmDYIDQo/C7kUFL_jMfZ9g7deil8AjA/edit?utm_content=DAGnmDYIDQo&utm_campaign=designshare&utm_medium=link2&utm_source=sharebutton)
* [3d Visualisation of All Moth Paths](https://www.desmos.com/3d/fb2pxzfkns)


---

## Motivation  

I’m taking an advanced computer graphics course and wanted to explore Pygame + OpenGL by building a project that ties together everything we’ve learned this semester including geometric transforms, scene graphs, dynamic cameras, collision detection using AABB, custom OBJ loading, multithreaded loading screens, and more.

---

## Environment  

This project was developed and tested in the course Conda environment. I activate it locally by running the following command:  
```bash
conda activate cpsc515
```
To recreate it locally, see the below two sections.

---


## Dependencies 

All core graphics functionality uses only NumPy, Pygame, and PyOpenGL. Additional helper libraries include:

| Library  | Version    | Install Command                               |
| -------- | ---------- | --------------------------------------------- |
| numpy    | `>=1.24.4` | `pip install numpy`                           |
| pygame   | `>=2.5.2`  | `pip install pygame`                          |
| PyOpenGL | `>=3.1.6`  | `pip install PyOpenGL`    |

You can also find all required installs in the `requirements.txt` file.

---


## How to Run Locally (By Downloadable Executable/App)

1. **Download the .exe or .app release in the `releases` folder without downloading or installing any dependencies**  

  * **Windows**
    * download the `TheBeeGame-Windows.zip`, unzip the folder, and double-click the .exe file 
  * **Mac'Linux**
    * download the `TheBeeGame-Macos.zip`, unzip the folder, and double-click the .app file 

2. **OR Download the most-recent verson from [Itch.io]()**  

---


## How to Run Locally (By Cloning the Repo)

1. **Clone the repo**  

   ```bash
   git clone https://github.com/nhuante/ImageProcessing_Graphics_Python.git
   cd beeGameFinal
   ```

2. **Create & Activate a Virtual Environment** 

This is not *entirely* necessary, but it is best practice to do so to avoid 
* Polluting your system Python, which might lead to version conflicts later if you start another project that needs a different version of, say, `pygame` or `numpy`

    ```bash
        python3 -m venv .venv       # or `python -m venv .venv` on Windows
        source .venv/bin/activate   # or `.venv\Scripts\activate`
    ```

3. **Install Dependencies**

Make sure you have `pip >= 20.3` then:
    ```bash
        pip install -r requirements.txt
    ```

4. **Run the Game**
*(Make sure you are in the root directory of the repo)*

    ```bash
        python ./beeGameFinal/beeGame_main.py
    ```


---

## Game Concept and Objective 

You play as a friendly, hard-working bee who must collect pollen and return it to the hive before time runs out. 

There are two "rooms" in the game you will enocunter:

* **Lobby**: Practice controls and read the help screen.
* **Level 1**: You have 120 seconds to
    * Collect pollen from flowers
    * Avoid or attack moth enemies (+points if you’re “angry,” –health if you’re not)
    * Deliver pollen to the beehive (+20 points per drop-off)
* **Win/Lose**: Reach 100 points to win; health ≤ 0 → loss.


--- 

## Player Controls - Look Up Table 
Use the below chart to navigate game controls.

| Key                       | Action                                           | Continuous?        |
| -----------------         | ------------------------------------------------ | :---------:        |
| **Movement**              |                                                  |                    |
| `←` / `→` / `↑` / `↓`     | Turn & fly forward/back/left, right              |      ✔️            |
| `Left Shift` / `Left Ctrl`| Ascend / Descend                                 |      ✔️            |
| **Camera**                |                                                  |                    |
| `W`/`A`/`S`/`D`           | Pan camera up/left/down/right                    |      ✔️            |
| `Q`/`E`                   | Zoom in / out                                    |      ✔️            |
| **View Modes**            |                                                  |                    |
| `Space`                   | Cycle: Third-person → First-person → …           |      ❌            |
| `0`                       | Reset camera in current view mode                |      ❌            |
| **Game**                  |                                                  |                    |
| `P`                       | Pause / Unpause                                  |      ❌            |
| `Z`                       | Activate “Angry” speed burst (once per recharge) |      ❌            |
| `X`/`C`                   | Pick up / Drop off pollen particle               |      ❌            |
| **UI Interaction**        |                                                  |                    |
| `Mouse`                   | Click GUI Buttons                                |      ❌            |



---

## Developer-Mode Controls - Look Up Table 
*(Press **Delete** to toggle developer mode)*

| Key | Effect                                           |
| --- | ------------------------------------------------ |
| 1   | ↓ Animation speed                                |
| 2   | ↑ Animation speed                                |
| 3   | ↓ Fly (walk) speed multiplier                    |
| 4   | ↑ Fly (walk) speed multiplier                    |
| 5   | ↓ Bee health by 20                               |
| 6   | ↑ Score by 50                                    |
| 7   | Toggle showing AABB colliders                    |
| 8   | Regenerate flower positions                      |
| 9   | Crash the game (throws an error to test “Uh-Oh”) |
| u   | Place the bee in front of corner camera 1 for better visualization when presenting or debugging bee mechanics |

---


## Potential Additions 

* Deploy to website 
* More complex difficulty levels and more levels 
    * Idea 1 - Pre-defined number of levels that the user can play through that is hooked up to a level select screen. The user should be able to replay any level they have already completed or play the current highest level that they have not yet completed. The user's overall score should be cached through their play time. 
    * Idea 2 - Endless "runner" mode with a personal high score. The user will play until they lose their health, with each next level being randomly generated (in terms of the enemies and props). The user's personal best should be cached so they can play multiple times and keep the highest score of all their runs. 
* Additional garden decor and interactable objects 
    * Idea 1 - Wind tunnel that gives a temporary boost to the player bee (mario-kart arrow boost style)
    * Idea 2 - Thorns on some flowers that harm the player bee if they collide with them 
    * Idea 3 - Different types of flowers whose pollen give different benefits to the player
    * Idea 4 - A prop (such as a bird bath) where the player can go and regenerate their health 
* New enemy types, power-ups, puzzles, etc. to keep the player engaged, challenged, and learning. 
* Two-Player/Co-Op Mode (would require some looking into servers)
* Sound/Music
* Attack Animations + More Character Animations

---

## Challenges & Takeaways

**Biggest Challenges**
* Refactoring and debugging OBJ file loader 
* Building a responsive, mulithreaded loading screen 
* Pausing and maintaing accurate countdown timers 
* Implementing robust AABB collision detection

**Key Takeaways**
* How grateful I am to have game engines like Unity and Unreal that make creating and manipulating 2d and 3d environments so easy! And that optimize the game environment very well.
* I feel now I understand how some of these tools would be implemented within the engine and can help me be a better designer and developer. 
* First time I have used pygame and openGL to create complete projects and I enjoyed it. 

---

## References
* [Clamping Floats in Python](https://stackoverflow.com/questions/9775731/clamping-floating-numbers-in-python)
* [Readme Formatting](https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax#links)
* [RGB Values - Shades of Blue](https://www.rapidtables.com/web/color/blue-color.html)
* [Minecraft Bee Inspo](https://minecraft.wiki/w/Bee)
* [Type Casting for Funciton Parameters](https://stackoverflow.com/questions/2489669/how-do-python-functions-handle-the-types-of-parameters-that-you-pass-in)
* [GLUT Bitmap Fonts](https://www.opengl.org/resources/libraries/glut/spec3/node76.html)
* [GLUT Solid Sphere Function](https://www.opengl.org/resources/libraries/glut/spec3/node81.html)
* [3d Graphing Tool to Visualize Paths](https://www.desmos.com/3d)
* [3d Visualisation of All Moth Paths](https://www.desmos.com/3d/fb2pxzfkns)
* [RGB 0-1 Color Picker](https://rgbcolorpicker.com/0-1)
* [Photoshop Express Adobe Desktop Version](https://new.express.adobe.com)
* [Rendering Images in PyGame and OpenGL](https://www.reddit.com/r/pygame/comments/17ob2qc/texturing_in_pyopengl_and_pygame/)
* 