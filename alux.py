"""
alux.py – Robot de fútbol con FSM
==================================
Para añadir un nuevo comportamiento:
  1. Crea un State en utils/r_states.py
  2. Crea las Rule(s) en utils/r_rules.py
  3. Construye tu FSM en build_machine() abajo
"""

from __future__ import annotations

import cv2
import argparse
from robot.aluxe3.v1.builder import Aluxe3v1aBuilder


def _run_test(args) -> None:
    import tests.robot_test as rtest
    rtest.run(sandbox=args.sandbox, debug=args.debug)


def _run_sandbox(args) -> None:
    import tests.matchs as matchs
    from sandbox.game.game import GameController

    game   = GameController(debug=args.debug, mosaic=not args.split_cams)
    robots = matchs.prepare_2v2(debug=args.debug, sandbox=args.sandbox)

    try:
        while game.running:
            game.step(robots)
            game.render(robots)
            if args.debug:
                game.show_virtual_cameras(robots)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    game.running = False
    except KeyboardInterrupt:
        pass
    finally:
        game.cleanup()
        cv2.destroyAllWindows()


def _run_robot(args) -> None:
    b = Aluxe3v1aBuilder()
    machine, ctx = b.build_machine(debug=args.debug, sandbox=False)

    try:
        while ctx.running:
            ctx.compute()
            machine.run(ctx)
            ctx.show_debug()
            if args.debug:
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break
    except KeyboardInterrupt:
        pass
    finally:
        ctx.cleanup()


def main() -> None:
    parser = argparse.ArgumentParser(description="Robot Agent Alpha 1")
    parser.add_argument("--debug",      action="store_true", help="Enable debug mode (UI)")
    parser.add_argument("--sandbox",    action="store_true", help="Run FSM in Pygame 2D simulator")
    parser.add_argument("--split-cams", action="store_true", help="Show individual camera windows instead of mosaic")
    parser.add_argument("--test",       action="store_true", help="Run manual actuator hardware test suite")
    args = parser.parse_args()

    if args.test:
        _run_test(args)
    elif args.sandbox:
        _run_sandbox(args)
    else:
        _run_robot(args)


if __name__ == "__main__":
    main()
