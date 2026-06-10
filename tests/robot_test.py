
from __future__ import annotations

import os
import cv2
import time
import numpy as np

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"
import pygame

# Color palette for HUD (matching hardware test aesthetics)
C_BG        = (23,  17,  14)       # Dark background (BGR: Dark Navy/Blue)
C_PANEL     = (34,  27,  22)       # Panel background (BGR)
C_BORDER    = (65,  50,  40)       # Border color (BGR)
C_ACCENT    = (255, 180, 80)       # Accent color (BGR: light blue/cyan)
C_GREEN     = (120, 220, 80)       # Green (BGR)
C_YELLOW    = (60,  210, 255)      # Yellow (BGR)
C_RED       = (80,  80,  255)      # Red (BGR)
C_GRAY      = (145, 130, 120)      # Gray (BGR)
C_WHITE     = (245, 235, 230)      # White (BGR)

from utils.actuators import IMotorController
from utils.logging import logger

_CV_SPEED_LEVELS = {
    ord('1'): ("LOW",      IMotorController.LOW),
    ord('2'): ("MID_LOW",  IMotorController.MID_LOW),
    ord('3'): ("MEDIUM",   IMotorController.MEDIUM),
    ord('4'): ("MID_HIGH", IMotorController.MID_HIGH),
    ord('5'): ("HIGH",     IMotorController.HIGH),
}

_CV_MOVE_KEYS = {
    ord('w'): "FORWARD",
    ord('s'): "BACKWARD",
    ord('a'): "STRAFE LEFT",
    ord('d'): "STRAFE RIGHT",
    ord('z'): "SPIN LEFT",
    ord('x'): "SPIN RIGHT",
    ord(' '): "STOP",
}

_PYGAME_SPEED_LEVELS = {
    pygame.K_1: ("LOW",      IMotorController.LOW),
    pygame.K_2: ("MID_LOW",  IMotorController.MID_LOW),
    pygame.K_3: ("MEDIUM",   IMotorController.MEDIUM),
    pygame.K_4: ("MID_HIGH", IMotorController.MID_HIGH),
    pygame.K_5: ("HIGH",     IMotorController.HIGH),
}

_PYGAME_MOVE_KEYS = {
    pygame.K_w: "FORWARD",
    pygame.K_s: "BACKWARD",
    pygame.K_a: "STRAFE LEFT",
    pygame.K_d: "STRAFE RIGHT",
    pygame.K_z: "SPIN LEFT",
    pygame.K_x: "SPIN RIGHT",
    pygame.K_SPACE: "STOP",
}




