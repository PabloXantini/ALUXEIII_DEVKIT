"""
alux.py - Robot de fútbol con FSM
==================================
Para añadir un nuevo comportamiento:
  1. Crea un State en utils/r_states.py
  2. Crea las Rule(s) en utils/r_rules.py
  3. Construye tu FSM en build_machine() abajo
"""

from __future__ import annotations

import argparse
import runners
import utils.input as inputs

class AluxeApp:
    def __init__(self, args) -> None:
        self.args = args
        self.input = inputs.init(sandbox=args.sandbox, debug=args.debug)

    def run(self) -> None:        
        if self.args.test:
            runners.run_test(
                sandbox=self.args.sandbox, 
                debug=self.args.debug, 
                input_manager=self.input
            )
        elif self.args.sandbox:
            runners.run_sandbox(
                debug=self.args.debug,
                sandbox=self.args.sandbox,
                split_cams=self.args.split_cams,
                input_manager=self.input
            )
        else:
            runners.run_robot(
                debug=self.args.debug, 
                input_manager=self.input
            )

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
