from __future__ import annotations
from sandbox.game.game import GameController
from utils.fsm import Machine
from utils.input import Key, InputManager
import time

def run_sandbox_proc(game:GameController, robots, input_manager: InputManager, debug: bool, on_step=None) -> None:
    try:
        while game.running:
            game.step(robots)
            game.render(robots)
            if debug:
                game.show_virtual_cameras(robots)
            if on_step:
                on_step()
            input_manager.poll(1)
            if input_manager.is_key_pressed(Key.Q) or input_manager.is_key_pressed(Key.ESC):
                game.running = False
    except KeyboardInterrupt:
        pass

def run_device_proc(machine:Machine, context, input_manager:InputManager, debug: bool, on_step=None) -> None:
    try:
        while context.running:
            context.compute()
            machine.run(context)
            if debug:
                context.show_debug()
            if on_step:
                on_step()
            input_manager.poll(1)
            if input_manager.is_key_pressed(Key.Q) or input_manager.is_key_pressed(Key.ESC):
                break
            time.sleep(0.03)
    except KeyboardInterrupt:
        pass
