# ALUXE III Development Kit - Autonomous Soccer Robot 🤖⚽

ALUXE III is an autonomous robotics project designed to create an omnidirectional vehicle capable of playing soccer, powered by a Finite State Machine (FSM). 

This repository serves as the "brain" of the robot, integrating physics, complex game rules, and a high-fidelity **2.5D/3D Simulation Environment (Sandbox)**. The sandbox allows for testing autonomous behaviors using synthetic Computer Vision, eliminating the need for physical hardware during the development and tuning phases.

---

## 🚀 Features

### Agent Behavior (FSM)
- **FSM Implementation**: Stateful machine architecture allowing complex behaviors like `Search`, `LookBall`, `GotoBall`, and `Stop`.
- **Context-Aware Decisions**: Robots evaluate the field, opponent positions, and ball trajectory in real-time.

### Kinematics & Physics
- **Omnidirectional Movement**: Optimized vector math for 360° fluid motion, including lateral sweeping and diagonal charging.
- **Physical Realism**: Simulation of friction, restitution (bounciness), wall collisions, and multi-agent occlusions. 

### Vision & Rendering Engine
- **Hybrid Rendering Pipeline**: Choose between a lightweight **OpenCV (Python)** renderer or a high-performance **OpenGL (C++)** engine.
- **GPU-Accelerated Effects**:
    - **Fisheye Distortion**: Real-time barrel deformation to mimic wide-angle physical lenses.
    - **Motion Blur**: Temporal accumulation for realistic high-speed movement visualization.
- **3D Geometry**: Advanced primitives (cylinders, complex goal meshes) for accurate visual occlusion and perspective.

>  **Note**: Motion Blur is only available in the OpenGL render implementation. 

### Competitive Match Rules
- **Official Ruleset**: Implementation of halves, scoring, and time limits.
- **Penalties & Banishing**: Automatic handling of "Out of Bounds", "Illegal Defense", and "Ball Inactivity" penalties.
- **Dynamic Kickoffs**: Intelligent positioning for initial and neutral kickoffs based on team possession and previous penalties.

---

## Project Structure

The project is divided into three main layers:

1.  **`sandbox/game`**: The core simulation logic.
    -   `physics.py`: Collision resolution and movement integration.
    -   `match_rules.py`: Game states, scoring, and robot penalties.
    -   `entities.py`: Data models for Robots, Balls, and the Pitch.
2.  **`sandbox/vision_cpp`**: High-performance C++ rendering engine.
    -   Compiled via `pybind11` for seamless Python integration.
    -   Uses modern OpenGL for GPU-based image processing.
3.  **`utils/`**: Behavioral implementation.
    -   Location for custom FSM states and robot-specific logic.

---

## 📦 Requirements and Installation

**Python 3.10+** is required. Install dependencies via:

```bash
pip install numpy opencv-python pygame pybind11
```

### 🛠 Building C++ Extensions
To enable the high-performance OpenGL renderer, you must compile the C++ module:

1.  **Close the simulation** to unlock the binary files.
2.  Run the compilation command:
```bash
cd sandbox/vision_cpp
python setup.py build_ext --inplace
```
*(Requires **MSVC** on Windows or **GCC/Clang** on Linux/Mac).*

---

## 🎮 Execution Modes

Run the project using `alux.py` with the following arguments:

### 1. Hardware Mode (Real-World)
For deployment on a Raspberry Pi with physical motors and camera.
```bash
python alux.py
```

### 2. Sandbox Mode (Full Simulation)
Launches the Pygame 2D environment and the autonomous agents.
```bash
python alux.py --sandbox
```

### 3. Debug Mode (Visual Insights)
Reveals the "eyes" of the robots and their internal states.
```bash
# Combine with sandbox for full experience
python alux.py --sandbox --debug
```
- **Mosaic View**: Shows all virtual cameras in a single grid (Default).
- **Split View**: Use `--split-cams` to open individual windows for each camera.

---

## ⌨️ Sandbox Controls

-   **Mouse Left-Click**: Grab and drag the ball.
-   **Mouse Release**: Throw the ball to simulate impacts.
-   **`Q` Key**: Gracefully terminate the simulation.
-   **`Enter` Key**: Restart the match after "Game Over".

---

### 4. VSCode Integration
This repository comes with a pre-configured `.vscode/tasks.json` file. You can effortlessly run the simulation commands directly from the IDE Tasks menu:
- Open the Command Palette (`Ctrl+Shift+P` or `Cmd+Shift+P`).
- Type and select **`Tasks: Run Task`**.
- Select your preferred task profile from the dropdown menu:
  - `Run` (Hardware mode)
  - `Run Debug` (Hardware mode with Virtual Camera)
  - `Run Sandbox` (Full 2D Simulation with Virtual Cameras)

## 🛠 Scaling the Intelligence

To create new robot behaviors:

1.  **Define States**: Create a class inheriting from `fsm.State`.
2.  **Define Rules**: Create logic inheriting from `fsm.Rule` to trigger transitions.
3.  **Build Machine**: Use `fsm.MachineBuilder` to connect states and rules.
4.  **Register**: Update `alux.py` to use your new builder.

Example state structure:
```python
from fsm import State

class MyCustomState(State):
    def on_init(self, ctx:RobotContext):
        print("Entering behavior...")

    def on_exit(self, ctx:RobotContext):
        print("Exiting behavior...")

    def execute(self, ctx:RobotContext):
        # Move forward using context actuators
```

Example rule structure:
```python
from fsm import Rule

class MyCustomRule(Rule):
    def applies(self, ctx:RobotContext) -> bool:
        return True
```
