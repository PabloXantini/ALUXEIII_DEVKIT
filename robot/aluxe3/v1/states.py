from __future__ import annotations

from utils.logging import logger
from utils.fsm import State
from utils.actuators import Speed
from utils.input import Key
from robot.aluxe3.context.real import RobotContext
import random

# states for Aluxe3v1a

class Search(State):
    """
    Ball Detected -> Align
    Action: Spin to right or left
    """
    def __init__(self):
        super().__init__()
        self.dir = random.uniform(0,1)

    def on_init(self, ctx: RobotContext):
        ctx.estado_label = "Buscando..."
        self.dir = random.uniform(0,1)
 
    def on_exit(self, ctx: RobotContext):
        ctx.actuators.motors.stop()
 
    def execute(self, ctx: RobotContext):
        if self.dir > 0.5:
            ctx.actuators.motors.spin_right()
        else:
            ctx.actuators.motors.spin_left()

class Wait(State):
    def on_init(self, ctx: RobotContext):
        ctx.estado_label = "Esperando..."
 
    def on_exit(self, ctx: RobotContext):
        ctx.actuators.motors.stop()
 
    def execute(self, ctx: RobotContext):
        ctx.actuators.motors.stop()
 
class LookBall(State):
    """
    Ball and Goal Aligned -> AproachToGoal
    Action: compute and align 
    """
    def on_init(self, ctx: RobotContext):
        ctx.estado_label = "Alineando a pelota..."
 
    def on_exit(self, ctx: RobotContext):
        ctx.actuators.motors.stop()
 
    def execute(self, ctx: RobotContext):
        self.align = ctx.info['ball']['offset_x']
        if self.align is None:
            return
        if self.align > 0:
            # Pelota a la derecha en imagen → corregir girando a la derecha
            ctx.state_label = "LookBall -> DER (Ajustando)"
            ctx.actuators.motors.spin_right(vel=Speed.MID_LOW.value)
        else:
            # Pelota a la izquierda en imagen → corregir girando a la izquierda
            ctx.state_label = "LookBall <- IZQ (Ajustando)"
            ctx.actuators.motors.spin_left(vel=Speed.MID_LOW.value)
 
# REVISAR
class GotoBall(State):
    """
    Action: Forward
    """
    def on_init(self, ctx: RobotContext):
        ctx.state_label = "Avanzando..."
 
    def on_exit(self, ctx: RobotContext):
        ctx.actuators.motors.stop()
 
    def execute(self, ctx: RobotContext):
        radius = ctx.info['ball']['radius']
        ctx.estado_label = f"GotoBall: Avanzando (R:{radius})"
        ctx.actuators.motors.go_forward()
 
class LookForShot(State):
    """
    Action: Think.
    """
    def on_init(self, ctx: RobotContext):
        ctx.estado_label = "CERCA! Alineando a porteria"
 
    def on_exit(self, ctx: RobotContext):
        ctx.actuators.motors.stop()
 
    def execute(self, ctx: RobotContext):
        o_ball = ctx.info['ball']['offset_x']
        o_goal = ctx.info['enemy_goal']['offset_x']
        if o_ball is None or o_goal is None:
            return
        self.align = o_ball - o_goal
        if self.align > 0:
            ctx.state_label = f"LookForShot: Derecha (A={self.align})"
            ctx.actuators.motors.go_right()
        else:
            ctx.state_label = f"LookForShot: Izquierda (A={self.align})"
            ctx.actuators.motors.go_left()
 
class GotoEnemyGoal(State):
    """
    Domain the ball
    Action: Forward
    """
    def on_init(self, ctx: RobotContext):
        ctx.state_label = "Avanzando con balon..."
 
    def on_exit(self, ctx: RobotContext):
        ctx.actuators.motors.stop()
 
    def execute(self, ctx: RobotContext):
        radius = ctx.info['ball']['radius']
        ctx.state_label = f"GotoEnemyGoal: Avanzando (R:{radius})"
        ctx.actuators.motors.go_forward()
 
class RedirectBall(State):
    def on_init(self, ctx: RobotContext):
        ctx.state_label = "Redirigiendo pelota..."
 
    def on_exit(self, ctx: RobotContext):
        ctx.actuators.motors.stop()
    
    def execute(self, ctx: RobotContext):
        o_ball = ctx.info['ball']['offset_x']
        if o_ball is None:
            return
        if o_ball > 0:
            ctx.state_label = "RedirectBall -> DER (Redirigiendo)"
            ctx.actuators.motors.go_left()
        else:
            ctx.state_label = "RedirectBall -> IZQ (Redirigiendo)"
            ctx.actuators.motors.go_right()

