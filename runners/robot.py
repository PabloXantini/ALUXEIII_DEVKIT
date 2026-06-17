from __future__ import annotations
import runners.process as proc

def run_robot(debug: bool, input_manager) -> None:
    from robot.aluxe3.v1.builder import Aluxe3v1aBuilder
    from robot.aluxe3 import manifest as m1
    from utils.resources import model
    from utils.resources import workspace

    ma3 = model.load_model(m1.MODEL_DIR, m1.ROBOT_MODEL)
    ws = workspace.load_workspace(m1.WORKSPACE_DIR, m1.WORKSPACE_ENV, m1.CONFIG_DIR)
    a3v1a = Aluxe3v1aBuilder(ma3, ws)
    machine, ctx = a3v1a.build_machine(debug=debug, sandbox=False)
    ctx.input_manager = input_manager

    proc.run_device_proc(machine, ctx, input_manager, debug)
    
    ctx.cleanup()