def draw_hud(action: str, speed_name: str, speed_val: int, context, last_cam_frame, sandbox: bool) -> np.ndarray:
    # Create an OpenCV frame for the HUD
    hud_w, hud_h = 600, 500
    hud = np.zeros((hud_h, hud_w, 3), dtype=np.uint8)
    hud[:] = C_BG

    # 1. Header Title
    mode_str = "Sandbox" if sandbox else "Hardware"
    cv2.putText(hud, f"ALUXE III - Actuator {mode_str} Test HUD", (20, 35),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, C_ACCENT, 2, cv2.LINE_AA)
    cv2.line(hud, (20, 50), (hud_w - 20, 50), C_BORDER, 1)

    # 2. Status Panel (Action, Speed, Heading)
    cv2.rectangle(hud, (20, 65), (hud_w - 20, 165), C_PANEL, -1)
    cv2.rectangle(hud, (20, 65), (hud_w - 20, 165), C_BORDER, 1)
    
    act_color = C_GREEN if action != "STOP" else C_GRAY
    cv2.putText(hud, f"Action : {action}", (35, 95),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, act_color, 1, cv2.LINE_AA)
    cv2.putText(hud, f"Speed  : {speed_name} ({speed_val}%)", (35, 125),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, C_YELLOW, 1, cv2.LINE_AA)
    
    heading = context.env.heading
    cv2.putText(hud, f"Heading: {heading:6.1f} deg", (320, 95),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, C_WHITE, 1, cv2.LINE_AA)

    # 3. Sensor Panel (Ultrasonic Distances)
    cv2.rectangle(hud, (20, 180), (hud_w - 20, 260), C_PANEL, -1)
    cv2.rectangle(hud, (20, 180), (hud_w - 20, 260), C_BORDER, 1)
    cv2.putText(hud, "Ultrasonic Distances", (35, 205),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, C_GRAY, 1, cv2.LINE_AA)

    def format_dist(v: float) -> str:
        return f"{v:5.1f} cm" if v >= 0 else "TIMEOUT"

    dist_l = context.env.us_left_dist
    dist_b = context.env.us_back_dist
    dist_r = context.env.us_right_dist

    cv2.putText(hud, f"LEFT: {format_dist(dist_l)}", (35, 235),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, C_WHITE, 1, cv2.LINE_AA)
    cv2.putText(hud, f"BACK: {format_dist(dist_b)}", (220, 235),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, C_WHITE, 1, cv2.LINE_AA)
    cv2.putText(hud, f"RIGHT: {format_dist(dist_r)}", (410, 235),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, C_WHITE, 1, cv2.LINE_AA)

    # 4. Embedded Camera Stream
    if last_cam_frame is not None:
        cam_h, cam_w = 160, 200
        resized = cv2.resize(last_cam_frame, (cam_w, cam_h))
        cv2.rectangle(hud, (35, 295), (35 + cam_w + 2, 295 + cam_h + 2), C_BORDER, 1)
        hud[296:296+cam_h, 36:36+cam_w] = resized
        cv2.putText(hud, "Camera Feed (POV)", (35, 285),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, C_GRAY, 1, cv2.LINE_AA)

    # 5. Instructions panel
    cv2.rectangle(hud, (260, 295), (hud_w - 20, 455), C_PANEL, -1)
    cv2.rectangle(hud, (260, 295), (hud_w - 20, 455), C_BORDER, 1)
    cv2.putText(hud, "Controls Info", (275, 320),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, C_GRAY, 1, cv2.LINE_AA)
    cv2.putText(hud, "WASD : Move", (275, 345),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, C_WHITE, 1, cv2.LINE_AA)
    cv2.putText(hud, "Q/E  : Spin Left/Right", (275, 370),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, C_WHITE, 1, cv2.LINE_AA)
    cv2.putText(hud, "SPACE: Stop", (275, 395),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, C_WHITE, 1, cv2.LINE_AA)
    cv2.putText(hud, "1-5  : Change Speed", (275, 420),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, C_WHITE, 1, cv2.LINE_AA)

    # 6. Exit text
    exit_msg = "Focus OpenCV HUD or Pygame. Press ESC to exit." if sandbox else "Focus OpenCV HUD. Press ESC to exit."
    cv2.putText(hud, exit_msg, (20, 485),
                cv2.FONT_HERSHEY_SIMPLEX, 0.45, C_GRAY, 1, cv2.LINE_AA)

    return hud


def run_test_loop(context, motors, sandbox: bool = False, debug: bool = False, game=None, robots=None) -> None:
    speed_name = "MEDIUM"
    speed_val = IMotorController.MEDIUM
    current_act = "STOP"
    last_dispatched_speed = IMotorController.MEDIUM

    dispatch = {
        "FORWARD":      lambda v: motors.go_forward(v),
        "BACKWARD":    lambda v: motors.go_backward(v),
        "STRAFE LEFT":  lambda v: motors.go_left(v),
        "STRAFE RIGHT": lambda v: motors.go_right(v),
        "SPIN LEFT":    lambda v: motors.spin_left(v),
        "SPIN RIGHT":   lambda v: motors.spin_right(v),
        "STOP":         lambda _: motors.stop(),
    }

    logger.msg("Actuator Test Loop started. Focus HUD or Pygame window.")
    cv2.namedWindow("Actuator Test HUD", cv2.WINDOW_AUTOSIZE)

    last_cv_key_time = time.time()
    last_cv_action = None

    running = True
    while running:
        # 1. Update context / simulation
        if sandbox:
            game.step(robots)
            game.render(robots)
            if not game.running:
                running = False
                break
        else:
            context.compute()

        # 2. Get POV debug frame
        last_cam_frame = context.get_debug_frame()

        # 3. Draw HUD
        hud_img = draw_hud(current_act, speed_name, speed_val, context, last_cam_frame, sandbox)
        cv2.imshow("Actuator Test HUD", hud_img)

        # 4. Input Polling
        active_action = "STOP"
        pygame_speed = None
        pygame_action = None

        # -- Poll Pygame (if sandbox)
        if sandbox:
            pressed = pygame.key.get_pressed()
            
            # check speed keys
            for p_key, (name, val) in _PYGAME_SPEED_LEVELS.items():
                if pressed[p_key]:
                    pygame_speed = (name, val)

            # check movement keys
            for p_key, act in _PYGAME_MOVE_KEYS.items():
                if pressed[p_key]:
                    pygame_action = act
            
            if pygame_speed is not None:
                speed_name, speed_val = pygame_speed
            
            if pygame_action is not None:
                active_action = pygame_action

        # -- Poll OpenCV
        cv_key = cv2.waitKey(1) & 0xFF
        cv_speed = None
        cv_action = None

        if cv_key == 27:  # ESC
            running = False
            break
        elif cv_key != 255:
            last_cv_key_time = time.time()
            if cv_key in _CV_SPEED_LEVELS:
                cv_speed = _CV_SPEED_LEVELS[cv_key]
            elif cv_key in _CV_MOVE_KEYS:
                cv_action = _CV_MOVE_KEYS[cv_key]

        if cv_speed is not None:
            speed_name, speed_val = cv_speed

        if cv_action is not None:
            active_action = cv_action
            last_cv_action = cv_action
        elif cv_key == 255:
            # OpenCV watchdog (keep action for 250ms unless Pygame overrides it)
            if last_cv_action is not None and (time.time() - last_cv_key_time < 0.25):
                if active_action == "STOP":
                    active_action = last_cv_action
            else:
                last_cv_action = None

        # 5. Dispatch Motor commands if changed or speed updated
        if (active_action != current_act) or (speed_val != last_dispatched_speed and active_action != "STOP"):
            current_act = active_action
            last_dispatched_speed = speed_val
            dispatch[active_action](speed_val)
            logger.msg(f"Motors -> {active_action} @ {speed_val}%")

        # In physical mode, we throttle CPU
        if not sandbox:
            time.sleep(0.03)
        elif debug:
            game.show_virtual_cameras(robots)

    motors.stop()
    logger.msg("Actuator Test Loop ended.")


