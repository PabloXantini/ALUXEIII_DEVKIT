from __future__ import annotations

import cv2
import runners.process as proc

def run_sandbox(debug: bool, sandbox: bool, split_cams: bool, input_manager) -> None:
    import tests.matchs as matchs
    from sandbox.game.game import GameController

    game = GameController(debug=debug, mosaic=not split_cams)
    robots = matchs.prepare_2v2(debug=debug, sandbox=sandbox)

    proc.run_sandbox_proc(game, robots, input_manager, debug)
    
    game.cleanup()
    cv2.destroyAllWindows()
