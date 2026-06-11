from __future__ import annotations

import os
import cv2
import time

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"

from utils.actuators import IMotorController
from utils.logging import logger
from tests.input import KeyboardListener
from tests.ui import RobotContextHUD


def run_process(context, motors, sandbox: bool = False, debug: bool = False, game=None, robots=None) -> None:
    current_act = "STOP"
    last_dispatched_speed = IMotorController.MEDIUM

    dispatch = {
        "FORWARD":      lambda v: motors.go_forward(v),
        "BACKWARD":    lambda v: motors.go_backward(v),
        "LEFT":  lambda v: motors.go_left(v),
        "RIGHT": lambda v: motors.go_right(v),
        "SPIN LEFT":    lambda v: motors.spin_left(v),
        "SPIN RIGHT":   lambda v: motors.spin_right(v),
        "STOP":         lambda _: motors.stop(),
    }

    logger.msg("Actuator Test Loop started. Focus HUD or Pygame window.")
    cv2.namedWindow("Actuator Test HUD", cv2.WINDOW_AUTOSIZE)

    hud = RobotContextHUD(context, sandbox)
    controller = KeyboardListener(sandbox)

    while controller.running:
        # 1. Update context / simulation
        if sandbox:
            game.step(robots)
            game.render(robots)
            if not game.running:
                controller.running = False
                break
        else:
            context.compute()
            if debug:
                context.show_debug()

        # 2. Get POV debug frame
        last_cam_frame = context.get_debug_frame() if debug and sandbox else None

        # 3. Draw HUD
        hud.update(current_act, controller.speed_name, controller.speed_val, last_cam_frame)
        hud_img = hud.draw()
        cv2.imshow("Actuator Test HUD", hud_img)

        # 4. Input Polling
        controller.poll_inputs()
        
        if not controller.running:
            break

        active_action = controller.active_action
        speed_val = controller.speed_val

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
        from sandbox.game.game import GameController
        from sandbox.game.entities import Robot
        from sandbox.sim_context import SimContext

        logger.msg("Initializing Sandbox Actuator Test...")
        game = GameController(debug=debug, mosaic=True)
        
        ctx = SimContext(debug=debug, name="TestBot", team_color="blue")
        robot = Robot(kickoff_x=300, kickoff_y=200, color=(0, 0, 255), brain=(None, ctx))
        robots = [robot]

        try:
            run_process(ctx, ctx.actuators.motors, sandbox=True, debug=debug, game=game, robots=robots)
        finally:
            cv2.destroyAllWindows()
            game.cleanup()
            logger.msg("Sandbox Actuator Test done.")
    else:
        from robot.aluxe3.context import RobotContext

        logger.msg("Initializing Hardware Actuator Test...")
        ctx = RobotContext()
        motors = ctx.actuators.motors

        try:
            run_process(ctx, motors, sandbox=False, debug=debug)
        except KeyboardInterrupt:
            motors.stop()
        finally:
            ctx.cleanup()
            cv2.destroyAllWindows()
            logger.msg("Hardware Actuator Test done.")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--sandbox", action="store_true")
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()
    run(sandbox=args.sandbox, debug=args.debug)