def run(sandbox: bool = False, debug: bool = False) -> None:
    if sandbox:
        from sandbox.sim_cache import SimState
        from sandbox.game.game import GameController
        import tests.matchs as matchs

        logger.msg("Initializing Sandbox Actuator Test...")
        game = GameController(debug=debug, mosaic=True)
        robots = matchs.prepare_solo(debug=debug, sandbox=True)

        if not robots:
            logger.error("No simulated robot prepared.")
            game.cleanup()
            return

        robot = robots[0]
        context = robot.context
        motors = context.actuators.motors

        # Disable autonomy/FSM behavior but keep sensor compute
        def custom_update(self_robot, game_ctrl, other_robots=None):
            if self_robot.ban_timer > 0:
                self_robot.ban_timer -= 1.0 / 60.0
                if self_robot.ban_timer < 0:
                    self_robot.ban_timer = 0
                return
            
            sim_state = SimState(
                ball=game_ctrl.ball,
                robots=other_robots or [],
                goals=[game_ctrl.ally_goal, game_ctrl.enemy_goal],
                pitch=game_ctrl.pitch
            )
            self_robot.context.compute(sim_state)
            
            # Sync sensor states
            self_robot.context.env.heading = self_robot.context.actuators.psensor.get_heading()
            self_robot.context.env.us_left_dist = self_robot.context.actuators.us_left.get_distance()
            self_robot.context.env.us_back_dist = self_robot.context.actuators.us_back.get_distance()
            self_robot.context.env.us_right_dist = self_robot.context.actuators.us_right.get_distance()

        robot.update = lambda game_ctrl, other_robots=None: custom_update(robot, game_ctrl, other_robots)

        try:
            run_test_loop(context, motors, sandbox=True, debug=debug, game=game, robots=robots)
        finally:
            cv2.destroyAllWindows()
            game.cleanup()
            logger.msg("Sandbox Actuator Test done.")
    else:
        from robot.aluxe3.context import RobotContext

        logger.msg("Initializing Hardware Actuator Test...")
        # Pygame is required for physical mode to initialize internally or if used elsewhere
        pygame.init()
        ctx = RobotContext()
        motors = ctx.actuators.motors

        try:
            run_test_loop(ctx, motors, sandbox=False, debug=debug)
        except KeyboardInterrupt:
            motors.stop()
        finally:
            ctx.cleanup()
            pygame.quit()
            cv2.destroyAllWindows()
            logger.msg("Hardware Actuator Test done.")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--sandbox", action="store_true")
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()
    run(sandbox=args.sandbox, debug=args.debug)