class AvoidAllyGoal(State):
    def on_init(self, ctx: RobotContext):
        ctx.estado_label = "Evitando a porteria aliada..."

    def on_exit(self, ctx: RobotContext):
        ctx.actuators.motors.stop()
    
    def execute(self, ctx: RobotContext):
        o_ball = ctx.info['ball']['offset_x']
        o_goal = ctx.info['ally_goal']['offset_x']
        if o_goal is None or o_ball is None:
            return
        self.align = o_goal - o_ball
        if self.align > 0:
            ctx.state_label = "AvoidAllyGoal -> DER (Evitando)"
            ctx.actuators.motors.go_right()
        else:
            ctx.state_label = "AvoidAllyGoal -> IZQ (Evitando)"
            ctx.actuators.motors.go_left()

# states for Aluxe3v1b
class SideMoveForShot(State):
    """
    Action: Move for shot.
    """
    def on_init(self, ctx: RobotContext):
        ctx.state_label = "CERCA! Alineando a porteria"
 
    def on_exit(self, ctx: RobotContext):
        ctx.actuators.motors.stop()
 
    def execute(self, ctx: RobotContext):
        o_ball = ctx.info['ball']['offset_x']
        if o_ball is None:
            return
        self.align = o_ball
        if self.align > 0:
            ctx.state_label = f"SideMoveForShot -> Derecha (A={self.align})"
            ctx.actuators.motors.go_right()
        else:
            ctx.state_label = f"SideMoveForShot -> Izquierda (A={self.align})"
            ctx.actuators.motors.go_left()

class Backwards(State):
    def on_init(self, ctx: RobotContext):
        ctx.estado_label = "Atras!"

    def on_exit(self, ctx: RobotContext):
        ctx.actuators.motors.stop()

    def execute(self, ctx: RobotContext):
        ctx.actuators.motors.go_backward()
        
class ManualControl(State):
    """
    Action: Control the robot manually using the InputManager.
    Requires ctx.input_manager to be set.
    """
    def __init__(self):
        super().__init__()
        self.speed = Speed.MEDIUM

    def on_init(self, ctx: RobotContext):
        ctx.estado_label = "Control Manual"

    def on_exit(self, ctx: RobotContext):
        ctx.actuators.motors.stop()

    def execute(self, ctx: RobotContext):
        if ctx.input_manager is None:
            ctx.estado_label = "Sin InputManager!"
            return

        im = ctx.input_manager

        # Speeds
        if im.is_key_pressed(Key.K_1): self.speed = Speed.LOW
        if im.is_key_pressed(Key.K_2): self.speed = Speed.MID_LOW
        if im.is_key_pressed(Key.K_3): self.speed = Speed.MEDIUM
        if im.is_key_pressed(Key.K_4): self.speed = Speed.MID_HIGH
        if im.is_key_pressed(Key.K_5): self.speed = Speed.HIGH
        if im.is_key_pressed(Key.UP) or im.is_key_pressed(Key.W): logger.msg("FORWARD")
        if im.is_key_pressed(Key.DOWN) or im.is_key_pressed(Key.S): logger.msg("BACKWARD")
        if im.is_key_pressed(Key.LEFT) or im.is_key_pressed(Key.A): logger.msg("GO LEFT")
        if im.is_key_pressed(Key.RIGHT) or im.is_key_pressed(Key.D): logger.msg("GO RIGHT")
        if im.is_key_pressed(Key.Z): logger.msg("SPIN LEFT")
        if im.is_key_pressed(Key.X): logger.msg("SPIN RIGHT")
        
        # Movement
        v_val = self.speed.value
        if im.is_key_held(Key.SPACE):
            ctx.actuators.motors.stop()
        elif im.is_key_held(Key.W) or im.is_key_held(Key.UP):
            ctx.actuators.motors.go_forward(vel=v_val)
        elif im.is_key_held(Key.S) or im.is_key_held(Key.DOWN):
            ctx.actuators.motors.go_backward(vel=v_val)
        elif im.is_key_held(Key.A) or im.is_key_held(Key.LEFT):
            ctx.actuators.motors.go_left(vel=v_val)
        elif im.is_key_held(Key.D) or im.is_key_held(Key.RIGHT):
            ctx.actuators.motors.go_right(vel=v_val)
        elif im.is_key_held(Key.Z):
            ctx.actuators.motors.spin_left(vel=v_val)
        elif im.is_key_held(Key.X):
            ctx.actuators.motors.spin_right(vel=v_val)
        else:
            ctx.actuators.motors.stop()