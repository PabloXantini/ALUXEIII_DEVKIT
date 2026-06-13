from __future__ import annotations
import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"

from utils.actuators import Speed
from utils.logging import logger
from tests.ui import RobotContextHUD
from sandbox.game.game import GameController
import runners.process as proc
import cv2

def run_test(sandbox: bool = False, debug: bool = False, input_manager=None) -> None:
    if input_manager is None:
        import utils.input as inputs
        input_manager = inputs.init(sandbox, debug)

    import tests.matchs as matchs
    machine, ctx, robots = matchs.prepare_test(debug=debug, sandbox=sandbox)
    ctx.input_manager = input_manager

    # Setup HUD
    cv2.namedWindow("Actuator Test HUD", cv2.WINDOW_AUTOSIZE)
    hud = RobotContextHUD(ctx, sandbox)

    def draw_hud():
        last_cam_frame = ctx.get_debug_frame() if debug else None
        speed = machine.cstate.speed if hasattr(machine.cstate, 'speed') else Speed.MEDIUM
        hud.update("MANUAL FSM", f"{speed.name}", speed.value, last_cam_frame)
        cv2.imshow("Actuator Test HUD", hud.draw())

    if sandbox:
        logger.msg("Initializing Sandbox Actuator Test...")
        game = GameController(debug=debug, mosaic=True)
        try:
            proc.run_sandbox_proc(game, robots, input_manager, debug, on_step=draw_hud)
        finally:
            cv2.destroyAllWindows()
            game.cleanup()
            logger.msg("Sandbox Actuator Test done.")
    else:
        logger.msg("Initializing Hardware Actuator Test...")
        try:
            proc.run_device_proc(machine, ctx, input_manager, debug, on_step=draw_hud)
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
    run_test(sandbox=args.sandbox, debug=args.debug)
