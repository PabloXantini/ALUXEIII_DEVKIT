# ALUXE III Development Kit - Autonomous Soccer Robot 🤖⚽

ALUXE III is an autonomous robotics project designed to create an omnidirectional vehicle capable of playing soccer, powered by a Finite State Machine (FSM). 

This repository hosts the complete logic of the "brain" and features an **Advanced 2.5D Simulation Environment (Sandbox)** that allows you to test and polish the robot's autonomous responses using synthetic Computer Vision without the need to have the physical hardware connected.

---

## 🚀 Features

- **Omnidirectional Kinematics**: Factored mathematics for forward, backward, and lateral sweeping movements using force vectors.
- **FSM Implementation**: Fully modularized cognitive stateful structure eg. (`Search`, `LookBall`, `GotoBall`, `Stop`).
- **Computer Vision Integrated**: Morphology, HSV masking, and contour tracking via OpenCV.
- **100% Sandbox Environment**:
  - Physics simulator supporting friction, wall bouncing, and occlusion between multiple agents.
  - 2.5D "Virtual Camera Engine" to recreate the physical camera and render object inside the simulation.
  - Computationally generated Fisheye Lens Barrel Distortion to maximize the realism of the physical sensors.

## 📦 Requirements and Installation

The repository is built on **Python 3.10+**. 
Install the main graphics and matrix computation libraries by running:

```bash
pip install numpy opencv-python pygame pybind11
```

### 🛠 Building C++ Extensions (OpenGL Renderer)
To ensure maximum performance in the simulation, the vision engine and mathematical components are written in C++ using OpenGL. If you modify any file in the C++ renderer (like `renderer.cpp` or `fast_math.cpp`), you must recompile the module:

1. **Close the simulation** (the `.pyd` file must be unlocked to be overwritten).
2. Run the compilation command:
```bash
cd sandbox/vision_cpp
python setup.py build_ext --inplace
```
*(Note: This requires a C++ compiler. On Windows, ensure you have **Visual Studio Build Tools (MSVC)** installed).*

---
*(Note: The engine automatically injects a mock simulation for the `RPi.GPIO` library to prevent dependency crashes when coding from environments like Windows or Mac).*

---

## 🎮 Execution Modes

The core of the project is orchestrated from the `alux.py` file. It features console arguments ready to be used:

### 1. Hardware Deployment (Real Mode)
Ideal for use inside the Raspberry Pi once physical tests are cleared. It will execute the code straight to the `L298N` motor drivers utilizing the physical camera.
```bash
python alux.py
```

### 2. Cross-Testing Sandbox Environment
Boots the Pygame window simulation where shows **the robot agents simulation instances** (currently blue and yellow robots) that they will fight for the ball.
```bash
python alux.py --sandbox
```
* **Interactivity**: You can use your mouse cursor to grab the ball, drag it, and throw it to simulate physical variables.

### 3. Visual Debugging Mode
Append the `--debug` flag to transparently reveal the robots' visual field of view.

If executed in Sandbox mode, it will simultaneously open the *synthetic virtual cameras* frames. Here you can mathematically evaluate the robots' blindness by occluding their field of view with the opponent and admire their panoramic *Fisheye* geometric deformation:

```bash
# Hardware/Real Camera Debug
python alux.py --debug

# Complete Simulator (Pygame + Multiple Computer Vision Cameras)
python alux.py --sandbox --debug
```

*(To gracefully terminate any of the visual processes, simply press the `Q` key while focusing the debugging screen).*

### 4. VSCode Integration
This repository comes with a pre-configured `.vscode/tasks.json` file. You can effortlessly run the simulation commands directly from the IDE Tasks menu:
- Open the Command Palette (`Ctrl+Shift+P` or `Cmd+Shift+P`).
- Type and select **`Tasks: Run Task`**.
- Select your preferred task profile from the dropdown menu:
  - `Run` (Hardware mode)
  - `Run Debug` (Hardware mode with Virtual Camera)
  - `Run Sandbox` (Full 2D Simulation with Virtual Cameras)

---

## 🛠 Scaling the Intelligence
You could create a folder for new robots behaviors in the `utils` folder
1. Put it a atractive name: eg. `aluxe3`
2. Create the Python modules for rules and state inside in
3. Use the `fsm` module for create new states, rules, context
4. Optionally can create another folder (eg. v1, v2, etc.) for differentiate behavior implementations.

### How to create an State
1. Import the `fsm` module in project root
2. Implement the class `State`

### How to create an Rule
1. Import the `fsm` module in project root
2. Implement the class `Rule`

### How hook my states and rules
1. Import the `fsm` module in project root
2. Implement the class `MachineBuilder`
3. Use the `build_machine` method for build you own machine
 
