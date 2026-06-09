from __future__ import annotations

from utils.fsm import State
from robot.aluxe3.context import RobotContext
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
            ctx.actuators.motors.spin_slow_left()
        else:
            # Pelota a la izquierda en imagen → corregir girando a la izquierda
            ctx.state_label = "LookBall <- IZQ (Ajustando)"
            ctx.actuators.motors.spin_slow_right()
 
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
        ctx.actuators.motors.go_forward(vel=ctx.actuators.motors.HIGH)
 
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
            ctx.actuators.motors.go_left(vel=ctx.actuators.motors.HIGH)
        else:
            ctx.state_label = "RedirectBall -> IZQ (Redirigiendo)"
            ctx.actuators.motors.go_right(vel=ctx.actuators.motors.HIGH)

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
            ctx.actuators.motors.go_right(vel=ctx.actuators.motors.HIGH)
        else:
            ctx.state_label = "AvoidAllyGoal -> IZQ (Evitando)"
            ctx.actuators.motors.go_left(vel=ctx.actuators.motors.HIGH)

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
   
    