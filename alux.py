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
import utils.input as inputs
from robot.aluxe3.v1.builder import Aluxe3v1aBuilder

class AluxeApp:
    def __init__(self, args) -> None:
        self.args = args
        self.input = inputs.init(sandbox=args.sandbox, debug=args.debug)
        self.machine, self.ctx = None, None

    def run(self) -> None:
        if self.args.test:
            self.run_test()
        elif self.args.sandbox:
            self.run_sandbox()
        else:
            self.run_robot()

    def run_test(self) -> None:
        import tests.robot_test as rtest
        rtest.run(sandbox=self.args.sandbox, debug=self.args.debug)

    def run_sandbox(self) -> None:
        import tests.matchs as matchs
        from sandbox.game.game import GameController

        game   = GameController(debug=self.args.debug, mosaic=not self.args.split_cams)
        robots = matchs.prepare_2v2(debug=self.args.debug, sandbox=self.args.sandbox)

        try:
            while game.running:
                game.step(robots)
                game.render(robots)
                if self.args.debug:
                    game.show_virtual_cameras(robots)
                if self.input.poll() in (27, ord('q')):
                    game.running = False
        except KeyboardInterrupt:
            pass
        finally:
            game.cleanup()
            cv2.destroyAllWindows()
    def run_robot(self) -> None:
        b = Aluxe3v1aBuilder()
        machine, ctx = b.build_machine(debug=self.args.debug, sandbox=False)

        try:
            while ctx.running:
                ctx.compute()
                machine.run(ctx)
                ctx.show_debug()
                if self.args.debug and self.input.poll() in (27, ord('q')):
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
    app = AluxeApp(args)
    app.run()

if __name__ == "__main__":
    main()
