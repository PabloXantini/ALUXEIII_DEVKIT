from __future__ import annotations
import runners.process as proc

def run_robot(debug: bool, input_manager) -> None:
    from robot.aluxe3.v1.builder import Aluxe3v1aBuilder

    a3v1a = Aluxe3v1aBuilder()
    machine, ctx = a3v1a.build_machine(debug=debug, sandbox=False)
    ctx.input_manager = input_manager

    proc.run_device_proc(machine, ctx, input_manager, debug)
    
    ctx.cleanup()
